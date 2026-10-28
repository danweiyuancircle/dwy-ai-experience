"""应用主体独立于认证表，真实 SQLite 覆盖事务与身份边界。"""

from uuid import uuid4

import pytest
from sqlalchemy import Boolean, Column, MetaData, String, Table, insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_auth.email_auth import EmailAuthConfig
from dwy_auth.models import AuthError

PASSWORD = "a safe registration password"
REPLACEMENT = "a different safe password"


class Mailbox:
    def __init__(self):
        self.messages = []
        self.delivered = True

    async def send(self, email, code, purpose, *, language="en"):
        self.messages.append((email, code, purpose))
        return self.delivered


class Subjects:
    """宿主自己的字符串主键表；故意不用 auth_users 和 UUID。"""

    def __init__(self, table):
        self.table = table
        self.fail = False

    async def create_subject(self, db, registration):
        subject = "customer:" + uuid4().hex
        await db.execute(insert(self.table).values(customer_key=subject, allowed=True))
        if self.fail:
            raise RuntimeError("business initialization failed")
        return subject

    async def is_active(self, db, subject):
        return (
            await db.scalar(select(self.table.c.allowed).where(self.table.c.customer_key == subject)) is True
        )


class ApplicationSessions:
    """应用可以使用自己的会话实现；撤销记录落在同一数据库事务。"""

    def __init__(self, table):
        self.table = table

    async def issue(self, identity, *, device_id, db):
        from dwy_auth.contracts import AuthPrincipal, SessionTokens

        principal = AuthPrincipal(identity.app_id, identity.subject, uuid4(), identity.method, device_id)
        return SessionTokens("application-access", "application-refresh", 900, principal)

    async def revoke_subject(self, subject, *, db):
        await db.execute(insert(self.table).values(subject=subject))


@pytest.fixture
async def runtime_env(tmp_path):
    from dwy_auth.runtime import AuthRuntime
    from dwy_auth.runtime_storage import build_runtime_tables

    metadata = MetaData()
    tables = build_runtime_tables(metadata)
    customers = Table(
        "business_customers",
        metadata,
        Column("customer_key", String, primary_key=True),
        Column("allowed", Boolean),
    )
    revocations = Table("app_revocations", metadata, Column("subject", String))
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/runtime.db")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)
    subjects, mailbox = Subjects(customers), Mailbox()
    backend = ApplicationSessions(revocations)
    runtime = AuthRuntime(
        "alpha",
        sessions,
        tables,
        subjects,
        session_backend=backend,
        email_sender=mailbox,
        email_config=EmailAuthConfig(challenge_secret="test-secret-" * 4),
    )
    yield runtime, tables, sessions, subjects, mailbox, backend
    await runtime.aclose()
    await engine.dispose()


async def register(runtime, mailbox, email="person@example.com"):
    challenge = await runtime.send_email_code(email, "register")
    return await runtime.register_email(email, PASSWORD, mailbox.messages[-1][1], challenge.challenge_id)


async def test_verified_external_identity_joins_application_transaction_and_rolls_back(runtime_env):
    """Apple 等多步骤授权必须与挑战、上游令牌和业务主体在同一事务落库。"""
    from dwy_auth.providers import ExternalIdentity

    runtime, tables, sessions, subjects, _, _ = runtime_env
    runtime.providers["apple"] = object()
    external = ExternalIdentity("https://appleid.apple.com", "apple-person")
    with pytest.raises(RuntimeError, match="rollback"):
        async with sessions() as db, db.begin():
            await runtime._resolve_external(db, "apple", external, "login")
            raise RuntimeError("rollback")
    async with sessions() as db:
        assert (await db.execute(select(subjects.table))).all() == []
        assert (await db.execute(select(tables.external_identities))).all() == []
        assert (await db.execute(select(tables.authentication_proofs))).all() == []
    async with sessions() as db, db.begin():
        first = await runtime._resolve_external(db, "apple", external, "login")
    async with sessions() as db, db.begin():
        again = await runtime._resolve_external(db, "apple", external, "login")
        assert again.subject == first.subject
        assert len((await db.execute(select(subjects.table))).all()) == 1


async def test_verified_external_identity_rejects_disabled_provider_and_unknown_reauthentication(runtime_env):
    from dwy_auth.providers import ExternalIdentity

    runtime, _, sessions, _, _, _ = runtime_env
    external = ExternalIdentity("https://appleid.apple.com", "unknown-person")
    async with sessions() as db, db.begin():
        with pytest.raises(AuthError, match="认证方式"):
            await runtime._resolve_external(db, "apple", external, "login")
        runtime.providers["apple"] = object()
        with pytest.raises(AuthError) as exc:
            await runtime._resolve_external(db, "apple", external, "bind")
        assert exc.value.code == "REAUTHENTICATION_INVALID"


async def test_registration_uses_application_subject_and_shared_password_for_username(runtime_env):
    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox, "Person@Example.com")
    assert identity.subject.startswith("customer:")
    assert identity.app_id == "alpha"
    principal = type("Principal", (), {"app_id": "alpha", "subject": identity.subject})()
    await runtime.bind_username(principal, "Account.Name", PASSWORD)
    by_email = await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    by_username = await runtime.authenticate("username", identifier="account.name", password=PASSWORD)
    assert by_email.subject == by_username.subject == identity.subject
    async with sessions() as db:
        assert len((await db.execute(select(tables.password_credentials))).all()) == 1


async def test_registration_failure_rolls_back_subject_identity_and_code(runtime_env):
    runtime, tables, sessions, subjects, mailbox, _ = runtime_env
    challenge = await runtime.send_email_code("person@example.com", "register")
    subjects.fail = True
    with pytest.raises(RuntimeError):
        await runtime.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )
    async with sessions() as db:
        assert (await db.execute(select(subjects.table))).all() == []
        assert (await db.execute(select(tables.identifiers))).all() == []
        assert await db.scalar(select(tables.email_challenges.c.consumed_at)) is None
    subjects.fail = False
    assert (
        await runtime.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )
    ).subject
    with pytest.raises(AuthError):
        await runtime.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )


async def test_disabled_methods_and_accounts_are_rejected(runtime_env):
    runtime, _, sessions, subjects, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    runtime.methods = frozenset({"username"})
    with pytest.raises(AuthError) as disabled:
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    assert disabled.value.code == "AUTH_METHOD_DISABLED"
    runtime.methods = frozenset({"email"})
    async with sessions() as db, db.begin():
        await db.execute(update(subjects.table).values(allowed=False))
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    assert identity.subject.startswith("customer:")


async def test_reset_consumes_code_and_revokes_custom_sessions_atomically(runtime_env):
    runtime, _, sessions, _, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)
    challenge = await runtime.send_email_code("person@example.com", "password_reset")
    await runtime.reset_password(
        "person@example.com", REPLACEMENT, mailbox.messages[-1][1], challenge.challenge_id
    )
    async with sessions() as db:
        assert await db.scalar(select(backend.table.c.subject)) == identity.subject
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    assert (
        await runtime.authenticate("email", identifier="person@example.com", password=REPLACEMENT)
    ).subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.reset_password(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )


async def test_app_scope_and_delivery_failure(runtime_env):
    from dwy_auth.runtime import AuthRuntime

    runtime, tables, sessions, subjects, mailbox, backend = runtime_env
    challenge = await runtime.send_email_code("person@example.com", "register")
    other = AuthRuntime(
        "beta",
        sessions,
        tables,
        subjects,
        session_backend=backend,
        email_sender=mailbox,
        email_config=runtime.email_config,
    )
    with pytest.raises(AuthError):
        await other.register_email(
            "person@example.com", PASSWORD, mailbox.messages[-1][1], challenge.challenge_id
        )
    mailbox.delivered = False
    with pytest.raises(AuthError) as failed:
        await other.send_email_code("other@example.com", "register")
    assert failed.value.code == "EMAIL_DELIVERY_FAILED"
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.id).where(tables.email_challenges.c.app_id == "beta")
            )
            is None
        )
    await other.aclose()


async def test_external_provider_uses_issuer_subject_never_email_and_explicit_binding(runtime_env):
    from dwy_auth.providers import ExternalIdentity

    runtime, _, _, _, mailbox, _ = runtime_env

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity(
                issuer="https://id.example.com", subject=credential, email="person@example.com"
            )

    runtime.providers["oidc"] = Provider()
    existing = await register(runtime, mailbox)
    external = await runtime.authenticate("oidc", credential="external-a")
    assert external.subject != existing.subject
    assert (await runtime.authenticate("oidc", credential="external-a")).subject == external.subject
    principal = type("Principal", (), {"app_id": "alpha", "subject": existing.subject})()
    reauth = await runtime.authenticate(
        "email", identifier="person@example.com", password=PASSWORD, purpose="bind"
    )
    await runtime.bind_external(principal, "oidc", "external-b", reauthentication=reauth)
    assert (await runtime.authenticate("oidc", credential="external-b")).subject == existing.subject
    with pytest.raises(AuthError):
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="bind"
        )
        await runtime.bind_external(principal, "oidc", "external-a", reauthentication=proof)


async def test_password_change_requires_old_password_and_last_credential_protected(runtime_env):
    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal = type("Principal", (), {"app_id": "alpha", "subject": identity.subject})()
    with pytest.raises(AuthError):
        await runtime.change_password(principal, "incorrect password", REPLACEMENT)
    await runtime.change_password(principal, PASSWORD, REPLACEMENT)
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    proof = await runtime.authenticate(
        "email", identifier="person@example.com", password=REPLACEMENT, purpose="unlink"
    )
    with pytest.raises(AuthError) as final:
        await runtime.unlink_identity(principal, "email", "person@example.com", reauthentication=proof)
    assert final.value.code == "LAST_CREDENTIAL"
    await runtime.bind_username(principal, "second.login", REPLACEMENT)
    await runtime.unlink_identity(principal, "email", "person@example.com", reauthentication=proof)
    assert (
        await runtime.authenticate("username", identifier="second.login", password=REPLACEMENT)
    ).subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=REPLACEMENT)


async def test_login_proof_is_short_lived_one_use_and_password_change_invalidates_it(runtime_env):
    from dataclasses import replace

    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal = type("Principal", (), {"app_id": "alpha", "subject": identity.subject})()
    proof = await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    await runtime.change_password(principal, PASSWORD, REPLACEMENT)
    with pytest.raises(AuthError):
        await runtime.issue(proof)
    fresh = await runtime.authenticate("email", identifier="person@example.com", password=REPLACEMENT)
    with pytest.raises(AuthError):
        await runtime.issue(replace(fresh, authenticated_at=0))
    with pytest.raises(AuthError):
        await runtime.issue(replace(fresh, subject="another subject"))
    tokens = await runtime.issue(fresh)
    assert tokens.principal.subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.issue(fresh)


async def test_external_binding_requires_scoped_single_use_reauthentication(runtime_env):
    from dwy_auth.providers import ExternalIdentity

    runtime, _, _, _, _, _ = runtime_env

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity("https://id.example.com", credential)

    runtime.providers["oidc"] = Provider()
    first = await runtime.authenticate("oidc", credential="first")
    principal = type("Principal", (), {"app_id": "alpha", "subject": first.subject})()
    wrong_purpose = await runtime.authenticate("oidc", credential="first")
    with pytest.raises(AuthError):
        await runtime.bind_external(principal, "oidc", "second", reauthentication=wrong_purpose)
    proof = await runtime.authenticate("oidc", credential="first", purpose="bind")
    await runtime.bind_external(principal, "oidc", "second", reauthentication=proof)
    with pytest.raises(AuthError):
        await runtime.bind_external(principal, "oidc", "third", reauthentication=proof)
    unlink = await runtime.authenticate("oidc", credential="second", purpose="unlink")
    await runtime.unlink_identity(
        principal, "oidc", "first", issuer="https://id.example.com", reauthentication=unlink
    )
    final = await runtime.authenticate("oidc", credential="second", purpose="unlink")
    with pytest.raises(AuthError) as error:
        await runtime.unlink_identity(
            principal, "oidc", "second", issuer="https://id.example.com", reauthentication=final
        )
    assert error.value.code == "LAST_CREDENTIAL"


async def test_reset_backend_failure_rolls_back_password_and_challenge(runtime_env):
    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    challenge = await runtime.send_email_code("person@example.com", "password_reset")

    class FailingSessions:
        async def revoke_subject(self, subject, *, db):
            raise RuntimeError("session store failed")

    runtime.session_backend = FailingSessions()
    with pytest.raises(RuntimeError):
        await runtime.reset_password(
            "person@example.com", REPLACEMENT, mailbox.messages[-1][1], challenge.challenge_id
        )
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.consumed_at).where(
                    tables.email_challenges.c.id == str(challenge.challenge_id)
                )
            )
            is None
        )
    assert (
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    ).subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=REPLACEMENT)


async def test_provider_configuration_and_issuer_both_scope_external_identity(runtime_env):
    from dwy_auth.providers import ExternalIdentity

    runtime, _, _, _, _, _ = runtime_env

    class Provider:
        def __init__(self, issuer):
            self.issuer = issuer

        async def verify(self, credential):
            return ExternalIdentity(self.issuer, "same-external-subject")

    runtime.providers["tenant_a"] = Provider("https://tenant-a.example.com")
    runtime.providers["tenant_b"] = Provider("https://tenant-a.example.com")
    first = await runtime.authenticate("tenant_a", credential="valid")
    second = await runtime.authenticate("tenant_b", credential="valid")
    runtime.providers["tenant_a"] = Provider("https://tenant-c.example.com")
    third = await runtime.authenticate("tenant_a", credential="valid")
    assert len({first.subject, second.subject, third.subject}) == 3


@pytest.mark.parametrize(
    "method,fields",
    [
        ("email", {"identifier": "x" * 321, "password": PASSWORD}),
        ("email", {"identifier": "person@example.com", "password": "密" * 25}),
        ("username", {"identifier": "x" * 65, "password": PASSWORD}),
        ("email", {"identifier": "person@example.com", "password": PASSWORD, "remote_key": "x" * 256}),
    ],
)
async def test_runtime_input_boundaries(runtime_env, method, fields):
    runtime, _, _, _, _, _ = runtime_env
    with pytest.raises(AuthError) as error:
        await runtime.authenticate(method, **fields)
    assert error.value.status_code == 422


async def test_google_adapter_reuses_existing_verified_identity(runtime_env):
    from test_auth import VerifiedGoogle

    from dwy_auth.providers import GoogleIdentityProvider

    runtime, _, _, _, _, _ = runtime_env
    runtime.providers["google"] = GoogleIdentityProvider(VerifiedGoogle())
    first = await runtime.authenticate("google", credential="a")
    second = await runtime.authenticate("google", credential="b")
    assert first.subject != second.subject
    assert (await runtime.authenticate("google", credential="a")).subject == first.subject
    with pytest.raises(AuthError):
        await runtime.authenticate("google", credential="unverified")


async def test_authentication_proofs_expire_and_outstanding_budget_is_bounded(runtime_env):
    import time

    from dwy_auth.providers import ExternalIdentity

    runtime, tables, sessions, _, _, _ = runtime_env

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity("https://id.example.com", "one-subject")

    runtime.providers["oidc"] = Provider()
    for _ in range(32):
        proof = await runtime.authenticate("oidc", credential="valid")
    with pytest.raises(AuthError) as limited:
        await runtime.authenticate("oidc", credential="valid")
    assert limited.value.status_code == 429
    async with sessions() as db, db.begin():
        await db.execute(update(tables.authentication_proofs).values(expires_at=int(time.time()) - 1))
    with pytest.raises(AuthError):
        await runtime.issue(proof)
    assert (await runtime.authenticate("oidc", credential="valid")).subject == proof.subject
    async with sessions() as db:
        assert len((await db.execute(select(tables.authentication_proofs))).all()) == 1


async def test_issue_failure_rolls_back_one_time_proof(runtime_env):
    runtime, _, _, _, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)

    class Unavailable:
        async def issue(self, identity, *, device_id, db):
            raise RuntimeError("application token creation failed")

    runtime.session_backend = Unavailable()
    with pytest.raises(RuntimeError):
        await runtime.issue(identity)
    runtime.session_backend = backend
    assert (await runtime.issue(identity)).principal.subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.issue(identity)


@pytest.mark.parametrize("name", ["email", "username", "external"])
async def test_provider_configuration_rejects_reserved_method_names(runtime_env, name):
    from dwy_auth.runtime import AuthRuntime

    runtime, tables, sessions, subjects, mailbox, backend = runtime_env
    with pytest.raises(ValueError):
        AuthRuntime(
            "other",
            sessions,
            tables,
            subjects,
            session_backend=backend,
            email_sender=mailbox,
            email_config=runtime.email_config,
            providers={name: object()},
        )


async def test_delete_account_cleanup_failure_rolls_back_every_authentication_record(runtime_env):
    from sqlalchemy import delete

    runtime, tables, sessions, subjects, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)
    principal = type("Principal", (), {"app_id": "alpha", "subject": identity.subject})()

    async def failing_cleanup(db, subject):
        await db.execute(delete(subjects.table).where(subjects.table.c.customer_key == subject))
        raise RuntimeError("business cleanup failed")

    with pytest.raises(RuntimeError):
        await runtime.delete_account(principal, cleanup=failing_cleanup)
    async with sessions() as db:
        assert await subjects.is_active(db, identity.subject)
        assert await db.scalar(select(tables.password_credentials.c.subject)) == identity.subject
        assert await db.scalar(select(tables.identifiers.c.subject)) == identity.subject
        assert await db.scalar(select(tables.authentication_proofs.c.subject)) == identity.subject
        assert (await db.execute(select(backend.table))).all() == []

    async def cleanup(db, subject):
        await db.execute(delete(subjects.table).where(subjects.table.c.customer_key == subject))

    await runtime.delete_account(principal, cleanup=cleanup)
    async with sessions() as db:
        assert not await subjects.is_active(db, identity.subject)
        assert (await db.execute(select(tables.identifiers))).all() == []
        assert (await db.execute(select(tables.password_credentials))).all() == []
        assert (await db.execute(select(tables.authentication_proofs))).all() == []
        assert await db.scalar(select(backend.table.c.subject)) == identity.subject
    with pytest.raises(AuthError):
        await runtime.issue(identity)


def test_table_prefix_cannot_exceed_postgres_identifier_budget():
    from sqlalchemy.dialects.postgresql import dialect

    from dwy_auth.runtime_storage import build_runtime_tables

    metadata = MetaData()
    build_runtime_tables(metadata, prefix="a" * 40)
    for table in metadata.tables.values():
        dialect().validate_identifier(table.name)
    with pytest.raises(ValueError):
        build_runtime_tables(MetaData(), prefix="a" * 43)
