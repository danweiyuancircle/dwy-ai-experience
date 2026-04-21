"""AppError 异常体系以及 FastAPI 全局 handler 注册。

service 层统一抛业务异常(AppError 子类),不感知 HTTP 概念,
由本模块注册的 handler 统一转换为标准 JSON 响应,保持错误格式一致。
"""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """应用级异常基类。

    所有业务异常都应直接或间接继承本类,便于 ``register_exception_handlers``
    按类型统一捕获并返回规范的 ``{"code", "message"}`` JSON 响应。
    """

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        """初始化异常。

        Args:
            message: 面向前端/调用方的提示信息,不得回显用户原始输入。
            code: 机器可读的错误码,供前端做分支处理,默认 ``UNKNOWN_ERROR``。
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


def register_exception_handlers(app: FastAPI) -> None:
    """为 FastAPI 应用注册 AppError 体系到 HTTP 响应的 handler。

    调用一次即可把 ``NotFoundError`` / ``BusinessError`` / ``PermissionDeniedError`` /
    ``AuthenticationError`` 映射到合适的状态码和统一的 JSON 格式。

    Args:
        app: 要挂载 handler 的 FastAPI 实例。
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """NotFoundError → 404 的 handler。"""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        """BusinessError → 422 的 handler。"""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        """PermissionDeniedError → 403 的 handler。"""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """AuthenticationError → 401 的 handler。"""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"code": exc.code, "message": exc.message},
        )
