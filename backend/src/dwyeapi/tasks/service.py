"""Task CRUD operations and state transitions."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dwyeapi import dt
from dwyeapi.tasks.model import Task, TaskStatus
from dwyeapi.tasks.schema import TaskCreate


async def create_task(session: AsyncSession, task_in: TaskCreate) -> Task:
    """Create a new task record in the database.

    Args:
        session: Async database session.
        task_in: Task creation payload.

    Returns:
        The newly created Task instance.
    """
    task = Task(
        task_type=task_in.task_type,
        params=task_in.params,
        logs=f"[{_now_str()}] 任务已创建, 等待执行\n",
    )
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def get_task(session: AsyncSession, task_id: str) -> Task | None:
    """Query a single task by ID.

    Args:
        session: Async database session.
        task_id: The task's unique identifier.

    Returns:
        The Task instance, or None if not found.
    """
    result = await session.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def list_tasks(
    session: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    status: TaskStatus | None = None,
    task_type: str | None = None,
) -> tuple[list[Task], int]:
    """List tasks with pagination and optional filters.

    Args:
        session: Async database session.
        page: 1-based page number.
        page_size: Number of items per page.
        status: Optional status filter.
        task_type: Optional task type filter.

    Returns:
        Tuple of (task list, total count).
    """
    query = select(Task)
    count_query = select(func.count()).select_from(Task)

    if status is not None:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    if task_type is not None:
        query = query.where(Task.task_type == task_type)
        count_query = count_query.where(Task.task_type == task_type)

    # Total count
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # Paginated items
    offset = (max(page, 1) - 1) * page_size
    query = query.order_by(Task.created_at.desc()).offset(offset).limit(page_size)
    result = await session.execute(query)
    items = list(result.scalars().all())

    return items, total


async def update_task_status(
    session: AsyncSession,
    task_id: str,
    status: TaskStatus,
    result: dict | None = None,
) -> None:
    """Update a task's status and optionally its result.

    Args:
        session: Async database session.
        task_id: The task's unique identifier.
        status: New status to set.
        result: Optional result data to store.
    """
    task = await get_task(session, task_id)
    if not task:
        return
    task.status = status
    if result is not None:
        task.result = result
    task.updated_at = dt.now()
    await session.commit()


async def update_task_progress(session: AsyncSession, task_id: str, progress: int) -> None:
    """Update a task's progress value (0-100).

    Args:
        session: Async database session.
        task_id: The task's unique identifier.
        progress: Progress percentage, clamped to 0-100.
    """
    task = await get_task(session, task_id)
    if not task:
        return
    task.progress = max(0, min(100, progress))
    await session.commit()


async def append_task_log(session: AsyncSession, task_id: str, message: str) -> None:
    """Append a timestamped log entry to a task.

    Args:
        session: Async database session.
        task_id: The task's unique identifier.
        message: Log message to append.
    """
    task = await get_task(session, task_id)
    if not task:
        return
    task.logs += f"[{_now_str()}] {message}\n"
    await session.commit()


def _now_str() -> str:
    """Return current time formatted as a string."""
    return dt.now_str()
