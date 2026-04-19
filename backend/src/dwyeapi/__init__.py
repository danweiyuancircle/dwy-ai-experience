"""dwyeapi — Lightweight FastAPI infrastructure.

Modules:
    config        — BaseSettings + 运行环境识别 API (is_dev/is_prod/get_environment)
    exceptions    — AppError hierarchy + FastAPI exception handlers
    database      — Async SQLAlchemy engine/session factory + Base + TimestampMixin
    dependencies  — get_db() FastAPI dependency factory
    security      — JWT + bcrypt helpers (stateless)
    cache         — Async Redis connection manager
    response      — Unified API response helpers
    pagination    — PaginationParams + paginate helper
    logger        — Loguru-based logger with daily+size rotation and stdlib interception
    tasks         — Async task processing system (ARQ-based, install with [tasks] extra)
    masking       — PII data masking utilities
"""

from . import logger
from .config import BaseSettings, get_environment, is_dev, is_prod

__all__ = ["BaseSettings", "get_environment", "is_dev", "is_prod", "logger"]
__version__ = "0.5.2"
