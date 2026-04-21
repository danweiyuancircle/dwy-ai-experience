"""异步 Redis 连接管理。

模块级单例的懒连接:``configure`` 阶段只记录 URL,首次 ``get_redis`` 调用才真正建立连接,
``close_redis`` 负责在应用关闭时释放资源,避免连接泄漏。
"""

import redis.asyncio as aioredis

_redis_url: str | None = None
_redis: aioredis.Redis | None = None


def configure(redis_url: str) -> None:
    """设置全局 Redis 连接 URL。

    通常在 FastAPI 的 ``lifespan`` 启动阶段调用一次。

    Args:
        redis_url: 标准 Redis 连接串,如 ``redis://localhost:6379/0``。
    """
    global _redis_url
    _redis_url = redis_url


async def get_redis() -> aioredis.Redis:
    """获取共享的异步 Redis 连接,首次调用时懒创建。

    ``decode_responses=True`` 让返回值直接为 ``str``,避免业务代码反复 decode。

    Returns:
        全局复用的 ``aioredis.Redis`` 实例。

    Raises:
        RuntimeError: 未先调用 ``configure`` 时抛出,提示装配缺失。
    """
    if _redis_url is None:
        raise RuntimeError("dwyeapi.cache not configured — call cache.configure(redis_url) first")
    global _redis
    if _redis is None:
        _redis = aioredis.from_url(_redis_url, decode_responses=True)
    return _redis


async def close_redis() -> None:
    """关闭全局 Redis 连接,未连接时也可安全重复调用。"""
    global _redis
    if _redis is not None:
        await _redis.close()
        _redis = None
