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

    async def update_email(self, db, subject, email):
        await db.execute(update(self.table).where(self.table.c.customer_key == subject).values(email=email))

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
        Column("email", String),
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


async def email_update(runtime, mailbox, identity, email="updated@example.com"):
    """使用真实短期证明，避免测试绕过重新认证边界。"""
    from dwy_auth.contracts import AuthPrincipal

    principal = AuthPrincipal("alpha", identity.subject, uuid4(), identity.method, uuid4())
    if identity.method == "email":
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="email_update"
        )
    else:
        proof = await runtime.authenticate("google", credential="google-sub", purpose="email_update")
    challenge = await runtime.send_email_update_code(principal, email, reauthentication=proof)
    return principal, challenge, mailbox.messages[-1][1]


async def test_email_update_keeps_subject_replaces_login_and_rotates_session(runtime_env):
    runtime, tables, sessions, subjects, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    assert mailbox.messages[-1][2] == "email_update"
    tokens = await runtime.update_email(principal, "UPDATED@example.com", code, challenge.challenge_id)
    assert tokens.principal.subject == identity.subject
    assert tokens.principal.device_id == principal.device_id
    assert (
        await runtime.authenticate("email", identifier="updated@example.com", password=PASSWORD)
    ).subject == identity.subject
    with pytest.raises(AuthError):
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    with pytest.raises(AuthError):
        await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    async with sessions() as db:
        assert await db.scalar(select(subjects.table.c.email)) == "updated@example.com"
        assert await db.scalar(select(backend.table.c.subject)) == identity.subject


async def test_google_adds_email_password_without_changing_external_identity(runtime_env):
    from dwy_auth.providers import ExternalIdentity

    runtime, tables, sessions, subjects, mailbox, _ = runtime_env

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity("https://accounts.google.com", credential, "provider@example.com")

    runtime.providers["google"] = Provider()
    identity = await runtime.authenticate("google", credential="google-sub")
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    with pytest.raises(AuthError) as missing:
        await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    assert missing.value.code == "PASSWORD_REQUIRED"
    tokens = await runtime.update_email(
        principal, "updated@example.com", code, challenge.challenge_id, new_password=PASSWORD
    )
    assert tokens.principal.subject == identity.subject
    assert (
        await runtime.authenticate("email", identifier="updated@example.com", password=PASSWORD)
    ).subject == identity.subject
    assert (await runtime.authenticate("google", credential="google-sub")).subject == identity.subject
    async with sessions() as db:
        external = (await db.execute(select(tables.external_identities))).mappings().one()
        assert external["external_subject"] == "google-sub"
        assert await db.scalar(select(subjects.table.c.email)) == "updated@example.com"


@pytest.mark.parametrize("mismatch", ["subject", "email", "purpose", "expired", "credential"])
async def test_email_update_challenge_rejects_mismatch_and_stale_credentials(runtime_env, mismatch):
    import time
    from dataclasses import replace

    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    target = "updated@example.com"
    if mismatch == "subject":
        other = await register(runtime, mailbox, "other@example.com")
        principal = replace(principal, subject=other.subject)
    if mismatch == "email":
        target = "wrong@example.com"
    if mismatch in {"purpose", "expired"}:
        async with sessions() as db, db.begin():
            values = (
                {"purpose": "register"} if mismatch == "purpose" else {"expires_at": int(time.time()) - 1}
            )
            await db.execute(
                update(tables.email_challenges)
                .where(tables.email_challenges.c.id == str(challenge.challenge_id))
                .values(**values)
            )
    if mismatch == "credential":
        await runtime.change_password(principal, PASSWORD, REPLACEMENT)
    with pytest.raises(AuthError):
        await runtime.update_email(principal, target, code, challenge.challenge_id)
    assert (
        await runtime.authenticate(
            "email",
            identifier="person@example.com",
            password=REPLACEMENT if mismatch == "credential" else PASSWORD,
        )
    ).subject == identity.subject


async def test_email_update_conflict_and_backend_failure_roll_back_challenge(runtime_env):
    runtime, tables, sessions, _, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    await register(runtime, mailbox, "updated@example.com")
    with pytest.raises(AuthError) as conflict:
        await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    assert conflict.value.code == "IDENTITY_ALREADY_BOUND"
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.consumed_at).where(
                    tables.email_challenges.c.id == str(challenge.challenge_id)
                )
            )
            is None
        )


async def test_email_update_reauth_is_subject_bound_expiring_and_single_use(runtime_env):
    from dataclasses import replace

    from dwy_auth.contracts import AuthPrincipal

    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    other = await register(runtime, mailbox, "other@example.com")
    principal = AuthPrincipal("alpha", other.subject, uuid4(), "email", uuid4())
    proof = await runtime.authenticate(
        "email", identifier="person@example.com", password=PASSWORD, purpose="email_update"
    )
    with pytest.raises(AuthError):
        await runtime.send_email_update_code(principal, "updated@example.com", reauthentication=proof)
    principal = replace(principal, subject=identity.subject)
    await runtime.send_email_update_code(principal, "updated@example.com", reauthentication=proof)
    with pytest.raises(AuthError):
        await runtime.send_email_update_code(principal, "another@example.com", reauthentication=proof)
    with pytest.raises(AuthError):
        await runtime.send_email_code("unprotected@example.com", "email_update")


async def test_email_update_session_failure_rolls_back_entire_change(runtime_env):
    runtime, tables, sessions, _, mailbox, backend = runtime_env
    identity = await register(runtime, mailbox)
    principal, challenge, code = await email_update(runtime, mailbox, identity)

    class FailedBackend:
        async def revoke_subject(self, subject, *, db):
            await backend.revoke_subject(subject, db=db)

        async def issue(self, identity, *, device_id, db):
            raise RuntimeError("session issue failed")

    runtime.session_backend = FailedBackend()
    with pytest.raises(RuntimeError):
        await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.consumed_at).where(
                    tables.email_challenges.c.id == str(challenge.challenge_id)
                )
            )
            is None
        )
        assert (await db.execute(select(backend.table))).all() == []
    runtime.session_backend = backend
    assert (
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    ).subject == identity.subject
    assert (
        await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    ).principal.subject == identity.subject


async def test_email_update_concurrent_consumption_has_one_winner(runtime_env):
    import asyncio

    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    results = await asyncio.gather(
        *[
            runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
            for _ in range(2)
        ],
        return_exceptions=True,
    )
    assert sum(not isinstance(result, BaseException) for result in results) == 1
    assert sum(isinstance(result, AuthError) for result in results) == 1


async def test_email_update_reauthentication_expiry_and_wrong_purpose_do_not_send(runtime_env):
    import time

    from dwy_auth.contracts import AuthPrincipal

    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal = AuthPrincipal("alpha", identity.subject, uuid4(), "email", uuid4())
    login = await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    with pytest.raises(AuthError):
        await runtime.send_email_update_code(principal, "updated@example.com", reauthentication=login)
    proof = await runtime.authenticate(
        "email", identifier="person@example.com", password=PASSWORD, purpose="email_update"
    )
    async with sessions() as db, db.begin():
        await db.execute(update(tables.authentication_proofs).values(expires_at=int(time.time()) - 1))
    with pytest.raises(AuthError):
        await runtime.send_email_update_code(principal, "updated@example.com", reauthentication=proof)
    assert len(mailbox.messages) == 1


async def test_identity_listing_is_scoped_and_excludes_disabled_or_secret_data(runtime_env):
    from dwy_auth.contracts import AuthPrincipal
    from dwy_auth.providers import ExternalIdentity

    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    other = await register(runtime, mailbox, "other@example.com")
    principal = AuthPrincipal("alpha", identity.subject, uuid4(), "email", uuid4())

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity("https://accounts.google.com", credential)

    runtime.providers["google"] = Provider()
    proof = await runtime.authenticate(
        "email", identifier="person@example.com", password=PASSWORD, purpose="bind"
    )
    await runtime.bind_external(principal, "google", "provider-sub", reauthentication=proof)
    identities = await runtime.list_identities(principal)
    assert [(row.kind, row.value) for row in identities] == [
        ("email", "person@example.com"),
        ("external", "provider-sub"),
    ]
    assert identities[1].provider == "google"
    runtime.methods = frozenset({"external"})
    assert [row.kind for row in await runtime.list_identities(principal)] == ["external"]
    assert all("password" not in repr(row) and other.subject not in repr(row) for row in identities)


@pytest.mark.parametrize("mutation", ["email", "password", "reset", "username", "external", "unlink"])
async def test_credential_mutations_permanently_invalidate_outstanding_email_updates(runtime_env, mutation):
    """凭据状态恢复成旧值也不能复活旧挑战，失效必须持久化。"""
    from dwy_auth.providers import ExternalIdentity

    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)

    class Provider:
        async def verify(self, credential):
            return ExternalIdentity("https://accounts.google.com", credential)

    runtime.providers["google"] = Provider()
    if mutation == "unlink":
        from dwy_auth.contracts import AuthPrincipal

        principal = AuthPrincipal("alpha", identity.subject, uuid4(), "email", uuid4())
        await runtime.bind_username(principal, "second.login", PASSWORD)
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    if mutation == "email":
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="email_update"
        )
        other = await runtime.send_email_update_code(principal, "second@example.com", reauthentication=proof)
        await runtime.update_email(
            principal, "second@example.com", mailbox.messages[-1][1], other.challenge_id
        )
    if mutation == "password":
        await runtime.change_password(principal, PASSWORD, REPLACEMENT)
    if mutation == "reset":
        reset = await runtime.send_email_code("person@example.com", "password_reset")
        await runtime.reset_password(
            "person@example.com", REPLACEMENT, mailbox.messages[-1][1], reset.challenge_id
        )
    if mutation == "username":
        await runtime.bind_username(principal, "second.login", PASSWORD)
    if mutation == "external":
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="bind"
        )
        await runtime.bind_external(principal, "google", "google-sub", reauthentication=proof)
    if mutation == "unlink":
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="unlink"
        )
        await runtime.unlink_identity(principal, "username", "second.login", reauthentication=proof)
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.consumed_at).where(
                    tables.email_challenges.c.id == str(challenge.challenge_id)
                )
            )
            is not None
        )


async def test_inflight_email_update_cannot_revive_after_credentials_restore(runtime_env):
    """发码插入前发生绑定再解绑，内容恢复但代次已变化，旧请求仍须拒绝。"""
    from dwy_auth.contracts import AuthPrincipal

    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    principal = AuthPrincipal("alpha", identity.subject, uuid4(), "email", uuid4())
    send = runtime._send_email_code

    async def delayed_send(*args, **kwargs):
        await runtime.bind_username(principal, "temporary.login", PASSWORD)
        proof = await runtime.authenticate(
            "email", identifier="person@example.com", password=PASSWORD, purpose="unlink"
        )
        await runtime.unlink_identity(principal, "username", "temporary.login", reauthentication=proof)
        return await send(*args, **kwargs)

    runtime._send_email_code = delayed_send
    proof = await runtime.authenticate(
        "email", identifier="person@example.com", password=PASSWORD, purpose="email_update"
    )
    challenge = await runtime.send_email_update_code(principal, "updated@example.com", reauthentication=proof)
    with pytest.raises(AuthError) as stale:
        await runtime.update_email(
            principal, "updated@example.com", mailbox.messages[-1][1], challenge.challenge_id
        )
    assert stale.value.code == "EMAIL_CODE_INVALID"


async def test_password_reset_code_is_bound_to_subject_and_credential_generation(runtime_env):
    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    challenge = await runtime.send_email_code("person@example.com", "password_reset")
    async with sessions() as db:
        row = (
            (
                await db.execute(
                    select(tables.email_challenges).where(
                        tables.email_challenges.c.id == str(challenge.challenge_id)
                    )
                )
            )
            .mappings()
            .one()
        )
        assert row["subject"] == identity.subject
        assert row["credential_version"] == await runtime._credential_state(db, identity.subject)


async def test_email_update_invalidates_legacy_unbound_password_reset_code(runtime_env):
    runtime, tables, sessions, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    reset = await runtime.send_email_code("person@example.com", "password_reset")
    async with sessions() as db, db.begin():
        await db.execute(
            update(tables.email_challenges)
            .where(tables.email_challenges.c.id == str(reset.challenge_id))
            .values(subject=None, credential_version=None)
        )
    principal, challenge, code = await email_update(runtime, mailbox, identity)
    await runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
    async with sessions() as db:
        assert (
            await db.scalar(
                select(tables.email_challenges.c.consumed_at).where(
                    tables.email_challenges.c.id == str(reset.challenge_id)
                )
            )
            is not None
        )


async def test_reset_rechecks_email_owner_after_subject_lock(runtime_env):
    """在适配器锁边界模拟映射变化；SQLite 不提供 PostgreSQL 行锁语义。"""
    runtime, tables, _, subjects, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    reset = await runtime.send_email_code("person@example.com", "password_reset")
    code = mailbox.messages[-1][1]
    original = subjects.is_active

    async def changed_at_lock(db, subject):
        await db.execute(
            update(tables.identifiers)
            .where(tables.identifiers.c.subject == subject, tables.identifiers.c.kind == "email")
            .values(value="updated@example.com")
        )
        return await original(db, subject)

    subjects.is_active = changed_at_lock
    with pytest.raises(AuthError) as error:
        await runtime.reset_password("person@example.com", REPLACEMENT, code, reset.challenge_id)
    assert error.value.code == "EMAIL_CODE_INVALID"
    subjects.is_active = original
    assert (
        await runtime.authenticate("email", identifier="person@example.com", password=PASSWORD)
    ).subject == identity.subject


async def test_reset_rejects_changed_generation_even_if_email_is_unchanged(runtime_env):
    runtime, _, _, _, mailbox, _ = runtime_env
    identity = await register(runtime, mailbox)
    reset = await runtime.send_email_code("person@example.com", "password_reset")
    code = mailbox.messages[-1][1]
    from dwy_auth.contracts import AuthPrincipal

    principal = AuthPrincipal("alpha", identity.subject, uuid4(), "email", uuid4())
    await runtime.change_password(principal, PASSWORD, REPLACEMENT)
    with pytest.raises(AuthError):
        await runtime.reset_password("person@example.com", PASSWORD, code, reset.challenge_id)


async def test_postgres_reset_waiting_for_email_update_lock_cannot_revoke_rotated_session():
    """真实 PostgreSQL 事务交错；未配置专用测试数据库时明确跳过。"""
    import asyncio
    import os

    from sqlalchemy.schema import CreateSchema, DropSchema

    from dwy_auth.runtime import AuthRuntime
    from dwy_auth.runtime_storage import build_runtime_tables

    url = os.getenv("APP_CLOUD_TEST_POSTGRES_URL")
    if not url:
        pytest.skip("PostgreSQL URL not configured; lock interleaving not exercised")
    schema = "runtime_reset_" + uuid4().hex
    base = create_async_engine(url)
    engine = base.execution_options(schema_translate_map={None: schema})
    metadata = MetaData()
    tables = build_runtime_tables(metadata)
    customers = Table(
        "customers",
        metadata,
        Column("customer_key", String, primary_key=True),
        Column("allowed", Boolean),
        Column("email", String),
    )
    revoked = Table("revoked", metadata, Column("subject", String))
    update_holds_lock, reset_waiting, release_update = asyncio.Event(), asyncio.Event(), asyncio.Event()

    class LockingSubjects(Subjects):
        armed = False
        calls = 0

        async def is_active(self, db, subject):
            if self.armed:
                self.calls += 1
                if self.calls == 2:
                    reset_waiting.set()
            active = await db.scalar(
                select(self.table.c.allowed).where(self.table.c.customer_key == subject).with_for_update()
            )
            if self.armed and self.calls == 1:
                update_holds_lock.set()
                await asyncio.wait_for(release_update.wait(), 10)
            return active is True

    runtime = None
    try:
        async with base.begin() as db:
            await db.execute(CreateSchema(schema))
        async with engine.begin() as db:
            await db.run_sync(metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        subjects, mailbox = LockingSubjects(customers), Mailbox()
        runtime = AuthRuntime(
            "alpha",
            sessions,
            tables,
            subjects,
            session_backend=ApplicationSessions(revoked),
            email_sender=mailbox,
            email_config=EmailAuthConfig(challenge_secret="test-secret-" * 4),
        )
        identity = await register(runtime, mailbox)
        reset = await runtime.send_email_code("person@example.com", "password_reset")
        reset_code = mailbox.messages[-1][1]
        principal, challenge, code = await email_update(runtime, mailbox, identity)
        subjects.armed = True
        changing = asyncio.create_task(
            runtime.update_email(principal, "updated@example.com", code, challenge.challenge_id)
        )
        await asyncio.wait_for(update_holds_lock.wait(), 10)
        resetting = asyncio.create_task(
            runtime.reset_password("person@example.com", REPLACEMENT, reset_code, reset.challenge_id)
        )
        await asyncio.wait_for(reset_waiting.wait(), 10)
        release_update.set()
        tokens = await changing
        with pytest.raises(AuthError) as rejected:
            await resetting
        assert rejected.value.code == "EMAIL_CODE_INVALID"
        subjects.armed = False
        assert (
            await runtime.authenticate("email", identifier="updated@example.com", password=PASSWORD)
        ).subject == identity.subject
        async with sessions() as db:
            assert len((await db.execute(select(revoked))).all()) == 1
        assert tokens.principal.subject == principal.subject
    finally:
        release_update.set()
        if runtime is not None:
            await runtime.aclose()
        async with base.begin() as db:
            await db.execute(DropSchema(schema, cascade=True, if_exists=True))
        await base.dispose()
