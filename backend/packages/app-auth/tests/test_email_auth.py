"""邮箱认证：真实数据库、公开 HTTP 与现有 Google 共存。"""

import asyncio
from uuid import uuid4

import httpx
import pytest
from dwyeapi.exceptions import AuthenticationError
from fastapi import FastAPI
from sqlalchemy import MetaData, func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from test_auth import VerifiedGoogle

from dwy_app_auth import AuthError, AuthService, build_auth_tables, install_auth_routes

PASSWORD = "correct horse battery staple"


class Mailbox:
    def __init__(self):
        self.messages = []
        self.succeed = True
        self.languages = []

    async def send(self, email, code, purpose, *, language="en"):
        self.messages.append((email, code, purpose))
        self.languages.append(language)
        return self.succeed


@pytest.fixture
async def email_environment(tmp_path):
    from dwy_app_auth import EmailAuthConfig

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/email.db")
    tables = build_auth_tables(MetaData())
    async with engine.begin() as connection:
        await connection.run_sync(tables.users.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    mailbox = Mailbox()
    service = AuthService(
        "adbox",
        sessions,
        tables,
        VerifiedGoogle(),
        email_sender=mailbox,
        email_config=EmailAuthConfig(challenge_secret="test-secret-" * 4),
    )
    yield service, tables, sessions, mailbox
    await service.aclose()
    await engine.dispose()


async def register(service, mailbox, email="person@example.com"):
    challenge = await service.send_email_code(email, "register")
    return await service.register_email(
        email, PASSWORD, mailbox.messages[-1][1], challenge.challenge_id, uuid4()
    )


@pytest.mark.parametrize(
    "header,language",
    [
        (None, "en"),
        ("zh-CN", "zh"),
        ("zh-Hant-TW", "zh"),
        ("en-US", "en"),
        ("vi-VN", "en"),
        ("en, zh;q=0.5", "zh"),
        ("zh;q=0, en", "en"),
    ],
)
async def test_http_email_language_reaches_sender(email_environment, header, language):
    """旧 HTTP 入口把语言送入真实验证码服务，未指定时默认英文。"""
    service, _, _, mailbox = email_environment
    app = FastAPI()
    install_auth_routes(app, service)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://auth.test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/email/code",
            headers={} if header is None else {"Accept-Language": header},
            json={"email": "person@example.com", "purpose": "register"},
        )
    assert response.status_code == 200
    assert mailbox.languages == [language]


async def test_email_registration_normalization_login_and_google_are_independent(email_environment):
    service, tables, sessions, mailbox = email_environment
    result = await register(service, mailbox, "Person@Example.com")
    login = await service.login_email("person@example.com", PASSWORD, uuid4())
    from dwy_app_auth import GoogleIdentity

    service.google_verifier.identities["a"] = GoogleIdentity(
        subject="google-a", email="person@example.com", display_name="A"
    )
    google = await service.login("a", uuid4())
    assert google.user.email == result.user.email
    assert result.user.id == login.user.id != google.user.id
    assert result.user.email == "person@example.com"
    async with sessions() as db:
        credential = (await db.execute(select(tables.password_credentials))).mappings().one()
        challenge = (await db.execute(select(tables.email_challenges))).mappings().one()
    assert credential["password_hash"].startswith("$2")
    assert PASSWORD not in str(credential)
    assert mailbox.messages[-1][1] not in str(challenge)
    assert challenge["consumed_at"] is not None


async def test_atomic_code_scope_replay_and_reset_revokes_sessions(email_environment):
    service, tables, sessions, mailbox = email_environment
    challenge = await service.send_email_code("person@example.com", "register")
    code = mailbox.messages[-1][1]
    results = await asyncio.gather(
        *[
            service.register_email("person@example.com", PASSWORD, code, challenge.challenge_id, uuid4())
            for _ in range(2)
        ],
        return_exceptions=True,
    )
    winners = [item for item in results if not isinstance(item, Exception)]
    assert len(winners) == 1
    old = winners[0]
    reset = await service.send_email_code("person@example.com", "password_reset")
    reset_code = mailbox.messages[-1][1]
    with pytest.raises(AuthError):
        await service.register_email("person@example.com", PASSWORD, reset_code, reset.challenge_id, uuid4())
    await service.reset_password(
        "person@example.com", "replacement password is strong", reset_code, reset.challenge_id
    )
    with pytest.raises(AuthenticationError):
        await service.verify(old.access_token)
    with pytest.raises(AuthError):
        await service.refresh(old.refresh_token)
    with pytest.raises(AuthError):
        await service.login_email("person@example.com", PASSWORD, uuid4())
    assert (
        await service.login_email("person@example.com", "replacement password is strong", uuid4())
    ).user.id == old.user.id


async def test_scoping_failure_attempts_and_delivery_failure(email_environment):
    from dwy_app_auth import EmailAuthConfig

    service, tables, sessions, mailbox = email_environment
    challenge = await service.send_email_code("person@example.com", "register")
    code = mailbox.messages[-1][1]
    foreign = AuthService(
        "rightflow",
        sessions,
        tables,
        VerifiedGoogle(),
        email_sender=mailbox,
        email_config=EmailAuthConfig(challenge_secret="test-secret-" * 4),
    )
    with pytest.raises(AuthError):
        await foreign.register_email("person@example.com", PASSWORD, code, challenge.challenge_id, uuid4())
    for _ in range(5):
        with pytest.raises(AuthError):
            await service.register_email(
                "person@example.com", PASSWORD, "badbad", challenge.challenge_id, uuid4()
            )
    with pytest.raises(AuthError):
        await service.register_email("person@example.com", PASSWORD, code, challenge.challenge_id, uuid4())
    with pytest.raises(AuthError) as limited:
        await service.send_email_code("person@example.com", "register")
    assert limited.value.status_code == 429
    mailbox.succeed = False
    with pytest.raises(AuthError) as failed:
        await service.send_email_code("failed@example.com", "register")
    assert failed.value.code == "EMAIL_DELIVERY_FAILED"
    async with sessions() as db:
        assert (
            await db.scalar(
                select(func.count())
                .select_from(tables.email_challenges)
                .where(
                    tables.email_challenges.c.email == "failed@example.com",
                    tables.email_challenges.c.delivered_at.is_not(None),
                )
            )
            == 0
        )


async def test_http_envelope_sensitive_validation_and_password_bounds(email_environment):
    service, _, _, mailbox = email_environment
    app = FastAPI()
    install_auth_routes(app, service)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://auth.test"
    ) as client:
        challenge = await client.post(
            "/api/v1/auth/email/code", json={"email": "person@example.com", "purpose": "register"}
        )
        assert challenge.status_code == 200
        data = challenge.json()["data"]
        assert set(data) == {"challenge_id", "expires_in", "resend_after", "code_length"}
        assert data["code_length"] == 6 and data["expires_in"] == 300
        body = {
            "email": "person@example.com",
            "password": PASSWORD,
            "code": mailbox.messages[-1][1],
            "challenge_id": data["challenge_id"],
            "device_id": str(uuid4()),
        }
        for password in ["short", "密" * 25]:
            response = await client.post("/api/v1/auth/register", json={**body, "password": password})
            assert response.status_code == 422
            assert password not in response.text
        registered = await client.post("/api/v1/auth/register", json=body)
        assert registered.status_code == 200 and registered.json()["code"] == "SUCCESS"
        assert registered.headers["cache-control"] == "no-store"
        invalid = await client.post(
            "/api/v1/auth/login",
            json={"email": "person@example.com", "password": PASSWORD, "device_id": "secret-invalid"},
        )
        assert (
            invalid.status_code == 422
            and PASSWORD not in invalid.text
            and "secret-invalid" not in invalid.text
        )


async def test_deleted_email_account_clears_credentials(email_environment):
    service, tables, sessions, mailbox = email_environment
    token = await register(service, mailbox)
    await service.delete_account(await service.verify(token.access_token))
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.password_credentials)) == 0
        assert await db.scalar(select(func.count()).select_from(tables.email_challenges)) == 0
    with pytest.raises(AuthError):
        await service.login_email("person@example.com", PASSWORD, uuid4())


async def test_resend_cooldown_new_code_invalidation_and_expiry(email_environment, monkeypatch):
    service, _, _, mailbox = email_environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_app_auth.email_auth.time.time", lambda: now[0])
    first = await service.send_email_code("person@example.com", "register")
    old_code = mailbox.messages[-1][1]
    now[0] += 60
    second = await service.send_email_code("person@example.com", "register")
    with pytest.raises(AuthError):
        await service.register_email("person@example.com", PASSWORD, old_code, first.challenge_id, uuid4())
    now[0] += 300
    with pytest.raises(AuthError):
        await service.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], second.challenge_id, uuid4()
        )


async def test_rolling_sessions_pass_months_cleanup_history_and_never_hit_lifetime_quota(
    email_environment, monkeypatch
):
    from dwy_app_auth import SessionPolicy

    service, tables, sessions, _ = email_environment
    service.session_policy = SessionPolicy(
        refresh_ttl=180 * 86400, rolling_refresh=True, replay_retention=86400
    )
    monkeypatch.setattr(service, "MAX_REFRESH_HISTORY", 2)
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_app_auth.service.time.time", lambda: now[0])
    token = await service.login("a", uuid4())
    for _ in range(6):
        now[0] += 31 * 86400
        token = await service.refresh(token.refresh_token)
    assert (await service.verify(token.access_token)).user_id == token.user.id
    async with sessions() as db:
        assert await db.scalar(select(tables.sessions.c.refresh_expires_at)) == now[0] + 180 * 86400
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 1


async def test_rolling_replay_still_revokes_successor(email_environment):
    from dwy_app_auth import SessionPolicy

    service, _, _, _ = email_environment
    service.session_policy = SessionPolicy(refresh_ttl=180 * 86400, rolling_refresh=True)
    first = await service.login("a", uuid4())
    second = await service.refresh(first.refresh_token)
    with pytest.raises(AuthError):
        await service.refresh(first.refresh_token)
    with pytest.raises(AuthenticationError):
        await service.verify(second.access_token)


async def test_atomic_send_budget_and_login_limits(email_environment):
    service, _, _, mailbox = email_environment
    sends = await asyncio.gather(
        *[service.send_email_code("person@example.com", "register") for _ in range(4)], return_exceptions=True
    )
    assert sum(not isinstance(item, Exception) for item in sends) == 1
    assert len(mailbox.messages) == 1
    for _ in range(10):
        with pytest.raises(AuthError) as error:
            await service.login_email("absent@example.com", PASSWORD, uuid4())
        assert error.value.code == "CREDENTIALS_INVALID"
    with pytest.raises(AuthError) as limited:
        await service.login_email("absent@example.com", PASSWORD, uuid4())
    assert limited.value.status_code == 429


async def test_eapi_sender_uses_transport_without_redis_or_internal_code_store():
    from dwyeapi.providers.email.base import EmailProviderBase

    from dwy_app_auth import EapiEmailCodeSender

    class Provider(EmailProviderBase):
        async def _send(self, target, code, *, language="en"):
            self.delivered = (target, code, language)
            return True

        async def _get_redis(self):
            raise AssertionError("SQL-backed authentication must not use Redis")

    provider = Provider(require_common_domain=False)
    assert await EapiEmailCodeSender(provider).send("person@example.com", "123456", "register", language="zh")
    assert provider.delivered == ("person@example.com", "123456", "zh")


async def test_migration_upgrades_populated_google_schema_without_changing_ids(tmp_path):
    from alembic.migration import MigrationContext
    from alembic.operations import Operations

    from dwy_app_auth import EmailAuthConfig
    from dwy_app_auth.migrations import upgrade_email_auth

    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/legacy.db")
    tables = build_auth_tables(MetaData())
    legacy = MetaData()
    for table in (tables.users, tables.sessions, tables.refresh_history):
        copied = table.to_metadata(legacy)
        if table.name == "auth_users":
            copied.c.google_subject.nullable = False
    async with engine.begin() as connection:
        await connection.run_sync(legacy.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    service = AuthService(
        "adbox",
        sessions,
        tables,
        VerifiedGoogle(),
        email_sender=Mailbox(),
        email_config=EmailAuthConfig(challenge_secret="migration-secret" * 3),
    )
    google = await service.login("a", uuid4())
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda bind: upgrade_email_auth(Operations(MigrationContext.configure(bind)))
        )
    assert (await service.verify(google.access_token)).user_id == google.user.id
    assert (await service.login("a", uuid4())).user.id == google.user.id
    email = await register(service, service.email_sender)
    assert email.user.id != google.user.id
    await engine.dispose()


async def test_password_work_cancellation_does_not_release_running_capacity(email_environment):
    import threading

    service, _, _, _ = email_environment
    started, release = threading.Event(), threading.Event()

    def slow():
        started.set()
        release.wait(timeout=5)
        return True

    task = asyncio.create_task(service._password_work(slow))
    while not started.is_set():
        await asyncio.sleep(0)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert service._password_inflight == 1
    release.set()
    for _ in range(100):
        if service._password_inflight == 0:
            break
        await asyncio.sleep(0.01)
    assert service._password_inflight == 0


async def test_http_login_reset_and_password_whitespace_are_preserved(email_environment):
    service, _, _, mailbox = email_environment
    await register(service, mailbox)
    app = FastAPI()
    install_auth_routes(app, service)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="https://auth.test"
    ) as client:
        login = await client.post(
            "/api/v1/auth/login",
            json={"email": "PERSON@example.com", "password": PASSWORD, "device_id": str(uuid4())},
        )
        assert login.status_code == 200 and login.json()["data"]["expires_in"] == 900
        old = login.json()["data"]
        challenge = await client.post(
            "/api/v1/auth/email/code", json={"email": "person@example.com", "purpose": "password_reset"}
        )
        replacement = "  password with spaces  "
        reset = await client.post(
            "/api/v1/auth/password/reset",
            json={
                "email": "person@example.com",
                "password": replacement,
                "code": mailbox.messages[-1][1],
                "challenge_id": challenge.json()["data"]["challenge_id"],
            },
        )
        assert reset.status_code == 200 and reset.json()["data"] == {"status": "completed"}
        refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": old["refresh_token"]})
        assert refreshed.status_code == 401
        with pytest.raises(AuthError):
            await service.login_email("person@example.com", replacement.strip(), uuid4())
        assert await service.login_email("person@example.com", replacement, uuid4())


async def test_rolling_refresh_retains_bounded_recent_replay_evidence(email_environment, monkeypatch):
    from dwy_app_auth import SessionPolicy

    service, tables, sessions, _ = email_environment
    service.session_policy = SessionPolicy(
        refresh_ttl=180 * 86400, rolling_refresh=True, replay_retention=86400
    )
    monkeypatch.setattr(service, "MAX_REFRESH_HISTORY", 2)
    token = await service.login("a", uuid4())
    token = await service.refresh(token.refresh_token)
    token = await service.refresh(token.refresh_token)
    with pytest.raises(AuthError) as limited:
        await service.refresh(token.refresh_token)
    assert limited.value.code == "REFRESH_QUOTA_EXCEEDED"
    assert await service.verify(token.access_token)
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 2


async def test_gmail_aliases_remain_separate_accounts(email_environment):
    service, _, _, mailbox = email_environment
    first = await register(service, mailbox, "person@gmail.com")
    second = await register(service, mailbox, "per.son+tag@gmail.com")
    assert first.user.id != second.user.id
    assert second.user.email == "per.son+tag@gmail.com"


@pytest.mark.parametrize("delay,remaining,resend", [(25, 275, 35), (65, 235, 0)])
async def test_delivery_latency_returns_actual_remaining_time(
    email_environment, monkeypatch, delay, remaining, resend
):
    service, _, _, mailbox = email_environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_app_auth.email_auth.time.time", lambda: now[0])
    original = mailbox.send

    async def delayed_send(email, code, purpose, *, language="en"):
        delivered = await original(email, code, purpose, language=language)
        now[0] += delay
        return delivered

    monkeypatch.setattr(mailbox, "send", delayed_send)
    challenge = await service.send_email_code("person@example.com", "register")
    assert challenge.expires_in == remaining
    assert challenge.resend_after == resend


async def test_delivery_expiring_before_response_never_returns_an_active_challenge(
    email_environment, monkeypatch
):
    service, tables, sessions, mailbox = email_environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_app_auth.email_auth.time.time", lambda: now[0])

    async def expired_send(email, code, purpose, *, language="en"):
        now[0] += 300
        return True

    monkeypatch.setattr(mailbox, "send", expired_send)
    with pytest.raises(AuthError) as expired:
        await service.send_email_code("person@example.com", "register")
    assert expired.value.code == "EMAIL_DELIVERY_FAILED"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.email_challenges)) == 0


async def test_reset_committing_after_bcrypt_blocks_inflight_old_password_login(
    email_environment, monkeypatch
):
    from dwy_app_auth.passwords import verify_password

    service, tables, sessions, mailbox = email_environment
    old = await register(service, mailbox)
    verified, release = asyncio.Event(), asyncio.Event()
    original = service._password_work

    async def pause_after_verify(function, *args):
        result = await original(function, *args)
        if function is verify_password:
            verified.set()
            await release.wait()
        return result

    monkeypatch.setattr(service, "_password_work", pause_after_verify)
    pending_login = asyncio.create_task(service.login_email("person@example.com", PASSWORD, uuid4()))
    await asyncio.wait_for(verified.wait(), timeout=5)
    challenge = await service.send_email_code("person@example.com", "password_reset")
    await service.reset_password(
        "person@example.com",
        "replacement password is strong",
        mailbox.messages[-1][1],
        challenge.challenge_id,
    )
    release.set()
    with pytest.raises(AuthError) as stale:
        await pending_login
    assert stale.value.code == "CREDENTIALS_INVALID"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.sessions)) == 1
    with pytest.raises(AuthenticationError):
        await service.verify(old.access_token)


async def test_http_email_limits_use_peer_address_and_ignore_forwarded_headers(email_environment):
    import hashlib

    service, tables, sessions, _ = email_environment
    app = FastAPI()
    install_auth_routes(app, service)
    peer, forged = "192.0.2.10", "198.51.100.20"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app, client=(peer, 12345)), base_url="https://auth.test"
    ) as client:
        response = await client.post(
            "/api/v1/auth/email/code",
            json={"email": "person@example.com", "purpose": "register"},
            headers={"X-Forwarded-For": forged, "Forwarded": f"for={forged}"},
        )
    assert response.status_code == 200
    async with sessions() as db:
        keys = set((await db.execute(select(tables.auth_rate_limits.c.key))).scalars())
    assert hashlib.sha256(f"send-ip\0{peer}".encode()).hexdigest() in keys
    assert hashlib.sha256(f"send-ip\0{forged}".encode()).hexdigest() not in keys
