"""ORM model base — re-exports from danweiyuan_base."""

from danweiyuan_base.database import Base, TimestampMixin

__all__ = ["Base", "TimestampMixin"]
