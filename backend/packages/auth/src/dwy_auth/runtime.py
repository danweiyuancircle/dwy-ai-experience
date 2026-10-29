"""可实例化认证核心：应用主体、第三方验证、会话均通过注入合同提供。"""

import asyncio
import hashlib
import json
import re
import time
from collections.abc import Awaitable, Callable, Mapping
from contextlib import asynccontextmanager
from typing import Literal
from uuid import UUID, uuid4

import anyio
from sqlalchemy import and_, delete, func, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .contracts import (
    AuthAdmission,
    AuthPrincipal,
    LoginIdentity,
    SessionBackend,
    SessionTokens,
    VerifiedIdentity,
)
from .email_auth import (
    EmailAuthConfig,
    EmailAuthMixin,
    EmailCodeChallenge,
    EmailCodePurpose,
    EmailCodeSender,
    EmailLanguage,
    normalize_email,
    validate_password,
)
from .models import AuthError
from .passwords import hash_password, verify_password
from .providers import ExternalIdentity, ExternalIdentityProvider
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
        admission: AuthAdmission | None = None,
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
        self.admission = admission
        self.providers, self.methods = dict(providers or {}), frozenset(methods)
        if any(
            name in {"email", "username", "external"} or not re.fullmatch(r"[a-z][a-z0-9_-]{0,63}", name)
            for name in self.providers
        ):
            raise ValueError("Invalid provider configuration name")
        self._password_limiter = anyio.CapacityLimiter(4)
        self._password_inflight, self._password_tasks = 0, set()
        self._dummy_password_hash = "$2b$12$s6AXc3y1CJPYmZEr.1nVUOwFXwslhbh3Cv.oA9kHOFJWx3/v2Np22"

    @asynccontextmanager
    async def _transaction(self, db: AsyncSession | None):
        """内部原子入口复用同一事务；旧的独立认证接口继续自行提交。"""
        if db is not None:
            yield db
            return
        async with self.sessions() as session, session.begin():
            yield session

    def _require_admission_entry(self, db: AsyncSession | None) -> None:
        """配置准入后，公开低层入口不能单独创建主体或签发会话。"""
        if self.admission is not None and db is None:
            raise AuthError("AUTH_ADMISSION_REQUIRED", "认证必须通过应用准入入口", 403)

    async def _prepare_admission(self, proof: str | None, *, remote_key: str = "local") -> object:
        """不解释业务凭据；限制外部输入预算，外部验证发生在数据库事务前。"""
        if proof is not None and (not isinstance(proof, str) or not 1 <= len(proof.encode()) <= 131072):
            raise AuthError("AUTH_ADMISSION_PROOF_INVALID", "准入证明格式无效", 422)
        if self.admission is None:
            return None
        # 证明验证有外网成本；独立预算不能被错误密码或无效 refresh 绕过。
        await self._rate("admission-ip", self._remote(remote_key), 100, 900)
        return await self.admission.prepare(proof)

    async def _admit(self, db: AsyncSession, subject: str, prepared: object) -> None:
        """业务归属检查和主体、凭据、会话共同提交或回滚。"""
        if self.admission is not None:
            await self.admission.admit(db, subject, prepared)

    async def register_email_session(
        self,
        email: str,
        password: str,
        code: str,
        challenge_id: UUID | str,
        *,
        remote_key: str = "local",
        device_id: UUID | None = None,
        admission_proof: str | None = None,
    ) -> SessionTokens:
        """注册主体、准入归属及首个会话必须作为一个原子操作。"""
        prepared = await self._prepare_admission(admission_proof, remote_key=remote_key)
        async with self.sessions() as db, db.begin():
            identity = await self.register_email(
                email, password, code, challenge_id, remote_key=remote_key, _db=db
            )
            await self._admit(db, identity.subject, prepared)
            return await self.issue(identity, device_id=device_id, _db=db)

    async def login(
        self,
        method: str,
        *,
        identifier: str | None = None,
        password: str | None = None,
        credential: str | None = None,
        remote_key: str = "local",
        device_id: UUID | None = None,
        admission_proof: str | None = None,
    ) -> SessionTokens:
        """首次第三方登录同样受准入保护，禁止先创建账号再补查业务资格。"""
        prepared = await self._prepare_admission(admission_proof, remote_key=remote_key)
        async with self.sessions() as db, db.begin():
            identity = await self.authenticate(
                method,
                identifier=identifier,
                password=password,
                credential=credential,
                remote_key=remote_key,
                _db=db,
            )
            await self._admit(db, identity.subject, prepared)
            return await self.issue(identity, device_id=device_id, _db=db)

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
        self,
        email: str,
        purpose: EmailCodePurpose,
        *,
        remote_key: str = "local",
        language: EmailLanguage = "en",
    ) -> EmailCodeChallenge:
        """重置挑战绑定发码时主体与代次；未知邮箱仍发相同信封，但不能事后接管新账号。"""
        email, remote_key = self._email(email), self._remote(remote_key)
        if purpose != "password_reset":
            return await super().send_email_code(email, purpose, remote_key=remote_key, language=language)
        self._require_email()
        i, binding = self.tables.identifiers, None
        query = select(i.c.subject).where(
            i.c.app_id == self.app_id, i.c.kind == "email", i.c.value == email, i.c.verified.is_(True)
        )
        async with self.sessions() as db, db.begin():
            subject = await db.scalar(query)
            if subject is not None:
                await self.require_active_subject(db, subject)
                # 等待主体锁期间邮箱可改动，不能把旧读取绑定到新的邮箱归属。
                if await db.scalar(query.with_for_update()) == subject:
                    binding = {
                        "subject": subject,
                        "credential_version": await self._credential_state(db, subject),
                    }
        return await self._send_email_code(
            email, purpose, remote_key=remote_key, language=language, binding=binding
        )

    async def _credential_state(self, db, subject):
        """主体锁下记录全部入口版本；改密、改邮箱或关联变化都会使旧挑战失效。"""
        values = []
        for table in (
            self.tables.identifiers,
            self.tables.password_credentials,
            self.tables.external_identities,
            self.tables.credential_versions,
        ):
            rows = (
                (
                    await db.execute(
                        select(table)
                        .where(table.c.app_id == self.app_id, table.c.subject == subject)
                        .with_for_update()
                    )
                )
                .mappings()
                .all()
            )
            values.append(sorted(json.dumps(dict(row), sort_keys=True) for row in rows))
        return hashlib.sha256(json.dumps(values).encode()).hexdigest()

    async def _invalidate_email_updates(self, db, subject, *, previous_email=None):
        """凭据版本不能随内容恢复；持久化随机代次也阻止发信期间的旧快照重新激活。"""
        if db.bind.dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as upsert
        else:
            from sqlalchemy.dialects.sqlite import insert as upsert
        v, c = self.tables.credential_versions, self.tables.email_challenges
        generation = str(uuid4())
        statement = upsert(v).values(app_id=self.app_id, subject=subject, generation=generation)
        await db.execute(
            statement.on_conflict_do_update(
                index_elements=[v.c.app_id, v.c.subject], set_={"generation": generation}
            )
        )
        i = self.tables.identifiers
        emails = list(
            (
                await db.scalars(
                    select(i.c.value).where(
                        i.c.app_id == self.app_id, i.c.subject == subject, i.c.kind == "email"
                    )
                )
            ).all()
        )
        if previous_email is not None:
            emails.append(previous_email)
        await db.execute(
            update(c)
            .where(
                c.c.app_id == self.app_id,
                c.c.consumed_at.is_(None),
                (c.c.subject == subject)
                | (c.c.subject.is_(None) & (c.c.purpose == "password_reset") & c.c.email.in_(emails)),
            )
            .values(consumed_at=int(time.time()))
        )

    async def send_email_update_code(
        self,
        principal: AuthPrincipal,
        email: str,
        *,
        reauthentication: VerifiedIdentity,
        remote_key: str = "local",
        language: EmailLanguage = "en",
    ) -> EmailCodeChallenge:
        """当前主体重新认证后发码；邮件不持有业务事务，验证码不能跨主体或凭据版本使用。"""
        self._require_email()
        email = self._email(email)
        remote_key = self._remote(remote_key)
        if not callable(getattr(self.subjects, "update_email", None)):
            raise AuthError("EMAIL_UPDATE_NOT_CONFIGURED", "邮箱变更尚未配置", 503)
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
            await self._consume_identity(db, reauthentication, "email_update", subject=principal.subject)
            version = await self._credential_state(db, principal.subject)
        return await self._send_email_code(
            email,
            "email_update",
            remote_key=remote_key,
            language=language,
            binding={"subject": principal.subject, "credential_version": version},
        )

    async def update_email(
        self,
        principal: AuthPrincipal,
        email: str,
        code: str,
        challenge_id: UUID | str,
        *,
        new_password: str | None = None,
        remote_key: str = "local",
        admission_proof: str | None = None,
    ) -> SessionTokens:
        """同事务更新邮箱、核销挑战并撤销所有旧会话；返回同一主体的新设备会话。"""
        prepared = await self._prepare_admission(admission_proof, remote_key=remote_key)
        self._require_email()
        email, challenge_id = self._email(email), self._code(code, challenge_id)
        if not callable(getattr(self.subjects, "update_email", None)):
            raise AuthError("EMAIL_UPDATE_NOT_CONFIGURED", "邮箱变更尚未配置", 503)
        hashed = None
        if new_password is not None:
            self._password(new_password, new=True)
            hashed = await self._password_work(hash_password, new_password)
        await self._code_attempt(email, "email_update", code, challenge_id, self._remote(remote_key))
        i, p, c = self.tables.identifiers, self.tables.password_credentials, self.tables.email_challenges
        try:
            async with self.sessions() as db, db.begin():
                await self._principal(db, principal)
                await self._admit(db, principal.subject, prepared)
                challenge = (
                    (
                        await db.execute(
                            select(c)
                            .where(
                                c.c.app_id == self.app_id,
                                c.c.id == str(challenge_id),
                                c.c.subject == principal.subject,
                            )
                            .with_for_update()
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
                if challenge is None or challenge["credential_version"] != await self._credential_state(
                    db, principal.subject
                ):
                    raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
                current = await db.scalar(
                    select(p.c.password_hash).where(
                        p.c.app_id == self.app_id, p.c.subject == principal.subject
                    )
                )
                if current is None and hashed is None:
                    raise AuthError("PASSWORD_REQUIRED", "首次添加邮箱登录必须设置密码", 422)
                await self._consume_code(db, email, "email_update", code, challenge_id)
                previous_email = await db.scalar(
                    select(i.c.value).where(
                        i.c.app_id == self.app_id, i.c.subject == principal.subject, i.c.kind == "email"
                    )
                )
                await db.execute(
                    delete(i).where(
                        i.c.app_id == self.app_id, i.c.subject == principal.subject, i.c.kind == "email"
                    )
                )
                await db.execute(
                    insert(i).values(
                        app_id=self.app_id,
                        subject=principal.subject,
                        kind="email",
                        value=email,
                        verified=True,
                    )
                )
                if current is None:
                    await db.execute(
                        insert(p).values(
                            app_id=self.app_id,
                            subject=principal.subject,
                            password_hash=hashed,
                            updated_at=int(time.time()),
                        )
                    )
                elif hashed is not None:
                    await db.execute(
                        update(p)
                        .where(p.c.app_id == self.app_id, p.c.subject == principal.subject)
                        .values(password_hash=hashed, updated_at=int(time.time()))
                    )
                await self.subjects.update_email(db, principal.subject, email)
                await self._invalidate_email_updates(db, principal.subject, previous_email=previous_email)
                await self.session_backend.revoke_subject(principal.subject, db=db)
                # 该身份仅在本事务交给会话后端，不形成可重放的公开登录 proof。
                identity = VerifiedIdentity(self.app_id, principal.subject, "email")
                return await self.session_backend.issue(identity, device_id=principal.device_id, db=db)
        except IntegrityError:
            raise AuthError("IDENTITY_ALREADY_BOUND", "登录标识已绑定", 409) from None

    async def register_email(
        self,
        email: str,
        password: str,
        code: str,
        challenge_id: UUID | str,
        *,
        remote_key: str = "local",
        _db: AsyncSession | None = None,
    ) -> VerifiedIdentity:
        """核销、应用初始化和凭据写入使用同一事务，失败整体回滚。"""
        self._require_admission_entry(_db)
        self._require_email()
        email, password = self._email(email), self._password(password, new=True)
        challenge_id = self._code(code, challenge_id)
        await self._code_attempt(email, "register", code, challenge_id, self._remote(remote_key))
        hashed = await self._password_work(hash_password, password)
        try:
            async with self._transaction(_db) as db:
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

    async def _password_identity(self, method, identifier, password, remote_key, purpose, _db=None):
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
        async with self._transaction(_db) as db:
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
        purpose: Literal["login", "bind", "unlink", "email_update"] = "login",
        _db: AsyncSession | None = None,
    ) -> VerifiedIdentity:
        """验证身份但不签发会话；provider 必须按配置注册，不能按邮箱自动合并。"""
        if purpose == "login":
            self._require_admission_entry(_db)
        self._require_method(method)
        if purpose not in {"login", "bind", "unlink", "email_update"}:
            raise AuthError("AUTH_PURPOSE_INVALID", "认证用途无效", 422)
        if method in {"email", "username"}:
            return await self._password_identity(method, identifier, password, remote_key, purpose, _db)
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
            async with self._transaction(_db) as db:
                proof = await self._resolve_external(db, method, identity, purpose)
        except IntegrityError:
            if _db is not None:
                # PostgreSQL 冲突后整个共享事务失效；交给外层回滚，再由客户端重试。
                raise AuthError("IDENTITY_CONFLICT", "请求未完成，请重试", 409) from None
            # 独立低层入口已退出失败事务，可以在新事务读取并发获胜的主体。
            async with self._transaction(None) as db:
                linked = (await db.execute(query)).mappings().one_or_none()
                if linked is None:
                    raise AuthError("IDENTITY_CONFLICT", "外部身份关联冲突", 409) from None
                subject = linked["subject"]
                await self.require_active_subject(db, subject)
                proof = await self._new_identity(
                    db, subject, method, purpose, identity.subject, linked["generation"], identity.issuer
                )
        return proof

    async def _resolve_external(
        self, db: AsyncSession, method: str, identity: ExternalIdentity, purpose: str
    ) -> VerifiedIdentity:
        """仅供已验签适配器使用；加入其挑战和令牌事务，绝不接受 HTTP 自报身份。"""
        self._require_method(method)
        if purpose not in {"login", "bind", "unlink", "email_update"}:
            raise AuthError("AUTH_PURPOSE_INVALID", "认证用途无效", 422)
        t = self.tables.external_identities
        linked = (
            (
                await db.execute(
                    select(t.c.subject, t.c.generation).where(
                        t.c.app_id == self.app_id,
                        t.c.provider == method,
                        t.c.issuer == identity.issuer,
                        t.c.external_subject == identity.subject,
                    )
                )
            )
            .mappings()
            .one_or_none()
        )
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
        return await self._new_identity(
            db, subject, method, purpose, identity.subject, generation, identity.issuer
        )

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
        i, p, c = self.tables.identifiers, self.tables.password_credentials, self.tables.email_challenges
        owner = select(i.c.subject).where(
            i.c.app_id == self.app_id, i.c.kind == "email", i.c.value == email, i.c.verified.is_(True)
        )
        async with self.sessions() as db, db.begin():
            subject = await db.scalar(owner)
            if subject is None:
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self.require_active_subject(db, subject)
            # READ COMMITTED 下等待主体锁后必须重查，旧邮箱读取不能授权修改新邮箱账号。
            current_owner = await db.scalar(owner.with_for_update())
            version = await db.scalar(
                select(c.c.credential_version)
                .where(c.c.app_id == self.app_id, c.c.id == str(challenge_id), c.c.subject == subject)
                .with_for_update()
            )
            if (
                current_owner != subject
                or version is None
                or version != await self._credential_state(db, subject)
            ):
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self._consume_code(db, email, "password_reset", code, challenge_id)
            result = await db.execute(
                update(p)
                .where(p.c.app_id == self.app_id, p.c.subject == subject)
                .values(password_hash=hashed, updated_at=int(time.time()))
            )
            if result.rowcount != 1:
                raise AuthError("EMAIL_CODE_INVALID", "验证码无效或已过期", 400)
            await self._invalidate_email_updates(db, subject)
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
                await self._invalidate_email_updates(db, principal.subject)
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
            await self._invalidate_email_updates(db, principal.subject)
            await self.session_backend.revoke_subject(principal.subject, db=db)
        return {"status": "completed"}

    async def list_identities(self, principal: AuthPrincipal) -> list[LoginIdentity]:
        """主体隔离的可用登录方式列表；禁用的方式和无密码的标识不伪装为可用入口。"""
        i, p, e = (
            self.tables.identifiers,
            self.tables.password_credentials,
            self.tables.external_identities,
        )
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
            identifiers = (
                (
                    await db.execute(
                        select(i.c.kind, i.c.value)
                        .select_from(i.join(p, and_(i.c.app_id == p.c.app_id, i.c.subject == p.c.subject)))
                        .where(
                            i.c.app_id == self.app_id,
                            i.c.subject == principal.subject,
                            i.c.verified.is_(True),
                        )
                    )
                )
                .mappings()
                .all()
            )
            result = [
                LoginIdentity(row["kind"], row["value"]) for row in identifiers if row["kind"] in self.methods
            ]
            if "external" in self.methods:
                externals = (
                    (
                        await db.execute(
                            select(e).where(e.c.app_id == self.app_id, e.c.subject == principal.subject)
                        )
                    )
                    .mappings()
                    .all()
                )
                result.extend(
                    LoginIdentity("external", row["external_subject"], row["provider"], row["issuer"])
                    for row in externals
                    if row["provider"] in self.providers
                )
            return sorted(result, key=lambda row: (row.kind, row.provider or "", row.issuer or "", row.value))

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
                await self._invalidate_email_updates(db, principal.subject)
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
            await self._invalidate_email_updates(db, principal.subject)

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

    async def issue(
        self, identity: VerifiedIdentity, *, device_id: UUID | None = None, _db: AsyncSession | None = None
    ) -> SessionTokens:
        """认证结果交给应用会话实现；只接受当前应用及启用方式。"""
        self._require_admission_entry(_db)
        if identity.app_id != self.app_id:
            raise AuthError("AUTH_APP_MISMATCH", "认证应用不匹配")
        self._require_method(identity.method)
        async with self._transaction(_db) as db:
            await self.require_active_subject(db, identity.subject)
            await self._consume_identity(db, identity, "login")
            return await self.session_backend.issue(identity, device_id=device_id, db=db)

    async def login_email(
        self,
        email: str,
        password: str,
        device_id: UUID | None = None,
        *,
        remote_key: str = "local",
        admission_proof: str | None = None,
    ) -> SessionTokens:
        """邮箱便利入口复用完整准入事务，不能绕过应用门禁。"""
        return await self.login(
            "email",
            identifier=email,
            password=password,
            device_id=device_id,
            remote_key=remote_key,
            admission_proof=admission_proof,
        )

    async def verify(self, token: str) -> AuthPrincipal:
        """每次访问检查当前应用、启用方式及业务主体状态。"""
        principal = await self.session_backend.verify(token)
        self._require_method(principal.method)
        async with self.sessions() as db, db.begin():
            await self._principal(db, principal)
        return principal

    async def refresh(
        self, refresh_token: str, *, admission_proof: str | None = None, remote_key: str = "local"
    ) -> SessionTokens:
        """准入在轮换生效前完成；拒绝回滚尚未提交的 CAS，不消费旧 refresh。"""
        prepared = await self._prepare_admission(admission_proof, remote_key=remote_key)
        if self.admission is not None:

            async def before_lock(db, principal):
                """主体检查先取 account 锁, 保持所有凭据变更的统一锁序。"""
                self._require_method(principal.method)
                await self._principal(db, principal)

            async def before_rotate(db, principal):
                """只有 CAS 和配额成功才写准入归属, 失败不留下业务副作用。"""
                await self._admit(db, principal.subject, prepared)

            return await self.session_backend.refresh(
                refresh_token, before_lock=before_lock, before_rotate=before_rotate
            )
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
                self.tables.credential_versions,
            ):
                await db.execute(
                    delete(table).where(table.c.app_id == self.app_id, table.c.subject == principal.subject)
                )
            challenges = self.tables.email_challenges
            await db.execute(
                delete(challenges).where(
                    challenges.c.app_id == self.app_id,
                    (challenges.c.email.in_(emails)) | (challenges.c.subject == principal.subject),
                )
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
