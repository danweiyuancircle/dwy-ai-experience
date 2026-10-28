"""邮箱认证共享能力；验证码、配额和凭据全部使用宿主事务。"""

import asyncio
import hashlib
import hmac
import re
import secrets
import time
from dataclasses import dataclass, field
from typing import Literal, Protocol
from uuid import UUID, uuid4

import anyio
from pydantic import BaseModel
from sqlalchemy import delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError

from .models import AuthError, TokenResponse, UserProfile
from .passwords import hash_password, verify_password

EmailCodePurpose = Literal["register", "password_reset"]
EmailLanguage = Literal["zh", "en"]


def resolve_email_language(accept_language: str | None) -> EmailLanguage:
    """有效且未被 q=0 排除的中文范围选中文，其余与缺省一律英文。"""
    for language_range in (accept_language or "").split(","):
        match = re.fullmatch(
            r"zh(?:-[a-z0-9]{1,8})*(?:\s*;\s*q=(0(?:\.[0-9]{0,3})?|1(?:\.0{0,3})?))?",
            language_range.strip().lower(),
        )
        if match and (match[1] is None or float(match[1]) > 0):
            return "zh"
    return "en"


def normalize_email(email: str) -> str:
    """身份规范仅 strip/lower；不折叠 Gmail 别名，避免改变用户明确输入的账号。"""
    value = email.strip().lower()
    if len(value) > 254 or not re.fullmatch(r"[^\s@<>]+@[^\s@<>.]+(?:\.[^\s@<>.]+)+", value):
        raise AuthError("EMAIL_INVALID", "邮箱格式无效", 422)
    return value


def validate_password(password: str, *, new: bool) -> str:
    """保留密码原样；bcrypt 只接受最多72字节，禁止静默截断。"""
    if len(password) < (15 if new else 1) or len(password.encode("utf-8")) > 72:
        raise AuthError("PASSWORD_INVALID", "密码需至少15个字符，且UTF-8编码不超过72字节", 422)
    return password


class EmailCodeSender(Protocol):
    """邮件传输边界；返回False代表未交付，不应记录验证码到日志。"""

    async def send(
        self, email: str, code: str, purpose: EmailCodePurpose, *, language: EmailLanguage = "en"
    ) -> bool: ...


class EapiEmailCodeSender:
    """适配EAPI邮件通道，只使用公开传输接口，不调用Redis发码/验码接口。"""

    def __init__(self, provider):
        self.provider = provider

    async def send(
        self, email: str, code: str, purpose: EmailCodePurpose, *, language: EmailLanguage = "en"
    ) -> bool:
        """用途隔离交给认证事务；品牌模板与TTL由宿主装配一致。"""
        return await self.provider.send_verification_code(email, code, language=language)


@dataclass(frozen=True)
class EmailAuthConfig:
    """secret由宿主密钥配置注入；所有实例必须共享，轮换后旧验证码失效。"""

    challenge_secret: str = field(repr=False)
    code_ttl: int = 300
    resend_after: int = 60

    def __post_init__(self):
        if len(self.challenge_secret.encode()) < 32 or self.code_ttl < 60 or self.resend_after < 1:
            raise ValueError("Invalid email authentication configuration")


@dataclass(frozen=True)
class SessionPolicy:
    """默认保持旧30天固定期限；长期续期由宿主显式启用。"""

    refresh_ttl: int = 30 * 86400
    rolling_refresh: bool = False
    replay_retention: int = 30 * 86400

    def __post_init__(self):
        if self.refresh_ttl < 900 or self.replay_retention < 900:
            raise ValueError("Invalid session policy")


class EmailCodeChallenge(BaseModel):
    challenge_id: UUID
    expires_in: int
    resend_after: int
    code_length: Literal[6] = 6


class EmailAuthMixin:
    """AuthService内部组合；保持Google接口和数据库所有权不变。"""

    def _require_email(self):
        if self.email_sender is None or self.email_config is None:
            raise AuthError("EMAIL_NOT_CONFIGURED", "邮箱认证尚未配置", 503)

    def _code_digest(self, challenge_id, email, purpose, code):
        value = "\0".join((self.app_id, str(challenge_id), email, purpose, code))
        return hmac.new(
            self.email_config.challenge_secret.encode(), value.encode(), hashlib.sha256
        ).hexdigest()

    async def _rate(self, action, key, limit, window):
        t, now = self.tables.auth_rate_limits, int(time.time())
        digest = hashlib.sha256(f"{action}\0{key}".encode()).hexdigest()
        async with self.sessions() as db, db.begin():
            if db.bind.dialect.name == "postgresql":
                from sqlalchemy.dialects.postgresql import insert as upsert
            else:
                from sqlalchemy.dialects.sqlite import insert as upsert
            await db.execute(delete(t).where(t.c.app_id == self.app_id, t.c.expires_at <= now))
            statement = upsert(t).values(app_id=self.app_id, key=digest, count=1, expires_at=now + window)
            result = await db.execute(
                statement.on_conflict_do_update(
                    index_elements=[t.c.app_id, t.c.key],
                    set_={"count": t.c.count + 1},
                    where=t.c.count < limit,
                )
            )
            allowed = result.rowcount == 1
            deadline = (
                await db.scalar(select(t.c.expires_at).where(t.c.app_id == self.app_id, t.c.key == digest))
                if allowed
                else None
            )
        if not allowed:
            raise AuthError("EMAIL_RATE_LIMITED", "操作过于频繁，请稍后重试", 429)
        return deadline

    async def _password_work(self, function, *args):
        # 线程池任务和等待队列都有上限；取消请求不提前释放仍运行的bcrypt并发槽。
        if self._password_inflight >= 32:
            raise AuthError("EMAIL_RATE_LIMITED", "操作过于频繁，请稍后重试", 429)
        self._password_inflight += 1
        task = asyncio.create_task(anyio.to_thread.run_sync(function, *args, limiter=self._password_limiter))
        self._password_tasks.add(task)

        def completed(done):
            self._password_inflight -= 1
            self._password_tasks.discard(done)
            if not done.cancelled():
                done.exception()

        task.add_done_callback(completed)
        return await asyncio.shield(task)

    async def send_email_code(
        self,
        email: str,
        purpose: EmailCodePurpose,
        *,
        remote_key: str = "local",
        language: EmailLanguage = "en",
    ):
        """预占发送预算；成功交付才激活challenge，新码使同用途旧码失效。"""
        self._require_email()
        email = normalize_email(email)
        if purpose not in ("register", "password_reset"):
            raise AuthError("EMAIL_PURPOSE_INVALID", "验证码用途无效", 422)
        await self._rate("send-ip", remote_key, 50, 3600)
        await self._rate("send-global", "app", 1000, 3600)
        resend_at = await self._rate("send-cooldown:" + purpose, email, 1, self.email_config.resend_after)
        await self._rate("send-hour:" + purpose, email, 10, 3600)
        t, now, challenge_id = self.tables.email_challenges, int(time.time()), uuid4()
        code = f"{secrets.randbelow(1000000):06d}"
        expires_at = now + self.email_config.code_ttl
        async with self.sessions() as db, db.begin():
            await db.execute(delete(t).where(t.c.app_id == self.app_id, t.c.expires_at <= now))
            await db.execute(
                insert(t).values(
                    app_id=self.app_id,
                    id=str(challenge_id),
                    email=email,
                    purpose=purpose,
                    code_hash=self._code_digest(challenge_id, email, purpose, code),
                    expires_at=expires_at,
                    attempts=0,
                )
            )
        try:
            delivered = await self.email_sender.send(email, code, purpose, language=language)
        except Exception:
            # 第三方异常可能含请求/密钥；只在HTTP边界返回固定消息。
            delivered = False
        delivered_at = int(time.time())
        async with self.sessions() as db, db.begin():
            if delivered and delivered_at < expires_at:
                activated = await db.execute(
                    update(t)
                    .where(
                        t.c.app_id == self.app_id,
                        t.c.id == str(challenge_id),
                        t.c.consumed_at.is_(None),
                        t.c.expires_at > delivered_at,
                    )
                    .values(delivered_at=delivered_at)
                )
                delivered = activated.rowcount == 1
            else:
                delivered = False
            if delivered:
                await db.execute(
                    update(t)
                    .where(
                        t.c.app_id == self.app_id,
                        t.c.email == email,
                        t.c.purpose == purpose,
                        t.c.id != str(challenge_id),
                        t.c.consumed_at.is_(None),
                    )
                    .values(consumed_at=delivered_at)
                )
            else:
                await db.execute(delete(t).where(t.c.app_id == self.app_id, t.c.id == str(challenge_id)))
        response_at = int(time.time())
        if delivered and response_at >= expires_at:
            async with self.sessions() as db, db.begin():
                await db.execute(delete(t).where(t.c.app_id == self.app_id, t.c.id == str(challenge_id)))
            delivered = False
        if not delivered:
            raise AuthError("EMAIL_DELIVERY_FAILED", "验证码发送失败，请稍后重试", 503)
        return EmailCodeChallenge(
            challenge_id=challenge_id,
            expires_in=expires_at - response_at,
            resend_after=max(0, resend_at - response_at),
        )

    async def _code_attempt(self, email, purpose, code, challenge_id, remote_key):
        await self._rate("verify-ip", remote_key, 100, 900)
        await self._rate("verify-email:" + purpose, email, 20, 900)
        t, now = self.tables.email_challenges, int(time.time())
        # 失败计数独立提交，业务事务回滚不能恢复试错预算。
        async with self.sessions() as db, db.begin():
            row = (
                await db.execute(
                    update(t)
                    .where(
                        t.c.app_id == self.app_id,
                        t.c.id == str(challenge_id),
                        t.c.email == email,
                        t.c.purpose == purpose,
                        t.c.delivered_at.is_not(None),
                        t.c.consumed_at.is_(None),
                        t.c.expires_at > now,
                        t.c.attempts < 5,
                    )
                    .values(attempts=t.c.attempts + 1)
                    .returning(t.c.code_hash)
                )
            ).scalar_one_or_none()
        if row is None or not hmac.compare_digest(row, self._code_digest(challenge_id, email, purpose, code)):
            raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)

    async def _consume_code(self, db, email, purpose, code, challenge_id):
        t, now = self.tables.email_challenges, int(time.time())
        result = await db.execute(
            update(t)
            .where(
                t.c.app_id == self.app_id,
                t.c.id == str(challenge_id),
                t.c.email == email,
                t.c.purpose == purpose,
                t.c.code_hash == self._code_digest(challenge_id, email, purpose, code),
                t.c.consumed_at.is_(None),
                t.c.delivered_at.is_not(None),
                t.c.expires_at > now,
                t.c.attempts <= 5,
            )
            .values(consumed_at=now)
        )
        if result.rowcount != 1:
            raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)

    async def _email_session(self, db, user, device_id):
        from .service import _digest, _tokens

        now, s = int(time.time()), self.tables.sessions
        await self._prune_expired(db, user["id"], now)
        count = await db.scalar(
            select(func.count())
            .select_from(s)
            .where(s.c.app_id == self.app_id, s.c.user_id == user["id"], s.c.refresh_expires_at > now)
        )
        if count >= self.MAX_UNEXPIRED_SESSIONS:
            raise AuthError("SESSION_QUOTA_EXCEEDED", "会话配额已满，请等待现有会话到期", 429)
        access, refresh = _tokens()
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
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            user=UserProfile(id=UUID(user["id"]), email=user["email"], display_name=user["display_name"]),
        )

    async def register_email(self, email, password, code, challenge_id, device_id, *, remote_key="local"):
        """成功核销与建号/会话同事务；不关联已有Google账户。"""
        self._require_email()
        email = normalize_email(email)
        validate_password(password, new=True)
        await self._code_attempt(email, "register", code, challenge_id, remote_key)
        password_hash = await self._password_work(hash_password, password)
        u, c, now, user_id = (
            self.tables.users,
            self.tables.password_credentials,
            int(time.time()),
            str(uuid4()),
        )
        try:
            async with self.sessions() as db, db.begin():
                await self._consume_code(db, email, "register", code, challenge_id)
                await db.execute(
                    insert(u).values(
                        app_id=self.app_id, id=user_id, email=email, disabled=False, created_at=now
                    )
                )
                await db.execute(
                    insert(c).values(
                        app_id=self.app_id,
                        email=email,
                        user_id=user_id,
                        password_hash=password_hash,
                        updated_at=now,
                    )
                )
                return await self._email_session(
                    db, {"id": user_id, "email": email, "display_name": None}, device_id
                )
        except IntegrityError:
            raise AuthError("EMAIL_ALREADY_REGISTERED", "邮箱已注册，请登录或找回密码", 409) from None

    async def login_email(self, email, password, device_id, *, remote_key="local"):
        """密码比较在线程执行，提交前锁账户并重查散列，阻止重置密码前旧请求登录。"""
        self._require_email()
        email = normalize_email(email)
        validate_password(password, new=False)
        await self._rate("login-ip", remote_key, 100, 900)
        await self._rate("login-email", email, 10, 900)
        c, u = self.tables.password_credentials, self.tables.users
        async with self.sessions() as db:
            credential = (
                (await db.execute(select(c).where(c.c.app_id == self.app_id, c.c.email == email)))
                .mappings()
                .one_or_none()
            )
        # 不存在用户也执行等成本bcrypt，避免廉价的时序账号枚举。
        hashed = credential["password_hash"] if credential else self._dummy_password_hash
        valid = await self._password_work(verify_password, password, hashed)
        if credential is None or not valid:
            raise AuthError("CREDENTIALS_INVALID", "邮箱或密码错误", 401)
        async with self.sessions() as db, db.begin():
            await self.require_active_account(db, credential["user_id"])
            user = (
                (
                    await db.execute(
                        select(u).where(u.c.app_id == self.app_id, u.c.id == credential["user_id"])
                    )
                )
                .mappings()
                .one()
            )
            current = await db.scalar(
                select(c.c.password_hash).where(c.c.app_id == self.app_id, c.c.email == email)
            )
            if current != hashed:
                raise AuthError("CREDENTIALS_INVALID", "邮箱或密码错误", 401)
            return await self._email_session(db, user, device_id)

    async def reset_password(self, email, password, code, challenge_id, *, remote_key="local"):
        """核销、密码更新和撤销旧family同事务；不自动建立新会话。"""
        self._require_email()
        email = normalize_email(email)
        validate_password(password, new=True)
        await self._code_attempt(email, "password_reset", code, challenge_id, remote_key)
        hashed = await self._password_work(hash_password, password)
        c, s, now = self.tables.password_credentials, self.tables.sessions, int(time.time())
        async with self.sessions() as db, db.begin():
            owner = await db.scalar(select(c.c.user_id).where(c.c.app_id == self.app_id, c.c.email == email))
            if owner is None:
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self.require_active_account(db, owner)
            await self._consume_code(db, email, "password_reset", code, challenge_id)
            await db.execute(
                update(c)
                .where(c.c.app_id == self.app_id, c.c.email == email)
                .values(password_hash=hashed, updated_at=now)
            )
            await db.execute(
                update(s).where(s.c.app_id == self.app_id, s.c.user_id == owner).values(revoked_at=now)
            )
        return {"status": "completed"}
