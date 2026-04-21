"""异步 SQLAlchemy 引擎/会话工厂、声明式 Base 与时间戳 Mixin。

集中收敛异步数据库接入方式,业务项目通过 ``create_async_engine_factory``
和 ``create_session_factory`` 装配引擎,继承 ``Base`` 与 ``TimestampMixin`` 写模型。
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """全局 ORM 声明式基类,所有业务模型直接继承此类以共享元数据。"""

    pass


class TimestampMixin:
    """为 ORM 模型补齐 ``created_at`` / ``updated_at`` 时间戳字段的 Mixin。

    时间值由数据库层生成(``server_default`` + ``onupdate``),避免应用时钟漂移
    影响排序,也保证事务回滚时时间戳与数据保持一致。
    """

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())


def create_async_engine_factory(
    database_url: str,
    pool_size: int = 5,
    max_overflow: int = 10,
    echo: bool = False,
) -> AsyncEngine:
    """创建异步 SQLAlchemy 引擎。

    SQLite 驱动不支持连接池参数,因此针对 ``sqlite`` 前缀 URL 单独走无池路径;
    其他数据库统一按传入的 pool_size/max_overflow 构建连接池。

    Args:
        database_url: 异步驱动的连接串,例如 ``postgresql+asyncpg://...``。
        pool_size: 常驻连接数(SQLite 忽略)。
        max_overflow: 突发时允许的额外连接数(SQLite 忽略)。
        echo: 是否把 SQL 语句打到日志,一般仅调试开启。

    Returns:
        构造好的 ``AsyncEngine`` 实例。
    """
    if database_url.startswith("sqlite"):
        return create_async_engine(database_url, echo=echo)
    return create_async_engine(
        database_url,
        pool_size=pool_size,
        max_overflow=max_overflow,
        echo=echo,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """基于引擎构造异步 Session 工厂。

    ``expire_on_commit=False`` 让 commit 后仍可访问 ORM 对象的属性,
    符合 FastAPI "请求内多次访问对象字段" 的典型用法。

    Args:
        engine: 已创建的 ``AsyncEngine``。

    Returns:
        绑定到该引擎的 ``async_sessionmaker``。
    """
    return async_sessionmaker(engine, expire_on_commit=False)
