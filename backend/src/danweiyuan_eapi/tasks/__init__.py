"""Async task processing system for FastAPI (ARQ-based).

Quick start::

    # 1. Install
    pip install danweiyuan-eapi[tasks]

    # 2. Register tasks
    from danweiyuan_eapi.tasks import register, TaskContext

    @register("process_data")
    async def process_data(ctx: TaskContext, params: dict):
        await ctx.log("Processing...")
        await ctx.update_progress(50)
        return {"done": True}

    # 3. Mount in FastAPI
    from danweiyuan_eapi.tasks import setup_tasks, task_router

    await setup_tasks(app, settings, session_factory)
    app.include_router(task_router)

    # 4. Run worker
    # arq app.worker.WorkerSettings

Public API:
    setup_tasks     — One-call initialization (ARQ pool + store session factory)
    task_router     — Ready-to-use APIRouter with CRUD endpoints
    register        — Decorator to register an async task function
    TaskContext      — Context object injected into task functions
    TaskStatus      — Task lifecycle status enum
    create_worker_settings — Factory to generate ARQ WorkerSettings from BaseSettings
"""

from __future__ import annotations

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from danweiyuan_eapi.config import BaseSettings
from danweiyuan_eapi.tasks.context import TaskContext
from danweiyuan_eapi.tasks.model import TaskStatus
from danweiyuan_eapi.tasks.registry import register
from danweiyuan_eapi.tasks.router import task_router
from danweiyuan_eapi.tasks.worker import create_worker_settings

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
    """Initialize the task system.

    Must be called during application startup (e.g. inside a lifespan).

    1. Configures the ARQ Redis pool from ``settings.redis_url``
    2. Stores the session_factory for TaskContext database access
    3. Registers a shutdown hook to close the pool

    Args:
        app: The FastAPI application instance.
        settings: An eapi BaseSettings instance with redis_url and task_* fields.
        session_factory: Async SQLAlchemy session factory for database access.

    Example::

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            await setup_tasks(app, settings, session_factory)
            yield

        app = FastAPI(lifespan=lifespan)
        app.include_router(task_router)
    """
    from danweiyuan_eapi.dependencies import create_get_db
    from danweiyuan_eapi.tasks import pool as _pool
    from danweiyuan_eapi.tasks import router as _router

    # Configure and warm up the ARQ pool
    _pool.configure(settings.redis_url)

    # Wire the db dependency into the router
    _router._get_db = create_get_db(session_factory)

    # Store session_factory on app state for worker access
    app.state.task_session_factory = session_factory
