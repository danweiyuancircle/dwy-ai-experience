"""通用认证的 EAPI 集成; 业务用户、权限及会话实现均由宿主显式注入。"""

from collections.abc import Awaitable, Callable
from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import Annotated, Literal
from uuid import UUID

from dwy_auth.contracts import AuthPrincipal, SessionTokens
from dwy_auth.email_auth import EapiEmailCodeSender, EmailAuthConfig, resolve_email_language
from dwy_auth.models import AuthError
from dwy_auth.runtime import AuthRuntime
from fastapi import APIRouter, Depends, FastAPI, Header, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from dwyeapi.response import ApiResponse

__all__ = [
    "AuthBinding",
    "EapiEmailCodeSender",
    "EmailAuthConfig",
    "create_principal_dependency",
    "install_runtime_auth",
]


class _Request(BaseModel):
    """拒绝未知字段并隐藏凭据输入, 防止请求扩展绕过边界。"""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)


class _AdmissionRequest(_Request):
    """宿主可选准入证明;通用认证不解释其业务内容,字节预算在外边界执行。"""

    admission_proof: str | None = Field(default=None, min_length=1, max_length=131072, repr=False)

    @field_validator("admission_proof")
    @classmethod
    def bounded_proof(cls, value):
        """JSON 字符数与网络字节数不同,防止多字节输入绕过同一预算。"""
        if value is not None and len(value.encode()) > 131072:
            raise ValueError("admission proof too large")
        return value


class _EmailCode(_Request):
    """限定邮箱长度和验证码用途。"""

    email: str = Field(min_length=3, max_length=254)
    purpose: Literal["register", "password_reset"]


class _EmailLogin(_AdmissionRequest):
    """密码不进入 repr; Web 登录允许省略设备。"""

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=1, max_length=72, repr=False)
    device_id: UUID | None = None


class _PasswordReset(_Request):
    """新密码与六位 challenge 证明共同校验。"""

    email: str = Field(min_length=3, max_length=254)
    password: str = Field(min_length=15, max_length=72, repr=False)
    code: str = Field(pattern=r"^[0-9]{6}$", min_length=6, max_length=6, repr=False)
    challenge_id: UUID


class _Registration(_PasswordReset, _AdmissionRequest):
    """注册复用重置的证明输入, 可关联原生设备。"""

    device_id: UUID | None = None


class _UsernameLogin(_AdmissionRequest):
    """登录名与展示昵称分离, 规范化由核心负责。"""

    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=72, repr=False)
    device_id: UUID | None = None


class _UsernameBinding(_Request):
    """绑定登录名需重新证明当前密码。"""

    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=72, repr=False)


class _GoogleLogin(_AdmissionRequest):
    """限制外部 ID token 大小并隐藏敏感内容。"""

    id_token: str = Field(min_length=1, max_length=16384, repr=False)
    device_id: UUID | None = None


class _ExternalLogin(_AdmissionRequest):
    """Provider 名仅选择宿主已注册适配器。"""

    provider: str = Field(pattern=r"^[a-z][a-z0-9_-]{0,63}$", min_length=1, max_length=64)
    credential: str = Field(min_length=1, max_length=16384, repr=False)
    device_id: UUID | None = None


class _Reauthentication(_Request):
    """敏感操作重新认证, 不接受客户端自报身份或 proof。"""

    method: Literal["email", "username", "external"]
    identifier: str | None = Field(default=None, min_length=1, max_length=254)
    password: str | None = Field(default=None, min_length=1, max_length=72, repr=False)
    credential: str | None = Field(default=None, min_length=1, max_length=32768, repr=False)


class _EmailUpdateCode(_Request):
    """改邮箱发码只能通过当前会话与限用途的重新认证。"""

    email: str = Field(min_length=3, max_length=254)
    reauthentication: _Reauthentication


class _EmailUpdate(_AdmissionRequest):
    """客户端不得指定主体或设备; 轮换复用当前会话的设备。"""

    email: str = Field(min_length=3, max_length=254)
    code: str = Field(pattern=r"^[0-9]{6}$", min_length=6, max_length=6, repr=False)
    challenge_id: UUID
    new_password: str | None = Field(default=None, min_length=15, max_length=72, repr=False)


class _ExternalBinding(_ExternalLogin):
    """绑定需同时证明当前身份和新外部身份。"""

    reauthentication: _Reauthentication


class _Unlink(_Request):
    """外部解绑必须精确定位 Provider、issuer 和 subject。"""

    kind: Literal["email", "username", "external"]
    value: str = Field(min_length=1, max_length=255)
    provider: str | None = Field(default=None, pattern=r"^[a-z][a-z0-9_-]{0,63}$", min_length=1, max_length=64)
    issuer: str | None = Field(default=None, min_length=1, max_length=512)
    reauthentication: _Reauthentication


class _PasswordChange(_Request):
    """改密需旧密码证明, 新密码遵守注册强度。"""

    old_password: str = Field(min_length=1, max_length=72, repr=False)
    new_password: str = Field(min_length=15, max_length=72, repr=False)


class _Refresh(_AdmissionRequest):
    """refresh 凭据限长且不进入调试表示。"""

    refresh_token: str = Field(min_length=1, max_length=8192, repr=False)


class AuthRequestLimitMiddleware:
    """认证请求按实际接收字节限长, 避免模型校验前解析无界 JSON; 业务接口不受影响。"""

    def __init__(self, app: ASGIApp, *, prefix: str, maximum: int = 163840):
        """只限制认证路由, 不改变业务上传限制。"""
        self.app, self.prefix, self.maximum = app, prefix, maximum

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        """解析 JSON 前按实际字节计数, 不信任 Content-Length。"""
        path = scope.get("path", "").removeprefix(scope.get("root_path", ""))
        if scope["type"] != "http" or not (path == self.prefix or path.startswith(self.prefix + "/")):
            await self.app(scope, receive, send)
            return

        async def secure_send(message: Message) -> None:
            """避免中间缓存保存认证凭据。"""
            if message["type"] == "http.response.start":
                message["headers"] = [*message.get("headers", []), (b"cache-control", b"no-store")]
            await send(message)

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > self.maximum:
                response = JSONResponse(
                    status_code=413,
                    content=ApiResponse(code="REQUEST_TOO_LARGE", message="请求体超过限制").model_dump(),
                )
                await response(scope, receive, secure_send)
                return
            body.extend(chunk)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            """将已限长的请求体交给下游一次。"""
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, secure_send)


@dataclass(frozen=True)
class AuthBinding:
    """宿主自行选择哪些接口使用身份依赖; 此对象不授予任何业务权限。"""

    runtime: AuthRuntime
    require_principal: Callable[..., Awaitable[AuthPrincipal]]
    optional_principal: Callable[..., Awaitable[AuthPrincipal | None]]


async def _token_payload(tokens: SessionTokens, profile_loader) -> ApiResponse:
    """各认证 transport 使用相同业务资料与令牌信封, 不返回内部证明。"""
    user = await profile_loader(tokens.principal)
    return ApiResponse.ok(
        {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": "Bearer",
            "expires_in": tokens.expires_in,
            "user": user.model_dump(mode="json") if isinstance(user, BaseModel) else user,
        }
    )


async def _reauthenticate(
    runtime: AuthRuntime,
    body: _Reauthentication,
    purpose: str,
    request: Request,
    principal: AuthPrincipal | None = None,
):
    """重新认证仍由服务端产生限用途证明, 不接受请求自报的可信身份。"""
    method = body.identifier if body.method == "external" else body.method
    if method is None:
        raise AuthError("INPUT_INVALID", "第三方配置名称缺失", 422)
    provider = runtime.providers.get(method)
    if method == "apple" and callable(getattr(provider, "reauthenticate", None)):
        if principal is None:
            raise AuthError("SESSION_INVALID", "请先登录原有账号", 401)
        return await provider.reauthenticate(
            principal,
            body.credential,
            purpose=purpose,
            remote_key=request.client.host if request.client else "unknown",
        )
    return await runtime.authenticate(
        method,
        identifier=body.identifier,
        password=body.password,
        credential=body.credential,
        purpose=purpose,
        remote_key=request.client.host if request.client else "unknown",
    )


def create_principal_dependency(
    runtime: AuthRuntime, *, optional: bool = False, authorization_limit: int = 8192
) -> Callable[..., Awaitable[AuthPrincipal | None]]:
    """缺失凭据可选匿名; 重复、无效或跨应用凭据始终拒绝, 避免静默降级。"""
    if not 1 <= authorization_limit <= 16384:
        raise ValueError("Invalid authorization limit")

    async def principal(request: Request) -> AuthPrincipal | None:
        """无凭据可匿名, 存在但无效的凭据不能降级。"""
        raw_headers = request.headers.getlist("authorization")
        if not raw_headers and optional:
            return None
        if len(raw_headers) != 1:
            raise AuthError("SESSION_INVALID", "认证失败", 401)
        raw = raw_headers[0]
        scheme, separator, token = raw.partition(" ")
        if (
            len(raw) > authorization_limit
            or scheme.lower() != "bearer"
            or not separator
            or not token
            or any(c.isspace() for c in token)
        ):
            raise AuthError("SESSION_INVALID", "认证失败", 401)
        result = await runtime.verify(token)
        if not isinstance(result, AuthPrincipal) or result.app_id != runtime.app_id:
            raise AuthError("SESSION_INVALID", "认证失败", 401)
        return result

    return principal


def install_runtime_auth(
    app: FastAPI,
    runtime: AuthRuntime,
    *,
    profile_loader: Callable[[AuthPrincipal], Awaitable[BaseModel | dict[str, object]]],
    prefix: str = "/api/v1/auth",
    authorization_limit: int = 8192,
) -> AuthBinding:
    """装配邮箱/第三方认证与可替换会话; 应用资料通过宿主回调返回, 数据库迁移另行执行。"""
    if not prefix.startswith("/") or prefix.endswith("/") or len(prefix) > 128:
        raise ValueError("Invalid authentication route prefix")
    app.add_middleware(AuthRequestLimitMiddleware, prefix=prefix)
    require = create_principal_dependency(runtime, authorization_limit=authorization_limit)
    optional = create_principal_dependency(runtime, optional=True, authorization_limit=authorization_limit)
    principal_dependency = Annotated[AuthPrincipal, Depends(require)]
    router = APIRouter(prefix=prefix, tags=["auth"])

    @app.exception_handler(AuthError)
    async def auth_error(request: Request, exc: AuthError) -> JSONResponse:
        """仅序列化预期认证错误, 不暴露内部异常。"""
        return JSONResponse(
            status_code=exc.status_code,
            content=ApiResponse(code=exc.code, message=exc.message).model_dump(mode="json"),
            headers={"Cache-Control": "no-store"},
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        """保留 EAPI 信封并省略含敏感输入的校验细节。"""
        # 凭据请求不回显 Pydantic input/ctx, 避免密码、验证码及 Provider token 进入响应。
        return JSONResponse(
            status_code=422, content=ApiResponse(code="VALIDATION_ERROR", message="请求参数校验失败").model_dump()
        )

    previous_lifespan = app.router.lifespan_context

    @asynccontextmanager
    async def lifespan(application: FastAPI):
        """保留宿主生命周期, 异常退出同样释放认证资源。"""
        try:
            async with previous_lifespan(application):
                yield
        finally:
            await runtime.aclose()

    app.router.lifespan_context = lifespan

    def remote_key(request: Request) -> str:
        """使用可信连接来源, 不直接信任可伪造的代理 Header。"""
        return request.client.host if request.client else "unknown"

    async def token_payload(tokens: SessionTokens) -> ApiResponse:
        """业务资料完全由宿主加载, 不泄露内部认证证明。"""
        return await _token_payload(tokens, profile_loader)

    async def reauthenticate(body: _Reauthentication, purpose: str, request: Request, principal: AuthPrincipal):
        """传入实际来源与用途, 防止证明跨操作复用。"""
        return await _reauthenticate(runtime, body, purpose, request, principal)

    @router.get("/capabilities")
    async def capabilities():
        """公布宿主启用方式, 不把客户端隐藏按钮视为禁用。"""
        return ApiResponse.ok(
            {
                "methods": sorted(runtime.methods),
                "providers": sorted(runtime.providers) if "external" in runtime.methods else [],
            }
        )

    @router.get("/identities")
    async def identities(principal: principal_dependency):
        """只展示当前主体的登录入口, 不允许通过请求选择其他账户。"""
        return ApiResponse.ok(await runtime.list_identities(principal))

    @router.post("/email/code")
    async def email_code(
        body: _EmailCode,
        request: Request,
        accept_language: Annotated[str | None, Header(max_length=512)] = None,
    ):
        """投递成功才返回 challenge, 来源预算交核心执行。"""
        result = await runtime.send_email_code(
            body.email,
            body.purpose,
            remote_key=remote_key(request),
            language=resolve_email_language(accept_language),
        )
        return ApiResponse.ok(result)

    @router.post("/email/update/code")
    async def email_update_code(
        body: _EmailUpdateCode,
        request: Request,
        principal: principal_dependency,
        accept_language: Annotated[str | None, Header(max_length=512)] = None,
    ):
        """目标邮箱验证码与当前主体绑定, 沿用共享邮件语言和配额。"""
        proof = await reauthenticate(body.reauthentication, "email_update", request, principal)
        result = await runtime.send_email_update_code(
            principal,
            body.email,
            reauthentication=proof,
            remote_key=remote_key(request),
            language=resolve_email_language(accept_language),
        )
        return ApiResponse.ok(result)

    @router.post("/email/update")
    async def email_update(body: _EmailUpdate, request: Request, principal: principal_dependency):
        """轮换成功以既有 token 信封返回同一用户资料。"""
        tokens = await runtime.update_email(
            principal,
            body.email,
            body.code,
            body.challenge_id,
            new_password=body.new_password,
            remote_key=remote_key(request),
            admission_proof=body.admission_proof,
        )
        return await token_payload(tokens)

    @router.post("/register")
    async def register(body: _Registration, request: Request):
        """主体、准入归属及首个会话在同一事务内完成。"""
        return await token_payload(
            await runtime.register_email_session(
                body.email,
                body.password,
                body.code,
                body.challenge_id,
                remote_key=remote_key(request),
                device_id=body.device_id,
                admission_proof=body.admission_proof,
            )
        )

    @router.post("/login")
    async def login(body: _EmailLogin, request: Request):
        """邮箱登录和准入通过后共同签发会话。"""
        return await token_payload(
            await runtime.login(
                "email",
                identifier=body.email,
                password=body.password,
                remote_key=remote_key(request),
                device_id=body.device_id,
                admission_proof=body.admission_proof,
            )
        )

    @router.post("/username/login")
    async def username_login(body: _UsernameLogin, request: Request):
        """用户名入口复用相同准入规则,不形成第二条签发路径。"""
        return await token_payload(
            await runtime.login(
                "username",
                identifier=body.username,
                password=body.password,
                remote_key=remote_key(request),
                device_id=body.device_id,
                admission_proof=body.admission_proof,
            )
        )

    @router.post("/google")
    async def google(body: _GoogleLogin, request: Request):
        """保留原生 Google 路由及缺配置错误,首次账号也必须通过准入。"""
        if "google" not in runtime.providers:
            raise AuthError("GOOGLE_NOT_CONFIGURED", "Google 登录未配置", 503)
        return await token_payload(
            await runtime.login(
                "google",
                credential=body.id_token,
                remote_key=remote_key(request),
                device_id=body.device_id,
                admission_proof=body.admission_proof,
            )
        )

    @router.post("/external/login")
    async def external_login(body: _ExternalLogin, request: Request):
        """按受控配置名选择 Provider,准入失败不留下首次第三方账号。"""
        return await token_payload(
            await runtime.login(
                body.provider,
                credential=body.credential,
                remote_key=remote_key(request),
                device_id=body.device_id,
                admission_proof=body.admission_proof,
            )
        )

    @router.post("/password/reset")
    async def reset(body: _PasswordReset, request: Request):
        """用途隔离的 challenge 消费与旧会话撤销交核心事务执行。"""
        result = await runtime.reset_password(
            body.email, body.password, body.code, body.challenge_id, remote_key=remote_key(request)
        )
        return ApiResponse.ok(result)

    @router.post("/password/change")
    async def change(body: _PasswordChange, principal: principal_dependency):
        """仅当前身份可改密, 成功后撤销已有会话。"""
        await runtime.change_password(principal, body.old_password, body.new_password)
        return ApiResponse.ok({"status": "completed"})

    @router.post("/username/bind")
    async def bind_username(body: _UsernameBinding, principal: principal_dependency):
        """将登录名绑定到当前主体, 不能指定其他用户。"""
        await runtime.bind_username(principal, body.username, body.password)
        return ApiResponse.ok({"status": "completed"})

    @router.post("/external/bind")
    async def bind_external(body: _ExternalBinding, request: Request, principal: principal_dependency):
        """以限用途二次认证证明关联外部身份。"""
        proof = await reauthenticate(body.reauthentication, "bind", request, principal)
        await runtime.bind_external(principal, body.provider, body.credential, reauthentication=proof)
        return ApiResponse.ok({"status": "completed"})

    @router.post("/identity/unlink")
    async def unlink(body: _Unlink, request: Request, principal: principal_dependency):
        """核心验证重新认证和最后登录方式保护后才解绑。"""
        kind = body.provider if body.kind == "external" else body.kind
        if kind is None:
            raise AuthError("INPUT_INVALID", "第三方配置名称缺失", 422)
        proof = await reauthenticate(body.reauthentication, "unlink", request, principal)
        await runtime.unlink_identity(principal, kind, body.value, issuer=body.issuer, reauthentication=proof)
        return ApiResponse.ok({"status": "completed"})

    @router.post("/refresh")
    async def refresh(body: _Refresh, request: Request):
        """完整刷新流程由所选会话后端负责。"""
        return await token_payload(
            await runtime.refresh(
                body.refresh_token, admission_proof=body.admission_proof, remote_key=remote_key(request)
            )
        )

    @router.post("/logout")
    async def logout(principal: principal_dependency):
        """撤销当前会话, 由后端确保后续验证失效。"""
        await runtime.logout(principal)
        return ApiResponse.ok(None)

    app.include_router(router)
    return AuthBinding(runtime, require, optional)
