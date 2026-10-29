"""认证方式和 transport 共用的最小身份合同，不携带业务用户资料。"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Literal, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass(frozen=True)
class VerifiedIdentity:
    """认证结果，subject 为不透明主体；proof 字段仅供 runtime 在五分钟内核销。

    自定义 SessionBackend 可继续使用前三字段；HTTP 不接收客户端自报的证明对象。
    密码/绑定变更后旧证明失效，业务资料不进入本合同。
    """

    app_id: str
    subject: str
    method: str
    authenticated_at: int = 0
    credential_version: str | None = field(default=None, repr=False)
    proof_id: UUID | None = field(default=None, repr=False)
    purpose: str = "login"


@dataclass(frozen=True)
class AuthPrincipal:
    """已验证的会话身份；设备不是账号标识，Web transport 可以不提供设备。"""

    app_id: str
    subject: str
    session_id: UUID
    method: str
    device_id: UUID | None


@dataclass(frozen=True)
class SessionTokens:
    """transport 自行选择 JSON 或 Cookie；repr 永远不包含凭据。"""

    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_in: int
    principal: AuthPrincipal


class SessionBackend(Protocol):
    """可替换会话实现；传入 db 的操作必须加入宿主事务，不得自行提交或关闭。"""

    async def issue(
        self, identity: VerifiedIdentity, *, device_id: UUID | None, db: AsyncSession
    ) -> SessionTokens: ...

    async def verify(self, token: str) -> AuthPrincipal: ...

    async def refresh(
        self,
        refresh_token: str,
        *,
        before_lock: Callable[[AsyncSession, AuthPrincipal], Awaitable[None]] | None = None,
        before_rotate: Callable[[AsyncSession, AuthPrincipal], Awaitable[None]] | None = None,
    ) -> SessionTokens: ...

    async def revoke(self, principal: AuthPrincipal) -> None: ...

    async def revoke_subject(self, subject: str, *, db: AsyncSession) -> None: ...


@dataclass(frozen=True)
class LoginIdentity:
    """仅返回当前账号可用入口的解绑定位字段；永不携带密码、版本或第三方 token。"""

    kind: Literal["email", "username", "external"]
    value: str
    provider: str | None = None
    issuer: str | None = None


class AuthAdmission(Protocol):
    """应用准入扩展；外部验证在事务外，归属检查与业务写入必须加入认证事务。"""

    async def prepare(self, proof: str | None) -> object:
        """验证本次请求证明并返回受信事实；缺失或无效时由应用明确拒绝。"""
        ...

    async def admit(self, db: AsyncSession, subject: str, prepared: object) -> None:
        """核对主体并持久化归属；不得自行提交、关闭事务或执行外网请求。"""
        ...
