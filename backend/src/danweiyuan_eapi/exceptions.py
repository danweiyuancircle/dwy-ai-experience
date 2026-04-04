"""AppError exception hierarchy and FastAPI exception handler registration."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base class for all application-level errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR") -> None:
        self.message = message
        self.code = code


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str) -> None:
        super().__init__(message=f"{resource}不存在", code="NOT_FOUND")


class BusinessError(AppError):
    """Business rule validation failure."""

    pass


class PermissionDeniedError(AppError):
    """Insufficient permissions."""

    def __init__(self) -> None:
        super().__init__(message="权限不足", code="PERMISSION_DENIED")


class AuthenticationError(AppError):
    """Authentication failed or missing."""

    def __init__(self) -> None:
        super().__init__(message="认证失败", code="AUTHENTICATION_FAILED")


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception-to-HTTP-response handlers on a FastAPI app."""

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Handle NotFoundError → 404."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError) -> JSONResponse:
        """Handle BusinessError → 422."""
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied_handler(request: Request, exc: PermissionDeniedError) -> JSONResponse:
        """Handle PermissionDeniedError → 403."""
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"code": exc.code, "message": exc.message},
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """Handle AuthenticationError → 401."""
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"code": exc.code, "message": exc.message},
        )
