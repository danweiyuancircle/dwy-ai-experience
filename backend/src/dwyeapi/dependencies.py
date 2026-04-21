"""FastAPI 依赖注入工厂。

基础设施不直接持有 session 工厂,而是通过工厂函数让业务项目装配,
保证每个项目的 session_factory 由各自的 Settings/engine 决定。
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def create_get_db(session_factory: async_sessionmaker[AsyncSession]):
    """基于 session 工厂创建 ``get_db`` FastAPI 依赖。

    返回的闭包可直接用作 ``Depends(get_db)``,请求结束时自动关闭 session。

    Args:
        session_factory: 业务侧 ``async_sessionmaker`` 实例。

    Returns:
        一个可作为 FastAPI 依赖的异步生成器函数。
    """

    async def get_db() -> AsyncGenerator[AsyncSession]:
        """产出一次请求期间使用的数据库会话,退出时自动关闭。"""
        async with session_factory() as session:
            yield session

    return get_db
