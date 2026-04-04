"""Async Redis connection manager."""

import redis.asyncio as aioredis

_redis_url: str | None = None
_redis: aioredis.Redis | None = None


def configure(redis_url: str) -> None:
    """Set the Redis connection URL."""
    global _redis_url
    _redis_url = redis_url


async def get_redis() -> aioredis.Redis:
    """Get or create the shared async Redis connection."""
    if _redis_url is None:
        raise RuntimeError("danweiyuan_eapi.cache not configured — call cache.configure(redis_url) first")
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(_redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """Close the Redis connection. Safe to call even if not connected."""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
