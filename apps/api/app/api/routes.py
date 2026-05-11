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

router = APIRouter(prefix="/api")


@router.get("/health", summary="健康检查")
def health_check() -> dict[str, str]:
    """用于确认后端服务是否正常启动。"""

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
