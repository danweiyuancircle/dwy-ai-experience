"""分页工具。

通过 Pydantic 校验分页参数,避免业务代码手动校验负数/过大 page_size 导致的全表扫描。
"""

from typing import NamedTuple

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """分页接口的查询参数模型。

    ``page_size`` 上限 100 用于防止前端或爬虫一次拉取全量数据导致 DB 压力过大。
    """

    page: int = Field(default=1, ge=1, description="页码(从 1 开始)")
    page_size: int = Field(default=20, ge=1, le=100, description="每页条数")


class OffsetLimit(NamedTuple):
    """``paginate()`` 的返回值,可直接用于 SQL 的 ``OFFSET`` / ``LIMIT`` 子句。"""

    offset: int
    limit: int


def paginate(page: int, page_size: int) -> OffsetLimit:
    """把 1 基的 page/page_size 换算成 SQL offset/limit。

    ``max(page, 1)`` 兜底保证传入异常值时不会得到负 offset,
    虽然 Pydantic 已校验,但此函数可能被其他非 API 场景直接调用。

    Args:
        page: 页码(从 1 开始)。
        page_size: 每页条数。

    Returns:
        ``OffsetLimit(offset, limit)`` 命名元组。
    """
    offset = (max(page, 1) - 1) * page_size
    return OffsetLimit(offset=offset, limit=page_size)
