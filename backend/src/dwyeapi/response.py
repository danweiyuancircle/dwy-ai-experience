"""统一 API 响应信封。

所有接口返回统一的 ``{code, message, data, timestamp}`` 信封,
便于前端拦截器按 ``code`` 判断业务状态,保持跨服务一致的响应结构。

- 成功态 ``code`` 固定为 ``"SUCCESS"``
- 错误态 ``code`` 由 ``dwyeapi.exceptions`` 的 handler 填入业务错误码(如 ``"NOT_FOUND"``)
- HTTP 状态码保持语义(404 就是 404),前端可按状态码和 ``code`` 字段双重判断
"""

import time
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PageData(BaseModel, Generic[T]):
    """分页数据载荷。

    配合 ``ApiResponse`` 使用,完整响应类型为 ``ApiResponse[PageData[UserResponse]]``。
    字段与 ``dwyeapi.pagination.PaginationParams`` 一一对应,前端一套分页组件通用。
    """

    items: list[T] = Field(description="当前页的数据列表")
    total: int = Field(description="匹配条件的数据总数")
    page: int = Field(description="当前页码(从 1 开始)")
    page_size: int = Field(description="每页条数")

    model_config = ConfigDict(from_attributes=True)


class ApiResponse(BaseModel, Generic[T]):
    """统一 API 响应信封。

    成功态通过 ``ApiResponse.ok()`` / ``ApiResponse.page()`` 构造;
    错误态由 ``register_exception_handlers`` 注册的 handler 统一构造,
    业务代码不应直接实例化本类用于错误响应。
    """

    code: str = Field(default="SUCCESS", description="业务状态码,成功为 SUCCESS,失败为业务错误码")
    message: str = Field(default="success", description="提示信息,可直接展示给用户")
    data: T | None = Field(default=None, description="响应数据载荷,错误时为 null")
    timestamp: int = Field(default_factory=lambda: int(time.time()), description="Unix 秒级时间戳")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def ok(cls, data: T, message: str = "success") -> "ApiResponse[T]":
        """构造单体成功响应。

        Args:
            data: 响应数据,可以是 Pydantic 模型、dict、list 或标量。
            message: 可选提示信息,默认 ``"success"``。

        Returns:
            封装好的 ``ApiResponse[T]`` 实例,可直接作为路由返回值。
        """
        return cls[T](code="SUCCESS", message=message, data=data)

    @classmethod
    def page(
        cls,
        items: list[T],
        total: int,
        page: int,
        page_size: int,
        message: str = "success",
    ) -> "ApiResponse[PageData[T]]":
        """构造分页成功响应。

        Args:
            items: 当前页数据列表。
            total: 命中条件的总数。
            page: 当前页码(从 1 开始)。
            page_size: 每页条数。
            message: 可选提示信息,默认 ``"success"``。

        Returns:
            封装好的 ``ApiResponse[PageData[T]]`` 实例。
        """
        return cls[PageData[T]](
            code="SUCCESS",
            message=message,
            data=PageData[T](items=items, total=total, page=page, page_size=page_size),
        )
