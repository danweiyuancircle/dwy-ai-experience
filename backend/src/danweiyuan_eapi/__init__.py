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
    tasks         — Async task processing system (ARQ-based, install with [tasks] extra)
    masking       — PII data masking utilities
"""

__version__ = "0.2.0"
