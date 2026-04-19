"""dwyeapi — Lightweight FastAPI infrastructure.

Modules:
    config        — BaseSettings with required fields
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

__all__ = ["logger"]
__version__ = "0.4.0"
