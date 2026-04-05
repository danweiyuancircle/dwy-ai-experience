"""TaskContext — rich context object injected into task functions.

Provides database access, logging, progress tracking, and cancellation
checking so that business task code stays minimal.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from danweiyuan_eapi.tasks import service
from danweiyuan_eapi.tasks.model import TaskStatus


class TaskContext:
    """Execution context passed to every registered task function.

    Provides helpers for logging, progress updates, cancellation checks,
    and database access so that task functions only contain business logic.

    Attributes:
        task_id: The unique identifier of the current task.
        task_type: The registered task type string.
        params: The parameters submitted with the task.
    """

    def __init__(
        self,
        *,
        task_id: str,
        task_type: str,
        params: dict[str, Any],
        session_factory: async_sessionmaker[AsyncSession],
        redis: Any,
    ) -> None:
        """Initialize TaskContext.

        Args:
            task_id: Unique task identifier.
            task_type: Registered task type name.
            params: Task input parameters.
            session_factory: Async SQLAlchemy session factory.
            redis: ARQ Redis connection for cancel-flag checks.
        """
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self._session_factory = session_factory
        self._redis = redis
        self._cancelled = False

    async def log(self, message: str) -> None:
        """Append a timestamped log entry.

        Args:
            message: The log message to record.
        """
        async with self._session() as session:
            await service.append_task_log(session, self.task_id, message)

    async def update_progress(self, value: int, message: str = "") -> None:
        """Update task progress (0-100) and optionally append a log.

        Args:
            value: Progress percentage (clamped to 0-100).
            message: Optional log message to append alongside the progress update.
        """
        async with self._session() as session:
            await service.update_task_progress(session, self.task_id, value)
            if message:
                await service.append_task_log(session, self.task_id, message)

    async def is_cancelled(self) -> bool:
        """Check whether a cancel request has been issued for this task.

        Reads a Redis key ``task_cancel:{task_id}``. Once detected, the
        result is cached so subsequent calls do not hit Redis again.

        Returns:
            True if the task has been marked for cancellation.
        """
        if self._cancelled:
            return True
        val = await self._redis.get(f"task_cancel:{self.task_id}")
        if val is not None:
            self._cancelled = True
        return self._cancelled

    @asynccontextmanager
    async def db(self) -> AsyncIterator[AsyncSession]:
        """Provide an async database session via context manager.

        Usage::

            async with ctx.db() as session:
                result = await session.execute(select(MyModel))

        Yields:
            An AsyncSession bound to the application's database.
        """
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[AsyncSession]:
        """Internal helper — short-lived session for framework operations."""
        async with self._session_factory() as session:
            yield session


async def run_task_with_context(
    task_id: str,
    task_type: str,
    params: dict[str, Any],
    func: Any,
    session_factory: async_sessionmaker[AsyncSession],
    redis: Any,
) -> None:
    """Execute a task function wrapped in lifecycle management.

    Handles the full task lifecycle:
    1. Set status to RUNNING
    2. Create TaskContext and call the business function
    3. On success → set status to SUCCESS with returned result
    4. On exception → set status to FAILED with error info
    5. On cancellation → set status to CANCELED

    Args:
        task_id: The task's unique identifier.
        task_type: The registered task type string.
        params: The task input parameters.
        func: The async business function to execute.
        session_factory: Async SQLAlchemy session factory.
        redis: ARQ Redis connection.
    """
    ctx = TaskContext(
        task_id=task_id,
        task_type=task_type,
        params=params,
        session_factory=session_factory,
        redis=redis,
    )

    # Mark as running
    async with session_factory() as session:
        await service.update_task_status(session, task_id, TaskStatus.RUNNING)
        await service.append_task_log(session, task_id, "任务开始执行")

    try:
        result = await func(ctx, params)

        # Check if cancelled during execution
        if ctx._cancelled:
            async with session_factory() as session:
                await service.update_task_status(session, task_id, TaskStatus.CANCELED)
                await service.append_task_log(session, task_id, "任务已取消")
            return

        # Success
        result_data = result if isinstance(result, dict) else {"result": result}
        async with session_factory() as session:
            await service.update_task_status(session, task_id, TaskStatus.SUCCESS, result=result_data)
            await service.update_task_progress(session, task_id, 100)
            await service.append_task_log(session, task_id, "任务执行成功")

    except Exception as exc:
        # Failed
        async with session_factory() as session:
            await service.update_task_status(
                session,
                task_id,
                TaskStatus.FAILED,
                result={"error": str(exc)},
            )
            await service.append_task_log(session, task_id, f"任务执行失败: {exc}")
        raise
