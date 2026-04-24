"""FastAPI 项目通用 Pydantic Settings 基类。

除了 database_url / redis_url / secret_key 等基础字段外,还提供运行环境识别 API:

- ``environment`` 字段: ``"dev"`` | ``"prod"``,默认 ``"prod"``(误配置时偏保守)
- ``get_environment()`` / ``is_dev()`` / ``is_prod()``:业务代码读取当前环境

业务项目实例化 ``Settings()`` 时会自动把 environment 值写入模块级全局变量,
之后任何地方 import 即可读,避免把 Settings 实例到处传递。
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
    """FastAPI 项目共用的配置基类。

    业务项目通过继承并追加项目专属字段使用,内置的 database_url / redis_url /
    secret_key 等字段覆盖最常用的基础设施需求,不需要每个项目重复声明。
    配置来源默认为 ``.env`` 文件,嵌套字段使用双下划线 ``__`` 分隔。
    """

    database_url: str = Field(
        description="数据库连接串(异步驱动),例 postgresql+asyncpg://user:pass@host:5432/db",
    )
    redis_url: str = Field(
        description="Redis 连接串,例 redis://localhost:6379/0",
    )
    secret_key: str = Field(
        description="应用密钥,用于 JWT 签名与敏感数据加密,至少 32 位随机字符串",
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT 签名算法,默认 HS256",
    )
    access_token_expire_minutes: int = Field(
        default=30,
        description="JWT access token 有效期(分钟),默认 30 分钟",
    )
    environment: Environment = Field(
        default="prod",
        description='运行环境,"dev" 开启调试特性 / 允许 mock providers,"prod" 关闭调试并禁用 mock',
    )
    allowed_origins: list[str] = Field(
        default_factory=list,
        description="CORS 允许的来源域名列表,生产环境禁止使用 ['*']",
    )

    # ── 异步任务配置(task_ 前缀)──
    task_max_jobs: int = Field(
        default=5,
        description="ARQ worker 并发执行的最大任务数",
    )
    task_job_timeout: int = Field(
        default=3600,
        description="单个任务执行超时(秒),超时后被中止,默认 1 小时",
    )
    task_failure_ttl: int = Field(
        default=86400,
        description="失败任务结果在 Redis 中的保留时长(秒),默认 1 天",
    )

    # ── 日志配置(log_ 前缀)──
    log_level: str = Field(
        default="INFO",
        description="最低日志级别:DEBUG / INFO / WARNING / ERROR / CRITICAL",
    )
    log_dir: str | None = Field(
        default=".",
        description='日志文件目录,默认 "." 即进程当前目录;显式设为 None 可关闭文件输出(仅控制台)',
    )
    log_filename: str = Field(
        default="app",
        description="日志文件基础名,最终文件形如 {filename}_YYYY-MM-DD.log",
    )
    log_max_bytes: int = Field(
        default=100 * 1024 * 1024,
        description="单个日志文件大小上限(字节),超出后滚动,默认 100 MB",
    )
    log_retention: str = Field(
        default="30 days",
        description='日志保留策略,loguru 语法,例 "30 days" / "1 week" / 整数个数',
    )
    log_console: bool = Field(
        default=True,
        description="是否输出带颜色的日志到 stderr 控制台",
    )
    log_serialize: bool = Field(
        default=False,
        description="文件 sink 是否按 JSON Lines 序列化,便于日志聚合系统解析",
    )
    log_intercept_stdlib: bool = Field(
        default=True,
        description="是否拦截 stdlib logging,让 uvicorn / SQLAlchemy / httpx 等共享同一套 sink",
    )

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
