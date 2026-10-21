"""真实 SQL/HTTP 会话授权，Google 网络边界才使用显式测试替身。"""

import asyncio
import hashlib
import os
import time
from uuid import uuid4

import httpx
import pytest
from dwyeapi.exceptions import AuthenticationError, register_exception_handlers
from fastapi import FastAPI
from sqlalchemy import MetaData, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_app_auth import (
    AuthError,
    AuthService,
    GoogleConfig,
    GoogleIdentity,
    OfficialGoogleVerifier,
    build_auth_tables,
    install_auth_routes,
)


class VerifiedGoogle:
    def __init__(self):
        self.identities = {
            "a": GoogleIdentity(subject="google-a", email="same@example.com", display_name="A"),
            "b": GoogleIdentity(subject="google-b", email="same@example.com", display_name="B"),
        }

    async def verify(self, value):
        if value not in self.identities:
            raise AuthError("GOOGLE_TOKEN_INVALID", "Google 凭据无效")
        return self.identities[value]


@pytest.fixture
async def environment(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/auth.db")
    metadata = MetaData()
    tables = build_auth_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    verifier = VerifiedGoogle()
    service = AuthService("adbox", sessions, tables, verifier)
    yield service, tables, sessions, verifier
    await engine.dispose()


async def test_subject_links_accounts_not_email(environment):
    service, _, _, _ = environment
    a = await service.login("a", uuid4())
    again = await service.login("a", uuid4())
    b = await service.login("b", uuid4())
    assert a.user.id == again.user.id
    assert a.user.id != b.user.id
    assert a.user.email == b.user.email
    assert a.access_token != again.access_token


async def test_device_is_session_metadata_not_identity(environment):
    service, _, _, _ = environment
    device = uuid4()
    a = await service.login("a", device)
    b = await service.login("b", device)
    assert a.user.id != b.user.id
    assert (await service.verify(a.access_token)).device_id == device


async def test_tokens_are_hashes_only(environment):
    service, tables, sessions, _ = environment
    result = await service.login("a", uuid4())
    async with sessions() as db:
        row = (await db.execute(select(tables.sessions))).mappings().one()
    assert row["access_hash"] == hashlib.sha256(result.access_token.encode()).hexdigest()
    assert row["refresh_hash"] == hashlib.sha256(result.refresh_token.encode()).hexdigest()
    assert result.access_token not in str(dict(row))
    assert result.refresh_token not in str(dict(row))
    assert result.access_token not in repr(result)


async def test_rotation_revokes_both_old_credentials(environment):
    service, _, _, _ = environment
    old = await service.login("a", uuid4())
    new = await service.refresh(old.refresh_token)
    assert old.user == new.user
    assert (await service.verify(new.access_token)).user_id == old.user.id
    with pytest.raises(AuthenticationError):
        await service.verify(old.access_token)
    with pytest.raises(AuthError):
        await service.refresh(old.refresh_token)
    with pytest.raises(AuthenticationError):
        await service.verify(new.refresh_token)


async def test_simultaneous_refresh_has_single_winner(environment):
    service, _, _, _ = environment
    old = await service.login("a", uuid4())
    results = await asyncio.gather(
        *[service.refresh(old.refresh_token) for _ in range(2)], return_exceptions=True
    )
    assert sum(not isinstance(item, Exception) for item in results) == 1
    assert sum(isinstance(item, AuthError) for item in results) == 1


async def test_logout_only_revokes_that_session(environment):
    service, _, _, _ = environment
    a = await service.login("a", uuid4())
    another = await service.login("a", uuid4())
    b = await service.login("b", uuid4())
    await service.logout(await service.verify(a.access_token))
    with pytest.raises(AuthenticationError):
        await service.verify(a.access_token)
    with pytest.raises(AuthError):
        await service.refresh(a.refresh_token)
    assert (await service.verify(another.access_token)).user_id == a.user.id
    assert (await service.verify(b.access_token)).user_id == b.user.id


async def test_scope_remains_independent_even_if_database_shared(environment):
    service, tables, sessions, verifier = environment
    other = AuthService("rightflow", sessions, tables, verifier)
    a = await service.login("a", uuid4())
    b = await other.login("a", uuid4())
    assert a.user.id != b.user.id
    with pytest.raises(AuthenticationError):
        await other.verify(a.access_token)
    with pytest.raises(AuthError):
        await other.refresh(a.refresh_token)
    with pytest.raises(AuthenticationError):
        await other.logout(await service.verify(a.access_token))


async def test_expiry_and_disabled_users_checked_per_request(environment):
    service, tables, sessions, _ = environment
    a = await service.login("a", uuid4())
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(access_expires_at=int(time.time()) - 1))
    with pytest.raises(AuthenticationError):
        await service.verify(a.access_token)
    fresh = await service.refresh(a.refresh_token)
    async with sessions() as db, db.begin():
        await db.execute(update(tables.users).values(disabled=True))
    with pytest.raises(AuthenticationError):
        await service.verify(fresh.access_token)
    with pytest.raises(AuthError):
        await service.refresh(fresh.refresh_token)
    with pytest.raises(AuthError):
        await service.login("a", uuid4())


async def test_refresh_absolute_expiry_cannot_be_extended(environment):
    service, tables, sessions, _ = environment
    a = await service.login("a", uuid4())
    absolute = int(time.time()) + 60
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(refresh_expires_at=absolute))
    await service.refresh(a.refresh_token)
    async with sessions() as db:
        assert (await db.execute(select(tables.sessions.c.refresh_expires_at))).scalar_one() == absolute


async def test_absolute_expiry_blocks_access_and_refresh(environment):
    service, tables, sessions, _ = environment
    a = await service.login("a", uuid4())
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(refresh_expires_at=int(time.time()) - 1))
    with pytest.raises(AuthenticationError):
        await service.verify(a.access_token)
    with pytest.raises(AuthError):
        await service.refresh(a.refresh_token)


async def test_logout_cannot_select_another_users_session(environment):
    service, _, _, _ = environment
    a = await service.login("a", uuid4())
    b = await service.login("b", uuid4())
    identity_a = await service.verify(a.access_token)
    identity_b = await service.verify(b.access_token)
    # 即使可信调用方误把 A 的 session_id 与 B 的 user_id 组合，也不能撤销 A/B。
    await service.logout(identity_b.model_copy(update={"session_id": identity_a.session_id}))
    assert (await service.verify(a.access_token)).user_id == a.user.id
    assert (await service.verify(b.access_token)).user_id == b.user.id


async def test_invalid_format_rejected_without_database():
    class NoDatabase:
        def __call__(self):
            raise AssertionError("invalid token must not touch database")

    service = AuthService("adbox", NoDatabase(), build_auth_tables(MetaData()), VerifiedGoogle())
    with pytest.raises(AuthenticationError):
        await service.verify("arbitrary")
    with pytest.raises(AuthError):
        await service.refresh("arbitrary")


async def test_http_auth_envelope_and_owner_injection(environment, tmp_path):
    service, tables, _, _ = environment
    app = FastAPI()
    register_exception_handlers(app)
    install_auth_routes(app, service)
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as client:
            assert (await client.post("/api/v1/auth/logout")).status_code == 401
            rejected = await client.post(
                "/api/v1/auth/google",
                json={
                    "id_token": "private-token",
                    "device_id": str(uuid4()),
                    "user_id": str(uuid4()),
                },
            )
            assert rejected.status_code == 422 and "private-token" not in rejected.text
            invalid = await client.post(
                "/api/v1/auth/google", json={"id_token": "secret-invalid-value", "device_id": str(uuid4())}
            )
            assert invalid.status_code == 401 and "secret-invalid-value" not in invalid.text
            response = await client.post(
                "/api/v1/auth/google", json={"id_token": "a", "device_id": str(uuid4())}
            )
            body = response.json()
            assert response.status_code == 200 and body["code"] == "SUCCESS"
            assert response.headers["Cache-Control"] == "no-store"
            assert set(body) == {"code", "message", "data", "timestamp"}
            token = body["data"]
            assert token["token_type"] == "Bearer" and token["expires_in"] == 900
            logout = await client.post(
                "/api/v1/auth/logout", headers={"Authorization": "Bearer " + token["access_token"]}
            )
            assert logout.status_code == 200
            assert (
                await client.post("/api/v1/auth/refresh", json={"refresh_token": token["refresh_token"]})
            ).status_code == 401


async def test_missing_google_configuration_is_closed():
    with pytest.raises(AuthError) as error:
        await OfficialGoogleVerifier(None).verify("anything")
    assert error.value.status_code == 503


def test_config_accepts_only_one_explicit_audience():
    from pydantic import ValidationError

    config = GoogleConfig(client_id="12345-sample.apps.googleusercontent.com")
    assert config.client_id.startswith("12345-")
    with pytest.raises(ValidationError):
        GoogleConfig(client_id="", dev_bypass=True)


@pytest.mark.skipif(not os.getenv("APP_CLOUD_TEST_POSTGRES_URL"), reason="PostgreSQL URL not configured")
async def test_postgres_concurrent_refresh_single_winner():
    from sqlalchemy.schema import CreateSchema, DropSchema

    schema = "auth_test_" + uuid4().hex
    base = create_async_engine(os.environ["APP_CLOUD_TEST_POSTGRES_URL"])
    engine = base.execution_options(schema_translate_map={None: schema})
    metadata = MetaData()
    tables = build_auth_tables(metadata)
    try:
        async with base.begin() as connection:
            await connection.execute(CreateSchema(schema))
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        service = AuthService("adbox", async_sessionmaker(engine), tables, VerifiedGoogle())
        result = await service.login("a", uuid4())
        outcomes = await asyncio.gather(
            *[service.refresh(result.refresh_token) for _ in range(4)], return_exceptions=True
        )
        assert sum(not isinstance(item, Exception) for item in outcomes) == 1
        assert sum(isinstance(item, AuthError) for item in outcomes) == 3
    finally:
        async with base.begin() as connection:
            await connection.execute(DropSchema(schema, cascade=True, if_exists=True))
        await base.dispose()


async def test_explicit_verifier_and_authorization_budget_preserve_host_boundary(environment):
    service, _, _, _ = environment
    tokens = await service.login("a", uuid4())
    identity = await service.verify(tokens.access_token)

    class TrustedAdapter:
        async def verify(self, token):
            if token != "trusted-adapter-token":
                raise AuthenticationError()
            return identity

    app = FastAPI()
    register_exception_handlers(app)
    install_auth_routes(app, service, identity_verifier=TrustedAdapter(), authorization_limit=32)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
        rejected = await client.post("/api/v1/auth/logout", headers={"Authorization": "Bearer " + "x" * 33})
        assert rejected.status_code == 401
        accepted = await client.post(
            "/api/v1/auth/logout", headers={"Authorization": "Bearer trusted-adapter-token"}
        )
        assert accepted.status_code == 200
        with pytest.raises(AuthenticationError):
            await service.verify(tokens.access_token)
