"""任务函数注册表,基于装饰器做注册。"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

# 异步任务函数签名别名: (TaskContext, dict) -> Any
TaskFunction = Callable[..., Coroutine[Any, Any, Any]]


class TaskRegistry:
    """把 task_type 字符串映射到异步函数的单例注册表。

    用法::

        from dwyeapi.tasks import register

        @register("process_data")
        async def process_data(ctx: TaskContext, params: dict):
            ...
    """

    def __init__(self) -> None:
        """初始化空注册表。"""
        self._tasks: dict[str, TaskFunction] = {}

    def register(self, task_type: str) -> Callable[[TaskFunction], TaskFunction]:
        """返回一个装饰器,把异步函数登记到指定 task_type 下。

        Args:
            task_type: 任务类型的全局唯一字符串。

        Returns:
            保持原函数不变的装饰器。

        Raises:
            ValueError: 同名 task_type 已注册时抛出,避免静默覆盖。
        """

        def decorator(func: TaskFunction) -> TaskFunction:
            if task_type in self._tasks:
                msg = f"Task type '{task_type}' is already registered"
                raise ValueError(msg)
            self._tasks[task_type] = func
            return func

        return decorator

    def get(self, task_type: str) -> TaskFunction | None:
        """根据类型查找已注册的任务函数。

        Args:
            task_type: 任务类型。

        Returns:
            找到则返回对应函数,否则返回 None。
        """
        return self._tasks.get(task_type)

    def list_types(self) -> list[str]:
        """返回所有已注册的 task_type。

        Returns:
            排序后的 task_type 列表。
        """
        return sorted(self._tasks.keys())

    def has(self, task_type: str) -> bool:
        """判断某个 task_type 是否已注册。

        Args:
            task_type: 任务类型。

        Returns:
            已注册返回 True。
        """
        return task_type in self._tasks


# 模块级单例
registry = TaskRegistry()
register = registry.register
