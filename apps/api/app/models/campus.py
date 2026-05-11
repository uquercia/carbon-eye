from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.app.db.session import Base


class Building(Base):
    """校园楼栋基础表。"""

    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(40), nullable=False)
    major: Mapped[str] = mapped_column(String(40), nullable=False)
    map_x: Mapped[float] = mapped_column(Float, nullable=False)
    map_y: Mapped[float] = mapped_column(Float, nullable=False)

    predictions: Mapped[list["EnergyPrediction"]] = relationship(back_populates="building")


class EnergyPrediction(Base):
    """楼栋某个时间步的实际/预测用水用电数据。"""

    __tablename__ = "energy_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    time_step: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    building_id: Mapped[str] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    electricity_actual: Mapped[float] = mapped_column(Float, nullable=False)
    electricity_predicted: Mapped[float] = mapped_column(Float, nullable=False)
    water_actual: Mapped[float] = mapped_column(Float, nullable=False)
    water_predicted: Mapped[float] = mapped_column(Float, nullable=False)
    electricity_error: Mapped[float] = mapped_column(Float, nullable=False)
    water_error: Mapped[float] = mapped_column(Float, nullable=False)

    building: Mapped[Building] = relationship(back_populates="predictions")


class BehaviorScore(Base):
    """问卷聚合后的专业低碳行为得分。"""

    __tablename__ = "behavior_scores"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    major_code: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    major_name: Mapped[str] = mapped_column(String(40), nullable=False)
    light_off_score: Mapped[float] = mapped_column(Float, nullable=False)
    charger_unplug_score: Mapped[float] = mapped_column(Float, nullable=False)
    daylight_score: Mapped[float] = mapped_column(Float, nullable=False)
    plug_unplug_score: Mapped[float] = mapped_column(Float, nullable=False)
    faucet_off_score: Mapped[float] = mapped_column(Float, nullable=False)
    shower_short_score: Mapped[float] = mapped_column(Float, nullable=False)
    laundry_batch_score: Mapped[float] = mapped_column(Float, nullable=False)
    repair_report_score: Mapped[float] = mapped_column(Float, nullable=False)
    total_score: Mapped[float] = mapped_column(Float, nullable=False)


class RecognitionSample(Base):
    """识别结果样例表。

    现在先用“训练完成后的示例数据”填充，后面接入真实模型后可直接写入真实识别结果。
    """

    __tablename__ = "recognition_samples"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    behavior_name: Mapped[str] = mapped_column(String(80), nullable=False)
    location_name: Mapped[str] = mapped_column(String(80), nullable=False)
    building_id: Mapped[str] = mapped_column(ForeignKey("buildings.id"), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    impact_level: Mapped[str] = mapped_column(String(20), nullable=False)
    impact_summary: Mapped[str] = mapped_column(Text, nullable=False)
    electricity_delta_kwh: Mapped[float] = mapped_column(Float, nullable=False)
    water_delta_m3: Mapped[float] = mapped_column(Float, nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)


class BehaviorImpact(Base):
    """行为对水电消耗影响的规则说明。"""

    __tablename__ = "behavior_impacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    behavior_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    electricity_factor: Mapped[float] = mapped_column(Float, nullable=False)
    water_factor: Mapped[float] = mapped_column(Float, nullable=False)


class TrainingImage(Base):
    """训练完成后的图片/图表展示表。"""

    __tablename__ = "training_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
