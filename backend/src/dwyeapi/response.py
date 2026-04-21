"""统一 API 响应封装。

所有接口返回统一的 ``{code, message, data, timestamp}`` 信封,
便于前端公共拦截器按 ``code`` 判断业务状态,保持跨服务一致的响应结构。
"""

import time
from typing import Any


def success(data: Any = None, message: str = "success") -> dict:
    """构造成功响应信封(HTTP 200)。

    Args:
        data: 需要返回给前端的数据,可以是任意可 JSON 序列化对象。
        message: 提示信息,默认 ``success``。

    Returns:
        统一格式的响应字典,包含 ``code`` / ``message`` / ``data`` / ``timestamp``。
    """
    return {"code": 200, "message": message, "data": data, "timestamp": int(time.time())}


def fail(code: int = 400, message: str = "fail") -> dict:
    """构造错误响应信封。

    ``data`` 固定为 None,避免前端在错误态误读 data 字段。

    Args:
        code: 业务错误码,默认 400。
        message: 错误提示,默认 ``fail``。

    Returns:
        统一格式的错误响应字典。
    """
    return {"code": code, "message": message, "data": None, "timestamp": int(time.time())}


def paginated(items: list, total: int, page: int, page_size: int) -> dict:
    """构造分页成功响应信封。

    在 ``success`` 的 ``data`` 中写入 items/total/page/page_size 四个标准字段,
    与全局 ``PaginationParams`` 保持一致,前端只需按此固定结构渲染分页组件。

    Args:
        items: 当前页的数据列表。
        total: 匹配条件的数据总数。
        page: 当前页码(从 1 开始)。
        page_size: 每页条数。

    Returns:
        统一格式的分页响应字典。
    """
    return success(data={"items": items, "total": total, "page": page, "page_size": page_size})
