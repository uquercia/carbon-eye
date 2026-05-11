from sqlalchemy import func, select
from sqlalchemy.orm import Session

from apps.api.app.models import (
    BehaviorImpact,
    BehaviorScore,
    Building,
    EnergyPrediction,
    RecognitionSample,
    TrainingImage,
)
from apps.api.app.schemas.dashboard import (
    BehaviorScoreOut,
    BuildingOut,
    DashboardOut,
    DashboardSummaryOut,
    TrendPointOut,
)


def get_latest_buildings(db: Session) -> list[BuildingOut]:
    """查询每栋楼最新时间步的水电预测数据。

    CSV 里同一栋楼会有多个时间步。页面表格只需要当前最新一批数据，
    所以这里先找到最大 time_step，再取这个时间步的所有楼栋记录。
    """

    latest_step = db.scalar(select(func.max(EnergyPrediction.time_step)))
    if latest_step is None:
        return []

    rows = db.execute(
        select(Building, EnergyPrediction)
        .join(EnergyPrediction, EnergyPrediction.building_id == Building.id)
        .where(EnergyPrediction.time_step == latest_step)
        .order_by(Building.name)
    ).all()

    return [
        BuildingOut(
            id=building.id,
            name=building.name,
            zone=building.zone,
            major=building.major,
            electricity_actual=prediction.electricity_actual,
            electricity_predicted=prediction.electricity_predicted,
            water_actual=prediction.water_actual,
            water_predicted=prediction.water_predicted,
            electricity_error=prediction.electricity_error,
            water_error=prediction.water_error,
            map_x=building.map_x,
            map_y=building.map_y,
        )
        for building, prediction in rows
    ]


def get_trends(db: Session) -> list[TrendPointOut]:
    """按时间步汇总所有楼栋的实际值和预测值，供折线图使用。"""

    rows = db.execute(
        select(
            EnergyPrediction.time_step,
            func.sum(EnergyPrediction.electricity_actual),
            func.sum(EnergyPrediction.electricity_predicted),
            func.sum(EnergyPrediction.water_actual),
            func.sum(EnergyPrediction.water_predicted),
        )
        .group_by(EnergyPrediction.time_step)
        .order_by(EnergyPrediction.time_step)
    ).all()

    return [
        TrendPointOut(
            time_step=time_step,
            electricity_actual=electricity_actual or 0,
            electricity_predicted=electricity_predicted or 0,
            water_actual=water_actual or 0,
            water_predicted=water_predicted or 0,
        )
        for (
            time_step,
            electricity_actual,
            electricity_predicted,
            water_actual,
            water_predicted,
        ) in rows
    ]


def get_dashboard(db: Session) -> DashboardOut:
    """组装首页需要的全部数据，前端只调一个接口即可渲染驾驶舱。"""

    buildings = get_latest_buildings(db)
    trends = get_trends(db)
    behavior_scores = [
        BehaviorScoreOut(major_name=item.major_name, total_score=item.total_score)
        for item in db.scalars(select(BehaviorScore).order_by(BehaviorScore.major_code)).all()
    ]
    recognition_samples = db.scalars(select(RecognitionSample).order_by(RecognitionSample.id)).all()
    behavior_impacts = db.scalars(select(BehaviorImpact).order_by(BehaviorImpact.id)).all()
    training_images = db.scalars(select(TrainingImage).order_by(TrainingImage.id)).all()

    latest = trends[-1] if trends else None
    avg_behavior = (
        sum(item.total_score for item in behavior_scores) / len(behavior_scores)
        if behavior_scores
        else 0
    )

    summary = DashboardSummaryOut(
        electricity_actual_total=latest.electricity_actual if latest else 0,
        electricity_predicted_total=latest.electricity_predicted if latest else 0,
        water_actual_total=latest.water_actual if latest else 0,
        water_predicted_total=latest.water_predicted if latest else 0,
        average_behavior_score=avg_behavior,
        building_count=len(buildings),
        recognition_count=len(recognition_samples),
    )

    return DashboardOut(
        summary=summary,
        buildings=buildings,
        behavior_scores=behavior_scores,
        trends=trends,
        recognition_samples=list(recognition_samples),
        behavior_impacts=list(behavior_impacts),
        training_images=list(training_images),
    )
