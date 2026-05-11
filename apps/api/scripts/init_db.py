from pathlib import Path
import sys

import pandas as pd
import pymysql
from dotenv import dotenv_values
from sqlalchemy import delete
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from apps.api.app.db.session import Base, engine
from apps.api.app.models import (
    BehaviorImpact,
    BehaviorScore,
    Building,
    EnergyPrediction,
    RecognitionSample,
    TrainingImage,
)

SOURCE_DIR = Path("G:/大创碳眸项目")
STATIC_DIR = ROOT / "apps" / "web" / "public" / "training"

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
DATABASE_NAME = "carbon_eye"

ENV_FILE = ROOT / "apps" / "api" / ".env"
ENV_VALUES = dotenv_values(ENV_FILE)
MYSQL_PASSWORD = ENV_VALUES.get("MYSQL_ROOT_PASSWORD") or "123456"

BUILDING_META = {
    "(溫室)園藝系": ("北区", "理工科", 24, 18),
    "人文大樓": ("西区", "文科", 16, 44),
    "動物醫學研究中心": ("东北区", "医学/生物", 58, 18),
    "動科大樓": ("东北区", "医学/生物", 74, 30),
    "化學大樓": ("中区", "理工科", 42, 42),
    "學生活動中心": ("生活区", "其他", 58, 58),
    "應科大樓": ("中区", "理工科", 34, 66),
    "機械館": ("东区", "理工科", 78, 56),
    "混凝土中心大樓": ("东区", "理工科", 86, 74),
    "游泳池": ("体育区", "其他", 50, 82),
    "生科大樓": ("北区", "医学/生物", 36, 24),
    "行政大樓": ("南区", "其他", 20, 78),
    "診斷中心": ("东北区", "医学/生物", 68, 46),
    "農環大樓": ("北区", "理工科", 48, 12),
    "體育館": ("体育区", "其他", 66, 86),
}

MAJOR_NAMES = {
    1: "理工科",
    2: "文科",
    3: "商科/管理",
    4: "艺术/设计",
    5: "医学/生物",
    6: "其他",
}


def create_database() -> None:
    """先连 MySQL 服务，再创建项目数据库。

    这一步不能直接用 SQLAlchemy 的 carbon_eye 连接串，因为数据库还没创建时会连不上。
    """

    connection = pymysql.connect(
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        charset="utf8mb4",
        autocommit=True,
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{DATABASE_NAME}` "
                "DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
    finally:
        connection.close()


def copy_training_images() -> None:
    """把已有训练/预测结果图复制到前端 public 目录，方便页面直接展示。"""

    STATIC_DIR.mkdir(parents=True, exist_ok=True)
    image_map = {
        "1.png": "electricity_prediction.png",
        "2.png": "training_loss.png",
        "3.png": "water_prediction.png",
        "微信图片_20260511142335.png": "behavior_score.png",
    }
    for source_name, target_name in image_map.items():
        source = SOURCE_DIR / source_name
        target = STATIC_DIR / target_name
        if source.exists():
            target.write_bytes(source.read_bytes())


def reset_tables(db: Session) -> None:
    """清空演示数据，保证重复执行脚本时不会插入重复记录。"""

    for model in [
        TrainingImage,
        BehaviorImpact,
        RecognitionSample,
        EnergyPrediction,
        BehaviorScore,
        Building,
    ]:
        db.execute(delete(model))
    db.commit()


def import_buildings_and_predictions(db: Session) -> None:
    prediction_file = SOURCE_DIR / "prediction_results.csv"
    df = pd.read_csv(prediction_file)

    building_names = sorted(df["建筑"].unique())
    for index, name in enumerate(building_names, start=1):
        zone, major, x, y = BUILDING_META.get(name, ("未分区", "其他", 20 + index * 4, 40))
        db.add(
            Building(
                id=f"building_{index:02d}",
                name=name,
                zone=zone,
                major=major,
                map_x=x,
                map_y=y,
            )
        )
    db.flush()

    building_id_by_name = {building.name: building.id for building in db.query(Building).all()}
    for row in df.itertuples(index=False):
        db.add(
            EnergyPrediction(
                time_step=int(row.时间步),
                building_id=building_id_by_name[row.建筑],
                electricity_actual=float(row.实际用电量),
                electricity_predicted=float(row.预测用电量),
                water_actual=float(row.实际用水量),
                water_predicted=float(row.预测用水量),
                electricity_error=float(row.用电量误差),
                water_error=float(row.用水量误差),
            )
        )
    db.commit()


def import_behavior_scores(db: Session) -> None:
    behavior_file = SOURCE_DIR / "behavior_summary(1).csv"
    df = pd.read_csv(behavior_file)

    for row in df.itertuples(index=False):
        major_code = int(row.专业编码)
        db.add(
            BehaviorScore(
                major_code=major_code,
                major_name=MAJOR_NAMES.get(major_code, "未知"),
                light_off_score=float(row.Q3_随手关灯关空调),
                charger_unplug_score=float(row.Q4_拔充电器),
                daylight_score=float(row.Q5_白天不开灯),
                plug_unplug_score=float(row.Q6_拔插头),
                faucet_off_score=float(row.Q7_关水龙头),
                shower_short_score=float(row.Q8_缩短淋浴),
                laundry_batch_score=float(row.Q9_集中洗涤),
                repair_report_score=float(row.Q10_主动报修),
                total_score=float(row.综合行为得分),
            )
        )
    db.commit()


def seed_behavior_examples(db: Session) -> None:
    impacts = [
        ("随手关灯关空调", "用电", "离开教室后关闭照明和空调，可直接降低空载用电。", -0.12, 0.0),
        ("拔掉闲置充电器", "用电", "减少待机功耗，对宿舍和活动中心的小负荷有持续影响。", -0.04, 0.0),
        ("白天优先自然采光", "用电", "白天减少照明开启时长，适合教学楼和办公楼。", -0.08, 0.0),
        ("及时关闭水龙头", "用水", "洗手、清洁后关闭水龙头，可降低公共区域用水浪费。", 0.0, -0.10),
        ("缩短淋浴时间", "用水", "降低宿舍和体育区生活热水/冷水消耗。", -0.02, -0.16),
        ("集中洗涤衣物", "用水", "减少洗衣机低负载运行次数，同时降低水电消耗。", -0.06, -0.12),
        ("主动报修漏水漏电", "综合", "通过报修异常设备减少持续浪费，是高价值干预行为。", -0.10, -0.14),
    ]
    for behavior_name, category, description, electricity_factor, water_factor in impacts:
        db.add(
            BehaviorImpact(
                behavior_name=behavior_name,
                category=category,
                description=description,
                electricity_factor=electricity_factor,
                water_factor=water_factor,
            )
        )

    samples = [
        (
            "随手关灯关空调",
            "教学楼教室",
            "building_05",
            0.93,
            "正向",
            "识别到离开教室后关闭电器，预计降低化学大楼夜间空载用电。",
            -18.5,
            0.0,
            "/training/electricity_prediction.png",
        ),
        (
            "及时关闭水龙头",
            "公共洗手区",
            "building_10",
            0.89,
            "正向",
            "识别到用水后关闭水龙头，预计减少体育区用水峰值。",
            0.0,
            -6.8,
            "/training/water_prediction.png",
        ),
        (
            "拔掉闲置充电器",
            "学生活动中心",
            "building_06",
            0.86,
            "正向",
            "识别到闲置插头被拔除，降低低负载持续耗电。",
            -4.2,
            0.0,
            "/training/behavior_score.png",
        ),
        (
            "缩短淋浴时间",
            "体育馆淋浴区",
            "building_15",
            0.81,
            "正向",
            "识别到用水时长缩短，对体育区用水和热水能耗均有影响。",
            -2.1,
            -9.5,
            "/training/water_prediction.png",
        ),
    ]
    for sample in samples:
        db.add(
            RecognitionSample(
                behavior_name=sample[0],
                location_name=sample[1],
                building_id=sample[2],
                confidence=sample[3],
                impact_level=sample[4],
                impact_summary=sample[5],
                electricity_delta_kwh=sample[6],
                water_delta_m3=sample[7],
                image_url=sample[8],
            )
        )

    images = [
        ("用电预测训练结果", "/training/electricity_prediction.png", "展示模型对各楼栋用电量的实际/预测对比。"),
        ("训练损失曲线", "/training/training_loss.png", "用于观察模型训练收敛情况。"),
        ("用水预测训练结果", "/training/water_prediction.png", "展示模型对各楼栋用水量的实际/预测对比。"),
        ("低碳行为得分", "/training/behavior_score.png", "展示不同专业学生低碳行为问卷得分。"),
    ]
    for title, image_url, description in images:
        db.add(TrainingImage(title=title, image_url=image_url, description=description))
    db.commit()


def main() -> None:
    create_database()
    Base.metadata.create_all(bind=engine)
    copy_training_images()
    with Session(engine) as db:
        reset_tables(db)
        import_buildings_and_predictions(db)
        import_behavior_scores(db)
        seed_behavior_examples(db)
    print("carbon_eye database initialized.")


if __name__ == "__main__":
    main()
