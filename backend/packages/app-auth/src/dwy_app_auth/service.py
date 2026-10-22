"""数据库会话验证与轮换，原始 access/refresh token 从不持久化。"""

import asyncio
import hashlib
import re
import secrets
import time
from collections.abc import Awaitable, Callable
from uuid import UUID, uuid4

import anyio
from dwyeapi.exceptions import AuthenticationError
from dwyeapi.identity import Principal
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from .email_auth import EmailAuthConfig, EmailAuthMixin, EmailCodeSender, SessionPolicy
from .models import (
    AccountDeletion,
    AuthError,
    DevicePage,
    DeviceQuery,
    DeviceSummary,
    GoogleVerifier,
    TokenResponse,
    UserProfile,
)
from .storage import AuthTables


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _tokens() -> tuple[str, str]:
    return "ac_" + secrets.token_urlsafe(32), "rf_" + secrets.token_urlsafe(48)


class AuthService(EmailAuthMixin):
    # 撤销会话也占用账户预算到 30 天绝对到期，避免反复登录/退出绕过配额。
    MAX_UNEXPIRED_SESSIONS = 100
    # 15 分钟刷新一次的 30 天常规用量为 2880；保留充足重试余量。
    MAX_REFRESH_HISTORY = 4096

    def __init__(
        self,
        app_id: str,
        sessions,
        tables: AuthTables,
        google_verifier: GoogleVerifier,
        *,
        email_sender: EmailCodeSender | None = None,
        email_config: EmailAuthConfig | None = None,
        session_policy: SessionPolicy | None = None,
    ):
        """宿主显式注入邮件传输、密钥和会话策略；默认保留旧Google行为。"""
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", app_id):
            raise ValueError("Invalid app id")
        self.app_id, self.sessions, self.tables, self.google_verifier = (
            app_id,
            sessions,
            tables,
            google_verifier,
        )
        self.email_sender, self.email_config = email_sender, email_config
        self.session_policy = session_policy if session_policy is not None else SessionPolicy()
        self._password_limiter = anyio.CapacityLimiter(4)
        self._password_inflight = 0
        self._password_tasks: set[asyncio.Task] = set()
        self._dummy_password_hash = "$2b$12$s6AXc3y1CJPYmZEr.1nVUOwFXwslhbh3Cv.oA9kHOFJWx3/v2Np22"
        # 清理由应用工厂显式装配；回调只能使用传入事务，不能自行提交。
        self._account_cleanup: dict[str, Callable[[AsyncSession, Principal], Awaitable[None]]] = {}

    async def login(self, id_token: str, device_id: UUID) -> TokenResponse:
        identity = await self.google_verifier.verify(id_token)
        now, user_id = int(time.time()), str(uuid4())
        access, refresh = _tokens()
        u, s = self.tables.users, self.tables.sessions
        profile = None
        async with self.sessions() as db, db.begin():
            dialect = db.bind.dialect.name
            if dialect == "postgresql":
                from sqlalchemy.dialects.postgresql import insert as upsert
            elif dialect == "sqlite":
                from sqlalchemy.dialects.sqlite import insert as upsert
            else:
                raise RuntimeError("Unsupported auth database dialect")
            await db.execute(
                upsert(u)
                .values(
                    app_id=self.app_id,
                    id=user_id,
                    google_subject=identity.subject,
                    email=identity.email,
                    display_name=identity.display_name,
                    disabled=False,
                    created_at=now,
                )
                .on_conflict_do_nothing(index_elements=[u.c.app_id, u.c.google_subject])
            )
            user = (
                (
                    await db.execute(
                        select(u)
                        .where(
                            u.c.app_id == self.app_id,
                            u.c.google_subject == identity.subject,
                        )
                        .with_for_update()
                    )
                )
                .mappings()
                .one()
            )
            if user["disabled"]:
                raise AuthError("ACCOUNT_DISABLED", "账户不可用", 403)
            await self._prune_expired(db, user["id"], now)
            count = await db.scalar(
                select(func.count())
                .select_from(s)
                .where(s.c.app_id == self.app_id, s.c.user_id == user["id"], s.c.refresh_expires_at > now)
            )
            if count < self.MAX_UNEXPIRED_SESSIONS:
                await db.execute(
                    update(u)
                    .where(u.c.app_id == self.app_id, u.c.id == user["id"])
                    .values(
                        email=identity.email,
                        display_name=identity.display_name,
                    )
                )
                await db.execute(
                    insert(s).values(
                        app_id=self.app_id,
                        id=str(uuid4()),
                        user_id=user["id"],
                        device_id=str(device_id),
                        access_hash=_digest(access),
                        refresh_hash=_digest(refresh),
                        access_expires_at=now + 900,
                        refresh_expires_at=now + self.session_policy.refresh_ttl,
                        created_at=now,
                    )
                )
                profile = UserProfile(
                    id=UUID(user["id"]), email=identity.email, display_name=identity.display_name
                )
        if profile is None:
            # 事务先提交到期清理；429 不应回滚已经安全删除的历史数据。
            raise AuthError("SESSION_QUOTA_EXCEEDED", "会话配额已满，请等待现有会话到期", 429)
        return TokenResponse(access_token=access, refresh_token=refresh, user=profile)

    async def _prune_expired(self, db: AsyncSession, user_id: str, now: int) -> None:
        """调用者已锁账户；先删到期摘要，再删无剩余重放证据的到期会话。"""
        s, h = self.tables.sessions, self.tables.refresh_history
        account_sessions = select(s.c.id).where(s.c.app_id == self.app_id, s.c.user_id == user_id)
        await db.execute(
            delete(h).where(
                h.c.app_id == self.app_id,
                h.c.session_id.in_(account_sessions),
                h.c.expires_at <= now,
            )
        )
        remaining_evidence = (
            select(h.c.refresh_hash).where(h.c.app_id == self.app_id, h.c.session_id == s.c.id).exists()
        )
        await db.execute(
            delete(s).where(
                s.c.app_id == self.app_id,
                s.c.user_id == user_id,
                s.c.refresh_expires_at <= now,
                ~remaining_evidence,
            )
        )

    def _joined(self):
        u, s = self.tables.users, self.tables.sessions
        return s.join(u, and_(u.c.app_id == s.c.app_id, u.c.id == s.c.user_id))

    async def verify(self, token: str) -> Principal:
        if not isinstance(token, str) or not re.fullmatch(r"ac_[A-Za-z0-9_-]{43}", token):
            raise AuthenticationError()
        s, u, now = self.tables.sessions, self.tables.users, int(time.time())
        async with self.sessions() as db:
            row = (
                (
                    await db.execute(
                        select(s)
                        .select_from(self._joined())
                        .where(
                            s.c.app_id == self.app_id,
                            s.c.access_hash == _digest(token),
                            s.c.revoked_at.is_(None),
                            s.c.access_expires_at > now,
                            s.c.refresh_expires_at > now,
                            u.c.disabled.is_(False),
                        )
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise AuthenticationError()
        return Principal(
            app_id=self.app_id,
            user_id=UUID(row["user_id"]),
            session_id=UUID(row["id"]),
            device_id=UUID(row["device_id"]),
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        """轮换只保留摘要；发现已消费摘要时提交 family 撤销后再报告错误。"""
        if not isinstance(refresh_token, str) or not re.fullmatch(r"rf_[A-Za-z0-9_-]{64}", refresh_token):
            raise AuthError("REFRESH_TOKEN_INVALID", "刷新凭据无效")
        s, u, h, now = self.tables.sessions, self.tables.users, self.tables.refresh_history, int(time.time())
        old_hash = _digest(refresh_token)
        access, refresh = _tokens()
        profile = None
        quota_exceeded = False
        async with self.sessions() as db, db.begin():
            # 所有写事务统一先锁账户再锁 family，避免与业务清理形成反向锁序。
            owner = (
                await db.execute(
                    select(s.c.user_id).where(
                        s.c.app_id == self.app_id,
                        s.c.refresh_hash == old_hash,
                    )
                )
            ).scalar_one_or_none()
            if owner is None:
                owner = (
                    await db.execute(
                        select(s.c.user_id)
                        .select_from(s.join(h, and_(s.c.app_id == h.c.app_id, s.c.id == h.c.session_id)))
                        .where(h.c.app_id == self.app_id, h.c.refresh_hash == old_hash)
                    )
                ).scalar_one_or_none()
            if owner is not None:
                await self.require_active_account(db, owner)
                await self._prune_expired(db, owner, now)
            row = (
                (
                    await db.execute(
                        select(s, u.c.email, u.c.display_name)
                        .select_from(self._joined())
                        .where(
                            s.c.app_id == self.app_id,
                            s.c.refresh_hash == old_hash,
                            s.c.revoked_at.is_(None),
                            s.c.refresh_expires_at > now,
                            u.c.disabled.is_(False),
                        )
                        .with_for_update()
                    )
                )
                .mappings()
                .one_or_none()
            )
            if row is None:
                previous_session = (
                    await db.execute(
                        select(h.c.session_id).where(
                            h.c.app_id == self.app_id, h.c.refresh_hash == old_hash, h.c.expires_at > now
                        )
                    )
                ).scalar_one_or_none()
                if previous_session is not None:
                    await db.execute(
                        update(s)
                        .where(
                            s.c.app_id == self.app_id, s.c.id == previous_session, s.c.revoked_at.is_(None)
                        )
                        .values(revoked_at=now)
                    )
            elif (
                await db.scalar(
                    select(func.count())
                    .select_from(h)
                    .where(h.c.app_id == self.app_id, h.c.session_id == row["id"])
                )
            ) >= self.MAX_REFRESH_HISTORY:
                quota_exceeded = True
            else:
                # 条件更新在 SQLite 上也保证同一 refresh token 只有一个请求胜出。
                result = await db.execute(
                    update(s)
                    .where(
                        s.c.app_id == self.app_id,
                        s.c.id == row["id"],
                        s.c.refresh_hash == old_hash,
                        s.c.revoked_at.is_(None),
                    )
                    .values(
                        access_hash=_digest(access),
                        refresh_hash=_digest(refresh),
                        access_expires_at=now + 900,
                        refresh_expires_at=(
                            now + self.session_policy.refresh_ttl
                            if self.session_policy.rolling_refresh
                            else row["refresh_expires_at"]
                        ),
                    )
                )
                if result.rowcount != 1:
                    await db.execute(
                        update(s)
                        .where(s.c.app_id == self.app_id, s.c.id == row["id"], s.c.revoked_at.is_(None))
                        .values(revoked_at=now)
                    )
                else:
                    await db.execute(
                        insert(h).values(
                            app_id=self.app_id,
                            refresh_hash=old_hash,
                            session_id=row["id"],
                            expires_at=(
                                min(row["refresh_expires_at"], now + self.session_policy.replay_retention)
                                if self.session_policy.rolling_refresh
                                else row["refresh_expires_at"]
                            ),
                        )
                    )
                    profile = UserProfile(
                        id=UUID(row["user_id"]), email=row["email"], display_name=row["display_name"]
                    )
        if quota_exceeded:
            raise AuthError("REFRESH_QUOTA_EXCEEDED", "刷新次数已达上限，请重新登录", 429)
        if profile is None:
            raise AuthError("REFRESH_TOKEN_INVALID", "刷新凭据无效")
        return TokenResponse(access_token=access, refresh_token=refresh, user=profile)

    async def require_active_account(self, db: AsyncSession, user_id: str) -> None:
        """业务写事务先锁账户再锁业务数据，防止删号后旧请求继续提交。"""
        u = self.tables.users
        row = (
            await db.execute(
                select(u.c.id)
                .where(
                    u.c.app_id == self.app_id,
                    u.c.id == user_id,
                    u.c.disabled.is_(False),
                    u.c.deleted_at.is_(None),
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if row is None:
            raise AuthError("ACCOUNT_UNAVAILABLE", "账户不可用", 401)

    async def _require_active(self, db: AsyncSession, principal: Principal) -> None:
        """服务层再次核对应用、用户、设备和会话归属，拒绝过期或伪造组合。"""
        if principal.app_id != self.app_id:
            raise AuthenticationError()
        await self.require_active_account(db, str(principal.user_id))
        s, u, now = self.tables.sessions, self.tables.users, int(time.time())
        row = (
            await db.execute(
                select(s.c.id)
                .select_from(self._joined())
                .where(
                    s.c.app_id == self.app_id,
                    s.c.id == str(principal.session_id),
                    s.c.user_id == str(principal.user_id),
                    s.c.device_id == str(principal.device_id),
                    s.c.revoked_at.is_(None),
                    s.c.access_expires_at > now,
                    s.c.refresh_expires_at > now,
                    u.c.disabled.is_(False),
                )
                .with_for_update()
            )
        ).scalar_one_or_none()
        if row is None:
            raise AuthenticationError()

    async def list_devices(
        self, principal: Principal, *, limit: int = 50, cursor: UUID | None = None
    ) -> DevicePage:
        """按设备聚合本人活跃会话；有界 UUID 游标避免无限结果。"""
        query = DeviceQuery(limit=limit, cursor=cursor)
        s, now = self.tables.sessions, int(time.time())
        async with self.sessions() as db, db.begin():
            await self._require_active(db, principal)
            statement = select(
                s.c.device_id,
                func.min(s.c.created_at).label("first_seen_at"),
                func.max(s.c.created_at).label("last_login_at"),
                func.count().label("active_sessions"),
            ).where(
                s.c.app_id == self.app_id,
                s.c.user_id == str(principal.user_id),
                s.c.revoked_at.is_(None),
                s.c.refresh_expires_at > now,
            )
            if query.cursor is not None:
                statement = statement.where(s.c.device_id > str(query.cursor))
            rows = (
                (
                    await db.execute(
                        statement.group_by(s.c.device_id).order_by(s.c.device_id).limit(query.limit + 1)
                    )
                )
                .mappings()
                .all()
            )
        page = [
            DeviceSummary(**dict(row), current=UUID(row["device_id"]) == principal.device_id)
            for row in rows[: query.limit]
        ]
        return DevicePage(devices=page, next_cursor=page[-1].device_id if len(rows) > query.limit else None)

    async def revoke_device(self, principal: Principal, device_id: UUID) -> None:
        """只撤销本人指定设备的全部 family，当前设备也立即失效。"""
        s, now = self.tables.sessions, int(time.time())
        async with self.sessions() as db, db.begin():
            await self._require_active(db, principal)
            result = await db.execute(
                update(s)
                .where(
                    s.c.app_id == self.app_id,
                    s.c.user_id == str(principal.user_id),
                    s.c.device_id == str(device_id),
                    s.c.revoked_at.is_(None),
                    s.c.refresh_expires_at > now,
                )
                .values(revoked_at=now)
            )
            if result.rowcount == 0:
                raise AuthError("DEVICE_NOT_FOUND", "设备不存在", 404)

    def register_account_cleanup(
        self,
        name: str,
        handler: Callable[[AsyncSession, Principal], Awaitable[None]],
    ) -> None:
        """应用启动时注册业务清理；失败回滚整个删除事务，不产生无人消费任务。"""
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,63}", name) or name in self._account_cleanup:
            raise ValueError("Invalid or duplicate account cleanup name")
        self._account_cleanup[name] = handler

    async def delete_account(self, principal: Principal) -> AccountDeletion:
        """去标识并撤销所有凭据，保留旧用户主键使 IAP 账本无法被新账户认领。"""
        u, s, now = self.tables.users, self.tables.sessions, int(time.time())
        async with self.sessions() as db, db.begin():
            await self._require_active(db, principal)
            c, challenges = self.tables.password_credentials, self.tables.email_challenges
            # Google-only 宿主尚未迁移邮箱表；删号仍需完整执行撤销与业务清理。
            if c is not None:
                email = await db.scalar(
                    select(c.c.email).where(c.c.app_id == self.app_id, c.c.user_id == str(principal.user_id))
                )
                if email is not None:
                    await db.execute(
                        delete(challenges).where(
                            challenges.c.app_id == self.app_id, challenges.c.email == email
                        )
                    )
                await db.execute(
                    delete(c).where(c.c.app_id == self.app_id, c.c.user_id == str(principal.user_id))
                )
            await db.execute(
                update(u)
                .where(u.c.app_id == self.app_id, u.c.id == str(principal.user_id))
                .values(
                    disabled=True,
                    google_subject="deleted:" + uuid4().hex,
                    email=None,
                    display_name=None,
                    deleted_at=now,
                )
            )
            await db.execute(
                update(s)
                .where(
                    s.c.app_id == self.app_id, s.c.user_id == str(principal.user_id), s.c.revoked_at.is_(None)
                )
                .values(revoked_at=now)
            )
            for handler in self._account_cleanup.values():
                await handler(db, principal)
        return AccountDeletion()

    async def logout(self, principal: Principal) -> None:
        if principal.app_id != self.app_id:
            raise AuthenticationError()
        s = self.tables.sessions
        async with self.sessions() as db, db.begin():
            await db.execute(
                update(s)
                .where(
                    s.c.app_id == self.app_id,
                    s.c.id == str(principal.session_id),
                    s.c.user_id == str(principal.user_id),
                    s.c.device_id == str(principal.device_id),
                )
                .values(revoked_at=int(time.time()))
            )

    async def aclose(self) -> None:
        if self._password_tasks:
            await asyncio.gather(*self._password_tasks, return_exceptions=True)
        closer = getattr(self.google_verifier, "aclose", None)
        if closer is not None:
            await closer()
