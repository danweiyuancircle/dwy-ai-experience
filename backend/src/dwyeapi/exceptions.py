"""AppError 异常体系以及 FastAPI 全局 handler 注册。

service 层统一抛业务异常(AppError 子类),不感知 HTTP 概念,
由本模块注册的 handler 统一转换为 ``ApiResponse`` 信封格式的 JSON 响应,
保持错误响应和成功响应的结构一致。

本模块除了映射 AppError 子类外,还会接管 FastAPI 默认的非业务异常:

- ``RequestValidationError`` — 请求参数校验失败,返回结构化字段错误列表。
- ``HTTPException`` — 第三方库(如 OAuth2)主动抛出的 HTTP 异常,透传状态码与 headers。
- 未捕获的 ``Exception`` — 兜底 500,堆栈打日志,生产脱敏、开发含详情。
"""

from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from dwyeapi.config import is_dev
from dwyeapi.logger import get_logger
from dwyeapi.response import ApiResponse

_logger = get_logger("dwyeapi.exceptions")


class AppError(Exception):
    """应用级异常基类。

    所有业务异常都应直接或间接继承本类,便于 ``register_exception_handlers``
    按类型统一捕获并返回规范的 ``ApiResponse`` 信封 JSON 响应。
    """

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        """初始化异常。

        Args:
            message: 面向前端/调用方的提示信息,不得回显用户原始输入。
            code: 机器可读的错误码,供前端做分支处理,默认 ``"UNKNOWN_ERROR"``。
        """
        self.message = message
        self.code = code


class NotFoundError(AppError):
    """资源不存在异常,handler 会转换为 HTTP 404 响应。"""

    def __init__(self, resource: str) -> None:
        """初始化资源不存在异常。

        Args:
            resource: 资源名(如 "用户"、"任务"),会被拼接为"{resource}不存在"的消息。
        """
        super().__init__(message=f"{resource}不存在", code="NOT_FOUND")


class BusinessError(AppError):
    """业务规则校验失败异常,handler 会转换为 HTTP 422 响应。

    调用方通常传入自定义 ``code``(如 ``INSUFFICIENT_BALANCE``)以便前端区分具体原因。
    """

    pass


class PermissionDeniedError(AppError):
    """权限不足异常,handler 会转换为 HTTP 403 响应。"""

    def __init__(self) -> None:
        """初始化权限不足异常,使用固定中文提示。"""
        super().__init__(message="权限不足", code="PERMISSION_DENIED")


class AuthenticationError(AppError):
    """认证失败或缺失异常,handler 会转换为 HTTP 401 响应。"""

    def __init__(self) -> None:
        """初始化认证失败异常,使用固定中文提示。"""
        super().__init__(message="认证失败", code="AUTHENTICATION_FAILED")


def _error_response(
    status_code: int,
    code: str,
    message: str,
    data: Any | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    """构造错误响应的 JSONResponse。

    错误响应与 ``ApiResponse.ok()`` 结构对齐:``{code, message, data, timestamp}``,
    仅 ``code`` 由业务错误码填入,``data`` 默认为 ``None``,特殊场景(如校验错误)
    可携带结构化详情。

    Args:
        status_code: HTTP 状态码。
        code: 业务错误码(字符串)。
        message: 错误提示信息。
        data: 可选的错误详情载荷,默认 ``None``。校验错误用它携带字段级错误列表。
        headers: 可选的响应头。用于透传 ``HTTPException.headers`` (如 OAuth2 的
            ``WWW-Authenticate``),避免客户端协商丢失。

    Returns:
        符合 ``ApiResponse`` 信封格式的 JSON 错误响应。
    """
    envelope = ApiResponse(code=code, message=message, data=data)
    return JSONResponse(
        status_code=status_code,
        content=envelope.model_dump(),
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册异常到 ``ApiResponse`` 信封的统一 handler。

    覆盖两类异常:

    1. **业务异常**(AppError 子类):``NotFoundError`` / ``BusinessError`` /
       ``PermissionDeniedError`` / ``AuthenticationError``,分别映射到 404/422/403/401。
    2. **框架异常**:``RequestValidationError`` / ``HTTPException`` / 未捕获 ``Exception``,
       避免 FastAPI 默认的 ``{"detail": ...}`` 格式绕过 ``ApiResponse`` 信封。

    调用一次即可。FastAPI 按异常类型精确匹配,AppError 子类 handler 不会被 ``Exception``
    fallback 截获。

    Args:
        app: 要挂载 handler 的 FastAPI 实例。
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """NotFoundError → 404 的 handler。"""
        return _error_response(status.HTTP_404_NOT_FOUND, exc.code, exc.message)

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        """BusinessError → 422 的 handler。"""
        return _error_response(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.code, exc.message)

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        """PermissionDeniedError → 403 的 handler。"""
        return _error_response(status.HTTP_403_FORBIDDEN, exc.code, exc.message)

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """AuthenticationError → 401 的 handler。"""
        return _error_response(status.HTTP_401_UNAUTHORIZED, exc.code, exc.message)

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """RequestValidationError → 422 的 handler。

        FastAPI 默认把 pydantic 错误原样塞进 ``{"detail": [...]}``,字段路径
        是带 ``body`` / ``query`` / ``path`` 前缀的 tuple,对前端不友好。
        这里把每条错误展平为 ``{field, message}``,field 保留完整路径
        (包括 ``body`` / ``query`` 等段,便于前端精确定位来源)。
        """
        errors: list[dict[str, str]] = [
            {
                "field": ".".join(str(x) for x in e.get("loc", ())),
                "message": e.get("msg", ""),
            }
            for e in exc.errors()
        ]
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_ENTITY,
            "VALIDATION_ERROR",
            "请求参数校验失败",
            data={"errors": errors},
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """HTTPException → 透传状态码 + headers 的 handler。

        透传 ``exc.headers`` 是为了保留 OAuth2 的 ``WWW-Authenticate: Bearer`` 等
        协商头,丢失会导致标准客户端无法按规范重试。
        """
        return _error_response(
            exc.status_code,
            f"HTTP_{exc.status_code}",
            str(exc.detail),
            data=None,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """未捕获 Exception → 500 的 fallback handler。

        生产环境不暴露 ``str(exc)`` 以免泄露字段名、文件路径、SQL 片段等内部信息;
        开发环境附带 ``str(exc)`` 方便定位。两种环境都通过 ``logger.exception``
        把完整 traceback 写到日志,确保排障证据不丢失。
        """
        _logger.exception("未捕获异常")
        message = f"服务器内部错误: {exc!s}" if is_dev() else "服务器内部错误"
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "INTERNAL_ERROR",
            message,
        )
