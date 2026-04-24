"""任务系统现成可挂载的 FastAPI router。

提供提交、查询、列表、取消、重试等接口,业务项目通过
``app.include_router(task_router)`` 直接挂载。所有接口返回统一 ``ApiResponse`` 信封。
"""

from __future__ import annotations

from collections.abc import AsyncGenerator, Callable

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dwyeapi.exceptions import BusinessError, NotFoundError
from dwyeapi.response import ApiResponse, PageData
from dwyeapi.tasks import pool
from dwyeapi.tasks.model import TaskStatus
from dwyeapi.tasks.registry import registry
from dwyeapi.tasks.schema import TaskCreate, TaskResponse
from dwyeapi.tasks.service import (
    append_task_log,
    create_task,
    get_task,
    list_tasks,
    update_task_progress,
    update_task_status,
)

task_router = APIRouter(prefix="/tasks", tags=["tasks"])

# 此变量由 setup_tasks() 在应用启动阶段注入。
_get_db: Callable[[], AsyncGenerator[AsyncSession]] | None = None


async def _db_dependency() -> AsyncGenerator[AsyncSession]:
    """代理到业务侧 get_db 依赖的异步生成器。

    Yields:
        从配置的 session 工厂取出的 AsyncSession。

    Raises:
        RuntimeError: 未调用过 ``setup_tasks()`` 时抛出。
    """
    if _get_db is None:
        msg = "Task system not initialized. Call setup_tasks() first."
        raise RuntimeError(msg)
    async for session in _get_db():
        yield session


@task_router.post("", response_model=ApiResponse[TaskResponse], summary="提交耗时任务")
async def submit_task(
    body: TaskCreate,
    db: AsyncSession = Depends(_db_dependency),
) -> ApiResponse[TaskResponse]:
    """提交一个新的异步任务到后台执行。"""
    if not registry.has(body.task_type):
        raise BusinessError(f"不支持的任务类型: {body.task_type}", code="INVALID_TASK_TYPE")

    task = await create_task(db, body)

    # 将任务推入 ARQ 队列
    arq_pool = await pool.get_pool()
    await arq_pool.enqueue_job("_task_executor", task.id, body.task_type, body.params)

    return ApiResponse.ok(TaskResponse.model_validate(task))


@task_router.get("/{task_id}", response_model=ApiResponse[TaskResponse], summary="查询任务状态")
async def query_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> ApiResponse[TaskResponse]:
    """查询指定任务的当前状态。"""
    task = await get_task(db, task_id)
    if not task:
        raise NotFoundError("任务")
    return ApiResponse.ok(TaskResponse.model_validate(task))


@task_router.get("", response_model=ApiResponse[PageData[TaskResponse]], summary="任务列表")
async def query_task_list(
    db: AsyncSession = Depends(_db_dependency),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页条数"),
    status: TaskStatus | None = Query(default=None, description="状态筛选"),
    task_type: str | None = Query(default=None, description="任务类型筛选"),
) -> ApiResponse[PageData[TaskResponse]]:
    """分页查询任务列表,支持按状态和类型过滤。"""
    items, total = await list_tasks(
        db,
        page=page,
        page_size=page_size,
        status=status,
        task_type=task_type,
    )
    return ApiResponse.page(
        items=[TaskResponse.model_validate(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@task_router.post("/{task_id}/cancel", response_model=ApiResponse[TaskResponse], summary="取消任务")
async def cancel_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> ApiResponse[TaskResponse]:
    """请求取消一个运行中或排队中的任务。

    实现方式是在 Redis 设置 ``task_cancel:{task_id}`` 标志,任务函数通过
    ``ctx.is_cancelled()`` 读取并按需退出;已结束的任务不能再被取消。
    """
    task = await get_task(db, task_id)
    if not task:
        raise NotFoundError("任务")

    terminal_states = {TaskStatus.SUCCESS, TaskStatus.FAILED, TaskStatus.CANCELED}
    if task.status in terminal_states:
        raise BusinessError(f"任务已结束, 状态为 {task.status.value}", code="TASK_ALREADY_FINISHED")

    # 在 Redis 中写入取消标志并设置 TTL,避免 key 长期残留
    arq_pool = await pool.get_pool()
    await arq_pool.set(f"task_cancel:{task_id}", b"1", ex=7200)

    return ApiResponse.ok(TaskResponse.model_validate(task))


@task_router.post("/{task_id}/retry", response_model=ApiResponse[TaskResponse], summary="重试任务")
async def retry_task(
    task_id: str,
    db: AsyncSession = Depends(_db_dependency),
) -> ApiResponse[TaskResponse]:
    """重试一个失败或已取消的任务。

    把状态重置为 PENDING、清空 result、进度归零,再次入队到 ARQ。
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

    # 清除 Redis 中的取消标志,避免重试后立即又被取消
    arq_pool = await pool.get_pool()
    await arq_pool.delete(f"task_cancel:{task_id}")

    # 重置任务状态
    await update_task_status(db, task_id, TaskStatus.PENDING)
    await update_task_progress(db, task_id, 0)
    await append_task_log(db, task_id, "任务重试, 重新入队")
    task.result = None
    await db.commit()

    # 重新入队
    await arq_pool.enqueue_job("_task_executor", task.id, task.task_type, task.params)

    # 刷新以拿到最新状态
    await db.refresh(task)
    return ApiResponse.ok(TaskResponse.model_validate(task))
