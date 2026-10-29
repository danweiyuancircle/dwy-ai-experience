"""默认 JWT access 与数据库 refresh family 后端，不把 JWT 自包含当作撤销机制。"""

import hashlib
import re
import secrets
import time
from collections.abc import Callable
from uuid import UUID, uuid4

from jose import JWTError, jwt
from sqlalchemy import func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import AuthPrincipal, SessionTokens, VerifiedIdentity
from .models import AuthError
from .session_storage import SessionTables


def _digest(token: str) -> str:
    """只持久化高熵refresh凭据的摘要，数据库不保留可直接使用的原文。"""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _invalid() -> AuthError:
    """统一认证失败结果，不把原始凭据或底层验签异常带入响应。"""
    return AuthError("SESSION_INVALID", "会话凭据无效", 401)


class JWTSessionBackend:
    """HS256 access 与不透明 refresh；密钥至少 32 字节，宿主负责安全保管和轮换。"""

    # 30 天每 15 分钟刷新约 2880 次；保留重试余量，同时限制一个 family 的存储增长。
    MAX_REFRESH_HISTORY = 4096

    def __init__(
        self,
        app_id: str,
        issuer: str,
        audience: str,
        secret: str,
        session_factory: Callable[[], AsyncSession],
        tables: SessionTables,
        *,
        access_ttl: int = 900,
        refresh_ttl: int = 30 * 86400,
    ):
        """校验并保存显式配置；session工厂供自持事务使用，不触发建表。"""
        if not isinstance(app_id, str) or not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", app_id):
            raise ValueError("Invalid app id")
        if not isinstance(secret, str) or len(secret.encode("utf-8")) < 32:
            raise ValueError("Session signing secret must contain at least 32 bytes")
        if any(not isinstance(value, str) or not 1 <= len(value) <= 512 for value in (issuer, audience)):
            raise ValueError("Session issuer and audience must be bounded nonempty strings")
        if type(access_ttl) is not int or not 1 <= access_ttl <= 3600:
            raise ValueError("Access TTL must be between 1 and 3600 seconds")
        if type(refresh_ttl) is not int or not access_ttl <= refresh_ttl <= 366 * 86400:
            raise ValueError("Refresh TTL must cover access TTL and be at most 366 days")
        self.app_id, self.issuer, self.audience = app_id, issuer, audience
        self._secret = secret
        self.session_factory, self.tables = session_factory, tables
        self.access_ttl, self.refresh_ttl = access_ttl, refresh_ttl

    def _tokens(
        self, principal: AuthPrincipal, now: int, jti: str, refresh: str, family_expires_at: int
    ) -> SessionTokens:
        """签发限用途JWT，期限受family绝对到期约束；不写数据库或记录凭据。"""
        # 接近 family 绝对到期时，返回值与 JWT 期限都不能超过数据库实际允许的期限。
        expires_in = min(self.access_ttl, family_expires_at - now)
        access = jwt.encode(
            {
                "iss": self.issuer,
                "aud": self.audience,
                "app_id": self.app_id,
                "sub": principal.subject,
                "sid": str(principal.session_id),
                "method": principal.method,
                "device_id": str(principal.device_id) if principal.device_id is not None else None,
                "type": "access",
                "iat": now,
                "exp": now + expires_in,
                "jti": jti,
            },
            self._secret,
            algorithm="HS256",
        )
        return SessionTokens(access, refresh, expires_in, principal)

    async def issue(
        self, identity: VerifiedIdentity, *, device_id: UUID | None, db: AsyncSession
    ) -> SessionTokens:
        """在调用方事务中签发，主体创建、凭据消费和会话必须共同提交或回滚。"""
        if identity.app_id != self.app_id:
            raise _invalid()
        if not isinstance(identity.subject, str) or not re.fullmatch(
            r"[^\x00-\x1f\x7f]{1,255}", identity.subject
        ):
            raise ValueError("Invalid session subject")
        if not isinstance(identity.method, str) or not re.fullmatch(
            r"[a-z][a-z0-9_-]{0,63}", identity.method
        ):
            raise ValueError("Invalid authentication method")
        now, jti = int(time.time()), str(uuid4())
        refresh = "rf_" + secrets.token_urlsafe(48)
        principal = AuthPrincipal(self.app_id, identity.subject, uuid4(), identity.method, device_id)
        await db.execute(
            insert(self.tables.sessions).values(
                app_id=self.app_id,
                id=str(principal.session_id),
                subject=identity.subject,
                method=identity.method,
                device_id=str(device_id) if device_id is not None else None,
                access_jti=jti,
                refresh_hash=_digest(refresh),
                created_at=now,
                expires_at=now + self.refresh_ttl,
            )
        )
        return self._tokens(principal, now, jti, refresh, now + self.refresh_ttl)

    async def verify(self, token: str) -> AuthPrincipal:
        """签名、用途和应用域校验后查询当前 family；退出和密码重置立即生效。"""
        if not isinstance(token, str) or not 1 <= len(token) <= 8192:
            raise _invalid()
        try:
            claims = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
                audience=self.audience,
                issuer=self.issuer,
                options={
                    "require_exp": True,
                    "require_iat": True,
                    "require_sub": True,
                    "require_aud": True,
                    "require_iss": True,
                    "require_jti": True,
                },
            )
            if (
                claims.get("app_id") != self.app_id
                or claims.get("type") != "access"
                or type(claims["iat"]) is not int
                or type(claims["exp"]) is not int
                or claims["iat"] > int(time.time())
                or not 0 < claims["exp"] - claims["iat"] <= self.access_ttl
                or not isinstance(claims["sub"], str)
                or not 1 <= len(claims["sub"]) <= 255
                or not isinstance(claims.get("method"), str)
            ):
                raise _invalid()
            principal = AuthPrincipal(
                self.app_id,
                claims["sub"],
                UUID(claims["sid"]),
                claims["method"],
                UUID(claims["device_id"]) if claims.get("device_id") is not None else None,
            )
        except (JWTError, ValueError, TypeError, KeyError, AttributeError):
            raise _invalid() from None
        s = self.tables.sessions
        async with self.session_factory() as db:
            row = (
                await db.execute(
                    select(s.c.id).where(
                        s.c.app_id == self.app_id,
                        s.c.id == str(principal.session_id),
                        s.c.subject == principal.subject,
                        s.c.method == principal.method,
                        s.c.device_id
                        == (str(principal.device_id) if principal.device_id is not None else None),
                        s.c.access_jti == claims["jti"],
                        s.c.revoked_at.is_(None),
                        s.c.expires_at > int(time.time()),
                    )
                )
            ).first()
        if row is None:
            raise _invalid()
        return principal

    async def refresh(self, refresh_token: str, *, before_lock=None, before_rotate=None) -> SessionTokens:
        """CAS 原子消费 refresh；旧摘要重用先提交 family 撤销，再返回认证失败。"""
        if not isinstance(refresh_token, str) or not re.fullmatch(r"rf_[A-Za-z0-9_-]{64}", refresh_token):
            raise _invalid()
        s, h = self.tables.sessions, self.tables.refresh_history
        old_hash, now = _digest(refresh_token), int(time.time())
        result = None
        quota_exceeded = False
        async with self.session_factory() as db, db.begin():
            row = (
                (
                    await db.execute(
                        select(s).where(
                            s.c.app_id == self.app_id,
                            s.c.refresh_hash == old_hash,
                            s.c.revoked_at.is_(None),
                            s.c.expires_at > now,
                        )
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is not None:
                principal = AuthPrincipal(
                    self.app_id,
                    row["subject"],
                    UUID(row["id"]),
                    row["method"],
                    UUID(row["device_id"]) if row["device_id"] is not None else None,
                )
                if before_lock is not None:
                    # 纯主体检查先锁 account, 与改密/删账号保持 account→session 顺序。
                    await before_lock(db, principal)
                refresh, jti = "rf_" + secrets.token_urlsafe(48), str(uuid4())
                consumed = await db.execute(
                    update(s)
                    .where(
                        s.c.app_id == self.app_id,
                        s.c.id == row["id"],
                        s.c.refresh_hash == old_hash,
                        s.c.revoked_at.is_(None),
                        s.c.expires_at > now,
                    )
                    .values(refresh_hash=_digest(refresh), access_jti=jti)
                )
                if consumed.rowcount == 1:
                    # CAS 已获得 family 写锁，计数与插入不会被同一 family 的并发刷新穿透。
                    count = await db.scalar(
                        select(func.count())
                        .select_from(h)
                        .where(h.c.app_id == self.app_id, h.c.session_id == row["id"])
                    )
                    if count >= self.MAX_REFRESH_HISTORY:
                        quota_exceeded = True
                        await db.execute(
                            update(s)
                            .where(s.c.app_id == self.app_id, s.c.id == row["id"])
                            .values(revoked_at=now)
                        )
                    else:
                        if before_rotate is not None:
                            # CAS 与配额允许后才认领；拒绝异常回滚尚未提交的轮换。
                            await before_rotate(db, principal)
                        await db.execute(
                            insert(h).values(
                                app_id=self.app_id,
                                refresh_hash=old_hash,
                                session_id=row["id"],
                                expires_at=row["expires_at"],
                            )
                        )
                        result = self._tokens(principal, now, jti, refresh, row["expires_at"])
            if result is None:
                replayed = select(h.c.session_id).where(
                    h.c.app_id == self.app_id, h.c.refresh_hash == old_hash, h.c.expires_at > now
                )
                await db.execute(
                    update(s)
                    .where(s.c.app_id == self.app_id, s.c.id.in_(replayed), s.c.revoked_at.is_(None))
                    .values(revoked_at=now)
                )
        if quota_exceeded:
            raise AuthError("REFRESH_QUOTA_EXCEEDED", "刷新次数已达上限，请重新登录", 429)
        if result is None:
            raise _invalid()
        return result

    async def revoke(self, principal: AuthPrincipal) -> None:
        """只撤销身份完整匹配的会话，不允许拼接 subject 和他人 session_id。"""
        if principal.app_id != self.app_id:
            raise _invalid()
        s = self.tables.sessions
        async with self.session_factory() as db, db.begin():
            await db.execute(
                update(s)
                .where(
                    s.c.app_id == self.app_id,
                    s.c.id == str(principal.session_id),
                    s.c.subject == principal.subject,
                    s.c.method == principal.method,
                    s.c.device_id == (str(principal.device_id) if principal.device_id is not None else None),
                    s.c.revoked_at.is_(None),
                )
                .values(revoked_at=int(time.time()))
            )

    async def revoke_subject(self, subject: str, *, db: AsyncSession) -> None:
        """密码重置/注销事务内撤销本应用主体的全部会话，不自行提交。"""
        s = self.tables.sessions
        await db.execute(
            update(s)
            .where(s.c.app_id == self.app_id, s.c.subject == subject, s.c.revoked_at.is_(None))
            .values(revoked_at=int(time.time()))
        )
