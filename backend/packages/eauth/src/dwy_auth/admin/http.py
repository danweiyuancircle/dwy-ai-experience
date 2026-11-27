"""独立 Cookie 登录装配；业务路由只复用返回的依赖，不进入认证包。"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Annotated
from urllib.parse import urlsplit

from dwyeapi import ApiResponse
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.concurrency import run_in_threadpool
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ..http import install_safe_validation_handler
from .config import AdminAuthConfig
from .service import COOKIE_NAME, AdminAuth


class LoginRequest(BaseModel):
    """固定有界登录 schema，错误响应不得回显密码。"""

    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256, repr=False)


class AdminSecurityMiddleware:
    """独立登录装配的有界请求与禁止缓存，不读取或拦截业务请求。"""

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] != "http" or not scope["path"].startswith("/api/admin/auth/"):
            await self.app(scope, receive, send)
            return

        async def secure_send(message: Message):
            if message["type"] == "http.response.start":
                message["headers"] = [
                    *message.get("headers", []),
                    (b"cache-control", b"no-store"),
                    (b"x-content-type-options", b"nosniff"),
                ]
            await send(message)

        body = bytearray()
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                return
            chunk = message.get("body", b"")
            if len(body) + len(chunk) > 4096:
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
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, secure_send)


@dataclass(frozen=True)
class AdminAuthBinding:
    """供宿主业务装配使用的管理员依赖，不授予任何用户 Principal。"""

    auth: AdminAuth
    require_admin: Callable[[Request], Awaitable[str]]
    same_origin: Callable[[Request], Awaitable[None]]


def install_admin_auth(
    app: FastAPI, config: AdminAuthConfig, *, install_security: bool = True
) -> AdminAuthBinding:
    """装配登录、当前会话及退出；宿主可保留覆盖全部管理 API 的既有安全中间件。"""
    auth = AdminAuth(config)
    app.state.admin_auth = auth
    install_safe_validation_handler(app)
    if install_security:
        app.add_middleware(AdminSecurityMiddleware)
    router = APIRouter(prefix="/api/admin", tags=["admin"])

    async def same_origin(request: Request):
        """JSON + Strict cookie 为默认边界，额外拒绝带跨域 Origin 的写请求。"""
        origin = request.headers.get("origin")
        if origin is not None:
            if len(origin) > 2048:
                raise HTTPException(403)
            if config.origin is not None:
                if origin != config.origin:
                    raise HTTPException(403)
                return
            try:
                parsed = urlsplit(origin)
            except ValueError:
                # 无效 IPv6 等外部输入不能穿过解析边界成为内部错误。
                raise HTTPException(403) from None
            if parsed.scheme != request.url.scheme or parsed.netloc != request.url.netloc:
                raise HTTPException(403)

    async def require_admin(request: Request) -> str:
        """仅接受宿主 cookie，不能将任一应用 Bearer 提升为管理员。"""
        token = request.cookies.get(COOKIE_NAME, "")
        session = auth.resolve(token)
        if session is None:
            raise HTTPException(401)
        return session.username

    @router.post("/auth/login", dependencies=[Depends(same_origin)])
    async def login(body: LoginRequest, request: Request, response: Response):
        """失败原因统一；密码派生移到框架线程池避免阻塞事件循环。"""
        address = request.client.host if request.client else "unknown"
        if not auth.allow_attempt(address):
            # 通用 HTTPException handler 刻意丢弃 detail；此处只返回固定安全文案。
            return JSONResponse(
                status_code=429,
                content=ApiResponse(
                    code="ADMIN_RATE_LIMITED", message="登录尝试过于频繁，请在5分钟后重试"
                ).model_dump(mode="json"),
                headers={"Retry-After": "300"},
            )
        if not await run_in_threadpool(auth.authenticate, body.username, body.password):
            return JSONResponse(
                status_code=401,
                content=ApiResponse(code="ADMIN_INVALID_CREDENTIALS", message="用户名或密码错误").model_dump(
                    mode="json"
                ),
            )
        previous = request.cookies.get(COOKIE_NAME, "")
        if previous:
            auth.revoke(previous)
        response.set_cookie(
            COOKIE_NAME,
            auth.create_session(),
            max_age=auth.lifetime,
            httponly=True,
            secure=config.secure_cookie,
            samesite="strict",
            path="/api/admin",
        )
        return ApiResponse.ok({"username": auth.username})

    @router.get("/auth/me")
    async def me(username: Annotated[str, Depends(require_admin)]):
        """刷新页面只确认管理身份，不读取业务库。"""
        return ApiResponse.ok({"username": username})

    @router.post("/auth/logout", dependencies=[Depends(require_admin), Depends(same_origin)])
    async def logout(request: Request, response: Response):
        """退出即时撤销服务端状态，删除 cookie 使用一致路径与安全属性。"""
        auth.revoke(request.cookies[COOKIE_NAME])
        response.delete_cookie(
            COOKIE_NAME,
            path="/api/admin",
            httponly=True,
            secure=config.secure_cookie,
            samesite="strict",
        )
        return ApiResponse.ok(None)

    app.include_router(router)
    return AdminAuthBinding(auth, require_admin, same_origin)
