"""ARQ Worker 配置工厂。

基于 eapi ``BaseSettings`` 动态生成 ARQ ``WorkerSettings`` 类,
把应用配置(Redis、任务并发、超时等)桥接到 ARQ,避免业务项目各自手写 WorkerSettings。
"""

from __future__ import annotations

from typing import Any

from dwyeapi.config import BaseSettings
from dwyeapi.logger import get_logger
from dwyeapi.tasks.pool import _parse_redis_url

_log = get_logger(__name__)


def create_worker_settings(
    settings: BaseSettings,
    session_factory: Any = None,
) -> type:
    """根据 eapi ``BaseSettings`` 生成 ARQ ``WorkerSettings`` 类。

    返回的类可直接作为 ``arq`` CLI 的入口::

        # app/worker.py
        import app.tasks  # 触发 @register 装饰器
        from app.settings import settings
        from dwyeapi.tasks import create_worker_settings
        from dwyeapi.database import create_async_engine_factory, create_session_factory

        engine = create_async_engine_factory(settings.database_url)
        sf = create_session_factory(engine)
        WorkerSettings = create_worker_settings(settings, session_factory=sf)

        # 运行: arq app.worker.WorkerSettings

    Args:
        settings: eapi ``BaseSettings`` 实例(或子类),需包含 redis_url、
            task_max_jobs、task_job_timeout、task_failure_ttl 等字段。
        session_factory: 异步 SQLAlchemy session 工厂,供 worker 内部 TaskContext 使用。

    Returns:
        可直接作为 ARQ WorkerSettings 使用的类。
    """
    from dwyeapi.tasks.context import run_task_with_context
    from dwyeapi.tasks.registry import registry

    _redis_settings = _parse_redis_url(settings.redis_url)
    _session_factory = session_factory

    async def _task_executor(ctx: dict, task_id: str, task_type: str, params: dict) -> None:
        """ARQ 的任务入口,按 task_type 派发到注册的业务函数。

        Args:
            ctx: ARQ worker 上下文字典(含 ``redis`` 等)。
            task_id: 任务唯一标识。
            task_type: 已注册的任务类型字符串。
            params: 任务输入参数。
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

    from arq.worker import func as arq_func

    async def _on_startup(ctx: dict) -> None:
        """Worker 启动时恢复未完成的任务。

        扫描 PostgreSQL 中 pending/running 状态的任务, 重新入队到 ARQ。
        running 状态的任务说明上次 Worker 中断, 重置为 pending 后重新执行。
        """
        from sqlalchemy import select

        from dwyeapi.tasks.model import Task, TaskStatus
        from dwyeapi.tasks.service import append_task_log, update_task_status

        redis = ctx["redis"]
        async with _session_factory() as session:
            result = await session.execute(
                select(Task).where(Task.status.in_([TaskStatus.PENDING, TaskStatus.RUNNING]))
            )
            stale_tasks = list(result.scalars().all())

        if not stale_tasks:
            return

        for task in stale_tasks:
            if task.status == TaskStatus.RUNNING:
                async with _session_factory() as session:
                    await update_task_status(session, task.id, TaskStatus.PENDING)
                    await append_task_log(session, task.id, "Worker 重启, 任务重新入队")

            await redis.enqueue_job("_task_executor", task.id, task.task_type, task.params)

        _log.info("恢复了 %s 个未完成的任务", len(stale_tasks))

    class WorkerSettings:
        """由 eapi BaseSettings 生成的 ARQ WorkerSettings 类。"""

        functions = [arq_func(_task_executor, name="_task_executor")]
        max_jobs = settings.task_max_jobs
        job_timeout = settings.task_job_timeout
        on_startup = _on_startup
        redis_settings = _redis_settings

    return WorkerSettings
