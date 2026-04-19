"""Task function registry with decorator-based registration."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

# Type alias for an async task function: (TaskContext, dict) -> Any
TaskFunction = Callable[..., Coroutine[Any, Any, Any]]


class TaskRegistry:
    """Singleton registry that maps task_type strings to async functions.

    Usage::

        from dwyeapi.tasks import register

        @register("process_data")
        async def process_data(ctx: TaskContext, params: dict):
            ...
    """

    def __init__(self) -> None:
        """Initialize an empty registry."""
        self._tasks: dict[str, TaskFunction] = {}

    def register(self, task_type: str) -> Callable[[TaskFunction], TaskFunction]:
        """Decorator that registers an async function under a task_type.

        Args:
            task_type: Unique string identifier for this task.

        Returns:
            The original function, unmodified.

        Raises:
            ValueError: If task_type is already registered.
        """

        def decorator(func: TaskFunction) -> TaskFunction:
            if task_type in self._tasks:
                msg = f"Task type '{task_type}' is already registered"
                raise ValueError(msg)
            self._tasks[task_type] = func
            return func

        return decorator

    def get(self, task_type: str) -> TaskFunction | None:
        """Look up a registered task function by type.

        Args:
            task_type: The task type to look up.

        Returns:
            The registered function, or None if not found.
        """
        return self._tasks.get(task_type)

    def list_types(self) -> list[str]:
        """Return all registered task type strings.

        Returns:
            Sorted list of registered task types.
        """
        return sorted(self._tasks.keys())

    def has(self, task_type: str) -> bool:
        """Check if a task type is registered.

        Args:
            task_type: The task type to check.

        Returns:
            True if registered.
        """
        return task_type in self._tasks


# Module-level singleton
registry = TaskRegistry()
register = registry.register
