"""ARQ Redis 连接池管理(内部模块)。

管理 ARQ 异步 Redis 连接池的生命周期,承载任务入队与执行。属内部实现,业务项目不应直接调用。
"""

from __future__ import annotations

from urllib.parse import urlparse

from arq import ArqRedis, create_pool
from arq.connections import RedisSettings

_pool: ArqRedis | None = None
_redis_settings: RedisSettings | None = None


def _parse_redis_url(redis_url: str) -> RedisSettings:
    """将标准 ``redis://`` URL 解析为 ARQ ``RedisSettings``。

    Args:
        redis_url: 标准 Redis 连接 URL。

    Returns:
        ARQ ``RedisSettings`` 实例。
    """
    parsed = urlparse(redis_url)
    return RedisSettings(
        host=parsed.hostname or "localhost",
        port=parsed.port or 6379,
        database=int(parsed.path.lstrip("/") or "0"),
        password=parsed.password,
    )


def configure(redis_url: str) -> None:
    """保存 Redis 设置以便后续懒创建连接池。

    Args:
        redis_url: 标准 Redis 连接 URL(如 ``redis://localhost:6379/0``)。
    """
    global _redis_settings
    _redis_settings = _parse_redis_url(redis_url)


def get_redis_settings() -> RedisSettings:
    """返回已配置的 ARQ ``RedisSettings``。

    Returns:
        ``RedisSettings`` 实例。

    Raises:
        RuntimeError: 未先调用 ``configure()`` 时抛出。
    """
    if _redis_settings is None:
        msg = "Task pool not configured. Call setup_tasks() first."
        raise RuntimeError(msg)
    return _redis_settings


async def get_pool() -> ArqRedis:
    """获取或懒创建 ARQ 异步 Redis 连接池。

    Returns:
        ``ArqRedis`` 连接池。

    Raises:
        RuntimeError: 未先调用 ``configure()`` 时抛出。
    """
    global _pool
    if _pool is None:
        _pool = await create_pool(get_redis_settings())
    return _pool


async def close_pool() -> None:
    """关闭 ARQ 连接池(若已创建),可重复调用。"""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
