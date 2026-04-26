"""任务 ORM 模型与状态枚举。"""

import enum
import uuid as uuid_lib

from sqlalchemy import JSON, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from dwyeapi.database import Base, TimestampMixin


class TaskStatus(enum.StrEnum):
    """任务生命周期状态枚举。

    由 pending(待执行)到 running(执行中),再到 success/failed/canceled 三种终态。
    """

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"


def _generate_task_id() -> str:
    """生成全局唯一的任务 ID(``task_`` + 32 位 UUID hex)。"""
    return f"task_{uuid_lib.uuid4().hex}"


class Task(Base, TimestampMixin):
    """持久化的任务记录。

    存储任务元数据、执行状态、进度、日志和结果。复用业务项目的数据库(共享 eapi Base),
    无需额外独立 DB 连接,也让任务历史与业务数据处于同一事务边界。
    """

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_generate_task_id, comment="任务 ID")  # 任务 ID
    task_type: Mapped[str] = mapped_column(String(50), index=True, comment="任务类型")  # 任务类型
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING, comment="执行状态")  # 执行状态
    params: Mapped[dict] = mapped_column(JSON, comment="任务参数(JSON)")  # 任务参数(JSON)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None, comment="执行结果(JSON)")  # 执行结果(JSON)
    progress: Mapped[int] = mapped_column(Integer, default=0, comment="进度百分比 0-100")  # 进度百分比 0-100
    logs: Mapped[str] = mapped_column(Text, default="", comment="执行日志")  # 执行日志
