"""可实例化认证核心：应用主体、第三方验证、会话均通过注入合同提供。"""

import asyncio
import hashlib
import re
import time
from collections.abc import Awaitable, Callable, Mapping
from typing import Literal
from uuid import UUID, uuid4

import anyio
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import AuthPrincipal, SessionBackend, SessionTokens, VerifiedIdentity
from .email_auth import (
    EmailAuthConfig,
    EmailAuthMixin,
    EmailCodeChallenge,
    EmailCodePurpose,
    EmailCodeSender,
    normalize_email,
    validate_password,
)
from .models import AuthError
from .passwords import hash_password, verify_password
from .providers import ExternalIdentityProvider
from .runtime_storage import RuntimeTables
from .subjects import SubjectAdapter, SubjectRegistration


def normalize_username(username: str) -> str:
    """登录名采用固定 ASCII 规则，与可修改的展示昵称分离。"""
    if not isinstance(username, str) or len(username) > 64:
        raise AuthError("USERNAME_INVALID", "用户名格式无效", 422)
    value = username.strip().lower()
    if not re.fullmatch(r"[a-z0-9][a-z0-9_.-]{2,63}", value):
        raise AuthError("USERNAME_INVALID", "用户名需为3至64位字母、数字、点、横线或下划线", 422)
    return value


class AuthRuntime(EmailAuthMixin):
    """只认证稳定 subject；复用 legacy 的 challenge/限流算法，不使用业务 User 表。"""

    def __init__(
        self,
        app_id: str,
        session_factory: Callable[[], AsyncSession],
        tables: RuntimeTables,
        subjects: SubjectAdapter,
        *,
        session_backend: SessionBackend,
        email_sender: EmailCodeSender | None = None,
        email_config: EmailAuthConfig | None = None,
        providers: Mapping[str, ExternalIdentityProvider] | None = None,
        methods: frozenset[str] = frozenset({"email", "username", "external"}),
    ):
        """注入应用独有配置与适配器；表迁移和业务主体生命周期仍由宿主负责。"""
        if not re.fullmatch(r"[a-z][a-z0-9-]{0,31}", app_id):
            raise ValueError("Invalid app id")
        if not methods <= {"email", "username", "external"}:
            raise ValueError("Unknown authentication method")
        self.app_id, self.sessions, self.tables, self.subjects = app_id, session_factory, tables, subjects
        self.session_backend, self.email_sender, self.email_config = (
            session_backend,
            email_sender,
            email_config,
        )
        self.providers, self.methods = dict(providers or {}), frozenset(methods)
        if any(
            name in {"email", "username", "external"} or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name)
            for name in self.providers
        ):
            raise ValueError("Invalid provider configuration name")
        self._password_limiter = anyio.CapacityLimiter(4)
        self._password_inflight, self._password_tasks = 0, set()
        self._dummy_password_hash = "$2b$12$s6AXc3y1CJPYmZEr.1nVUOwFXwslhbh3Cv.oA9kHOFJWx3/v2Np22"

    def _require_method(self, method):
        """在服务端强制启用策略；第三方方式必须对应本实例的配置名称。"""
        group = method if method in {"email", "username"} else "external"
        if group not in self.methods or (group == "external" and method not in self.providers):
            raise AuthError("AUTH_METHOD_DISABLED", "认证方式未启用", 403)

    def _require_email(self):
        """同时要求邮箱方式启用和邮件发送配置可用，缺配置不得报告成功。"""
        self._require_method("email")
        super()._require_email()

    def _remote(self, remote_key):
        """约束宿主传入的来源预算键，避免无界输入进入限流摘要计算。"""
        if not isinstance(remote_key, str) or not 1 <= len(remote_key) <= 255:
            raise AuthError("INPUT_INVALID", "请求来源无效", 422)
        return remote_key

    def _email(self, email):
        """先限制原始输入，再沿用固定邮箱规范，避免改变存量账号身份。"""
        if not isinstance(email, str) or len(email) > 320:
            raise AuthError("EMAIL_INVALID", "邮箱格式无效", 422)
        return normalize_email(email)

    def _password(self, password, *, new):
        """限制输入并复用密码策略；新密码与兼容登录采用不同长度下限。"""
        if not isinstance(password, str) or len(password) > 72:
            raise AuthError("PASSWORD_INVALID", "密码格式无效", 422)
        return validate_password(password, new=new)

    def _code(self, code, challenge_id):
        """校验验证码与challenge标识，统一拒绝畸形或过大输入。"""
        if not isinstance(code, str) or not re.fullmatch(r"[0-9]{6}", code):
            raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
        if not isinstance(challenge_id, UUID) and (
            not isinstance(challenge_id, str) or len(challenge_id) != 36
        ):
            raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
        try:
            return UUID(str(challenge_id))
        except (ValueError, TypeError, AttributeError):
            raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400) from None

    async def require_active_subject(self, db, subject):
        """应用适配器负责禁用和删除检查；写事务中须遵循宿主锁顺序。"""
        if not isinstance(subject, str) or not 1 <= len(subject) <= 255:
            raise AuthError("ACCOUNT_UNAVAILABLE", "账户不可用")
        if not await self.subjects.is_active(db, subject):
            raise AuthError("ACCOUNT_UNAVAILABLE", "账户不可用")

    async def _principal(self, db, principal):
        """在调用方事务内核对应用归属与业务主体状态，不把会话身份当作权限。"""
        if principal.app_id != self.app_id:
            raise AuthError("AUTH_APP_MISMATCH", "认证应用不匹配")
        await self.require_active_subject(db, principal.subject)

    async def send_email_code(
        self, email: str, purpose: EmailCodePurpose, *, remote_key: str = "local"
    ) -> EmailCodeChallenge:
        """复用同一 challenge 状态机；外部发信不持有业务事务。"""
        return await super().send_email_code(self._email(email), purpose, remote_key=self._remote(remote_key))

    async def register_email(
        self, email: str, password: str, code: str, challenge_id: UUID | str, *, remote_key: str = "local"
    ) -> VerifiedIdentity:
        """核销、应用初始化和凭据写入使用同一事务，失败整体回滚。"""
        self._require_email()
        email, password = self._email(email), self._password(password, new=True)
        challenge_id = self._code(code, challenge_id)
        await self._code_attempt(email, "register", code, challenge_id, self._remote(remote_key))
        hashed = await self._password_work(hash_password, password)
        try:
            async with self.sessions() as db, db.begin():
                await self._consume_code(db, email, "register", code, challenge_id)
                subject = await self.subjects.create_subject(db, SubjectRegistration("email", email=email))
                await self.require_active_subject(db, subject)
                await db.execute(
                    insert(self.tables.identifiers).values(
                        app_id=self.app_id, kind="email", value=email, subject=subject, verified=True
                    )
                )
                await db.execute(
                    insert(self.tables.password_credentials).values(
                        app_id=self.app_id, subject=subject, password_hash=hashed, updated_at=int(time.time())
                    )
                )
                identity = await self._new_identity(db, subject, "email", "login", email, hashed)
        except IntegrityError:
            raise AuthError("IDENTITY_ALREADY_BOUND", "登录标识已绑定", 409) from None
        return identity

    async def _password_identity(self, method, identifier, password, remote_key, purpose):
        """异步验证密码后锁定并复核凭据版本，只为未变更身份生成短期证明。"""
        value = self._email(identifier) if method == "email" else normalize_username(identifier)
        password = self._password(password, new=False)
        await self._rate("login-ip", self._remote(remote_key), 100, 900)
        await self._rate("login-identity:" + method, value, 20, 900)
        i, p = self.tables.identifiers, self.tables.password_credentials
        query = (
            select(i.c.subject, p.c.password_hash)
            .select_from(i.join(p, and_(i.c.app_id == p.c.app_id, i.c.subject == p.c.subject)))
            .where(i.c.app_id == self.app_id, i.c.kind == method, i.c.value == value, i.c.verified.is_(True))
        )
        async with self.sessions() as db:
            row = (await db.execute(query)).mappings().one_or_none()
        hashed = row["password_hash"] if row else self._dummy_password_hash
        valid = await self._password_work(verify_password, password, hashed)
        if row is None or not valid:
            raise AuthError("CREDENTIALS_INVALID", "登录标识或密码错误")
        async with self.sessions() as db, db.begin():
            await self.require_active_subject(db, row["subject"])
            # 比较期间密码或标识被改动，禁止旧请求继续完成认证。
            current = (await db.execute(query.with_for_update())).mappings().one_or_none()
            if current is None or current["subject"] != row["subject"] or current["password_hash"] != hashed:
                raise AuthError("CREDENTIALS_INVALID", "登录标识或密码错误")
            identity = await self._new_identity(db, row["subject"], method, purpose, value, hashed)
        return identity

    async def authenticate(
        self,
        method: str,
        *,
        identifier: str | None = None,
        password: str | None = None,
        credential: str | None = None,
        remote_key: str = "local",
        purpose: Literal["login", "bind", "unlink"] = "login",
    ) -> VerifiedIdentity:
        """验证身份但不签发会话；provider 必须按配置注册，不能按邮箱自动合并。"""
        self._require_method(method)
        if purpose not in {"login", "bind", "unlink"}:
            raise AuthError("AUTH_PURPOSE_INVALID", "认证用途无效", 422)
        if method in {"email", "username"}:
            return await self._password_identity(method, identifier, password, remote_key, purpose)
        await self._rate("external-ip", self._remote(remote_key), 100, 900)
        identity = await self._external(method, credential)
        t = self.tables.external_identities
        query = select(t.c.subject, t.c.generation).where(
            t.c.app_id == self.app_id,
            t.c.provider == method,
            t.c.issuer == identity.issuer,
            t.c.external_subject == identity.subject,
        )
        try:
            async with self.sessions() as db, db.begin():
                linked = (await db.execute(query)).mappings().one_or_none()
                if linked is None and purpose != "login":
                    raise AuthError("REAUTHENTICATION_INVALID", "重新认证身份无效")
                if linked is None:
                    subject = await self.subjects.create_subject(
                        db, SubjectRegistration(method, identity.email, identity)
                    )
                    await self.require_active_subject(db, subject)
                    generation = str(uuid4())
                    await db.execute(
                        insert(t).values(
                            app_id=self.app_id,
                            provider=method,
                            issuer=identity.issuer,
                            external_subject=identity.subject,
                            subject=subject,
                            generation=generation,
                        )
                    )
                else:
                    subject, generation = linked["subject"], linked["generation"]
                await self.require_active_subject(db, subject)
                proof = await self._new_identity(
                    db, subject, method, purpose, identity.subject, generation, identity.issuer
                )
        except IntegrityError:
            # 并发首次登录只保留一个主体，失败事务中的业务初始化自动回滚。
            async with self.sessions() as db, db.begin():
                linked = (await db.execute(query)).mappings().one_or_none()
                if linked is None:
                    raise AuthError("IDENTITY_CONFLICT", "外部身份关联冲突", 409) from None
                subject = linked["subject"]
                await self.require_active_subject(db, subject)
                proof = await self._new_identity(
                    db, subject, method, purpose, identity.subject, linked["generation"], identity.issuer
                )
        return proof

    async def _external(self, method, credential):
        """限定凭据大小后交给注册适配器验签，不从邮箱或请求字段推断身份。"""
        self._require_method(method)
        if not isinstance(credential, str) or not 1 <= len(credential) <= 16384:
            raise AuthError("EXTERNAL_TOKEN_INVALID", "外部凭据无效")
        return await self.providers[method].verify(credential)

    async def reset_password(
        self, email: str, password: str, code: str, challenge_id: UUID | str, *, remote_key: str = "local"
    ) -> dict[str, str]:
        """验证码核销、共享密码更新和应用会话撤销全部在同一事务。"""
        self._require_email()
        email, password = self._email(email), self._password(password, new=True)
        challenge_id = self._code(code, challenge_id)
        await self._code_attempt(email, "password_reset", code, challenge_id, self._remote(remote_key))
        hashed = await self._password_work(hash_password, password)
        i, p = self.tables.identifiers, self.tables.password_credentials
        async with self.sessions() as db, db.begin():
            subject = await db.scalar(
                select(i.c.subject).where(
                    i.c.app_id == self.app_id, i.c.kind == "email", i.c.value == email, i.c.verified.is_(True)
                )
            )
            if subject is None:
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self.require_active_subject(db, subject)
            await self._consume_code(db, email, "password_reset", code, challenge_id)
            result = await db.execute(
                update(p)
                .where(p.c.app_id == self.app_id, p.c.subject == subject)
                .values(password_hash=hashed, updated_at=int(time.time()))
            )
            if result.rowcount != 1:
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self.session_backend.revoke_subject(subject, db=db)
        return {"status": "completed"}

    async def _prove_password(self, subject, password):
        """为敏感操作验证当前密码；调用方写事务须再次比较返回的凭据版本。"""
        self._password(password, new=False)
        await self._rate("sensitive-password", subject, 20, 900)
        p = self.tables.password_credentials
        async with self.sessions() as db:
            hashed = await db.scalar(
                select(p.c.password_hash).where(p.c.app_id == self.app_id, p.c.subject == subject)
            )
        valid = await self._password_work(verify_password, password, hashed or self._dummy_password_hash)
        if hashed is None or not valid:
            raise AuthError("CREDENTIALS_INVALID", "登录标识或密码错误")
        return hashed

    async def bind_username(self, principal: AuthPrincipal, username: str, password: str):
        """必须证明当前共享密码；只绑定标识，不另建密码副本。"""
        self._require_method("username")
        username = normalize_username(username)
        hashed = await self._prove_password(principal.subject, password)
        p, i = self.tables.password_credentials, self.tables.identifiers
        try:
            async with self.sessions() as db, db.begin():
                await self._principal(db, principal)
                current = await db.scalar(
                    select(p.c.password_hash)
                    .where(p.c.app_id == self.app_id, p.c.subject == principal.subject)
                    .with_for_update()
                )
                if current != hashed:
                    raise AuthError("CREDENTIALS_INVALID", "登录标识或密码错误")
                await db.execute(
                    insert(i).values(
                        app_id=self.app_id,
                        kind="username",
                        value=username,
                        subject=principal.subject,
                        verified=True,
                    )
                )
        except IntegrityError:
            raise AuthError("IDENTITY_ALREADY_BOUND", "登录标识已绑定", 409) from None

    async def change_password(self, principal: AuthPrincipal, old_password: str, new_password: str):
        """旧密码验证后以散列条件更新，防止并发改密覆盖；撤销所有会话。"""
        if not self.methods & {"email", "username"}:
            raise AuthError("AUTH_METHOD_DISABLED", "认证方式未启用", 403)
        self._password(new_password, new=True)
        old = await self._prove_password(principal.subject, old_password)
        hashed = await self._password_work(hash_password, new_password)
        p = self.tables.password_credentials
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
            changed = await db.execute(
                update(p)
                .where(p.c.app_id == self.app_id, p.c.subject == principal.subject, p.c.password_hash == old)
                .values(password_hash=hashed, updated_at=int(time.time()))
            )
            if changed.rowcount != 1:
                raise AuthError("CREDENTIALS_INVALID", "登录标识或密码错误")
            await self.session_backend.revoke_subject(principal.subject, db=db)
        return {"status": "completed"}

    async def bind_external(
        self, principal: AuthPrincipal, provider: str, credential: str, *, reauthentication: VerifiedIdentity
    ):
        """当前已认证主体显式绑定新凭据；同邮箱永不参与关联。"""
        external = await self._external(provider, credential)
        t = self.tables.external_identities
        try:
            async with self.sessions() as db, db.begin():
                await self._principal(db, principal)
                await self._consume_identity(db, reauthentication, "bind", subject=principal.subject)
                await db.execute(
                    insert(t).values(
                        app_id=self.app_id,
                        provider=provider,
                        issuer=external.issuer,
                        external_subject=external.subject,
                        subject=principal.subject,
                        generation=str(uuid4()),
                    )
                )
        except IntegrityError:
            raise AuthError("IDENTITY_ALREADY_BOUND", "外部身份已绑定", 409) from None

    async def unlink_identity(
        self,
        principal: AuthPrincipal,
        kind: str,
        value: str,
        *,
        reauthentication: VerifiedIdentity,
        issuer: str | None = None,
    ):
        """移除标识前检查剩余已启用凭据；宿主主体锁串行化并发解绑。"""
        self._require_method(kind)
        i, e, p = self.tables.identifiers, self.tables.external_identities, self.tables.password_credentials
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
            password = await db.scalar(
                select(p.c.subject)
                .where(p.c.app_id == self.app_id, p.c.subject == principal.subject)
                .with_for_update()
            )
            identifiers = (
                (
                    await db.execute(
                        select(i)
                        .where(i.c.app_id == self.app_id, i.c.subject == principal.subject)
                        .with_for_update()
                    )
                )
                .mappings()
                .all()
            )
            externals = (
                (
                    await db.execute(
                        select(e)
                        .where(e.c.app_id == self.app_id, e.c.subject == principal.subject)
                        .with_for_update()
                    )
                )
                .mappings()
                .all()
            )
            if kind in {"email", "username"}:
                value = self._email(value) if kind == "email" else normalize_username(value)
                target = [r for r in identifiers if r["kind"] == kind and r["value"] == value]
                usable = sum(
                    password is not None and r["verified"] and r["kind"] in self.methods
                    for r in identifiers
                    if not (r["kind"] == kind and r["value"] == value)
                )
                usable += sum(
                    "external" in self.methods and r["provider"] in self.providers for r in externals
                )
                predicate = (
                    i.c.app_id == self.app_id,
                    i.c.subject == principal.subject,
                    i.c.kind == kind,
                    i.c.value == value,
                )
                table = i
            else:
                if (
                    not isinstance(value, str)
                    or not 1 <= len(value) <= 255
                    or not isinstance(issuer, str)
                    or not 1 <= len(issuer) <= 512
                ):
                    raise AuthError("INPUT_INVALID", "外部身份参数无效", 422)
                target = [
                    r
                    for r in externals
                    if r["provider"] == kind and r["issuer"] == issuer and r["external_subject"] == value
                ]
                usable = sum(
                    password is not None and r["verified"] and r["kind"] in self.methods for r in identifiers
                )
                usable += sum(
                    "external" in self.methods and r["provider"] in self.providers
                    for r in externals
                    if not (
                        r["provider"] == kind and r["issuer"] == issuer and r["external_subject"] == value
                    )
                )
                predicate = (
                    e.c.app_id == self.app_id,
                    e.c.subject == principal.subject,
                    e.c.provider == kind,
                    e.c.issuer == issuer,
                    e.c.external_subject == value,
                )
                table = e
            if not target:
                raise AuthError("IDENTITY_NOT_FOUND", "登录标识不存在", 404)
            if not usable:
                raise AuthError("LAST_CREDENTIAL", "不能移除最后一种可用登录方式", 409)
            await self._consume_identity(db, reauthentication, "unlink", subject=principal.subject)
            await db.execute(delete(table).where(*predicate))

    async def _new_identity(self, db, subject, method, purpose, value, version, issuer=None):
        """在当前事务记录限用途、限时和有数量上限的一次性认证证明。"""
        now, proof_id = int(time.time()), uuid4()
        t = self.tables.authentication_proofs
        await db.execute(delete(t).where(t.c.app_id == self.app_id, t.c.expires_at <= now))
        outstanding = await db.scalar(
            select(func.count())
            .select_from(t)
            .where(t.c.app_id == self.app_id, t.c.subject == subject, t.c.consumed_at.is_(None))
        )
        if outstanding >= 32:
            raise AuthError("AUTH_RATE_LIMITED", "操作过于频繁，请稍后重试", 429)
        digest = hashlib.sha256(version.encode()).hexdigest()
        await db.execute(
            insert(t).values(
                app_id=self.app_id,
                id=str(proof_id),
                subject=subject,
                method=method,
                purpose=purpose,
                credential_value=value,
                issuer=issuer,
                credential_version=digest,
                created_at=now,
                expires_at=now + 300,
            )
        )
        return VerifiedIdentity(self.app_id, subject, method, now, digest, proof_id, purpose)

    async def _consume_identity(self, db, identity, purpose, *, subject=None):
        """在当前事务锁定并复核用途、主体和凭据版本，原子消费证明且不自行提交。"""
        now, t = int(time.time()), self.tables.authentication_proofs
        self._require_method(identity.method)
        if (
            identity.app_id != self.app_id
            or identity.purpose != purpose
            or (subject is not None and identity.subject != subject)
            or identity.proof_id is None
        ):
            raise AuthError("REAUTHENTICATION_INVALID", "认证证明无效或已过期")
        predicate = (
            t.c.app_id == self.app_id,
            t.c.id == str(identity.proof_id),
            t.c.subject == identity.subject,
            t.c.method == identity.method,
            t.c.purpose == purpose,
            t.c.created_at == identity.authenticated_at,
            t.c.credential_version == identity.credential_version,
            t.c.expires_at > now,
            t.c.consumed_at.is_(None),
        )
        proof = (await db.execute(select(t).where(*predicate).with_for_update())).mappings().one_or_none()
        if proof is None:
            raise AuthError("REAUTHENTICATION_INVALID", "认证证明无效或已过期")
        if identity.method in {"email", "username"}:
            i, p = self.tables.identifiers, self.tables.password_credentials
            version = await db.scalar(
                select(p.c.password_hash)
                .select_from(i.join(p, and_(i.c.app_id == p.c.app_id, i.c.subject == p.c.subject)))
                .where(
                    i.c.app_id == self.app_id,
                    i.c.subject == identity.subject,
                    i.c.kind == identity.method,
                    i.c.value == proof["credential_value"],
                    i.c.verified.is_(True),
                )
                .with_for_update()
            )
        else:
            e = self.tables.external_identities
            version = await db.scalar(
                select(e.c.generation)
                .where(
                    e.c.app_id == self.app_id,
                    e.c.subject == identity.subject,
                    e.c.provider == identity.method,
                    e.c.issuer == proof["issuer"],
                    e.c.external_subject == proof["credential_value"],
                )
                .with_for_update()
            )
        if version is None or hashlib.sha256(version.encode()).hexdigest() != identity.credential_version:
            raise AuthError("REAUTHENTICATION_INVALID", "认证证明无效或已过期")
        consumed = await db.execute(update(t).where(*predicate).values(consumed_at=now))
        if consumed.rowcount != 1:
            raise AuthError("REAUTHENTICATION_INVALID", "认证证明无效或已过期")

    async def issue(self, identity: VerifiedIdentity, *, device_id: UUID | None = None) -> SessionTokens:
        """认证结果交给应用会话实现；只接受当前应用及启用方式。"""
        if identity.app_id != self.app_id:
            raise AuthError("AUTH_APP_MISMATCH", "认证应用不匹配")
        self._require_method(identity.method)
        async with self.sessions() as db, db.begin():
            await self.require_active_subject(db, identity.subject)
            await self._consume_identity(db, identity, "login")
            return await self.session_backend.issue(identity, device_id=device_id, db=db)

    async def login_email(
        self, email: str, password: str, device_id: UUID | None = None, *, remote_key: str = "local"
    ) -> SessionTokens:
        """原生 transport 的便利入口，核心 authenticate 保持与会话签发解耦。"""
        identity = await self.authenticate(
            "email", identifier=email, password=password, remote_key=remote_key
        )
        return await self.issue(identity, device_id=device_id)

    async def verify(self, token: str) -> AuthPrincipal:
        """每次访问检查当前应用、启用方式及业务主体状态。"""
        principal = await self.session_backend.verify(token)
        self._require_method(principal.method)
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
        return principal

    async def refresh(self, refresh_token: str) -> SessionTokens:
        """应用会话后端负责原子轮换，运行时复核新的最小身份。"""
        tokens = await self.session_backend.refresh(refresh_token)
        self._require_method(tokens.principal.method)
        async with self.sessions() as db, db.begin():
            await self._principal(db, tokens.principal)
        return tokens

    async def delete_account(
        self, principal: AuthPrincipal, *, cleanup: Callable[[AsyncSession, str], Awaitable[None]]
    ) -> dict[str, str]:
        """撤销所有会话、清理身份并执行宿主删除，同库事务中失败全部回滚。

        principal 必须来自 transport 的当前会话验证；cleanup 不得自行提交或跨库宣称原子性。
        会话后端保留撤销记录以识别重放，认证核心不直接操作其物理表。
        """
        i = self.tables.identifiers
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
            emails = list(
                (
                    await db.scalars(
                        select(i.c.value).where(
                            i.c.app_id == self.app_id, i.c.subject == principal.subject, i.c.kind == "email"
                        )
                    )
                ).all()
            )
            await self.session_backend.revoke_subject(principal.subject, db=db)
            for table in (
                self.tables.identifiers,
                self.tables.password_credentials,
                self.tables.external_identities,
                self.tables.authentication_proofs,
            ):
                await db.execute(
                    delete(table).where(table.c.app_id == self.app_id, table.c.subject == principal.subject)
                )
            challenges = self.tables.email_challenges
            await db.execute(
                delete(challenges).where(challenges.c.app_id == self.app_id, challenges.c.email.in_(emails))
            )
            await cleanup(db, principal.subject)
        return {"status": "completed"}

    async def logout(self, principal: AuthPrincipal) -> None:
        """退出当前应用会话，不读取或拥有业务 User。"""
        if principal.app_id != self.app_id:
            raise AuthError("AUTH_APP_MISMATCH", "认证应用不匹配")
        await self.session_backend.revoke(principal)

    async def aclose(self) -> None:
        """等待密码线程结束并释放实例拥有的 Provider 资源。"""
        if self._password_tasks:
            await asyncio.gather(*self._password_tasks, return_exceptions=True)
        for provider in self.providers.values():
            closer = getattr(provider, "aclose", None)
            if closer is not None:
                await closer()
