"""Apple 网络边界使用假上游，事务和会话使用真实 SQLite。"""

import asyncio
import hashlib
from types import SimpleNamespace
from uuid import uuid4

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import Boolean, Column, MetaData, String, Table, func, insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_auth.apple import AppleAuthorization, AppleRevocationRequired, AppleSignInConfig
from dwy_auth.contracts import AuthPrincipal
from dwy_auth.models import AuthError
from dwy_auth.providers import ExternalIdentity
from dwy_auth.runtime import AuthRuntime
from dwy_auth.runtime_storage import build_runtime_tables
from dwy_auth.session_backend import JWTSessionBackend
from dwy_auth.session_storage import register_session_tables


class Gateway:
    def __init__(self):
        key = ec.generate_private_key(ec.SECP256R1()).private_bytes(
            serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
        )
        self.config = AppleSignInConfig(
            client_id="app.test",
            team_id="TEAM123456",
            key_id="KEY1234567",
            private_key=key.decode(),
            token_encryption_key=Fernet.generate_key().decode(),
        )
        self.calls, self.revoked = [], []
        self.fail = False
        self.claims = {}

    async def authorize(self, identity_token, authorization_code, nonce, display_name=None):
        self.calls.append(nonce)
        await asyncio.sleep(0)
        return AppleAuthorization(
            identity=ExternalIdentity("https://appleid.apple.com", identity_token),
            refresh_token="apple-refresh-" + authorization_code,
            client_id="app.test",
        )

    async def revoke(self, refresh_token, client_id=None):
        if self.fail:
            raise AuthError("APPLE_UNAVAILABLE", "服务不可用", 503)
        self.revoked.append((refresh_token, client_id))

    async def verify_notification(self, payload):
        return self.claims


@pytest.fixture
async def env(tmp_path):
    from dwy_auth.apple_auth import AppleAuthService
    from dwy_auth.apple_storage import build_apple_tables

    metadata = MetaData()
    runtime_tables = build_runtime_tables(metadata)
    session_tables = register_session_tables(metadata)
    apple_tables = build_apple_tables(metadata)
    customers = Table(
        "customers", metadata, Column("subject", String, primary_key=True), Column("active", Boolean)
    )
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/apple.db")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    class Subjects:
        async def create_subject(self, db, registration):
            subject = str(uuid4())
            await db.execute(insert(customers).values(subject=subject, active=True))
            return subject

        async def is_active(self, db, subject):
            return await db.scalar(select(customers.c.active).where(customers.c.subject == subject))

    backend = JWTSessionBackend("alpha", "test", "test", "x" * 32, sessions, session_tables)
    runtime = AuthRuntime("alpha", sessions, runtime_tables, Subjects(), session_backend=backend)
    gateway = Gateway()

    async def revoke_sessions(db, subject):
        await db.execute(
            update(session_tables.sessions)
            .where(
                session_tables.sessions.c.app_id == "alpha",
                session_tables.sessions.c.subject == subject,
                session_tables.sessions.c.method == "apple",
            )
            .values(revoked_at=1)
        )

    service = AppleAuthService(runtime, apple_tables, gateway, revoke_sessions=revoke_sessions)
    runtime.providers["apple"] = service
    yield SimpleNamespace(
        service=service,
        runtime=runtime,
        tables=apple_tables,
        sessions=sessions,
        gateway=gateway,
        customers=customers,
        session_tables=session_tables,
    )
    await engine.dispose()


async def login(env, identity="person", code="code"):
    challenge = await env.service.challenge()
    return await env.service.login(challenge["challenge_id"], identity, code)


async def test_challenge_hash_replay_and_stable_subject(env):
    challenge = await env.service.challenge()
    async with env.sessions() as db:
        row = (await db.execute(select(env.tables.challenges))).mappings().one()
        assert row["nonce_hash"] == hashlib.sha256(challenge["nonce"].encode()).hexdigest()
        assert challenge["nonce"] not in repr(row)
    first = await env.service.login(challenge["challenge_id"], "person", "first")
    with pytest.raises(AuthError):
        await env.service.login(challenge["challenge_id"], "person", "first")
    second = await login(env, code="second")
    assert first.principal.subject == second.principal.subject
    assert env.gateway.calls[0] == challenge["nonce"]
    async with env.sessions() as db:
        grant = (await db.execute(select(env.tables.grants))).mappings().one()
        assert "apple-refresh" not in repr(grant)
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 1
    with pytest.raises(AuthError) as error:
        await env.runtime.authenticate("apple", credential="token")
    assert error.value.code == "AUTH_APPLE_FLOW_REQUIRED"


async def test_expired_cross_app_and_concurrent_challenge(env):
    challenge = await env.service.challenge()
    async with env.sessions() as db, db.begin():
        await db.execute(update(env.tables.challenges).values(expires_at=0))
    with pytest.raises(AuthError):
        await env.service.login(challenge["challenge_id"], "person", "code")
    challenge = await env.service.challenge()
    env.runtime.app_id = "beta"
    with pytest.raises(AuthError):
        await env.service.login(challenge["challenge_id"], "person", "code")
    env.runtime.app_id = "alpha"
    outcomes = await asyncio.gather(
        *[env.service.login(challenge["challenge_id"], "person", "code") for _ in range(2)],
        return_exceptions=True,
    )
    assert sum(not isinstance(item, Exception) for item in outcomes) == 1
    assert len(env.gateway.calls) == 1


async def test_concurrent_first_logins_keep_one_subject(env):
    results = await asyncio.gather(login(env, code="a"), login(env, code="b"), return_exceptions=True)
    successful = [result for result in results if not isinstance(result, Exception)]
    assert successful
    assert len({result.principal.subject for result in successful}) == 1
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 1


async def test_bind_scoped_challenge_preserves_old_subject(env):
    old = await login(env, identity="old")
    principal = old.principal
    rt = env.runtime
    async with env.sessions() as db, db.begin():
        external = rt.tables.external_identities
        generation = await db.scalar(select(external.c.generation))
        proof = await rt._new_identity(
            db, principal.subject, "apple", "bind", "old", generation, "https://appleid.apple.com"
        )
    challenge = await env.service.challenge(principal=principal, purpose="bind")
    foreign = AuthPrincipal("alpha", "other", uuid4(), "apple", None)
    with pytest.raises(AuthError):
        await env.service.bind(foreign, challenge["challenge_id"], "new", "new", reauthentication=proof)
    await env.service.bind(principal, challenge["challenge_id"], "new", "new", reauthentication=proof)
    assert (await login(env, identity="new", code="again")).principal.subject == principal.subject


async def test_delete_rollback_durable_outbox_and_retry(env):
    tokens = await login(env)
    with pytest.raises(RuntimeError):
        async with env.sessions() as db, db.begin():
            await env.service.prepare_delete(db, tokens.principal.subject)
            raise RuntimeError("rollback")
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.tables.grants)) == 1
        assert await db.scalar(select(func.count()).select_from(env.tables.revocations)) == 0
    async with env.sessions() as db, db.begin():
        jobs = await env.service.prepare_delete(db, tokens.principal.subject)
        assert len(jobs) == 1
        assert await db.scalar(select(env.tables.revocations.c.id)) == jobs[0]
    env.gateway.fail = True
    assert await env.service.process_revocations() == 0
    async with env.sessions() as db, db.begin():
        assert await db.scalar(select(func.count()).select_from(env.tables.revocations)) == 1
        await db.execute(update(env.tables.revocations).values(next_attempt_at=0))
    env.gateway.fail = False
    outcomes = await asyncio.gather(env.service.process_revocations(), env.service.process_revocations())
    assert sum(outcomes) == 1
    assert env.gateway.revoked == [("apple-refresh-code", "app.test")]
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.tables.revocations)) == 0


async def test_notification_revokes_only_apple_and_deduplicates(env):
    tokens = await login(env)
    async with env.sessions() as db, db.begin():
        from dwy_auth.contracts import VerifiedIdentity

        other = await env.runtime.session_backend.issue(
            VerifiedIdentity("alpha", tokens.principal.subject, "google"), device_id=None, db=db
        )
    env.gateway.claims = {
        "jti": "notice",
        "iss": "https://appleid.apple.com",
        "events": {"type": "consent-revoked", "sub": "person"},
    }
    assert await env.service.notification("signed") == {"status": "completed"}
    assert await env.service.notification("signed") == {"status": "completed"}
    with pytest.raises(AuthError):
        await env.runtime.session_backend.verify(tokens.access_token)
    assert await env.runtime.session_backend.verify(other.access_token)
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.tables.notifications)) == 1
        assert await db.scalar(select(func.count()).select_from(env.tables.grants)) == 0
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 1


async def test_notification_blocks_authorization_already_in_flight(env):
    original = await login(env)
    challenge = await env.service.challenge()
    authorize = env.gateway.authorize

    async def during_authorize(*args):
        result = await authorize(*args)
        env.gateway.claims = {
            "jti": "late",
            "iss": "https://appleid.apple.com",
            "events": {"type": "consent-revoked", "sub": "person"},
        }
        await env.service.notification("signed")
        return result

    env.gateway.authorize = during_authorize
    with pytest.raises(AuthError) as error:
        await env.service.login(challenge["challenge_id"], "person", "inflight")
    assert error.value.code == "AUTH_APPLE_AUTHORIZATION_REVOKED"
    with pytest.raises(AuthError):
        await env.runtime.session_backend.verify(original.access_token)


async def test_session_failure_rolls_back_subject_grant_and_queues_upstream_revoke(env):
    async def fail(*args, **kwargs):
        raise RuntimeError("session storage failed")

    env.runtime.session_backend.issue = fail
    with pytest.raises(RuntimeError):
        await login(env)
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 0
        assert await db.scalar(select(func.count()).select_from(env.tables.grants)) == 0
        assert await db.scalar(select(func.count()).select_from(env.runtime.tables.external_identities)) == 0
        assert await db.scalar(select(func.count()).select_from(env.tables.revocations)) == 1


async def test_notification_callback_failure_rolls_back_dedup_and_binding(env):
    tokens = await login(env)
    original = env.service.revoke_sessions

    async def fail(db, subject):
        raise RuntimeError("session storage failed")

    env.service.revoke_sessions = fail
    env.gateway.claims = {
        "jti": "retry-notice",
        "iss": "https://appleid.apple.com",
        "events": {"type": "account-deleted", "sub": "person"},
    }
    with pytest.raises(RuntimeError):
        await env.service.notification("signed")
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.tables.notifications)) == 0
        assert await db.scalar(select(func.count()).select_from(env.tables.grants)) == 1
    assert await env.runtime.session_backend.verify(tokens.access_token)
    env.service.revoke_sessions = original
    await env.service.notification("signed")


async def test_email_notification_is_acknowledged_without_revocation(env):
    tokens = await login(env)
    env.gateway.claims = {
        "jti": "email",
        "iss": "https://appleid.apple.com",
        "events": '{"type":"email-disabled","sub":"person"}',
    }
    await env.service.notification("signed")
    assert await env.runtime.session_backend.verify(tokens.access_token)


async def test_delete_blocks_authorization_already_in_flight(env):
    from sqlalchemy import delete

    tokens = await login(env)
    challenge = await env.service.challenge()
    authorize = env.gateway.authorize

    async def during_authorize(*args):
        result = await authorize(*args)

        async def cleanup(db, subject):
            await env.service.prepare_delete(db, subject)
            await db.execute(delete(env.customers).where(env.customers.c.subject == subject))

        await env.runtime.delete_account(tokens.principal, cleanup=cleanup)
        return result

    env.gateway.authorize = during_authorize
    with pytest.raises(AuthError):
        await env.service.login(challenge["challenge_id"], "person", "inflight")
    async with env.sessions() as db:
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 0
        assert await db.scalar(select(func.count()).select_from(env.tables.grants)) == 0
        assert await db.scalar(select(func.count()).select_from(env.tables.revocations)) == 2


async def test_failed_gateway_compensation_is_encrypted_and_durable(env):
    async def failed_exchange(*args):
        raise AppleRevocationRequired("recoverable-refresh", "app.test")

    env.gateway.authorize = failed_exchange
    with pytest.raises(AppleRevocationRequired) as error:
        await login(env)
    assert "recoverable-refresh" not in repr(error.value)
    async with env.sessions() as db:
        row = (await db.execute(select(env.tables.revocations))).mappings().one()
        assert "recoverable-refresh" not in repr(row)
        assert await db.scalar(select(func.count()).select_from(env.customers)) == 0
    assert await env.service.process_revocations() == 1
    assert env.gateway.revoked == [("recoverable-refresh", "app.test")]
