from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from apps.api.app.core.config import get_settings


class Base(DeclarativeBase):
    """所有数据库模型的基类。

    后续每张表都继承它，SQLAlchemy 才能知道这些类对应数据库表。
    """


settings = get_settings()

# 数据库引擎。
# 它负责真正连接 MySQL。后续所有查询、插入、更新最终都会通过 engine 执行。
# pool_pre_ping=True 会在使用连接前先检查连接是否有效，
# 避免 MySQL 长时间空闲断开后，第一次请求直接报“连接已失效”。
engine = create_engine(settings.database_url, pool_pre_ping=True)

# sessionmaker 是“数据库会话工厂”。
# 你可以把 SessionLocal() 理解成“打开一次数据库操作窗口”。
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db() -> Generator[Session, None, None]:
    """FastAPI 依赖函数：每个请求创建一个数据库会话，用完自动关闭。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
