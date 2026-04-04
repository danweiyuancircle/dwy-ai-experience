"""danweiyuan-eapi — Lightweight FastAPI infrastructure.

Modules:
    config        — BaseSettings with required fields
    exceptions    — AppError hierarchy + FastAPI exception handlers
    database      — Async SQLAlchemy engine/session factory + Base + TimestampMixin
    dependencies  — get_db() FastAPI dependency factory
    security      — JWT + bcrypt helpers (stateless)
    cache         — Async Redis connection manager
    response      — Unified API response helpers
    pagination    — PaginationParams + paginate helper
"""

__version__ = "0.1.0"
