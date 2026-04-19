"""Base Pydantic Settings class for FastAPI projects."""

from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict


class BaseSettings(PydanticBaseSettings):
    """Base settings — subclass and add project-specific fields."""

    database_url: str
    redis_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    debug: bool = False
    allowed_origins: list[str] = Field(default_factory=list)

    # Task module settings (task_ prefix)
    task_max_jobs: int = 5
    task_job_timeout: int = 3600
    task_failure_ttl: int = 86400

    # Logger module settings (log_ prefix)
    log_level: str = "INFO"
    log_dir: str | None = None
    log_filename: str = "app"
    log_max_bytes: int = 100 * 1024 * 1024
    log_retention: str = "30 days"
    log_console: bool = True
    log_serialize: bool = False
    log_intercept_stdlib: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
