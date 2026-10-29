"""Apple transport 使用真实认证依赖; 这里只隔离 Apple 服务边界。"""

from contextlib import asynccontextmanager
from uuid import uuid4

import httpx
import pytest
from dwy_auth.contracts import AuthPrincipal, SessionTokens
from fastapi import FastAPI

from dwyeapi.auth import install_runtime_auth


@asynccontextmanager
async def environment():
    from dwyeapi.auth_apple import install_apple_auth

    user = str(uuid4())

    class Runtime:
        app_id = "test"

        def __init__(self):
            self.methods = frozenset({"external"})
            self.providers = {"apple": object()}

        async def verify(self, token):
            from dwy_auth.models import AuthError

            if token != "current-session":
                raise AuthError("SESSION_INVALID", "会话无效")
            return AuthPrincipal("test", user, uuid4(), "google", None)

        async def authenticate(self, method, **kwargs):
            from dwy_auth.contracts import VerifiedIdentity

            assert method == "email" and kwargs["purpose"] == "bind"
            return VerifiedIdentity("test", user, "email", purpose="bind")

        async def aclose(self):
            pass

    class Apple:
        runtime = Runtime()

        async def challenge(self, **kwargs):
            self.challenge_args = kwargs
            return {"challenge_id": str(uuid4()), "nonce": "server-nonce", "expires_in": 300}

        async def login(self, challenge_id, identity_token, authorization_code, **kwargs):
            assert identity_token == "apple-id" and authorization_code == "apple-code"
            self.device = kwargs["device_id"]
            self.admission_proof = kwargs["admission_proof"]
            return SessionTokens(
                "app-access",
                "app-refresh",
                900,
                AuthPrincipal("test", user, uuid4(), "apple", kwargs["device_id"]),
            )

        async def bind(self, principal, *args, **kwargs):
            assert principal.subject == user and kwargs["reauthentication"].purpose == "bind"

        async def notification(self, payload):
            assert payload == "signed-notification"
            return {"status": "completed"}

    apple = Apple()
    app = FastAPI()

    async def profile(principal):
        return {"id": principal.subject, "email": None, "display_name": "Person"}

    binding = install_runtime_auth(app, apple.runtime, profile_loader=profile)
    install_apple_auth(app, apple, binding=binding, profile_loader=profile)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="https://auth.test") as client:
        yield client, apple


async def test_apple_http_structured_exchange_preserves_existing_session_envelope():
    async with environment() as (client, apple):
        challenge = await client.post("/api/v1/auth/apple/challenges", json={})
        assert challenge.status_code == 200
        assert challenge.json()["data"]["nonce"] == "server-nonce"
        device = uuid4()
        response = await client.post(
            "/api/v1/auth/apple",
            json={
                "challenge_id": challenge.json()["data"]["challenge_id"],
                "identity_token": "apple-id",
                "authorization_code": "apple-code",
                "device_id": str(device),
                "admission_proof": "request-proof",
            },
        )
        assert response.status_code == 200
        data = response.json()["data"]
        assert data["access_token"] == "app-access" and data["token_type"] == "Bearer"
        assert data["user"]["display_name"] == "Person" and apple.device == device
        assert apple.admission_proof == "request-proof"
        assert "no-store" in response.headers["cache-control"]


@pytest.mark.parametrize("purpose", ["reauth_bind", "reauth_unlink", "reauth_email_update"])
async def test_apple_reauthentication_challenges_require_current_session(purpose):
    async with environment() as (client, apple):
        response = await client.post("/api/v1/auth/apple/challenges", json={"purpose": purpose})
        assert response.status_code == 401
        response = await client.post(
            "/api/v1/auth/apple/challenges",
            json={"purpose": purpose},
            headers={"Authorization": "Bearer current-session"},
        )
        assert response.status_code == 200
        assert apple.challenge_args["purpose"] == purpose
        assert apple.challenge_args["principal"] is not None


async def test_email_update_routes_apple_reauthentication_through_dedicated_service():
    from dwy_auth.contracts import VerifiedIdentity

    async with environment() as (client, apple):

        async def reauthenticate(principal, credential, *, purpose, remote_key):
            assert credential == "structured-apple-authorization" and purpose == "email_update"
            return VerifiedIdentity("test", principal.subject, "apple", purpose=purpose)

        async def send_code(principal, email, *, reauthentication, **kwargs):
            assert reauthentication.subject == principal.subject and reauthentication.method == "apple"
            return {"challenge_id": str(uuid4()), "expires_in": 300, "resend_after": 60, "code_length": 6}

        apple.reauthenticate = reauthenticate
        apple.runtime.providers["apple"] = apple
        apple.runtime.send_email_update_code = send_code
        response = await client.post(
            "/api/v1/auth/email/update/code",
            headers={"Authorization": "Bearer current-session"},
            json={
                "email": "new@example.com",
                "reauthentication": {
                    "method": "external",
                    "identifier": "apple",
                    "credential": "structured-apple-authorization",
                },
            },
        )
        assert response.status_code == 200


async def test_apple_binding_requires_current_session_and_reauthentication():
    async with environment() as (client, _):
        assert (await client.post("/api/v1/auth/apple/challenges", json={"purpose": "bind"})).status_code == 401
        headers = {"Authorization": "Bearer current-session"}
        challenge = await client.post("/api/v1/auth/apple/challenges", json={"purpose": "bind"}, headers=headers)
        assert challenge.status_code == 200
        response = await client.post(
            "/api/v1/auth/apple/bind",
            headers=headers,
            json={
                "challenge_id": challenge.json()["data"]["challenge_id"],
                "identity_token": "apple-id",
                "authorization_code": "apple-code",
                "reauthentication": {"method": "email", "identifier": "person@example.com", "password": "old-password"},
            },
        )
        assert response.status_code == 200 and response.json()["data"] == {"status": "completed"}


async def test_apple_transport_rejects_oversize_and_does_not_echo_credentials():
    async with environment() as (client, _):
        secret = "sensitive-apple-material"
        response = await client.post(
            "/api/v1/auth/apple",
            json={
                "challenge_id": secret,
                "identity_token": secret,
                "authorization_code": secret,
            },
        )
        assert response.status_code == 422 and secret not in response.text
        response = await client.post("/api/v1/auth/apple", content=b"x" * 163841)
        assert response.status_code == 413
        notification = await client.post("/api/v1/auth/apple/notifications", json={"payload": "signed-notification"})
        assert notification.status_code == 200
