"""ARQ Redis connection pool management (internal module).

Manages the lifecycle of the ARQ async Redis pool used for enqueuing
and executing tasks. Not intended for direct use by integrators.
"""

from __future__ import annotations

from urllib.parse import urlparse

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

_pool: ArqRedis | None = None
_redis_settings: RedisSettings | None = None


def _parse_redis_url(redis_url: str) -> RedisSettings:
    """Convert a redis:// URL to ARQ RedisSettings.

    Args:
        redis_url: Standard Redis connection URL.

    Returns:
        ARQ RedisSettings instance.
    """
    parsed = urlparse(redis_url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
        password=parsed.password,
    )


def configure(redis_url: str) -> None:
    """Store Redis settings for later pool creation.

    Args:
        redis_url: Standard Redis connection URL (e.g. redis://localhost:6379/0).
    """
    global _redis_settings
    _redis_settings = _parse_redis_url(redis_url)


def get_redis_settings() -> RedisSettings:
    """Return the configured ARQ RedisSettings.

    Returns:
        The RedisSettings instance.

    Raises:
        RuntimeError: If configure() has not been called.
    """
    if _redis_settings is None:
        msg = "Task pool not configured. Call setup_tasks() first."
        raise RuntimeError(msg)
    return _redis_settings


async def get_pool() -> ArqRedis:
    """Get or create the ARQ async Redis pool.

    Returns:
        The ArqRedis connection pool.

    Raises:
        RuntimeError: If configure() has not been called.
    """
    global _pool
    if _pool is None:
        _pool = await create_pool(get_redis_settings())
    return _pool


async def close_pool() -> None:
    """Close the ARQ pool if it exists. Safe to call multiple times."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
