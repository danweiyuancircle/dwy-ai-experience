"""通用准入不得留下被拒注册主体，也不得先消费 refresh 再拒绝。"""

import hashlib

import pytest
from sqlalchemy import func, select
from test_runtime import PASSWORD
from test_runtime import runtime_env as runtime_env_fixture

from dwy_auth.models import AuthError
from dwy_auth.providers import ExternalIdentity

# 复用真实应用数据库 fixture, 不复制账号/凭据初始化。
runtime_env = runtime_env_fixture


class Admission:
    """仅模拟业务决定；实际账号、凭据和会话均使用真实数据库。"""

    def __init__(self):
        self.prepared = []
        self.admitted = []
        self.reject = False

    async def prepare(self, proof):
        self.prepared.append(proof)
        if proof != "valid-proof":
            raise AuthError("ACCESS_PROOF_REQUIRED", "需要准入证明", 403)
        return proof

    async def admit(self, db, subject, prepared):
        self.admitted.append(subject)
        if self.reject:
            raise AuthError("ACCESS_DENIED", "准入拒绝", 403)


async def register_session(runtime, mailbox, proof="valid-proof"):
    """通过实际验证码注册入口测试原子完成认证。"""
    challenge = await runtime.send_email_code("person@example.com", "register")
    return await runtime.register_email_session(
        "person@example.com",
        PASSWORD,
        mailbox.messages[-1][1],
        challenge.challenge_id,
        admission_proof=proof,
    )


async def test_rejected_registration_rolls_back_subject_and_credentials(runtime_env):
    runtime, tables, sessions, subjects, mailbox, _ = runtime_env
    runtime.admission = admission = Admission()
    admission.reject = True
    with pytest.raises(AuthError, match="准入拒绝"):
        await register_session(runtime, mailbox)
    async with sessions() as db:
        for table in [subjects.table, tables.identifiers, tables.password_credentials]:
            assert await db.scalar(select(func.count()).select_from(table)) == 0
    assert len(admission.admitted) == 1


async def test_atomic_registration_and_each_login_prepare_fresh_proof(runtime_env):
    runtime, _, _, _, mailbox, _ = runtime_env
    runtime.admission = admission = Admission()
    tokens = await register_session(runtime, mailbox)
    logged_in = await runtime.login(
        "email", identifier="person@example.com", password=PASSWORD, admission_proof="valid-proof"
    )
    assert tokens.principal.subject == logged_in.principal.subject
    assert admission.prepared == ["valid-proof", "valid-proof"]
    with pytest.raises(AuthError, match="需要准入证明"):
        await runtime.login("email", identifier="person@example.com", password=PASSWORD)


async def test_external_admission_preparation_has_its_own_persisted_network_budget(runtime_env):
    """错误密码或 refresh 也不能绕过准入外网预算, 超限不调用外部 prepare。"""
    runtime, _, _, _, _, _ = runtime_env
    runtime.admission = admission = Admission()
    for _ in range(100):
        await runtime._prepare_admission("valid-proof", remote_key="198.51.100.10")
    with pytest.raises(AuthError) as rejected:
        await runtime._prepare_admission("valid-proof", remote_key="198.51.100.10")
    assert rejected.value.code == "EMAIL_RATE_LIMITED"
    assert len(admission.prepared) == 100
    await runtime._prepare_admission("valid-proof", remote_key="198.51.100.11")
    assert len(admission.prepared) == 101


async def test_admission_configured_low_level_login_cannot_bypass_gate(runtime_env):
    runtime, _, _, _, mailbox, _ = runtime_env
    runtime.admission = Admission()
    challenge = await runtime.send_email_code("person@example.com", "register")
    with pytest.raises(AuthError) as denied:
        await runtime.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )
    assert denied.value.code == "AUTH_ADMISSION_REQUIRED"
    from dwy_auth.contracts import VerifiedIdentity

    with pytest.raises(AuthError) as denied:
        await runtime.issue(VerifiedIdentity("alpha", "injected-subject", "email"))
    assert denied.value.code == "AUTH_ADMISSION_REQUIRED"
    with pytest.raises(AuthError) as denied:
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    assert denied.value.code == "AUTH_ADMISSION_REQUIRED"


async def test_rejected_external_first_login_creates_no_subject(runtime_env):
    runtime, tables, sessions, subjects, _, _ = runtime_env

    class Provider:
        """上游已验签身份，准入失败仍必须回滚首次主体。"""

        async def verify(self, credential):
            return ExternalIdentity("https://issuer.example.test", "external-person")

    runtime.providers["test"] = Provider()
    runtime.admission = admission = Admission()
    admission.reject = True
    with pytest.raises(AuthError, match="准入拒绝"):
        await runtime.login("test", credential="identity", admission_proof="valid-proof")
    async with sessions() as db:
        for table in [subjects.table, tables.external_identities]:
            assert await db.scalar(select(func.count()).select_from(table)) == 0


async def test_shared_external_conflict_never_reuses_failed_transaction_and_rolls_back(runtime_env):
    """模拟 PostgreSQL aborted 状态, 不能用 SQLite 允许继续查询掩盖事务错误。"""
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.sql.dml import Insert

    runtime, tables, sessions, subjects, _, _ = runtime_env
    runtime.admission = admission = Admission()
    failed_transaction_queries = []
    original_create = subjects.create_subject

    class Provider:
        """稳定外部身份触发首次注册分支。"""

        async def verify(self, credential):
            return ExternalIdentity("https://issuer.example.test", "concurrent-person")

    async def concurrent_subject(db, registration):
        """先写入真实业务主体, 再模拟同一事务的外部唯一键冲突。"""
        subject = await original_create(db, registration)
        original_execute = db.execute
        failed = False

        async def execute(statement, *args, **kwargs):
            nonlocal failed
            if failed:
                failed_transaction_queries.append(statement)
                raise RuntimeError("PostgreSQL aborted transaction reused")
            if isinstance(statement, Insert) and statement.table is tables.external_identities:
                failed = True
                raise IntegrityError("external identity insert", {}, RuntimeError("unique conflict"))
            return await original_execute(statement, *args, **kwargs)

        db.execute = execute
        return subject

    subjects.create_subject = concurrent_subject
    runtime.providers["test"] = Provider()
    with pytest.raises(AuthError) as rejected:
        await runtime.login("test", credential="identity", admission_proof="valid-proof")
    assert rejected.value.code == "IDENTITY_CONFLICT"
    assert not failed_transaction_queries and not admission.admitted
    async with sessions() as db:
        for table in [subjects.table, tables.external_identities]:
            assert await db.scalar(select(func.count()).select_from(table)) == 0


async def test_session_issuance_failure_rolls_back_admitted_registration(runtime_env):
    """即使业务准入成功，会话失败也不能留下已创建账号或密码。"""
    runtime, tables, sessions, subjects, mailbox, backend = runtime_env
    runtime.admission = Admission()

    async def unavailable(*args, **kwargs):
        raise RuntimeError("session issuance failed")

    backend.issue = unavailable
    with pytest.raises(RuntimeError, match="session issuance failed"):
        await register_session(runtime, mailbox)
    async with sessions() as db:
        for table in [subjects.table, tables.identifiers, tables.password_credentials]:
            assert await db.scalar(select(func.count()).select_from(table)) == 0


async def test_refresh_admits_before_rotation_and_denial_keeps_old_token(runtime_env):
    runtime, _, sessions, _, mailbox, _ = runtime_env
    from sqlalchemy import MetaData

    from dwy_auth.session_backend import JWTSessionBackend
    from dwy_auth.session_storage import register_session_tables

    tables = register_session_tables(MetaData())
    async with sessions.kw["bind"].begin() as connection:
        await connection.run_sync(tables.sessions.metadata.create_all)
    runtime.session_backend = JWTSessionBackend(
        "alpha",
        "https://auth.example.test",
        "native-app",
        "test-secret-at-least-32-bytes-long",
        sessions,
        tables,
    )
    runtime.admission = admission = Admission()
    tokens = await register_session(runtime, mailbox)
    old_hash = hashlib.sha256(tokens.refresh_token.encode()).hexdigest()
    admission.reject = True
    with pytest.raises(AuthError, match="准入拒绝"):
        await runtime.refresh(tokens.refresh_token, admission_proof="valid-proof")
    async with sessions() as db:
        assert await db.scalar(select(tables.sessions.c.refresh_hash)) == old_hash
    admission.reject = False
    refreshed = await runtime.refresh(tokens.refresh_token, admission_proof="valid-proof")
    assert refreshed.refresh_token != tokens.refresh_token
