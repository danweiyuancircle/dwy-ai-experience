"""Ready-to-use FastAPI router for the task system.

Provides endpoints to submit, query, list, and cancel tasks.
Integrators mount it via ``app.include_router(task_router)``.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dwyeapi.exceptions import BusinessError, NotFoundError
from dwyeapi.response import success
from dwyeapi.tasks import pool
from dwyeapi.tasks.model import TaskStatus
from dwyeapi.tasks.registry import registry
from dwyeapi.tasks.schema import TaskCreate, TaskListResponse, TaskResponse
from dwyeapi.tasks.service import (
    append_task_log,
    create_task,
    get_task,
    list_tasks,
    update_task_progress,
    update_task_status,
)

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

# This will be set by setup_tasks() at application startup.
_get_db: Callable[[], AsyncGenerator[AsyncSession]] | None = None


async def _db_dependency() -> AsyncGenerator[AsyncSession]:
    """Async generator that delegates to the actual get_db dependency.

    Yields:
        An AsyncSession from the configured session factory.

    Raises:
        RuntimeError: If setup_tasks() has not been called.
    """
    if _get_db is None:
        msg = "Task system not initialized. Call setup_tasks() first."
        raise RuntimeError(msg)
    async for session in _get_db():
        yield session


@task_router.post("", summary="提交耗时任务")
async def submit_task(
    body: TaskCreate,
    db: AsyncSession = Depends(_db_dependency),
) -> dict:
    """Submit a new async task for background execution.

    Args:
        body: Task creation payload with task_type and params.
        db: Injected database session.

    Returns:
        Unified success response containing the created task.
    """
    if not registry.has(body.task_type):
        raise BusinessError(f"不支持的任务类型: {body.task_type}", code="INVALID_TASK_TYPE")

    task = await create_task(db, body)

    # Enqueue into ARQ
    arq_pool = await pool.get_pool()
    await arq_pool.enqueue_job("_task_executor", task.id, body.task_type, body.params)

    return success(data=TaskResponse.model_validate(task).model_dump(mode="json"))


@task_router.get("/{task_id}", summary="查询任务状态")
async def query_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> dict:
    """Query the current state of a specific task.

    Args:
        task_id: The task's unique identifier.
        db: Injected database session.

    Returns:
        Unified success response containing the task details.
    """
    task = await get_task(db, task_id)
    if not task:
        raise NotFoundError("任务")
    return success(data=TaskResponse.model_validate(task).model_dump(mode="json"))


@task_router.get("", summary="任务列表")
async def query_task_list(
    db: AsyncSession = Depends(_db_dependency),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    status: TaskStatus | None = Query(default=None, description="状态筛选"),
    task_type: str | None = Query(default=None, description="任务类型筛选"),
) -> dict:
    """List tasks with pagination and optional filters.

    Args:
        db: Injected database session.
        page: 1-based page number.
        page_size: Items per page (1-100).
        status: Optional status filter.
        task_type: Optional task type filter.

    Returns:
        Unified success response containing paginated task list.
    """
    items, total = await list_tasks(
        db,
        page=page,
        page_size=page_size,
        status=status,
        task_type=task_type,
    )
    data = TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in items],
        total=total,
    )
    return success(data=data.model_dump(mode="json"))


@task_router.post("/{task_id}/cancel", summary="取消任务")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> dict:
    """Request cancellation of a running or pending task.

    Sets a Redis flag that the task function can check via ``ctx.is_cancelled()``.
    Tasks that have already completed cannot be cancelled.

    Args:
        task_id: The task's unique identifier.
        db: Injected database session.

    Returns:
        Unified success response with updated task info.
    """
    task = await get_task(db, task_id)
    if not task:
        raise NotFoundError("任务")

    terminal_states = {TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELED}
    if task.status in terminal_states:
        raise BusinessError(f"任务已结束, 状态为 {task.status.value}", code="TASK_ALREADY_FINISHED")

    # Set cancel flag in Redis with TTL
    arq_pool = await pool.get_pool()
    await arq_pool.set(f"task_cancel:{task_id}", b"1", ex=7200)

    return success(data=TaskResponse.model_validate(task).model_dump(mode="json"))


@task_router.post("/{task_id}/retry", summary="重试任务")
async def retry_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> dict:
    """Retry a failed or canceled task.

    Resets status to PENDING, clears result, resets progress, and re-enqueues to ARQ.

    Args:
        task_id: The task's unique identifier.
        db: Injected database session.

    Returns:
        Unified success response with updated task info.
    """
    task = await get_task(db, task_id)
    if not task:
        raise NotFoundError("任务")

    retryable_states = {TaskStatus.FAILED, TaskStatus.CANCELED}
    if task.status not in retryable_states:
        raise BusinessError(
            f"只有失败或已取消的任务可以重试, 当前状态为 {task.status.value}",
            code="TASK_NOT_RETRYABLE",
        )

    # Clear cancel flag from Redis
    arq_pool = await pool.get_pool()
    await arq_pool.delete(f"task_cancel:{task_id}")

    # Reset task state
    await update_task_status(db, task_id, TaskStatus.PENDING)
    await update_task_progress(db, task_id, 0)
    await append_task_log(db, task_id, "任务重试, 重新入队")
    task.result = None
    await db.commit()

    # Re-enqueue
    await arq_pool.enqueue_job("_task_executor", task.id, task.task_type, task.params)

    # Refresh to get latest state
    await db.refresh(task)
    return success(data=TaskResponse.model_validate(task).model_dump(mode="json"))
