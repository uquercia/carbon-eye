from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from apps.api.app.core.config import get_settings


class Base(DeclarativeBase):
    """所有数据库模型的基类。

    后续每张表都继承它，SQLAlchemy 才能知道这些类对应数据库表。
    """


settings = get_settings()

# pool_pre_ping=True 会在使用连接前先检查连接是否有效，避免 MySQL 长时间空闲断开后报错。
engine = create_engine(settings.database_url, pool_pre_ping=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖函数：每个请求创建一个数据库会话，用完自动关闭。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
