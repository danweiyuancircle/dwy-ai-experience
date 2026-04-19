"""Base Pydantic Settings class for FastAPI projects.

除基础字段外,还提供运行环境识别 API:

- ``environment`` 字段: ``"dev"`` | ``"prod"``,默认 ``"prod"`` (误配置时保守)
- ``get_environment()`` / ``is_dev()`` / ``is_prod()``: 业务代码读当前环境

业务项目实例化 ``Settings()`` 时会自动把值写入模块级全局,之后任何地方 import 即可读。
"""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings as PydanticBaseSettings
from pydantic_settings import SettingsConfigDict

Environment = Literal["dev", "prod"]

_current_environment: Environment = "prod"


def get_environment() -> Environment:
    """返回当前运行环境。

    未实例化 Settings 前默认返回 ``"prod"`` (保守),业务 ``Settings()`` 加载
    后会同步为配置值。
    """
    return _current_environment


def is_dev() -> bool:
    """当前是否为开发环境。"""
    return _current_environment == "dev"


def is_prod() -> bool:
    """当前是否为生产环境。"""
    return _current_environment == "prod"


def set_current_environment(env: Environment) -> None:
    """内部使用: 由 BaseSettings 校验钩子或测试显式切换时调用。"""
    global _current_environment
    _current_environment = env


class BaseSettings(PydanticBaseSettings):
    """Base settings — subclass and add project-specific fields."""

    database_url: str
    redis_url: str
    secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    environment: Environment = "prod"
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

    @model_validator(mode="after")
    def _sync_environment_to_module(self) -> "BaseSettings":
        """把 ``environment`` 写入模块全局,让 ``is_dev()`` / ``is_prod()`` 跨模块可读。"""
        set_current_environment(self.environment)
        return self
