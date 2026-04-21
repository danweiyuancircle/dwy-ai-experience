"""面向 FastAPI 的异步任务系统(基于 ARQ)。

快速开始::

    # 1. 安装
    pip install dwyeapi[tasks]

    # 2. 注册任务
    from dwyeapi.tasks import register, TaskContext

    @register("process_data")
    async def process_data(ctx: TaskContext, params: dict):
        await ctx.log("Processing...")
        await ctx.update_progress(50)
        return {"done": True}

    # 3. 在 FastAPI 中挂载
    from dwyeapi.tasks import setup_tasks, task_router

    await setup_tasks(app, settings, session_factory)
    app.include_router(task_router)

    # 4. 启动 worker
    # arq app.worker.WorkerSettings

公开 API:
    setup_tasks     — 一次性初始化(配置 ARQ 连接池 + 注册 session 工厂)
    task_router     — 现成的 FastAPI router,内置任务 CRUD 端点
    register        — 注册异步任务函数的装饰器
    TaskContext     — 注入到任务函数的上下文对象
    TaskStatus      — 任务生命周期状态枚举
    create_worker_settings — 基于 BaseSettings 生成 ARQ WorkerSettings 的工厂
"""

from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dwyeapi.config import BaseSettings
from dwyeapi.tasks.context import TaskContext
from dwyeapi.tasks.model import TaskStatus
from dwyeapi.tasks.registry import register
from dwyeapi.tasks.router import task_router
from dwyeapi.tasks.worker import create_worker_settings

# Re-export for convenient imports
__all__ = [
    "TaskContext",
    "TaskStatus",
    "create_worker_settings",
    "register",
    "setup_tasks",
    "task_router",
]


async def setup_tasks(
    app: FastAPI,
    settings: BaseSettings,
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    """初始化任务系统。

    必须在应用启动阶段调用(建议在 FastAPI ``lifespan`` 中),完成三件事:

    1. 根据 ``settings.redis_url`` 配置 ARQ Redis 连接池;
    2. 将 session_factory 注入 router,供 TaskContext 访问数据库;
    3. 把 session_factory 绑定到 ``app.state``,worker 侧可取用。

    Args:
        app: FastAPI 应用实例。
        settings: 继承自 eapi ``BaseSettings`` 的配置,需包含 redis_url 和 task_* 字段。
        session_factory: 异步 SQLAlchemy session 工厂,供任务访问数据库。

    Example::

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await setup_tasks(app, settings, session_factory)
            yield

        app = FastAPI(lifespan=lifespan)
        app.include_router(task_router)
    """
    from dwyeapi.dependencies import create_get_db
    from dwyeapi.tasks import pool as _pool
    from dwyeapi.tasks import router as _router

    # 配置并预热 ARQ 连接池
    _pool.configure(settings.redis_url)

    # 把 db 依赖装配到 router
    _router._get_db = create_get_db(session_factory)

    # session_factory 记录到 app.state 供 worker 访问
    app.state.task_session_factory = session_factory
