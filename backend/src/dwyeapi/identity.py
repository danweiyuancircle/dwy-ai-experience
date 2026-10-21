"""只定义可信身份合同;本包不签发 token,也不选择登录方式。"""

import re
from collections.abc import Awaitable, Callable
from typing import Annotated, Protocol
from uuid import UUID

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field

from dwyeapi.exceptions import AuthenticationError


class Principal(BaseModel):
    """验证器产出的不可变身份;UUID 必须来自已验证的应用内账户/会话/设备。"""

    model_config = ConfigDict(strict=True, extra="forbid", frozen=True, hide_input_in_errors=True)

    app_id: str = Field(
        min_length=1,
        max_length=32,
        pattern=r"^[a-z][a-z0-9-]*$",
        description="身份适用应用,HTTP 层再次比对",
    )
    user_id: UUID = Field(description="应用内用户 UUID,不接受客户端归属声明")
    session_id: UUID = Field(description="验证器已检查有效/未撤销的会话 UUID")
    device_id: UUID = Field(description="验证器已检查归属的设备 UUID")
    scopes: frozenset[Annotated[str, Field(min_length=1, max_length=64)]] = Field(
        default_factory=frozenset,
        max_length=64,
        description="验证器授予的有界权限集合",
    )


class IdentityVerifier(Protocol):
    """应用独立验证器;实现者必须验证签名、目标应用及账户/会话/设备状态。"""

    async def verify(self, token: str) -> Principal:
        """返回可信身份;无效、过期、撤销或错误应用 token 抛 AuthenticationError。"""
        ...


class IdentityNotConfiguredError(AuthenticationError):
    """尚未装配登录提供方时显式关闭业务接口。"""

    def __init__(self) -> None:
        """固定错误内容,不泄露配置或原始凭据。"""
        super().__init__()
        self.code = "IDENTITY_NOT_CONFIGURED"
        self.message = "身份验证尚未配置"


class DenyIdentityVerifier:
    """安全默认值:任何凭据都不能换取匿名或调试身份。"""

    async def verify(self, token: str) -> Principal:
        """拒绝所有 token;没有生产跳过鉴权开关。"""
        raise IdentityNotConfiguredError()


def create_identity_dependency(
    app_id: str, verifier: IdentityVerifier, *, authorization_limit: int = 4096
) -> Callable[[Request], Awaitable[Principal]]:
    """显式绑定应用和验证器,不读取全局设置、宿主 runtime 或客户端归属。"""
    if not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", app_id) or authorization_limit < 1:
        raise ValueError("Invalid identity boundary")

    async def require_principal(request: Request) -> Principal:
        """有界 Bearer 只换取当前应用的可信 Principal。"""
        raw = request.headers.get("authorization", "")
        if len(raw) > authorization_limit:
            raise AuthenticationError()
        scheme, separator, token = raw.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token or any(c.isspace() for c in token):
            raise AuthenticationError()
        principal = await verifier.verify(token)
        if not isinstance(principal, Principal) or principal.app_id != app_id:
            raise AuthenticationError()
        return principal

    return require_principal
