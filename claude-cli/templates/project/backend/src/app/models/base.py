"""ORM model base — re-exports from dwyeapi."""

from dwyeapi.database import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
