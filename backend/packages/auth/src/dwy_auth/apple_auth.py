"""Apple 授权在网络边界外完成，本地身份、授权与应用会话原子提交。"""

import hashlib
import hmac
import json
import secrets
import time
from uuid import UUID, uuid4

import anyio
from cryptography.fernet import Fernet
from sqlalchemy import delete, func, insert, select, text, update
from sqlalchemy.exc import IntegrityError

from .apple import AppleRevocationRequired
from .models import AuthError


class AppleAuthService:
    """宿主注入 runtime、独立表和上游；会话撤销回调必须加入传入事务。"""

    def __init__(self, runtime, tables, gateway, *, revoke_sessions):
        self.runtime, self.tables, self.gateway = runtime, tables, gateway
        self.revoke_sessions = revoke_sessions
        self._cipher = Fernet(gateway.config.token_encryption_key.get_secret_value().encode("ascii"))

    async def verify(self, credential):
        """拒绝通用单凭据路径，所有 Apple 登录必须经过一次性挑战。"""
        raise AuthError("AUTH_APPLE_FLOW_REQUIRED", "Apple 认证必须使用专用授权流程", 400)

    async def aclose(self):
        """释放本服务拥有的上游客户端。"""
        closer = getattr(self.gateway, "aclose", None)
        if closer is not None:
            await closer()

    async def challenge(self, *, remote_key="local", principal=None, purpose="login"):
        """返回原始 nonce；客户端直接传给 Apple，不做额外散列。"""
        rt, t, now = self.runtime, self.tables.challenges, int(time.time())
        rt._require_method("apple")
        if purpose not in {"login", "bind", "reauth_bind", "reauth_unlink", "reauth_email_update"} or (
            purpose != "login"
        ) != (principal is not None):
            raise AuthError("AUTH_PURPOSE_INVALID", "认证用途无效", 422)
        await rt._rate("apple-global", "app", 1000, 900)
        await rt._rate("apple-challenge", rt._remote(remote_key), 30, 900)
        nonce, challenge_id = secrets.token_urlsafe(32), str(uuid4())
        async with rt.sessions() as db, db.begin():
            await self._prune_notifications(db)
            if principal is not None:
                await rt._principal(db, principal)
            await db.execute(delete(t).where(t.c.app_id == rt.app_id, t.c.expires_at <= now))
            if await db.scalar(select(func.count()).select_from(t).where(t.c.app_id == rt.app_id)) >= 1000:
                raise AuthError("AUTH_RATE_LIMITED", "操作过于频繁，请稍后重试", 429)
            await db.execute(
                insert(t).values(
                    app_id=rt.app_id,
                    id=challenge_id,
                    nonce_hash=hashlib.sha256(nonce.encode()).hexdigest(),
                    nonce_ciphertext=self._cipher.encrypt(nonce.encode()).decode(),
                    purpose=purpose,
                    subject=principal.subject if principal is not None else None,
                    created_at=time.time_ns(),
                    expires_at=now + 300,
                )
            )
        return {"challenge_id": challenge_id, "nonce": nonce, "expires_in": 300}

    async def _authorize(
        self, challenge_id, identity_token, authorization_code, purpose, subject, display_name, remote_key
    ):
        rt, t, now = self.runtime, self.tables.challenges, int(time.time())
        rt._require_method("apple")
        await rt._rate("apple-login-global", "app", 1000, 900)
        await rt._rate("apple-login", rt._remote(remote_key), 100, 900)
        try:
            challenge_id = str(UUID(str(challenge_id)))
        except (ValueError, TypeError, AttributeError):
            raise AuthError("AUTH_APPLE_CHALLENGE_INVALID", "Apple 挑战无效或已过期", 400) from None
        # 先原子领取并提交，再调用上游；失败也不能恢复一次性授权码的使用资格。
        async with rt.sessions() as db, db.begin():
            row = (
                (
                    await db.execute(
                        update(t)
                        .where(
                            t.c.app_id == rt.app_id,
                            t.c.id == challenge_id,
                            t.c.purpose == purpose,
                            t.c.subject == subject,
                            t.c.expires_at > now,
                            t.c.claimed_at.is_(None),
                        )
                        .values(claimed_at=now)
                        .returning(t)
                    )
                )
                .mappings()
                .one_or_none()
            )
        if row is None:
            raise AuthError("AUTH_APPLE_CHALLENGE_INVALID", "Apple 挑战无效或已过期", 400)
        nonce = self._cipher.decrypt(row["nonce_ciphertext"].encode()).decode()
        if not hmac.compare_digest(hashlib.sha256(nonce.encode()).hexdigest(), row["nonce_hash"]):
            raise AuthError("AUTH_APPLE_CHALLENGE_INVALID", "Apple 挑战无效或已过期", 400)
        try:
            authorization = await self.gateway.authorize(
                identity_token, authorization_code, nonce, display_name
            )
        except AppleRevocationRequired as error:
            with anyio.CancelScope(shield=True):
                async with rt.sessions() as db, db.begin():
                    await self._queue(
                        db,
                        self._cipher.encrypt(error.revocation_token.get_secret_value().encode()).decode(),
                        error.client_id,
                    )
            raise
        return row, authorization

    async def _identity_lock(self, db, issuer, subject):
        # PostgreSQL 锁定不存在的外部身份键，避免通知与首次建号互相错过。
        if db.bind.dialect.name == "postgresql":
            value = "\0".join((self.runtime.app_id, issuer, subject))
            key = int.from_bytes(hashlib.sha256(value.encode()).digest()[:8], "big", signed=True)
            await db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})

    async def _check_authorization(self, db, challenge, authorization):
        rt, t, identity = self.runtime, self.tables.notifications, authorization.identity
        await self._identity_lock(db, identity.issuer, identity.subject)
        # SQLite 的首条写语句也使后续身份读写与通知事务串行。
        c = self.tables.challenges
        changed = await db.execute(
            update(c)
            .where(
                c.c.app_id == rt.app_id,
                c.c.id == challenge["id"],
                c.c.expires_at > int(time.time()),
            )
            .values(claimed_at=challenge["claimed_at"])
        )
        if changed.rowcount != 1:
            raise AuthError("AUTH_APPLE_CHALLENGE_INVALID", "Apple 挑战无效或已过期", 400)
        revoked = await db.scalar(
            select(t.c.id)
            .where(
                t.c.app_id == rt.app_id,
                t.c.issuer == identity.issuer,
                t.c.external_subject == identity.subject,
                t.c.event.in_(("consent-revoked", "account-deleted", "local-delete")),
                t.c.received_at >= challenge["created_at"],
            )
            .limit(1)
        )
        if revoked is not None:
            raise AuthError("AUTH_APPLE_AUTHORIZATION_REVOKED", "Apple 授权已撤销，请重新授权", 401)

    async def _store_grant(self, db, authorization, subject):
        t, identity, rt = self.tables.grants, authorization.identity, self.runtime
        if db.bind.dialect.name == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as upsert
        else:
            from sqlalchemy.dialects.sqlite import insert as upsert
        values = dict(
            subject=subject,
            client_id=authorization.client_id,
            refresh_ciphertext=self._cipher.encrypt(authorization.refresh_token.encode()).decode(),
            created_at=time.time_ns(),
        )
        await db.execute(
            upsert(t)
            .values(app_id=rt.app_id, issuer=identity.issuer, external_subject=identity.subject, **values)
            .on_conflict_do_update(index_elements=[t.c.app_id, t.c.issuer, t.c.external_subject], set_=values)
        )

    async def _queue(self, db, ciphertext, client_id):
        t, job_id = self.tables.revocations, str(uuid4())
        await db.execute(
            insert(t).values(
                app_id=self.runtime.app_id,
                id=job_id,
                refresh_ciphertext=ciphertext,
                client_id=client_id,
                attempts=0,
                next_attempt_at=int(time.time()),
                lease_until=0,
            )
        )
        return job_id

    async def _failed_authorization(self, authorization):
        async with self.runtime.sessions() as db, db.begin():
            await self._queue(
                db,
                self._cipher.encrypt(authorization.refresh_token.encode()).decode(),
                authorization.client_id,
            )

    async def login(
        self,
        challenge_id,
        identity_token,
        authorization_code,
        *,
        device_id=None,
        display_name=None,
        remote_key="local",
        admission_proof=None,
    ):
        """兑换完成后将身份关联、proof 核销、授权和应用会话放进同一事务。"""
        rt = self.runtime
        prepared = await rt._prepare_admission(admission_proof, remote_key=remote_key)
        challenge, authorization = await self._authorize(
            challenge_id, identity_token, authorization_code, "login", None, display_name, remote_key
        )
        try:
            for attempt in range(2):
                try:
                    async with rt.sessions() as db, db.begin():
                        await self._check_authorization(db, challenge, authorization)
                        identity = await rt._resolve_external(db, "apple", authorization.identity, "login")
                        await rt._admit(db, identity.subject, prepared)
                        # 等待宿主主体锁期间可能已完成删号，旧授权不能据此再建号。
                        await self._check_authorization(db, challenge, authorization)
                        await rt._consume_identity(db, identity, "login")
                        await self._store_grant(db, authorization, identity.subject)
                        await db.execute(
                            update(self.tables.challenges)
                            .where(
                                self.tables.challenges.c.app_id == rt.app_id,
                                self.tables.challenges.c.id == challenge["id"],
                            )
                            .values(subject=identity.subject)
                        )
                        return await rt.session_backend.issue(identity, device_id=device_id, db=db)
                except IntegrityError:
                    if attempt:
                        raise AuthError("IDENTITY_CONFLICT", "外部身份关联冲突", 409) from None
        except BaseException:
            with anyio.CancelScope(shield=True):
                await self._failed_authorization(authorization)
            raise

    async def reauthenticate(self, principal, credential, *, purpose, remote_key="local"):
        """消费当前主体的限用途 Apple 挑战; 只返回一次性 proof, 不创建主体或会话。"""
        if purpose not in {"bind", "unlink", "email_update"}:
            raise AuthError("AUTH_PURPOSE_INVALID", "认证用途无效", 422)
        try:
            if not isinstance(credential, str) or not 1 <= len(credential.encode()) <= 32768:
                raise ValueError
            payload = json.loads(credential)
            if not isinstance(payload, dict) or set(payload) != {
                "challenge_id",
                "identity_token",
                "authorization_code",
            }:
                raise ValueError
            for key, limit in (("challenge_id", 36), ("identity_token", 16384), ("authorization_code", 4096)):
                value = payload[key]
                if not isinstance(value, str) or not 1 <= len(value.encode()) <= limit:
                    raise ValueError
        except (ValueError, RecursionError):
            raise AuthError("REAUTHENTICATION_INVALID", "Apple 重新认证材料无效", 400) from None
        challenge, authorization = await self._authorize(
            payload["challenge_id"],
            payload["identity_token"],
            payload["authorization_code"],
            "reauth_" + purpose,
            principal.subject,
            None,
            remote_key,
        )
        rt = self.runtime
        try:
            async with rt.sessions() as db, db.begin():
                await self._check_authorization(db, challenge, authorization)
                await rt._principal(db, principal)
                proof = await rt._resolve_external(db, "apple", authorization.identity, purpose)
                if proof.subject != principal.subject:
                    raise AuthError("REAUTHENTICATION_INVALID", "重新认证必须属于当前账号", 403)
                await self._check_authorization(db, challenge, authorization)
                await self._store_grant(db, authorization, principal.subject)
                return proof
        except BaseException:
            with anyio.CancelScope(shield=True):
                await self._failed_authorization(authorization)
            raise

    async def bind(
        self,
        principal,
        challenge_id,
        identity_token,
        authorization_code,
        *,
        reauthentication,
        display_name=None,
        remote_key="local",
    ):
        """绑定必须同时提供本人用途挑战与近期的一次性重新认证证明。"""
        rt = self.runtime
        if principal.app_id != rt.app_id:
            raise AuthError("AUTH_APP_MISMATCH", "认证应用不匹配")
        challenge, authorization = await self._authorize(
            challenge_id,
            identity_token,
            authorization_code,
            "bind",
            principal.subject,
            display_name,
            remote_key,
        )
        try:
            async with rt.sessions() as db, db.begin():
                await self._identity_lock(db, authorization.identity.issuer, authorization.identity.subject)
                await rt._principal(db, principal)
                await self._check_authorization(db, challenge, authorization)
                await rt._consume_identity(db, reauthentication, "bind", subject=principal.subject)
                external = authorization.identity
                await db.execute(
                    insert(rt.tables.external_identities).values(
                        app_id=rt.app_id,
                        provider="apple",
                        issuer=external.issuer,
                        external_subject=external.subject,
                        subject=principal.subject,
                        generation=str(uuid4()),
                    )
                )
                await self._store_grant(db, authorization, principal.subject)
        except BaseException as error:
            with anyio.CancelScope(shield=True):
                await self._failed_authorization(authorization)
            if isinstance(error, IntegrityError):
                raise AuthError("IDENTITY_ALREADY_BOUND", "外部身份已绑定", 409) from None
            raise

    async def prepare_delete(self, db, subject) -> list[str]:
        """加入宿主删号事务并返回任务 id；调用方可据此报告上游撤销仍待重试。"""
        rt, g, jobs = self.runtime, self.tables.grants, []
        grants = (
            (
                await db.execute(
                    select(g).where(g.c.app_id == rt.app_id, g.c.subject == subject).with_for_update()
                )
            )
            .mappings()
            .all()
        )
        for grant in grants:
            jobs.append(await self._queue(db, grant["refresh_ciphertext"], grant["client_id"]))
            await self._record_notification(
                db, str(uuid4()), grant["issuer"], grant["external_subject"], "local-delete"
            )
        await db.execute(delete(g).where(g.c.app_id == rt.app_id, g.c.subject == subject))
        t = self.tables.challenges
        await db.execute(delete(t).where(t.c.app_id == rt.app_id, t.c.subject == subject))
        return jobs

    async def process_revocations(self, limit=25):
        """有租约的 outbox worker；上游失败保留密文并指数退避，成功才删除。"""
        if type(limit) is not int or not 1 <= limit <= 100:
            raise ValueError("Revocation batch size must be between 1 and 100")
        rt, t, completed = self.runtime, self.tables.revocations, 0
        for _ in range(limit):
            now, lease = int(time.time()), str(uuid4())
            async with rt.sessions() as db, db.begin():
                candidate = (
                    select(t.c.id)
                    .where(t.c.app_id == rt.app_id, t.c.next_attempt_at <= now, t.c.lease_until <= now)
                    .order_by(t.c.next_attempt_at, t.c.id)
                    .limit(1)
                    .scalar_subquery()
                )
                row = (
                    (
                        await db.execute(
                            update(t)
                            .where(t.c.app_id == rt.app_id, t.c.id == candidate, t.c.lease_until <= now)
                            .values(lease_id=lease, lease_until=now + 120)
                            .returning(t)
                        )
                    )
                    .mappings()
                    .one_or_none()
                )
            if row is None:
                break
            try:
                token = self._cipher.decrypt(row["refresh_ciphertext"].encode()).decode()
                await self.gateway.revoke(token, client_id=row["client_id"])
            except Exception:
                async with rt.sessions() as db, db.begin():
                    await db.execute(
                        update(t)
                        .where(t.c.app_id == rt.app_id, t.c.id == row["id"], t.c.lease_id == lease)
                        .values(
                            attempts=row["attempts"] + 1,
                            lease_id=None,
                            lease_until=0,
                            next_attempt_at=int(time.time()) + min(86400, 30 * 2 ** min(row["attempts"], 12)),
                        )
                    )
            else:
                async with rt.sessions() as db, db.begin():
                    result = await db.execute(
                        delete(t).where(t.c.app_id == rt.app_id, t.c.id == row["id"], t.c.lease_id == lease)
                    )
                    completed += result.rowcount
        return completed

    async def _prune_notifications(self, db):
        t, now = self.tables.notifications, int(time.time())
        await db.execute(delete(t).where(t.c.app_id == self.runtime.app_id, t.c.expires_at <= now))

    async def _record_notification(self, db, notice_id, issuer, subject, event):
        t, now = self.tables.notifications, int(time.time())
        if (
            await db.scalar(select(func.count()).select_from(t).where(t.c.app_id == self.runtime.app_id))
            >= 10000
        ):
            raise AuthError("AUTH_RATE_LIMITED", "通知存储配额已满", 503)
        await db.execute(
            insert(t).values(
                app_id=self.runtime.app_id,
                id=notice_id,
                issuer=issuer,
                external_subject=subject,
                event=event,
                received_at=time.time_ns(),
                expires_at=now + 30 * 86400,
            )
        )

    async def notification(self, payload):
        """仅处理已验签通知；去重、凭据失效和 Apple 会话撤销在同一事务。"""
        claims = await self.gateway.verify_notification(payload)
        event = claims["events"]
        if isinstance(event, str):
            event = json.loads(event)
        rt, t, e = self.runtime, self.tables.notifications, self.runtime.tables.external_identities
        # 清理全应用过期行必须早于主体事务，避免与宿主删号的会话锁形成逆序。
        async with rt.sessions() as db, db.begin():
            await self._prune_notifications(db)
        try:
            async with rt.sessions() as db, db.begin():
                await self._identity_lock(db, claims["iss"], event["sub"])
                if await db.scalar(select(t.c.id).where(t.c.app_id == rt.app_id, t.c.id == claims["jti"])):
                    return {"status": "completed"}
                await self._record_notification(db, claims["jti"], claims["iss"], event["sub"], event["type"])
                if event["type"] in {"consent-revoked", "account-deleted"}:
                    predicate = (
                        e.c.app_id == rt.app_id,
                        e.c.provider == "apple",
                        e.c.issuer == claims["iss"],
                        e.c.external_subject == event["sub"],
                    )
                    subjects = (await db.execute(select(e.c.subject).where(*predicate))).scalars().all()
                    for subject in subjects:
                        await self.revoke_sessions(db, subject)
                        p = rt.tables.authentication_proofs
                        await db.execute(
                            delete(p).where(
                                p.c.app_id == rt.app_id, p.c.subject == subject, p.c.method == "apple"
                            )
                        )
                    await db.execute(delete(e).where(*predicate))
                    g = self.tables.grants
                    await db.execute(
                        delete(g).where(
                            g.c.app_id == rt.app_id,
                            g.c.issuer == claims["iss"],
                            g.c.external_subject == event["sub"],
                        )
                    )
        except IntegrityError:
            async with rt.sessions() as db:
                if not await db.scalar(
                    select(t.c.id).where(t.c.app_id == rt.app_id, t.c.id == claims["jti"])
                ):
                    raise
        return {"status": "completed"}
