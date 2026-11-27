"""会话合同：真实签名和数据库事务，避免以模拟调用替代撤销与轮换验收。"""

import asyncio
import hashlib
import importlib
import os
import time
from dataclasses import replace
from uuid import uuid4

import pytest
from jose import jwt
from sqlalchemy import MetaData, func, insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_auth.models import AuthError

SECRET = "session-test-secret-at-least-32-bytes"


@pytest.fixture
async def environment(tmp_path):
    contracts = importlib.import_module("dwy_auth.contracts")
    backend_module = importlib.import_module("dwy_auth.session_backend")
    storage = importlib.import_module("dwy_auth.session_storage")
    metadata = MetaData()
    tables = storage.register_session_tables(metadata)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/sessions.db")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    def backend(app_id="adbox", **kwargs):
        return backend_module.JWTSessionBackend(
            app_id, "https://auth.example.test", "native-app", SECRET, sessions, tables, **kwargs
        )

    yield backend, contracts, tables, sessions
    await engine.dispose()


async def issue(environment, subject="42", device_id=None, app_id="adbox", **kwargs):
    factory, contracts, _, sessions = environment
    backend = factory(app_id, **kwargs)
    async with sessions() as db, db.begin():
        tokens = await backend.issue(
            contracts.VerifiedIdentity(app_id, subject, "password"), device_id=device_id, db=db
        )
    return backend, tokens


async def test_integer_subject_optional_device_signed_access_hash_only_refresh(environment):
    backend, tokens = await issue(environment)
    _, _, tables, sessions = environment
    assert tokens.principal.subject == "42"
    assert tokens.principal.device_id is None
    assert await backend.verify(tokens.access_token) == tokens.principal
    claims = jwt.decode(tokens.access_token, SECRET, algorithms=["HS256"], audience="native-app")
    assert claims["sub"] == "42" and claims["type"] == "access"
    assert claims["app_id"] == "adbox"
    assert tokens.expires_in == 900
    async with sessions() as db:
        row = (await db.execute(select(tables.sessions))).mappings().one()
    assert row["refresh_hash"] == hashlib.sha256(tokens.refresh_token.encode()).hexdigest()
    assert tokens.refresh_token not in str(dict(row))
    assert tokens.access_token not in str(dict(row))
    assert tokens.access_token not in repr(tokens)
    assert tokens.refresh_token not in repr(tokens)
    assert SECRET not in repr(backend)
    assert all(not table.foreign_keys for table in tables.sessions.metadata.tables.values())


async def test_provider_configuration_name_supports_64_characters_through_rotation(environment):
    factory, contracts, _, sessions = environment
    backend = factory()
    method = "provider_" + "x" * 55
    async with sessions() as db, db.begin():
        tokens = await backend.issue(contracts.VerifiedIdentity("adbox", "42", method), device_id=None, db=db)
    assert (await backend.verify(tokens.access_token)).method == method
    assert (await backend.refresh(tokens.refresh_token)).principal.method == method


async def test_issue_rolls_back_with_host_transaction(environment):
    factory, contracts, tables, sessions = environment
    backend = factory()
    async with sessions() as db:
        tokens = await backend.issue(
            contracts.VerifiedIdentity("adbox", "42", "password"), device_id=None, db=db
        )
        await db.rollback()
    with pytest.raises(AuthError):
        await backend.verify(tokens.access_token)
    async with sessions() as db:
        assert (await db.execute(select(tables.sessions))).first() is None


@pytest.mark.parametrize("rolling_refresh", [False, True])
async def test_refresh_rotates_and_replay_revokes_family(environment, rolling_refresh):
    backend, old = await issue(environment, device_id=uuid4(), rolling_refresh=rolling_refresh)
    fresh = await backend.refresh(old.refresh_token)
    assert fresh.refresh_token != old.refresh_token
    assert fresh.access_token != old.access_token
    assert fresh.principal == old.principal
    assert await backend.verify(fresh.access_token) == fresh.principal
    with pytest.raises(AuthError):
        await backend.verify(old.access_token)
    with pytest.raises(AuthError):
        await backend.refresh(old.refresh_token)
    with pytest.raises(AuthError):
        await backend.verify(fresh.access_token)
    with pytest.raises(AuthError):
        await backend.refresh(fresh.refresh_token)


@pytest.mark.parametrize("rolling_refresh", [False, True])
async def test_refresh_concurrency_has_one_winner_and_revokes_replayed_family(environment, rolling_refresh):
    backend, old = await issue(environment, rolling_refresh=rolling_refresh)
    results = await asyncio.gather(
        backend.refresh(old.refresh_token), backend.refresh(old.refresh_token), return_exceptions=True
    )
    winners = [result for result in results if not isinstance(result, Exception)]
    assert len(winners) == 1
    assert sum(isinstance(result, AuthError) for result in results) == 1
    with pytest.raises(AuthError):
        await backend.verify(winners[0].access_token)


@pytest.mark.parametrize("rolling_refresh", [False, True])
async def test_refresh_history_boundary_revokes_family_commits_and_preserves_evidence(
    environment, rolling_refresh
):
    _, _, tables, sessions = environment
    backend, tokens = await issue(environment, rolling_refresh=rolling_refresh)
    _, independent = await issue(environment)
    async with sessions() as db, db.begin():
        await db.execute(
            insert(tables.refresh_history),
            [
                dict(
                    app_id="adbox",
                    refresh_hash=hashlib.sha256(f"consumed-{index}".encode()).hexdigest(),
                    session_id=str(tokens.principal.session_id),
                    expires_at=int(time.time()) + 3600,
                )
                for index in range(4095)
            ],
        )
    last = await backend.refresh(tokens.refresh_token)
    with pytest.raises(AuthError) as error:
        await backend.refresh(last.refresh_token)
    assert error.value.status_code == 429
    assert error.value.code == "REFRESH_QUOTA_EXCEEDED"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 4096
        assert (
            await db.scalar(
                select(tables.sessions.c.revoked_at).where(
                    tables.sessions.c.id == str(tokens.principal.session_id)
                )
            )
            is not None
        )
    with pytest.raises(AuthError):
        await backend.verify(last.access_token)
    with pytest.raises(AuthError):
        await backend.refresh(last.refresh_token)
    assert await backend.verify(independent.access_token) == independent.principal


async def test_app_isolation_blocks_verify_refresh_revoke_and_issue(environment):
    factory, contracts, _, sessions = environment
    backend, tokens = await issue(environment)
    other = factory("rightflow")
    for action in (
        other.verify(tokens.access_token),
        other.refresh(tokens.refresh_token),
        other.revoke(tokens.principal),
    ):
        with pytest.raises(AuthError):
            await action
    async with sessions() as db, db.begin():
        with pytest.raises(AuthError):
            await other.issue(contracts.VerifiedIdentity("adbox", "42", "password"), device_id=None, db=db)
    assert await backend.verify(tokens.access_token) == tokens.principal


async def test_revoke_rejects_forged_subject_and_revokes_only_requested_session(environment):
    backend, first = await issue(environment)
    _, second = await issue(environment)
    await backend.revoke(replace(first.principal, subject="someone-else"))
    assert await backend.verify(first.access_token) == first.principal
    await backend.revoke(first.principal)
    with pytest.raises(AuthError):
        await backend.verify(first.access_token)
    with pytest.raises(AuthError):
        await backend.refresh(first.refresh_token)
    assert await backend.verify(second.access_token) == second.principal


async def test_subject_revocation_uses_callers_transaction_and_app_scope(environment):
    _, _, _, sessions = environment
    backend, first = await issue(environment)
    _, second = await issue(environment)
    other, foreign = await issue(environment, app_id="rightflow")
    async with sessions() as db:
        await backend.revoke_subject("42", db=db)
        await db.rollback()
    assert await backend.verify(first.access_token) == first.principal
    async with sessions() as db, db.begin():
        await backend.revoke_subject("42", db=db)
    for tokens in (first, second):
        with pytest.raises(AuthError):
            await backend.verify(tokens.access_token)
    assert await other.verify(foreign.access_token) == foreign.principal


@pytest.mark.parametrize(
    "claim,value",
    [
        ("iss", "wrong"),
        ("aud", "wrong"),
        ("type", "reset"),
        ("app_id", "rightflow"),
        ("sub", "wrong"),
        ("sid", "invalid"),
        ("iat", "bad"),
        ("exp", 1),
        ("method", "google"),
    ],
)
async def test_signed_wrong_claims_are_rejected(environment, claim, value):
    backend, tokens = await issue(environment)
    claims = jwt.get_unverified_claims(tokens.access_token)
    claims[claim] = value
    with pytest.raises(AuthError):
        await backend.verify(jwt.encode(claims, SECRET, algorithm="HS256"))


@pytest.mark.parametrize(
    "claim", ["iss", "aud", "type", "app_id", "sub", "sid", "iat", "exp", "method", "jti"]
)
async def test_missing_required_claims_are_rejected(environment, claim):
    backend, tokens = await issue(environment)
    claims = jwt.get_unverified_claims(tokens.access_token)
    del claims[claim]
    with pytest.raises(AuthError):
        await backend.verify(jwt.encode(claims, SECRET, algorithm="HS256"))


async def test_expired_family_cannot_verify_or_refresh_and_rotation_preserves_deadline(environment):
    _, _, tables, sessions = environment
    backend, tokens = await issue(environment)
    deadline = int(time.time()) + 30
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(expires_at=deadline))
    rotated = await backend.refresh(tokens.refresh_token)
    assert 0 < rotated.expires_in <= 30
    assert jwt.get_unverified_claims(rotated.access_token)["exp"] == deadline
    async with sessions() as db:
        assert (await db.scalar(select(tables.sessions.c.expires_at))) == deadline
    async with sessions() as db, db.begin():
        await db.execute(update(tables.sessions).values(expires_at=1))
    with pytest.raises(AuthError):
        await backend.verify(rotated.access_token)
    with pytest.raises(AuthError):
        await backend.refresh(rotated.refresh_token)


async def test_rolling_refresh_extends_30_days_from_each_success(environment, monkeypatch):
    _, _, tables, sessions = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, tokens = await issue(environment, rolling_refresh=True)
    for day in (25, 50):
        now[0] = 2_000_000_000 + day * 86400
        tokens = await backend.refresh(tokens.refresh_token)
        assert tokens.expires_in == 900
        assert jwt.get_unverified_claims(tokens.access_token)["exp"] == now[0] + 900
        async with sessions() as db:
            assert await db.scalar(select(tables.sessions.c.expires_at)) == now[0] + 30 * 86400


@pytest.mark.parametrize("state", ["expired", "revoked"])
async def test_rolling_refresh_never_restores_expired_or_revoked_session(environment, monkeypatch, state):
    _, _, tables, sessions = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, tokens = await issue(environment, rolling_refresh=True)
    if state == "expired":
        now[0] += 30 * 86400
    else:
        await backend.revoke(tokens.principal)
    async with sessions() as db:
        original = (await db.execute(select(tables.sessions))).mappings().one()
    with pytest.raises(AuthError):
        await backend.refresh(tokens.refresh_token)
    async with sessions() as db:
        current = (await db.execute(select(tables.sessions))).mappings().one()
    assert current["expires_at"] == original["expires_at"]
    assert current["refresh_hash"] == original["refresh_hash"]


async def test_rolling_refresh_prunes_expired_history_without_lifetime_quota(environment, monkeypatch):
    _, _, tables, sessions = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, tokens = await issue(environment, rolling_refresh=True)
    backend.MAX_REFRESH_HISTORY = 2
    for _ in range(8):
        now[0] += 20 * 86400
        tokens = await backend.refresh(tokens.refresh_token)
    async with sessions() as db:
        rows = (await db.execute(select(tables.refresh_history))).mappings().all()
        assert len(rows) == 2
        assert all(now[0] < row["expires_at"] <= now[0] + 30 * 86400 for row in rows)
        assert await db.scalar(select(tables.sessions.c.revoked_at)) is None


async def test_rolling_replay_after_original_deadline_still_revokes_successor(environment, monkeypatch):
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, original = await issue(environment, rolling_refresh=True)
    now[0] += 25 * 86400
    fresh = await backend.refresh(original.refresh_token)
    now[0] += 10 * 86400
    with pytest.raises(AuthError):
        await backend.refresh(original.refresh_token)
    with pytest.raises(AuthError):
        await backend.refresh(fresh.refresh_token)


async def test_rolling_cleanup_keeps_other_family_and_bounds_replay_retention(environment, monkeypatch):
    _, _, tables, sessions = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, original = await issue(environment, rolling_refresh=True)
    _, independent = await issue(environment, subject="43", rolling_refresh=True)
    await backend.refresh(independent.refresh_token)
    now[0] += 25 * 86400
    fresh = await backend.refresh(original.refresh_token)
    now[0] += 30 * 86400 - 1
    fresh = await backend.refresh(fresh.refresh_token)
    now[0] += 1
    fresh = await backend.refresh(fresh.refresh_token)
    async with sessions() as db:
        history = (await db.execute(select(tables.refresh_history))).mappings().all()
        assert len(history) == 3
        assert any(row["session_id"] == str(independent.principal.session_id) for row in history)
        assert not any(
            row["refresh_hash"] == hashlib.sha256(original.refresh_token.encode()).hexdigest()
            for row in history
        )
    with pytest.raises(AuthError):
        await backend.refresh(original.refresh_token)
    assert (await backend.refresh(fresh.refresh_token)).refresh_token != fresh.refresh_token


async def test_rolling_extension_rolls_back_when_admission_rejects(environment, monkeypatch):
    _, _, tables, sessions = environment
    now = [2_000_000_000]
    monkeypatch.setattr("dwy_auth.session_backend.time.time", lambda: now[0])
    backend, tokens = await issue(environment, rolling_refresh=True)
    now[0] += 25 * 86400

    async def reject(db, principal):
        raise AuthError("ADMISSION_DENIED", "准入被拒绝", 403)

    with pytest.raises(AuthError, match="准入被拒绝"):
        await backend.refresh(tokens.refresh_token, before_rotate=reject)
    async with sessions() as db:
        assert await db.scalar(select(tables.sessions.c.expires_at)) == 2_000_000_000 + 30 * 86400
        assert await db.scalar(select(func.count()).select_from(tables.refresh_history)) == 0
    assert (await backend.refresh(tokens.refresh_token)).refresh_token != tokens.refresh_token


async def test_token_tampering_and_opaque_refresh_are_not_access_credentials(environment):
    backend, tokens = await issue(environment)
    for token in (tokens.refresh_token, "invalid", tokens.access_token + "x", "x" * 8193):
        with pytest.raises(AuthError) as error:
            await backend.verify(token)
        assert token not in str(error.value)
    for token in (tokens.access_token, "invalid", "x" * 8193):
        with pytest.raises(AuthError):
            await backend.refresh(token)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"access_ttl": 0},
        {"access_ttl": 3601},
        {"access_ttl": True},
        {"refresh_ttl": 899},
        {"refresh_ttl": 367 * 86400},
        {"rolling_refresh": 1},
        {"rolling_refresh": "true"},
    ],
)
async def test_invalid_ttl_configuration_is_closed(environment, kwargs):
    factory, _, _, _ = environment
    with pytest.raises(ValueError):
        factory(**kwargs)


@pytest.mark.parametrize(
    "subject,method",
    [("", "password"), ("x" * 256, "password"), ("42\n", "password"), ("42", ""), ("42", "x" * 65)],
)
async def test_identity_lengths_and_control_characters_rejected_before_write(environment, subject, method):
    factory, contracts, tables, sessions = environment
    async with sessions() as db, db.begin():
        with pytest.raises(ValueError):
            await factory().issue(contracts.VerifiedIdentity("adbox", subject, method), device_id=None, db=db)
        assert (await db.execute(select(tables.sessions))).first() is None


@pytest.mark.parametrize(
    "kwargs", [{"secret": "short"}, {"issuer": ""}, {"audience": "x" * 513}, {"app_id": "wrong_app"}]
)
def test_unsafe_signing_configuration_rejected(kwargs):
    backend_module = importlib.import_module("dwy_auth.session_backend")
    storage = importlib.import_module("dwy_auth.session_storage")
    config = dict(
        app_id="adbox",
        issuer="https://auth.example.test",
        audience="native-app",
        secret=SECRET,
        session_factory=None,
        tables=storage.register_session_tables(MetaData()),
    )
    config.update(kwargs)
    with pytest.raises(ValueError) as error:
        backend_module.JWTSessionBackend(**config)
    assert SECRET not in str(error.value)


@pytest.mark.skipif(not os.getenv("APP_CLOUD_TEST_POSTGRES_URL"), reason="PostgreSQL URL not configured")
@pytest.mark.parametrize("rolling_refresh", [False, True])
async def test_postgres_refresh_has_single_winner_and_replay_revokes_winner(rolling_refresh):
    from sqlalchemy.schema import CreateSchema, DropSchema

    contracts = importlib.import_module("dwy_auth.contracts")
    backend_module = importlib.import_module("dwy_auth.session_backend")
    storage = importlib.import_module("dwy_auth.session_storage")
    schema = "session_test_" + uuid4().hex
    base = create_async_engine(os.environ["APP_CLOUD_TEST_POSTGRES_URL"])
    engine = base.execution_options(schema_translate_map={None: schema})
    metadata = MetaData()
    tables = storage.register_session_tables(metadata)
    sessions = async_sessionmaker(engine)
    try:
        async with base.begin() as connection:
            await connection.execute(CreateSchema(schema))
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        backend = backend_module.JWTSessionBackend(
            "adbox",
            "https://auth.example.test",
            "native-app",
            SECRET,
            sessions,
            tables,
            rolling_refresh=rolling_refresh,
        )
        async with sessions() as db, db.begin():
            tokens = await backend.issue(
                contracts.VerifiedIdentity("adbox", "42", "password"), device_id=None, db=db
            )
        results = await asyncio.gather(
            *[backend.refresh(tokens.refresh_token) for _ in range(4)], return_exceptions=True
        )
        winners = [result for result in results if not isinstance(result, Exception)]
        assert len(winners) == 1
        assert sum(isinstance(result, AuthError) for result in results) == 3
        with pytest.raises(AuthError):
            await backend.verify(winners[0].access_token)
    finally:
        async with base.begin() as connection:
            await connection.execute(DropSchema(schema, cascade=True, if_exists=True))
        await base.dispose()


async def test_refresh_quota_failure_does_not_persist_admission_claim(environment):
    """不能先认领资格再因刷新配额失败返回错误, 同时保留旧 family 撤销。"""
    from sqlalchemy import Column, String, Table

    backend, tokens = await issue(environment)
    _, _, tables, sessions = environment
    claims = Table("admission_claims", tables.sessions.metadata, Column("subject", String, primary_key=True))
    async with sessions.kw["bind"].begin() as connection:
        await connection.run_sync(claims.create)
    backend.MAX_REFRESH_HISTORY = 0

    async def admit(db, principal):
        """模拟真实业务 claim 写入, 不以 mock 调用次数代替事务验收。"""
        await db.execute(insert(claims).values(subject=principal.subject))

    with pytest.raises(AuthError) as rejected:
        await backend.refresh(tokens.refresh_token, before_rotate=admit)
    assert rejected.value.code == "REFRESH_QUOTA_EXCEEDED"
    async with sessions() as db:
        assert await db.scalar(select(func.count()).select_from(claims)) == 0
        assert await db.scalar(select(tables.sessions.c.revoked_at)) is not None


async def test_refresh_locks_principal_before_session_cas_and_admits_after_success(environment):
    """断言 account→session→业务写入顺序, 不把 SQLite 当作 PG 死锁验收。"""
    from sqlalchemy import event
    from sqlalchemy.sql.dml import Update

    backend, tokens = await issue(environment)
    _, _, tables, sessions = environment
    phases = []

    def before_execute(connection, statement, multiparams, params, execution_options):
        """记录真实 CAS SQL 的执行位置, 验证回调不能把锁序反转。"""
        if isinstance(statement, Update) and statement.table is tables.sessions:
            phases.append("session-cas")

    async def before_lock(db, principal):
        """主体校验只取锁与检查, 不执行资格认领等业务副作用。"""
        phases.append("account-lock")

    async def before_rotate(db, principal):
        """成功刷新才执行可持久化的准入写入。"""
        phases.append("admit")

    event.listen(sessions.kw["bind"].sync_engine, "before_execute", before_execute)
    try:
        await backend.refresh(tokens.refresh_token, before_lock=before_lock, before_rotate=before_rotate)
    finally:
        event.remove(sessions.kw["bind"].sync_engine, "before_execute", before_execute)
    assert phases == ["account-lock", "session-cas", "admit"]


async def test_refresh_failed_cas_never_executes_admission(environment):
    """真实零行 CAS 不得触发 claim, 纯主体锁检查仍必须发生在 CAS 前。"""
    from sqlalchemy import false
    from sqlalchemy.sql.dml import Update

    backend, tokens = await issue(environment)
    _, _, tables, _ = environment
    phases = []

    async def before_lock(db, principal):
        """仅让本次真实 CAS 的 WHERE 不匹配, 精确覆盖并发失败分支。"""
        phases.append("account-lock")
        original_execute = db.execute

        async def execute(statement, *args, **kwargs):
            if isinstance(statement, Update) and "refresh_hash" in statement._values:
                phases.append("session-cas")
                statement = statement.where(false())
            return await original_execute(statement, *args, **kwargs)

        db.execute = execute

    async def before_rotate(db, principal):
        raise AssertionError("failed CAS must never admit")

    with pytest.raises(AuthError):
        await backend.refresh(tokens.refresh_token, before_lock=before_lock, before_rotate=before_rotate)
    assert phases == ["account-lock", "session-cas"]
    # 零行 CAS 没有消费旧凭据, 正常重试仍能完成轮换。
    assert (await backend.refresh(tokens.refresh_token)).refresh_token != tokens.refresh_token
