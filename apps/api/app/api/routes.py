from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from apps.api.app.db.session import get_db
from apps.api.app.schemas.dashboard import (
    BehaviorImpactOut,
    BuildingOut,
    DashboardOut,
    RecognitionSampleOut,
    TrainingImageOut,
    TrendPointOut,
)
from apps.api.app.services.dashboard_service import get_dashboard, get_latest_buildings, get_trends
from apps.api.app.models import BehaviorImpact, RecognitionSample, TrainingImage

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
