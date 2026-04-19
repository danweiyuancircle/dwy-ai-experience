"""Pydantic schemas for task API requests and responses."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from dwyeapi.tasks.model import TaskStatus


class TaskCreate(BaseModel):
    """Request body for submitting a new task."""

    task_type: str
    params: dict[str, Any]


class TaskResponse(BaseModel):
    """Single task detail returned by the API."""

    id: str
    task_type: str
    status: TaskStatus
    params: dict[str, Any]
    result: dict[str, Any] | None
    progress: int
    logs: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """Paginated task list returned by the API."""

    items: list[TaskResponse]
    total: int
