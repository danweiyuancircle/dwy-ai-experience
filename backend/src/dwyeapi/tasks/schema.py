"""任务 API 请求/响应的 Pydantic schema。"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from dwyeapi.tasks.model import TaskStatus

# 与 Task ORM 列 String(50) 对齐；params 键数/体积限制防超大 body
_TASK_TYPE_MAX_LEN = 50
_PARAMS_MAX_KEYS = 50


class TaskCreate(BaseModel):
    """提交新任务的请求体。

    约束与 ORM / 输入限长规则对齐：``task_type`` 最长 50；``params`` 最多 50 个键。
    """

    task_type: str = Field(min_length=1, max_length=_TASK_TYPE_MAX_LEN, description="已注册的任务类型名")
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="任务参数；键数量上限 50，避免超大 JSON 入库",
        max_length=_PARAMS_MAX_KEYS,
    )


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
