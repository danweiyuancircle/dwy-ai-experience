"""认证存储预算、实际外键删除顺序及绝对到期边界。"""

import asyncio
import hashlib
import os
from uuid import uuid4

import pytest
from dwyeapi.exceptions import AuthenticationError
from sqlalchemy import MetaData, event, func, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.schema import CreateSchema, DropSchema
from test_auth import VerifiedGoogle

from dwy_auth import AuthError, AuthService, build_auth_tables


@pytest.fixture
async def environment(tmp_path):
    url = os.environ.get("APP_CLOUD_TEST_POSTGRES_URL")
    schema = f"auth_growth_{uuid4().hex}" if url else None
    engine = create_async_engine(url or f"sqlite+aiosqlite:///{tmp_path}/growth.db")
    if schema:
        engine = engine.execution_options(schema_translate_map={None: schema})
    else:

        @event.listens_for(engine.sync_engine, "connect")
        def enforce_foreign_keys(connection, record):
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    tables = build_auth_tables(MetaData())
    async with engine.begin() as connection:
        if schema:
            await connection.execute(CreateSchema(schema))
        await connection.run_sync(tables.users.metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    verifier = VerifiedGoogle()
    service = AuthService("adbox", sessions, tables, verifier)
    try:
        yield service, tables, sessions, verifier
    finally:
        if schema:
            async with engine.begin() as connection:
                await connection.execute(DropSchema(schema, cascade=True))
        await engine.dispose()


def digest(token):
    return hashlib.sha256(token.encode()).hexdigest()


async def test_login_quota_counts_revoked_sessions_and_isolates_users_and_apps(environment, monkeypatch):
    service, tables, sessions, verifier = environment
    monkeypatch.setattr(AuthService, "MAX_UNEXPIRED_SESSIONS", 2, raising=False)
    first = await service.login("a", uuid4())
    revoked = await service.login("a", uuid4())
    await service.logout(await service.verify(revoked.access_token))
    with pytest.raises(AuthError) as error:
        await service.login("a", uuid4())
    assert error.value.status_code == 429 and error.value.code == "SESSION_QUOTA_EXCEEDED"
    async with sessions() as db:
        count = await db.scalar(select(func.count()).select_from(tables.sessions))
    assert count == 2
    assert (await service.verify(first.access_token)).user_id == first.user.id
    await service.login("b", uuid4())
    await AuthService("rightflow", sessions, tables, verifier).login("a", uuid4())


async def test_refresh_quota_preserves_current_credentials_and_replay_detection(environment, monkeypatch):
    service, tables, sessions, _ = environment
    monkeypatch.setattr(AuthService, "MAX_REFRESH_HISTORY", 2, raising=False)
    original = await service.login("a", uuid4())
    first = await service.refresh(original.refresh_token)
    current = await service.refresh(first.refresh_token)
    with pytest.raises(AuthError) as error:
        await service.refresh(current.refresh_token)
    assert error.value.status_code == 429 and error.value.code == "REFRESH_QUOTA_EXCEEDED"
    assert (await service.verify(current.access_token)).user_id == original.user.id
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 2
        assert await db.scalar(select(tables.sessions.c.refresh_hash)) == digest(current.refresh_token)
    independent = await service.login("a", uuid4())
    assert (await service.refresh(independent.refresh_token)).user.id == original.user.id
    with pytest.raises(AuthError) as replay:
        await service.refresh(original.refresh_token)
    assert replay.value.code == "REFRESH_TOKEN_INVALID"
    with pytest.raises(AuthenticationError):
        await service.verify(current.access_token)


@pytest.mark.parametrize("operation", ["login", "refresh"])
async def test_cleanup_at_exact_expiry_preserves_other_account_app_and_live_evidence(
    environment, monkeypatch, operation
):
    service, tables, sessions, verifier = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.service.time.time", lambda: now[0])
    expired = await service.login("a", uuid4())
    await service.refresh(expired.refresh_token)
    other = await service.login("b", uuid4())
    await service.refresh(other.refresh_token)
    foreign = AuthService("rightflow", sessions, tables, verifier)
    foreign_expired = await foreign.login("a", uuid4())
    await foreign.refresh(foreign_expired.refresh_token)
    now[0] += 1
    live = await service.login("a", uuid4())
    live_current = await service.refresh(live.refresh_token)
    now[0] += 30 * 86400 - 1
    if operation == "login":
        monkeypatch.setattr(AuthService, "MAX_UNEXPIRED_SESSIONS", 2, raising=False)
        await service.login("a", uuid4())
    else:
        await service.refresh(live_current.refresh_token)
    async with sessions() as db:
        rows = (await db.execute(select(tables.sessions))).mappings().all()
        history = (await db.execute(select(tables.refresh_history))).mappings().all()
    own = [row for row in rows if row["app_id"] == "adbox" and row["user_id"] == str(live.user.id)]
    assert len(own) == (2 if operation == "login" else 1)
    assert all(row["refresh_expires_at"] > now[0] for row in own)
    hashes = {row["refresh_hash"] for row in history}
    assert digest(expired.refresh_token) not in hashes
    assert digest(live.refresh_token) in hashes
    assert digest(other.refresh_token) in hashes
    assert digest(foreign_expired.refresh_token) in hashes
    assert any(row["user_id"] == str(other.user.id) for row in rows)
    assert any(row["user_id"] == str(foreign_expired.user.id) for row in rows)


async def test_cleanup_commits_even_when_login_quota_rejects_request(environment, monkeypatch):
    service, tables, sessions, _ = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.service.time.time", lambda: now[0])
    expired = await service.login("a", uuid4())
    await service.refresh(expired.refresh_token)
    now[0] += 1
    await service.login("a", uuid4())
    now[0] += 30 * 86400 - 1
    monkeypatch.setattr(AuthService, "MAX_UNEXPIRED_SESSIONS", 1, raising=False)
    with pytest.raises(AuthError) as error:
        await service.login("a", uuid4())
    assert error.value.code == "SESSION_QUOTA_EXCEEDED"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.sessions)) == 1
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 0


async def test_expired_refresh_cleans_evidence_and_session_before_reporting_invalid(environment, monkeypatch):
    service, tables, sessions, _ = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.service.time.time", lambda: now[0])
    original = await service.login("a", uuid4())
    await service.refresh(original.refresh_token)
    now[0] += 30 * 86400
    with pytest.raises(AuthError) as error:
        await service.refresh(original.refresh_token)
    assert error.value.code == "REFRESH_TOKEN_INVALID"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 0
        assert await db.scalar(select(func.count()).select_from(tables.sessions)) == 0


async def test_cleanup_never_removes_unexpired_replay_evidence(environment, monkeypatch):
    service, tables, sessions, _ = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.service.time.time", lambda: now[0])
    old = await service.login("a", uuid4())
    current = await service.refresh(old.refresh_token)
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(refresh_expires_at=now[0]))
    await service.login("a", uuid4())
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 1
        assert await db.scalar(select(func.count()).select_from(tables.sessions)) == 2
    with pytest.raises(AuthError):
        await service.refresh(old.refresh_token)
    async with sessions() as db:
        revoked = await db.scalar(
            select(tables.sessions.c.revoked_at).where(
                tables.sessions.c.refresh_hash == digest(current.refresh_token)
            )
        )
    assert revoked == now[0]


@pytest.mark.skipif(not os.environ.get("APP_CLOUD_TEST_POSTGRES_URL"), reason="requires PostgreSQL")
async def test_postgres_concurrent_logins_cannot_exceed_account_quota(environment, monkeypatch):
    service, tables, sessions, _ = environment
    monkeypatch.setattr(AuthService, "MAX_UNEXPIRED_SESSIONS", 2, raising=False)
    await service.login("a", uuid4())
    results = await asyncio.gather(
        service.login("a", uuid4()), service.login("a", uuid4()), return_exceptions=True
    )
    assert sum(isinstance(result, AuthError) and result.status_code == 429 for result in results) == 1
    assert sum(not isinstance(result, BaseException) for result in results) == 1
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.sessions)) == 2
