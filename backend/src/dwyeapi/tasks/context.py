"""TaskContext — 注入到任务函数的上下文对象。

统一封装数据库访问、日志记录、进度更新、取消检查等能力,业务任务函数只聚焦核心逻辑,
无需重复处理这些跨任务通用的样板代码。
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from dwyeapi.tasks import service
from dwyeapi.tasks.model import TaskStatus


class TaskContext:
    """注入到每个已注册任务函数的执行上下文。

    提供日志、进度更新、取消检查与数据库访问等辅助方法,让任务函数只需写业务逻辑。

    Attributes:
        task_id: 当前任务的唯一标识。
        task_type: 已注册的任务类型字符串。
        params: 任务提交时传入的参数。
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
        """初始化 TaskContext。

        Args:
            task_id: 任务唯一标识。
            task_type: 已注册的任务类型名称。
            params: 任务输入参数。
            session_factory: 异步 SQLAlchemy session 工厂。
            redis: ARQ Redis 连接,用于读取取消标记。
        """
        self.task_id = task_id
        self.task_type = task_type
        self.params = params
        self._session_factory = session_factory
        self._redis = redis
        self._cancelled = False

    async def log(self, message: str) -> None:
        """追加一条带时间戳的任务日志。

        Args:
            message: 要写入任务日志的消息内容。
        """
        async with self._session() as session:
            await service.append_task_log(session, self.task_id, message)

    async def update_progress(self, value: int, message: str = "") -> None:
        """更新任务进度(0-100),可选附带一条日志。

        Args:
            value: 进度百分比,service 层会裁剪到 0-100 范围。
            message: 附加日志消息,为空时只更新进度不写日志。
        """
        async with self._session() as session:
            await service.update_task_progress(session, self.task_id, value)
            if message:
                await service.append_task_log(session, self.task_id, message)

    async def is_cancelled(self) -> bool:
        """检查当前任务是否被请求取消。

        读取 Redis key ``task_cancel:{task_id}``,首次检测到后缓存到内存,
        避免业务代码在循环里反复查询 Redis。

        Returns:
            任务已被标记为取消返回 True,否则 False。
        """
        if self._cancelled:
            return True
        val = await self._redis.get(f"task_cancel:{self.task_id}")
        if val is not None:
            self._cancelled = True
        return self._cancelled

    @asynccontextmanager
    async def db(self) -> AsyncIterator[AsyncSession]:
        """以上下文管理器形式提供异步数据库会话。

        用法::

            async with ctx.db() as session:
                result = await session.execute(select(MyModel))

        Yields:
            绑定到应用数据库的 AsyncSession。
        """
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def _session(self) -> AsyncIterator[AsyncSession]:
        """内部短生命周期 session 辅助方法,专门给框架内部调用。"""
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
    """执行任务函数并包装完整的生命周期管理。

    处理任务生命周期:

    1. 设置状态为 RUNNING;
    2. 创建 TaskContext 并调用业务函数;
    3. 正常返回 → 状态 SUCCESS,结果写入 result 字段;
    4. 抛异常 → 状态 FAILED,错误信息写入 result;
    5. 业务函数内已标记取消 → 状态 CANCELED。

    Args:
        task_id: 任务唯一标识。
        task_type: 已注册的任务类型字符串。
        params: 任务输入参数。
        func: 要执行的异步业务函数。
        session_factory: 异步 SQLAlchemy session 工厂。
        redis: ARQ Redis 连接。
    """
    ctx = TaskContext(
        task_id=task_id,
        task_type=task_type,
        params=params,
        session_factory=session_factory,
        redis=redis,
    )

    # 标记为 RUNNING
    async with session_factory() as session:
        await service.update_task_status(session, task_id, TaskStatus.RUNNING)
        await service.append_task_log(session, task_id, "任务开始执行")

    try:
        result = await func(ctx, params)

        # 若业务函数内部已标记取消,则按取消收尾
        if ctx._cancelled:
            async with session_factory() as session:
                await service.update_task_status(session, task_id, TaskStatus.CANCELED)
                await service.append_task_log(session, task_id, "任务已取消")
            return

        # 成功路径
        result_data = result if isinstance(result, dict) else {"result": result}
        async with session_factory() as session:
            await service.update_task_status(session, task_id, TaskStatus.SUCCESS, result=result_data)
            await service.update_task_progress(session, task_id, 100)
            await service.append_task_log(session, task_id, "任务执行成功")

    except Exception as exc:
        # 失败路径
        async with session_factory() as session:
            await service.update_task_status(
                session,
                task_id,
                TaskStatus.FAILED,
                result={"error": str(exc)},
            )
            await service.append_task_log(session, task_id, f"任务执行失败: {exc}")
        raise
