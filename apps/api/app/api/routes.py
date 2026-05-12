from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from apps.api.app.core.config import get_settings
from apps.api.app.db.session import SessionLocal, get_db
from apps.api.app.models import (
    BehaviorImpact,
    RecognitionResult,
    RecognitionSample,
    RecognitionTask,
    TrainingImage,
    UploadedImage,
)
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
from apps.api.app.services.storage_service import save_upload_file
from apps.api.app.services.vision_service import (
    UNCERTAIN_BEHAVIOR_NAME,
    UNCERTAIN_RECOGNITION_TIPS,
    analyze_image_with_vision_model,
)

router = APIRouter(prefix="/api")

TERMINAL_TASK_STATUSES = {"succeeded", "failed", "pending_model_config"}
TASK_STAGE_LABELS = {
    "queued": "已入队",
    "running": "视觉识别中",
    "succeeded": "识别完成",
    "failed": "识别失败",
    "pending_model_config": "等待模型配置",
}
TASK_PROGRESS = {
    "queued": 28,
    "running": 76,
    "succeeded": 100,
    "failed": 100,
    "pending_model_config": 100,
}


def _build_result_tips(results: list[RecognitionResult], task: RecognitionTask) -> list[str]:
    if task.status == "pending_model_config":
        return [
            "当前云端已完成上传，但还需要可用的视觉模型配置后才能给出真实识别结果。",
            "建议优先拍到人物与灯、空调、水龙头、插线板等设备的明确交互动作。",
        ]

    if any(result.behavior_name == UNCERTAIN_BEHAVIOR_NAME for result in results):
        return UNCERTAIN_RECOGNITION_TIPS

    if results:
        return [
            "如需更稳定识别，建议尽量让关键设备完整入镜，并减少逆光、模糊和遮挡。",
        ]

    if task.status == "failed":
        return [
            "本次识别失败，可重新上传更清晰的图片，或检查视觉模型服务配置是否正常。",
        ]

    return []


def _build_task_message(task: RecognitionTask, results: list[RecognitionResult]) -> str:
    if task.status == "queued":
        return "图片已上传，正在排队进入识别任务。"
    if task.status == "running":
        return "图片已上传，视觉模型正在分析中。"
    if task.status == "succeeded" and results:
        return "图片已上传，并已完成视觉识别与影响分析。"
    if task.status == "pending_model_config":
        return "图片已上传，但当前尚未完成视觉模型配置。"
    if task.status == "failed":
        return task.error_message or "视觉模型调用失败。"
    return "图片已上传，等待后续分析。"


def _serialize_task_response(
    uploaded_image: UploadedImage,
    task: RecognitionTask,
    results: list[RecognitionResult],
) -> UploadImageResponse:
    return UploadImageResponse(
        image=uploaded_image,
        task=task,
        results=results,
        message=_build_task_message(task, results),
        progress=TASK_PROGRESS.get(task.status, 0),
        stage=TASK_STAGE_LABELS.get(task.status, "处理中"),
        tips=_build_result_tips(results, task),
    )


def _process_recognition_task(task_id: int) -> None:
    settings = get_settings()
    with SessionLocal() as db:
        task = db.get(RecognitionTask, task_id)
        if task is None:
            return

        uploaded_image = db.get(UploadedImage, task.image_id)
        if uploaded_image is None:
            task.status = "failed"
            task.error_message = "未找到关联的上传图片记录。"
            task.finished_at = datetime.utcnow()
            db.commit()
            return

        if not settings.vision_api_key or not settings.vision_model:
            task.status = "pending_model_config"
            task.error_message = "未配置视觉大模型 API Key 或模型名称。"
            task.finished_at = datetime.utcnow()
            db.commit()
            return

        try:
            task.status = "running"
            task.error_message = ""
            db.commit()

            image_path = Path(settings.upload_dir) / uploaded_image.object_key
            model_results = analyze_image_with_vision_model(image_path)

            db.query(RecognitionResult).filter(RecognitionResult.task_id == task.id).delete()
            db.flush()

            for item in model_results:
                db.add(
                    RecognitionResult(
                        task_id=task.id,
                        behavior_name=str(item.get("behavior_name", "未知行为")),
                        location_name=str(item.get("location_name", "未知位置")),
                        confidence=float(item.get("confidence", 0)),
                        impact_summary=str(item.get("impact_summary", "模型未给出影响说明")),
                        electricity_delta_kwh=float(item.get("electricity_delta_kwh", 0)),
                        water_delta_m3=float(item.get("water_delta_m3", 0)),
                    )
                )

            task.status = "succeeded"
            task.error_message = ""
            task.finished_at = datetime.utcnow()
            db.commit()
        except Exception as exc:  # noqa: BLE001
            task.status = "failed"
            task.error_message = f"视觉模型调用失败：{exc}"
            task.finished_at = datetime.utcnow()
            db.commit()


def _load_task_bundle(db: Session, task_id: int) -> tuple[UploadedImage, RecognitionTask, list[RecognitionResult]]:
    task = db.get(RecognitionTask, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="未找到识别任务")

    uploaded_image = db.get(UploadedImage, task.image_id)
    if uploaded_image is None:
        raise HTTPException(status_code=404, detail="未找到上传图片记录")

    results = (
        db.query(RecognitionResult)
        .filter(RecognitionResult.task_id == task.id)
        .order_by(RecognitionResult.id)
        .all()
    )
    return uploaded_image, task, results


@router.get("/health", summary="健康检查")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/dashboard", response_model=DashboardOut, summary="获取驾驶舱全部数据")
def read_dashboard(db: Session = Depends(get_db)) -> DashboardOut:
    return get_dashboard(db)


@router.get("/buildings", response_model=list[BuildingOut], summary="获取楼栋最新水电数据")
def read_buildings(db: Session = Depends(get_db)) -> list[BuildingOut]:
    return get_latest_buildings(db)


@router.get("/trends", response_model=list[TrendPointOut], summary="获取水电趋势")
def read_trends(db: Session = Depends(get_db)) -> list[TrendPointOut]:
    return get_trends(db)


@router.get("/recognition-samples", response_model=list[RecognitionSampleOut], summary="获取识别行为样例")
def read_recognition_samples(db: Session = Depends(get_db)) -> list[RecognitionSampleOut]:
    return list(db.query(RecognitionSample).order_by(RecognitionSample.id).all())


@router.get("/behavior-impacts", response_model=list[BehaviorImpactOut], summary="获取行为影响说明")
def read_behavior_impacts(db: Session = Depends(get_db)) -> list[BehaviorImpactOut]:
    return list(db.query(BehaviorImpact).order_by(BehaviorImpact.id).all())


@router.get("/training-images", response_model=list[TrainingImageOut], summary="获取训练结果图片")
def read_training_images(db: Session = Depends(get_db)) -> list[TrainingImageOut]:
    return list(db.query(TrainingImage).order_by(TrainingImage.id).all())


@router.get("/uploads/tasks/{task_id}", response_model=UploadImageResponse, summary="查询识别任务状态")
def get_upload_task(task_id: int, db: Session = Depends(get_db)) -> UploadImageResponse:
    uploaded_image, task, results = _load_task_bundle(db, task_id)
    return _serialize_task_response(uploaded_image, task, results)


@router.post("/uploads/images", response_model=UploadImageResponse, summary="上传校园图片并创建识别任务")
def upload_campus_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> UploadImageResponse:
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

    has_model_config = bool(settings.vision_api_key and settings.vision_model)
    task = RecognitionTask(
        image_id=uploaded_image.id,
        status="queued" if has_model_config else "pending_model_config",
        model_provider=settings.vision_provider if settings.vision_api_key else "none",
        model_name=settings.vision_model,
        error_message="" if has_model_config else "未配置视觉大模型 API Key，已完成图片保存。",
    )
    db.add(task)
    db.commit()
    db.refresh(uploaded_image)
    db.refresh(task)

    if has_model_config:
        background_tasks.add_task(_process_recognition_task, task.id)

    return _serialize_task_response(uploaded_image, task, [])
