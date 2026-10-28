"""Apple 多步骤授权 transport; 宿主先安装通用认证的异常、限长与会话依赖。"""

from collections.abc import Awaitable, Callable
from typing import Annotated, Literal
from uuid import UUID

from dwy_auth.contracts import AuthPrincipal
from dwy_auth.models import AuthError
from fastapi import APIRouter, Body, Depends, FastAPI, Request
from pydantic import BaseModel, Field

from dwyeapi.auth import AuthBinding, _reauthenticate, _Reauthentication, _Request, _token_payload
from dwyeapi.response import ApiResponse


class AppleChallengeRequest(_Request):
    """绑定挑战必须关联当前会话; 普通登录不信任客户端指定的主体。"""

    purpose: Literal["login", "bind"] = "login"


class AppleLoginRequest(_Request):
    """授权材料只用于本次交换, 不回显或进入模型调试输出。"""

    challenge_id: UUID
    identity_token: str = Field(min_length=1, max_length=16384, repr=False)
    authorization_code: str = Field(min_length=1, max_length=4096, repr=False)
    device_id: UUID | None = None
    display_name: str | None = Field(default=None, max_length=255)


class AppleBindingRequest(AppleLoginRequest):
    """同时验证原有账号与新 Apple 授权, 不能按邮箱合并。"""

    reauthentication: _Reauthentication


class AppleNotificationRequest(_Request):
    """Apple 登录账号通知使用 payload JWT, 与 App Store 通知协议分开。"""

    payload: str = Field(min_length=1, max_length=16384, repr=False)


def install_apple_auth(
    app: FastAPI,
    service,
    *,
    binding: AuthBinding,
    profile_loader: Callable[[AuthPrincipal], Awaitable[BaseModel | dict[str, object]]],
    prefix: str = "/api/v1/auth",
) -> None:
    """安装已配置应用的 Apple 路由; 表迁移、重试工作器与业务清理由宿主装配。"""
    if binding.runtime is not service.runtime:
        raise ValueError("Apple transport must use the application's authentication runtime")
    if not prefix.startswith("/") or prefix.endswith("/") or len(prefix) > 128:
        raise ValueError("Invalid authentication route prefix")
    required = Annotated[AuthPrincipal, Depends(binding.require_principal)]
    optional = Annotated[AuthPrincipal | None, Depends(binding.optional_principal)]
    router = APIRouter(prefix=prefix + "/apple", tags=["auth"])

    @router.post("/challenges", status_code=200, response_model=ApiResponse)
    async def challenge(
        request: Request,
        principal: optional,
        body: Annotated[AppleChallengeRequest | None, Body()] = None,
    ):
        body = body or AppleChallengeRequest()
        if body.purpose == "bind" and principal is None:
            raise AuthError("SESSION_INVALID", "请先登录原有账号", 401)
        return ApiResponse.ok(
            await service.challenge(
                purpose=body.purpose,
                principal=principal if body.purpose == "bind" else None,
                remote_key=request.client.host if request.client else "unknown",
            )
        )

    @router.post("", status_code=200, response_model=ApiResponse)
    async def login(body: AppleLoginRequest, request: Request):
        tokens = await service.login(
            str(body.challenge_id),
            body.identity_token,
            body.authorization_code,
            device_id=body.device_id,
            display_name=body.display_name,
            remote_key=request.client.host if request.client else "unknown",
        )
        return await _token_payload(tokens, profile_loader)

    @router.post("/bind", status_code=200, response_model=ApiResponse)
    async def bind(body: AppleBindingRequest, request: Request, principal: required):
        proof = await _reauthenticate(binding.runtime, body.reauthentication, "bind", request)
        await service.bind(
            principal,
            str(body.challenge_id),
            body.identity_token,
            body.authorization_code,
            reauthentication=proof,
            display_name=body.display_name,
            remote_key=request.client.host if request.client else "unknown",
        )
        return ApiResponse.ok({"status": "completed"})

    @router.post("/notifications", status_code=200, response_model=ApiResponse)
    async def notification(body: AppleNotificationRequest):
        return ApiResponse.ok(await service.notification(body.payload))

    app.include_router(router)
