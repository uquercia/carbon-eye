from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.api.app.db.session import Base


class Building(Base):
    """校园楼栋基础表。

    这张表只放楼栋“基本信息”，例如名称、区域、专业映射、地图坐标。
    水电数据不直接放这里，因为同一栋楼会有很多时间步的数据。
    """

    __tablename__ = "buildings"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    zone: Mapped[str] = mapped_column(String(40), nullable=False)
    major: Mapped[str] = mapped_column(String(40), nullable=False)
    map_x: Mapped[float] = mapped_column(Float, nullable=False)
    map_y: Mapped[float] = mapped_column(Float, nullable=False)

    # relationship 不是数据库字段，而是 SQLAlchemy 提供的对象关联。
    # 有了它，可以通过 building.predictions 访问这栋楼的预测记录。
    predictions: Mapped[list["EnergyPrediction"]] = relationship(back_populates="building")


class EnergyPrediction(Base):
    """楼栋某个时间步的实际/预测用水用电数据。

    一栋楼会在多个 time_step 下出现多条记录。
    前端表格默认取最新 time_step 的数据。
    """

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
    """问卷聚合后的专业低碳行为得分。

    这张表来自 behavior_summary CSV。
    每一行代表一个专业类别的平均行为得分。
    """

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

    现在先用“训练完成后的示例数据”填充。
    后面接入真实图片上传和模型推理后，可以把真实识别结果写入类似结构的表。
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
    """行为对水电消耗影响的规则说明。

    这张表不是识别结果，而是“知识库/提示库”。
    用户还没上传图片时，页面展示这些通用环保提示。
    """

    __tablename__ = "behavior_impacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    behavior_name: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(40), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    electricity_factor: Mapped[float] = mapped_column(Float, nullable=False)
    water_factor: Mapped[float] = mapped_column(Float, nullable=False)


class TrainingImage(Base):
    """训练完成后的图片/图表展示表。

    数据库只保存图片 URL，不保存图片二进制内容。
    这样数据库更轻，前端也可以直接通过 URL 加载图片。
    """

    __tablename__ = "training_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(80), nullable=False)
    image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
