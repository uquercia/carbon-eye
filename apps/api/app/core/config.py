from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

API_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """读取后端配置。

    BaseSettings 会自动从环境变量或 .env 文件读取配置。
    这样数据库密码不用写死在业务代码里，后续部署时也更好改。
    """

    database_url: str = "mysql+pymysql://root:你的MySQL密码@127.0.0.1:3306/carbon_eye?charset=utf8mb4"
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    storage_backend: str = "local"
    upload_dir: str = "apps/api/storage/uploads"
    public_upload_base_url: str = "http://127.0.0.1:8000/uploads"
    vision_provider: str = "ark"
    vision_api_key: str = ""
    vision_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    vision_model: str = ""

    model_config = SettingsConfigDict(
        env_file=API_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """缓存配置对象，避免每次请求都重复读取配置文件。"""

    return Settings()
