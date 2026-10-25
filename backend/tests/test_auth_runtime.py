"""EAPI 认证集成以真实 SQLite/HTTP 验证, 应用资料和权限由宿主提供。"""

from contextlib import asynccontextmanager
from typing import Annotated
from uuid import uuid4

import httpx
import pytest
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import Boolean, Column, MetaData, String, Table, insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

PASSWORD = "correct horse battery staple"


@asynccontextmanager
async def environment(
    tmp_path, *, app_id="adbox", session_backend_factory=None, providers=None, authorization_limit=8192
):
    from dwy_auth.email_auth import EmailAuthConfig
    from dwy_auth.runtime import AuthRuntime
    from dwy_auth.runtime_storage import build_runtime_tables
    from dwy_auth.session_backend import JWTSessionBackend
    from dwy_auth.session_storage import register_session_tables

    from dwyeapi.auth import install_runtime_auth

    metadata = MetaData()
    users = Table(
        "business_people",
        metadata,
        Column("key", String(36), primary_key=True),
        Column("mailbox", String(254)),
        Column("active", Boolean, nullable=False),
    )
    auth_tables = build_runtime_tables(metadata)
    session_tables = register_session_tables(metadata)
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path}/{app_id}.db")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = async_sessionmaker(engine, expire_on_commit=False)

    class Subjects:
        async def create_subject(self, db, registration):
            subject = str(uuid4())
            await db.execute(insert(users).values(key=subject, mailbox=registration.email, active=True))
            return subject

        async def is_active(self, db, subject):
            return bool(await db.scalar(select(users.c.active).where(users.c.key == subject)))

    class Mailbox:
        def __init__(self):
            self.messages = []
            self.succeed = True
            self.languages = []

        async def send(self, email, code, purpose, *, language="en"):
            self.messages.append((email, code, purpose))
            self.languages.append(language)
            return self.succeed

    mailbox = Mailbox()
    backend = (
        session_backend_factory(app_id)
        if session_backend_factory is not None
        else JWTSessionBackend(
            app_id, "https://issuer.test", app_id, "integration-test-secret-" * 3, sessions, session_tables
        )
    )
    runtime = AuthRuntime(
        app_id,
        sessions,
        auth_tables,
        Subjects(),
        session_backend=backend,
        email_sender=mailbox,
        email_config=EmailAuthConfig(challenge_secret="challenge-test-secret-" * 3),
        providers=providers,
    )
    app = FastAPI()

    async def profile(principal):
        async with sessions() as db:
            email = await db.scalar(select(users.c.mailbox).where(users.c.key == principal.subject))
        return {"id": principal.subject, "email": email, "display_name": "Application profile"}

    binding = install_runtime_auth(app, runtime, profile_loader=profile, authorization_limit=authorization_limit)
    from dwy_auth.contracts import AuthPrincipal

    optional_principal = Annotated[AuthPrincipal | None, Depends(binding.optional_principal)]
    required_principal = Annotated[AuthPrincipal, Depends(binding.require_principal)]

    @app.get("/public")
    async def public():
        return {"public": True}

    @app.get("/optional")
    async def optional(principal: optional_principal):
        return {"subject": principal.subject if principal else None}

    @app.get("/private")
    async def private(principal: required_principal):
        return {"subject": principal.subject}

    @app.get("/app-admin")
    async def app_admin(principal: required_principal):
        raise HTTPException(403, "Application permission denied")

    try:
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://auth.test") as client:
            yield client, mailbox, runtime
    finally:
        await runtime.aclose()
        await engine.dispose()


async def register(client, mailbox):
    response = await client.post("/api/v1/auth/email/code", json={"email": "person@example.com", "purpose": "register"})
    assert response.status_code == 200
    challenge = response.json()["data"]
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "person@example.com",
            "password": PASSWORD,
            "code": mailbox.messages[-1][1],
            "challenge_id": challenge["challenge_id"],
            "device_id": str(uuid4()),
        },
    )
    assert response.status_code == 200
    return response.json()["data"]


@pytest.mark.parametrize(
    "header,language",
    [
        (None, "en"),
        ("zh", "zh"),
        ("ZH-Hans-CN", "zh"),
        ("en", "en"),
        ("ja-JP", "en"),
        ("en,zh-TW;q=0.5", "zh"),
        ("zh;q=0", "en"),
    ],
)
async def test_runtime_http_email_language_reaches_sender(tmp_path, header, language):
    """通用运行时必须穿过覆盖方法把请求语言送到发件通道。"""
    async with environment(tmp_path) as (client, mailbox, _):
        response = await client.post(
            "/api/v1/auth/email/code",
            headers={} if header is None else {"Accept-Language": header},
            json={"email": "person@example.com", "purpose": "register"},
        )
        assert response.status_code == 200
        assert mailbox.languages == [language]


async def test_runtime_http_email_language_header_is_bounded(tmp_path):
    """过长语言头在发码之前拒绝, 不消耗邮件发送预算。"""
    async with environment(tmp_path) as (client, mailbox, _):
        response = await client.post(
            "/api/v1/auth/email/code",
            headers={"Accept-Language": "z" * 513},
            json={"email": "person@example.com", "purpose": "register"},
        )
        assert response.status_code == 422
        assert mailbox.messages == []


@pytest.mark.parametrize("purpose", ["register", "password_reset"])
@pytest.mark.parametrize("header,language", [(None, "en"), ("zh-CN", "zh"), ("vi-VN", "en")])
async def test_request_language_selects_resend_mail_contents(tmp_path, monkeypatch, purpose, header, language):
    """真实 HTTP、运行时和通道适配器一起决定主题、HTML 与纯文本语言。"""
    from unittest.mock import AsyncMock

    from dwy_auth.email_auth import EapiEmailCodeSender

    from dwyeapi.providers.email.resend import ResendEmailProvider

    provider = ResendEmailProvider(
        api_key="test-not-used", from_email="sender@example.com", require_common_domain=False
    )
    delivery = AsyncMock(return_value={"id": "language-test"})
    monkeypatch.setattr(provider._resend.Emails, "send_async", delivery)
    async with environment(tmp_path) as (client, _, runtime):
        runtime.email_sender = EapiEmailCodeSender(provider)
        response = await client.post(
            "/api/v1/auth/email/code",
            headers={} if header is None else {"Accept-Language": header},
            json={"email": "person@example.com", "purpose": purpose},
        )
        assert response.status_code == 200
    delivery.assert_awaited_once()
    payload = delivery.await_args.args[0]
    if language == "zh":
        assert payload["subject"] == "验证码"
        assert 'lang="zh-CN"' in payload["html"]
        assert "您的验证码" in payload["text"]
    else:
        assert payload["subject"] == "Verification code"
        assert 'lang="en"' in payload["html"]
        assert "verification code" in payload["text"].lower()
        assert not any("\u4e00" <= char <= "\u9fff" for char in payload["html"] + payload["text"])


async def test_changing_email_language_cannot_bypass_resend_cooldown(tmp_path):
    """同邮箱切换语言仍共享发送冷却, 不能增加验证码发送预算。"""
    async with environment(tmp_path) as (client, mailbox, _):
        body = {"email": "person@example.com", "purpose": "register"}
        assert (await client.post("/api/v1/auth/email/code", json=body)).status_code == 200
        repeated = await client.post("/api/v1/auth/email/code", headers={"Accept-Language": "zh"}, json=body)
        assert repeated.status_code == 429
        assert len(mailbox.messages) == 1


async def test_runtime_http_register_login_profile_refresh_and_logout(tmp_path):
    async with environment(tmp_path) as (client, mailbox, _):
        first = await register(client, mailbox)
        assert first["user"]["email"] == "person@example.com"
        assert first["user"]["display_name"] == "Application profile"
        assert first["access_token"].count(".") == 2
        assert first["expires_in"] == 900
        headers = {"Authorization": "Bearer " + first["access_token"]}
        assert (await client.get("/private", headers=headers)).json()["subject"] == first["user"]["id"]
        login = await client.post("/api/v1/auth/login", json={"email": "person@example.com", "password": PASSWORD})
        assert login.status_code == 200
        refreshed = await client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
        assert refreshed.status_code == 200
        current = refreshed.json()["data"]
        headers = {"Authorization": "Bearer " + current["access_token"]}
        assert (await client.post("/api/v1/auth/logout", headers=headers)).status_code == 200
        assert (await client.get("/private", headers=headers)).status_code == 401


async def test_public_optional_identity_and_application_permissions_remain_separate(tmp_path):
    async with environment(tmp_path) as (client, mailbox, _):
        assert (await client.get("/public")).status_code == 200
        assert (await client.get("/optional")).json() == {"subject": None}
        assert (await client.get("/private")).status_code == 401
        forged = {"Authorization": "Bearer invalid"}
        assert (await client.get("/optional", headers=forged)).status_code == 401
        first = await register(client, mailbox)
        headers = {"Authorization": "Bearer " + first["access_token"]}
        assert (await client.get("/optional", headers=headers)).json()["subject"] == first["user"]["id"]
        assert (await client.get("/app-admin", headers=headers)).status_code == 403


async def test_reset_revokes_old_session_and_validation_never_echoes_credentials(tmp_path):
    async with environment(tmp_path) as (client, mailbox, _):
        first = await register(client, mailbox)
        challenge = await client.post(
            "/api/v1/auth/email/code", json={"email": "person@example.com", "purpose": "password_reset"}
        )
        reset = await client.post(
            "/api/v1/auth/password/reset",
            json={
                "email": "person@example.com",
                "password": "replacement password is strong",
                "code": mailbox.messages[-1][1],
                "challenge_id": challenge.json()["data"]["challenge_id"],
            },
        )
        assert reset.status_code == 200 and reset.json()["data"] == {"status": "completed"}
        headers = {"Authorization": "Bearer " + first["access_token"]}
        assert (await client.get("/private", headers=headers)).status_code == 401
        response = await client.post(
            "/api/v1/auth/login",
            json={"email": "person@example.com", "password": PASSWORD, "device_id": "sensitive-value"},
        )
        assert response.status_code == 422
        assert PASSWORD not in response.text and "sensitive-value" not in response.text
        oversized = await client.post(
            "/api/v1/auth/login", content=b"x" * 32769, headers={"Content-Type": "application/json"}
        )
        assert oversized.status_code == 413


async def test_failed_delivery_does_not_report_success_and_disabled_google_stays_closed(tmp_path):
    async with environment(tmp_path) as (client, mailbox, _):
        mailbox.succeed = False
        failure = await client.post(
            "/api/v1/auth/email/code", json={"email": "failed@example.com", "purpose": "register"}
        )
        assert failure.status_code == 503
        assert failure.json()["code"] == "EMAIL_DELIVERY_FAILED"
        google = await client.post("/api/v1/auth/google", json={"id_token": "not-configured"})
        assert google.status_code == 503 and google.json()["code"] == "GOOGLE_NOT_CONFIGURED"
        capabilities = await client.get("/api/v1/auth/capabilities")
        assert capabilities.status_code == 200
        assert capabilities.json()["data"]["providers"] == []


async def test_registered_google_and_generic_external_login_share_application_subject(tmp_path):
    from dwy_auth import GoogleIdentity
    from dwy_auth.providers import GoogleIdentityProvider

    class VerifiedGoogle:
        async def verify(self, token):
            assert token == "verified-google-token"
            return GoogleIdentity(subject="google-account-42", email="person@example.com", display_name="Google")

    async with environment(tmp_path, providers={"google": GoogleIdentityProvider(VerifiedGoogle())}) as (client, _, _):
        first = await client.post("/api/v1/auth/google", json={"id_token": "verified-google-token"})
        assert first.status_code == 200
        second = await client.post(
            "/api/v1/auth/external/login", json={"provider": "google", "credential": "verified-google-token"}
        )
        assert second.status_code == 200
        assert first.json()["data"]["user"]["id"] == second.json()["data"]["user"]["id"]


async def test_username_password_change_and_external_binding_require_current_credentials(tmp_path):
    from dwy_auth import GoogleIdentity
    from dwy_auth.providers import GoogleIdentityProvider

    class VerifiedGoogle:
        async def verify(self, token):
            assert token == "verified-google-token"
            return GoogleIdentity(subject="google-account-42", email="person@example.com", display_name="Google")

    async with environment(tmp_path, providers={"google": GoogleIdentityProvider(VerifiedGoogle())}) as (
        client,
        mailbox,
        runtime,
    ):
        first = await register(client, mailbox)
        headers = {"Authorization": "Bearer " + first["access_token"]}
        bound = await client.post(
            "/api/v1/auth/username/bind", headers=headers, json={"username": "person_42", "password": PASSWORD}
        )
        assert bound.status_code == 200
        username = await client.post(
            "/api/v1/auth/username/login", json={"username": "person_42", "password": PASSWORD}
        )
        assert username.status_code == 200
        assert username.json()["data"]["user"]["id"] == first["user"]["id"]
        reauthentication = {"method": "email", "identifier": "person@example.com", "password": PASSWORD}
        # Spy only records the boundary rate-limit key; real authentication and DB operations still run.
        original_authenticate = runtime.authenticate
        remote_keys = []

        async def record_authentication(*args, **kwargs):
            remote_keys.append(kwargs.get("remote_key"))
            return await original_authenticate(*args, **kwargs)

        runtime.authenticate = record_authentication
        linked = await client.post(
            "/api/v1/auth/external/bind",
            headers=headers,
            json={"provider": "google", "credential": "verified-google-token", "reauthentication": reauthentication},
        )
        assert linked.status_code == 200 and remote_keys[-1] == "127.0.0.1"
        external = await client.post("/api/v1/auth/google", json={"id_token": "verified-google-token"})
        assert external.status_code == 200
        assert external.json()["data"]["user"]["id"] == first["user"]["id"]
        unlinked = await client.post(
            "/api/v1/auth/identity/unlink",
            headers=headers,
            json={
                "kind": "external",
                "provider": "google",
                "issuer": "https://accounts.google.com",
                "value": "google-account-42",
                "reauthentication": reauthentication,
            },
        )
        assert unlinked.status_code == 200 and remote_keys[-1] == "127.0.0.1"
        changed = await client.post(
            "/api/v1/auth/password/change",
            headers=headers,
            json={"old_password": PASSWORD, "new_password": "a different strong password"},
        )
        assert changed.status_code == 200
        assert (await client.get("/private", headers=headers)).status_code == 401
        old = await client.post("/api/v1/auth/username/login", json={"username": "person_42", "password": PASSWORD})
        assert old.status_code == 401
        new = await client.post(
            "/api/v1/auth/username/login", json={"username": "person_42", "password": "a different strong password"}
        )
        assert new.status_code == 200


async def test_application_can_replace_jwt_with_complete_opaque_session_backend(tmp_path):
    from dwy_auth.contracts import AuthPrincipal, SessionTokens
    from dwy_auth.models import AuthError

    class ApplicationSessions:
        """Small host-owned session store proves the HTTP integration never parses JWT itself."""

        def __init__(self, app_id):
            self.app_id, self.tokens, self.refreshes = app_id, {}, {}

        async def issue(self, identity, *, device_id, db):
            principal = AuthPrincipal(self.app_id, identity.subject, uuid4(), identity.method, device_id)
            return self._tokens(principal)

        def _tokens(self, principal):
            access, refresh = "host_" + uuid4().hex, "renew_" + uuid4().hex
            self.tokens[access], self.refreshes[refresh] = principal, principal
            return SessionTokens(access, refresh, 60, principal)

        async def verify(self, token):
            if token not in self.tokens:
                raise AuthError("SESSION_INVALID", "认证失败", 401)
            return self.tokens[token]

        async def refresh(self, refresh_token):
            principal = self.refreshes.pop(refresh_token)
            await self.revoke(principal)
            return self._tokens(principal)

        async def revoke(self, principal):
            self.tokens = {key: value for key, value in self.tokens.items() if value.session_id != principal.session_id}
            self.refreshes = {
                key: value for key, value in self.refreshes.items() if value.session_id != principal.session_id
            }

        async def revoke_subject(self, subject, *, db):
            self.tokens = {key: value for key, value in self.tokens.items() if value.subject != subject}
            self.refreshes = {key: value for key, value in self.refreshes.items() if value.subject != subject}

    async with environment(tmp_path, session_backend_factory=ApplicationSessions) as (client, mailbox, _):
        first = await register(client, mailbox)
        assert first["access_token"].startswith("host_") and "." not in first["access_token"]
        headers = {"Authorization": "Bearer " + first["access_token"]}
        assert (await client.get("/private", headers=headers)).status_code == 200
        refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": first["refresh_token"]})
        assert refresh.status_code == 200
        assert (await client.get("/private", headers=headers)).status_code == 401
        headers = {"Authorization": "Bearer " + refresh.json()["data"]["access_token"]}
        assert (await client.post("/api/v1/auth/logout", headers=headers)).status_code == 200
        assert (await client.get("/private", headers=headers)).status_code == 401


async def test_host_authorization_limit_applies_to_auth_and_business_dependencies(tmp_path):
    async with environment(tmp_path, authorization_limit=64) as (client, mailbox, _):
        first = await register(client, mailbox)
        headers = {"Authorization": "Bearer " + first["access_token"]}
        assert len(headers["Authorization"]) > 64
        assert (await client.get("/private", headers=headers)).status_code == 401
        assert (await client.get("/optional", headers=headers)).status_code == 401
        assert (await client.post("/api/v1/auth/logout", headers=headers)).status_code == 401
