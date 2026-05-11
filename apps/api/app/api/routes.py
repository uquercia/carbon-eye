from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from apps.api.app.core.config import get_settings
from apps.api.app.db.session import get_db
from apps.api.app.schemas.dashboard import (
    BehaviorImpactOut,
    BuildingOut,
    DashboardOut,
    RecognitionSampleOut,
    TrainingImageOut,
    TrendPointOut,
    UploadImageResponse,
)
from apps.api.app.services.dashboard_service import get_dashboard, get_latest_buildings, get_trends
from apps.api.app.models import (
    BehaviorImpact,
    RecognitionResult,
    RecognitionSample,
    RecognitionTask,
    TrainingImage,
    UploadedImage,
)
from apps.api.app.services.storage_service import save_upload_file
from apps.api.app.services.vision_service import analyze_image_with_vision_model

# APIRouter 用来集中管理一组接口。
# prefix="/api" 表示这里的接口地址都会自动带上 /api 前缀。
# 例如下面写的是 /health，真实访问地址就是 /api/health。
router = APIRouter(prefix="/api")


@router.get("/health", summary="健康检查")
def health_check() -> dict[str, str]:
    """用于确认后端服务是否正常启动。

    这个接口不查数据库，只要能返回 {"status": "ok"}，
    就说明 FastAPI 服务本身已经启动。
    """

    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardOut, summary="获取驾驶舱全部数据")
def read_dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    """首页主接口。

    前端驾驶舱需要很多数据：楼栋表格、趋势图、训练图片、环保提示等。
    如果让前端分别请求很多接口会比较乱，所以这里提供一个聚合接口。
    """

    return get_dashboard(db)


@router.get("/buildings", response_model=list[BuildingOut], summary="获取楼栋最新水电数据")
def read_buildings(db: Session = Depends(get_db)) -> list[BuildingOut]:
    """返回右侧楼栋表格和中间地图节点需要的数据。"""

    return get_latest_buildings(db)


@router.get("/trends", response_model=list[TrendPointOut], summary="获取水电趋势")
def read_trends(db: Session = Depends(get_db)) -> list[TrendPointOut]:
    """返回底部用电/用水趋势图需要的数据。"""

    return get_trends(db)


@router.get("/recognition-samples", response_model=list[RecognitionSampleOut], summary="获取识别行为样例")
def read_recognition_samples(db: Session = Depends(get_db)) -> list[RecognitionSampleOut]:
    """返回识别行为样例。

    当前这些数据是演示数据。后续接入真实图片上传和模型推理后，
    这里可以改成返回某个上传任务的真实识别结果。
    """

    return list(db.query(RecognitionSample).order_by(RecognitionSample.id).all())


@router.get("/behavior-impacts", response_model=list[BehaviorImpactOut], summary="获取行为影响说明")
def read_behavior_impacts(db: Session = Depends(get_db)) -> list[BehaviorImpactOut]:
    """返回环保行为提示。

    页面在用户还没有上传图片时，不应该直接给出“已识别结果”，
    所以先展示这些通用提示，等上传图片分析完成后再展示具体影响。
    """

    return list(db.query(BehaviorImpact).order_by(BehaviorImpact.id).all())


@router.get("/training-images", response_model=list[TrainingImageOut], summary="获取训练结果图片")
def read_training_images(db: Session = Depends(get_db)) -> list[TrainingImageOut]:
    """返回训练完成后的图片或图表，用于页面训练结果展示区。"""

    return list(db.query(TrainingImage).order_by(TrainingImage.id).all())


@router.post("/uploads/images", response_model=UploadImageResponse, summary="上传校园图片并创建识别任务")
def upload_campus_image(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadImageResponse:
    """上传校园图片。

    当前流程：
    1. 保存图片到本地 uploads 目录。
    2. 在 uploaded_images 表记录图片 URL。
    3. 创建 recognition_tasks 任务。
    4. 如果已经配置视觉大模型，就调用模型并写入 recognition_results。
    5. 如果没配置模型，就返回 pending_model_config，让前端提示等待配置。
    """

    settings = get_settings()
    try:
        object_key, public_url, file_size = save_upload_file(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    uploaded_image = UploadedImage(
        original_filename=file.filename or "校园图片",
        stored_filename=object_key,
        storage_type=settings.storage_backend,
        object_key=object_key,
        public_url=public_url,
        content_type=file.content_type or "application/octet-stream",
        file_size=file_size,
    )
    db.add(uploaded_image)
    db.flush()

    task = RecognitionTask(
        image_id=uploaded_image.id,
        status="pending_model_config",
        model_provider=settings.vision_provider if settings.vision_api_key else "none",
        model_name=settings.vision_model,
        error_message="未配置视觉大模型 API Key，已完成图片保存，等待后续分析。",
    )
    db.add(task)
    db.flush()

    results: list[RecognitionResult] = []
    if settings.vision_api_key and settings.vision_model:
        try:
            task.status = "running"
            db.flush()

            image_path = Path(settings.upload_dir) / object_key
            model_results = analyze_image_with_vision_model(image_path)
            for item in model_results:
                result = RecognitionResult(
                    task_id=task.id,
                    behavior_name=str(item.get("behavior_name", "未知行为")),
                    location_name=str(item.get("location_name", "未知位置")),
                    confidence=float(item.get("confidence", 0)),
                    impact_summary=str(item.get("impact_summary", "模型未给出影响说明")),
                    electricity_delta_kwh=float(item.get("electricity_delta_kwh", 0)),
                    water_delta_m3=float(item.get("water_delta_m3", 0)),
                )
                db.add(result)
                results.append(result)
            task.status = "succeeded"
            task.error_message = ""
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error_message = f"视觉模型调用失败：{exc}"

    db.commit()
    db.refresh(uploaded_image)
    db.refresh(task)
    for result in results:
        db.refresh(result)

    message = "图片已上传，等待配置视觉大模型后分析。"
    if task.status == "succeeded":
        message = "图片已上传，并已完成视觉大模型分析。"
    if task.status == "failed":
        message = task.error_message

    return UploadImageResponse(image=uploaded_image, task=task, results=results, message=message)
