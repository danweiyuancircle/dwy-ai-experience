"""任务 CRUD 与状态流转实现。

router 层只做参数接收与响应封装,所有与数据库交互的逻辑集中在本模块,
便于单元测试和被 TaskContext 复用。
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from dwyeapi import dt
from dwyeapi.tasks.model import Task, TaskStatus
from dwyeapi.tasks.schema import TaskCreate


async def create_task(session: AsyncSession, task_in: TaskCreate) -> Task:
    """在数据库中创建一条新任务记录。

    Args:
        session: 异步数据库会话。
        task_in: 任务创建请求体。

    Returns:
        刚创建并 refresh 后的 Task 实例。
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
    """按 ID 查询单个任务。

    Args:
        session: 异步数据库会话。
        task_id: 任务唯一标识。

    Returns:
        查到返回 Task 实例,否则 None。
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
    """分页查询任务列表,支持按状态和类型过滤。

    Args:
        session: 异步数据库会话。
        page: 页码(从 1 开始)。
        page_size: 每页条数。
        status: 可选,按任务状态过滤。
        task_type: 可选,按任务类型过滤。

    Returns:
        ``(任务列表, 总数)`` 元组。
    """
    query = select(Task)
    count_query = select(func.count()).select_from(Task)

    if status is not None:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    if task_type is not None:
        query = query.where(Task.task_type == task_type)
        count_query = count_query.where(Task.task_type == task_type)

    # 计算总数(单独 count 查询,避免 ORM 取出全部行)
    total_result = await session.execute(count_query)
    total = total_result.scalar_one()

    # 分页数据
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
    """更新任务状态,可选一起写入 result。

    任务不存在时静默返回,避免 worker 侧状态流转与前台 CRUD 竞争时抛异常。

    Args:
        session: 异步数据库会话。
        task_id: 任务唯一标识。
        status: 新状态。
        result: 可选,要写入的结果数据。
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
    """更新任务进度值。

    进度数值会被裁剪到 0-100,防止业务方误传越界值污染 UI。

    Args:
        session: 异步数据库会话。
        task_id: 任务唯一标识。
        progress: 进度百分比,将被裁剪到 0-100。
    """
    task = await get_task(session, task_id)
    if not task:
        return
    task.progress = max(0, min(100, progress))
    await session.commit()


async def append_task_log(session: AsyncSession, task_id: str, message: str) -> None:
    """向任务追加一条带时间戳的日志。

    Args:
        session: 异步数据库会话。
        task_id: 任务唯一标识。
        message: 要写入的日志消息。
    """
    task = await get_task(session, task_id)
    if not task:
        return
    task.logs += f"[{_now_str()}] {message}\n"
    await session.commit()


def _now_str() -> str:
    """返回格式化的当前时间字符串,供日志时间戳使用。"""
    return dt.now_str()
