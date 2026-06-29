from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "RepoLens API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # GitHub
    GITHUB_TOKEN: str = ""

    # Database (SQLite for dev, swap to Postgres later)
    DATABASE_URL: str = "sqlite:///./repolens.db"

    # Redis (unused for now, in-memory cache used instead)
    REDIS_URL: str = ""

    # Cache TTL in seconds
    CACHE_TTL: int = 300  # 5 minutes

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
