"""Google 登录公开但必须验签，刷新使用独立凭据，退出使用应用会话鉴权。"""

from contextlib import asynccontextmanager
from typing import Annotated, Literal
from uuid import UUID

from dwyeapi import ApiResponse
from dwyeapi.identity import IdentityVerifier, Principal, create_identity_dependency
from fastapi import Depends, FastAPI, Query, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from .email_auth import EmailCodeChallenge, EmailCodePurpose
from .models import AccountDeletion, AuthError, DevicePage, DeviceQuery, TokenResponse
from .service import AuthService


class GoogleLogin(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    id_token: str = Field(min_length=1, max_length=16384, repr=False)
    device_id: UUID


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    refresh_token: str = Field(min_length=1, max_length=256, repr=False)


class EmailRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    email: str = Field(min_length=3, max_length=254)


class EmailCodeRequest(EmailRequest):
    purpose: EmailCodePurpose


class EmailLogin(EmailRequest):
    password: str = Field(min_length=1, max_length=72, repr=False)
    device_id: UUID


class PasswordReset(EmailRequest):
    password: str = Field(min_length=15, max_length=72, repr=False)
    code: str = Field(min_length=6, max_length=6, pattern=r"^[0-9]{6}$", repr=False)
    challenge_id: UUID


class EmailRegistration(PasswordReset):
    device_id: UUID


class PasswordResetResponse(BaseModel):
    status: Literal["completed"] = "completed"


def install_safe_validation_handler(app: FastAPI) -> None:
    """不回显请求凭据；使用认证包的宿主应对业务错误沿用安全信封。"""

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ApiResponse(code="VALIDATION_ERROR", message="请求参数校验失败").model_dump(),
        )


def install_auth_routes(
    app: FastAPI,
    service: AuthService,
    *,
    identity_verifier: IdentityVerifier | None = None,
    authorization_limit: int = 8192,
) -> None:
    """显式装配服务、可信验证适配器与输入预算，不读取宿主配置。"""
    install_safe_validation_handler(app)
    require_principal = create_identity_dependency(
        service.app_id,
        identity_verifier if identity_verifier is not None else service,
        authorization_limit=authorization_limit,
    )
    app.state.auth_service = service
    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application):
        try:
            async with previous_lifespan(application):
                yield
        finally:
            await service.aclose()

    app.router.lifespan_context = lifespan

    @app.exception_handler(AuthError)
    async def auth_error(request: Request, exc: AuthError):
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(
                code=exc.code,
                message=exc.message,
                data=None,
            ).model_dump(mode="json"),
        )

    def remote_key(request: Request) -> str:
        # 只信ASGI peer；代理宿主需显式配置可信proxy，禁止消费任意X-Forwarded-For。
        return request.client.host if request.client else "unknown"

    @app.post("/api/v1/auth/email/code", response_model=ApiResponse[EmailCodeChallenge])
    async def email_code(body: EmailCodeRequest, request: Request, response: Response):
        response.headers["Cache-Control"] = "no-store"
        return ApiResponse.ok(
            await service.send_email_code(body.email, body.purpose, remote_key=remote_key(request))
        )

    @app.post("/api/v1/auth/register", response_model=ApiResponse[TokenResponse])
    async def email_register(body: EmailRegistration, request: Request, response: Response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return ApiResponse.ok(
            await service.register_email(
                body.email,
                body.password,
                body.code,
                body.challenge_id,
                body.device_id,
                remote_key=remote_key(request),
            )
        )

    @app.post("/api/v1/auth/login", response_model=ApiResponse[TokenResponse])
    async def email_login(body: EmailLogin, request: Request, response: Response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return ApiResponse.ok(
            await service.login_email(
                body.email, body.password, body.device_id, remote_key=remote_key(request)
            )
        )

    @app.post("/api/v1/auth/password/reset", response_model=ApiResponse[PasswordResetResponse])
    async def password_reset(body: PasswordReset, request: Request, response: Response):
        response.headers["Cache-Control"] = "no-store"
        return ApiResponse.ok(
            await service.reset_password(
                body.email, body.password, body.code, body.challenge_id, remote_key=remote_key(request)
            )
        )

    @app.post("/api/v1/auth/google", response_model=ApiResponse[TokenResponse])
    async def google(body: GoogleLogin, response: Response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return ApiResponse.ok(await service.login(body.id_token, body.device_id))

    @app.post("/api/v1/auth/refresh", response_model=ApiResponse[TokenResponse])
    async def refresh(body: RefreshRequest, response: Response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["Pragma"] = "no-cache"
        return ApiResponse.ok(await service.refresh(body.refresh_token))

    @app.post("/api/v1/auth/logout", response_model=ApiResponse[None])
    async def logout(identity: Annotated[Principal, Depends(require_principal)]):
        await service.logout(identity)
        return ApiResponse.ok(None)

    @app.get("/api/v1/devices", response_model=ApiResponse[DevicePage])
    async def devices(
        query: Annotated[DeviceQuery, Query()],
        identity: Annotated[Principal, Depends(require_principal)],
        response: Response,
    ):
        """本人设备列表不接受用户标识，结果禁止缓存。"""
        response.headers["Cache-Control"] = "no-store"
        return ApiResponse.ok(await service.list_devices(identity, limit=query.limit, cursor=query.cursor))

    @app.delete("/api/v1/devices/{device_id}", response_model=ApiResponse[None])
    async def revoke_device(device_id: UUID, identity: Annotated[Principal, Depends(require_principal)]):
        """设备 UUID 只作为本人会话过滤条件，不能选择其他账户。"""
        await service.revoke_device(identity, device_id)
        return ApiResponse.ok(None)

    @app.delete("/api/v1/account", response_model=ApiResponse[AccountDeletion])
    async def delete_account(identity: Annotated[Principal, Depends(require_principal)]):
        """仅删除当前鉴权账户，业务清理与撤销凭据同事务完成。"""
        return ApiResponse.ok(await service.delete_account(identity))
