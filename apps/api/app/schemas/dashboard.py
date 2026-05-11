from pydantic import BaseModel, ConfigDict


class BuildingOut(BaseModel):
    """楼栋及最新水电预测数据。"""

    id: str
    name: str
    zone: str
    major: str
    electricity_actual: float
    electricity_predicted: float
    water_actual: float
    water_predicted: float
    electricity_error: float
    water_error: float
    map_x: float
    map_y: float


class BehaviorScoreOut(BaseModel):
    """专业低碳行为得分。"""

    major_name: str
    total_score: float


class TrendPointOut(BaseModel):
    """某个时间步的总用电/用水趋势点。"""

    time_step: int
    electricity_actual: float
    electricity_predicted: float
    water_actual: float
    water_predicted: float


class RecognitionSampleOut(BaseModel):
    """识别行为样例。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    behavior_name: str
    location_name: str
    building_id: str
    confidence: float
    impact_level: str
    impact_summary: str
    electricity_delta_kwh: float
    water_delta_m3: float
    image_url: str


class BehaviorImpactOut(BaseModel):
    """行为影响规则。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    behavior_name: str
    category: str
    description: str
    electricity_factor: float
    water_factor: float


class TrainingImageOut(BaseModel):
    """训练结果图片。"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    image_url: str
    description: str


class DashboardSummaryOut(BaseModel):
    """驾驶舱汇总数据。"""

    electricity_actual_total: float
    electricity_predicted_total: float
    water_actual_total: float
    water_predicted_total: float
    average_behavior_score: float
    building_count: int
    recognition_count: int


class DashboardOut(BaseModel):
    """前端首页一次性需要的数据。"""

    summary: DashboardSummaryOut
    buildings: list[BuildingOut]
    behavior_scores: list[BehaviorScoreOut]
    trends: list[TrendPointOut]
    recognition_samples: list[RecognitionSampleOut]
    behavior_impacts: list[BehaviorImpactOut]
    training_images: list[TrainingImageOut]
