"""任务 API 请求/响应的 Pydantic schema。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict

from dwyeapi.tasks.model import TaskStatus


class TaskCreate(BaseModel):
    """提交新任务的请求体。"""

    task_type: str
    params: dict[str, Any]


class TaskResponse(BaseModel):
    """任务详情响应体,覆盖状态、进度、日志与结果等字段。"""

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
    """任务分页列表响应体,``total`` 用于前端分页组件计算总页数。"""

    items: list[TaskResponse]
    total: int
