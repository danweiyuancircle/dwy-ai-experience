"""Task ORM model and status enumeration."""

import enum
import uuid as uuid_lib

from sqlalchemy import JSON, Enum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from dwyeapi.database import Base, TimestampMixin


class TaskStatus(enum.StrEnum):
    """Task lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELED = "canceled"


def _generate_task_id() -> str:
    """Generate a globally unique task ID."""
    return f"task_{uuid_lib.uuid4().hex}"


class Task(Base, TimestampMixin):
    """Persistent task record.

    Stores task metadata, execution state, progress, logs, and results.
    Uses the same database as the host application via eapi's Base.
    """

    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=_generate_task_id)
    task_type: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[TaskStatus] = mapped_column(Enum(TaskStatus), default=TaskStatus.PENDING)
    params: Mapped[dict] = mapped_column(JSON)
    result: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=None)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    logs: Mapped[str] = mapped_column(Text, default="")
