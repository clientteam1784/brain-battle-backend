from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# 환경 변수 또는 .env에서 읽는 실행 설정입니다. 기본값은 로컬 개발용입니다.
class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = (
        "mysql+pymysql://brain_battle:change-me@localhost:3306/brain_battle?charset=utf8mb4"
    )
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])
    jwt_secret: str = "development-only-change-me"
    jwt_expire_minutes: int = 480
    teacher_access_code: str = "teacher-dev-code"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# 설정 객체를 한 번만 읽어 앱 전체가 동일한 환경 설정을 사용하도록 합니다.
@lru_cache
def get_settings() -> Settings:
    return Settings()
