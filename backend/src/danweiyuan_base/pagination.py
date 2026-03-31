"""Pagination utilities."""

from typing import NamedTuple

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-based)")
    page_size: int = Field(default=20, ge=1, le=100, description="Items per page")


class OffsetLimit(NamedTuple):
    """Result of paginate() — ready for SQL OFFSET / LIMIT."""

    offset: int
    limit: int


def paginate(page: int, page_size: int) -> OffsetLimit:
    """Calculate SQL offset and limit from 1-based page and page_size."""
    offset = (max(page, 1) - 1) * page_size
    return OffsetLimit(offset=offset, limit=page_size)
