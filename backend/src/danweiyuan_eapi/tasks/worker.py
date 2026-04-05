"""Worker configuration factory.

Generates an ARQ ``WorkerSettings`` class from eapi's ``BaseSettings``,
bridging configuration between the two systems.
"""

from __future__ import annotations

from typing import Any

from danweiyuan_eapi.config import BaseSettings
from danweiyuan_eapi.tasks.pool import _parse_redis_url


def create_worker_settings(
    settings: BaseSettings,
    session_factory: Any = None,
) -> type:
    """Create an ARQ WorkerSettings class from eapi BaseSettings.

    The returned class can be used directly with ``arq`` CLI::

        # app/worker.py
        import app.tasks  # trigger @register decorators
        from app.settings import settings
        from danweiyuan_eapi.tasks import create_worker_settings
        from danweiyuan_eapi.database import create_async_engine_factory, create_session_factory

        engine = create_async_engine_factory(settings.database_url)
        sf = create_session_factory(engine)
        WorkerSettings = create_worker_settings(settings, session_factory=sf)

        # Run: arq app.worker.WorkerSettings

    Args:
        settings: An eapi BaseSettings instance (or subclass) with
            redis_url, task_max_jobs, task_job_timeout, task_failure_ttl.
        session_factory: Async SQLAlchemy session factory for TaskContext
            database access inside worker tasks.

    Returns:
        A class suitable as ARQ WorkerSettings.
    """
    from danweiyuan_eapi.tasks.context import run_task_with_context
    from danweiyuan_eapi.tasks.registry import registry

    _redis_settings = _parse_redis_url(settings.redis_url)
    _session_factory = session_factory

    async def _task_executor(ctx: dict, task_id: str, task_type: str, params: dict) -> None:
        """ARQ entry point — dispatches to the registered task function.

        Args:
            ctx: ARQ worker context dict (contains 'redis').
            task_id: Unique task identifier.
            task_type: Registered task type string.
            params: Task input parameters.
        """
        func = registry.get(task_type)
        if func is None:
            msg = f"Unknown task type: {task_type}"
            raise ValueError(msg)

        await run_task_with_context(
            task_id=task_id,
            task_type=task_type,
            params=params,
            func=func,
            session_factory=_session_factory,
            redis=ctx["redis"],
        )

    class WorkerSettings:
        """ARQ WorkerSettings generated from eapi BaseSettings."""

        functions = [_task_executor]
        max_jobs = settings.task_max_jobs
        job_timeout = settings.task_job_timeout
        # ARQ reads this attribute name
        redis_settings = _redis_settings

    return WorkerSettings
