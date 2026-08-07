"""dwyeapi — 轻量 FastAPI 基础设施包。

业务项目只通过本包的公开 API 访问配置、数据库、缓存、安全等基础能力,
避免在各项目中重复手写相同逻辑。

Modules:
    config        — BaseSettings + 运行环境识别 API(is_dev/is_prod/get_environment)
    exceptions    — AppError 异常体系 + FastAPI 全局 handler 注册
    database      — 异步 SQLAlchemy engine/session 工厂 + Base + TimestampMixin
    dependencies  — FastAPI 依赖注入工厂(如 get_db)
    security      — JWT 令牌与 bcrypt 密码哈希工具(无状态)
    cache         — 异步 Redis 连接管理
    response      — 统一 API 响应信封(ApiResponse[T] + PageData[T])
    pagination    — 分页参数与 offset/limit 计算
    logger        — 基于 loguru 的全局日志,支持按天与按大小轮转、stdlib 拦截
    tasks         — 异步任务系统(基于 ARQ,需安装 [tasks] extra)
    masking       — PII 数据脱敏工具
    health        — 健康检查路由工厂(只探活,不探依赖)
"""

from . import health, logger
from .config import BaseSettings, get_environment, is_dev, is_prod
from .response import ApiResponse, PageData

__all__ = [
    "ApiResponse",
    "BaseSettings",
    "PageData",
    "get_environment",
    "health",
    "is_dev",
    "is_prod",
    "logger",
]
__version__ = "0.9.5"
