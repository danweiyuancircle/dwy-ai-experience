"""Apple 登录上游使用真实本地签名，仅替换网络传输，不读取真实凭据。"""

import asyncio
import json
from urllib.error import HTTPError
from urllib.request import Request

import pytest
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from jose import jwk, jwt
from pydantic import ValidationError

from dwy_auth.models import AuthError

NOW = 1_800_000_000
CLIENT = "com.example.app"
ISSUER = "https://appleid.apple.com"


@pytest.fixture
def apple():
    from dwy_auth.apple import AppleGateway, AppleSignInConfig

    signing = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    client_key = ec.generate_private_key(ec.SECP256R1())
    private = client_key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    ).decode()
    public = jwk.construct(signing.public_key(), "RS256").to_dict()
    public.update(kid="apple-key", alg="RS256", use="sig")
    config = AppleSignInConfig(
        client_id=CLIENT,
        team_id="ABCDE12345",
        key_id="12345ABCDE",
        private_key=private,
        token_encryption_key=Fernet.generate_key().decode(),
    )
    calls = []
    state = {"keys": [public], "exchange_changes": {}, "refresh_token": "private-refresh"}

    def token(changes=None, key=signing, kid="apple-key", algorithm="RS256"):
        claims = {
            "iss": ISSUER,
            "aud": CLIENT,
            "sub": "apple-sub",
            "iat": NOW - 1,
            "exp": NOW + 300,
            "nonce": "challenge-nonce",
            "email": "hidden@example.com",
            "email_verified": "true",
        }
        claims.update(changes or {})
        claims = {name: value for name, value in claims.items() if value is not None}
        return jwt.encode(claims, key, algorithm=algorithm, headers={"kid": kid})

    async def request(method, url, data=None):
        calls.append((method, url, data))
        if url.endswith("/keys"):
            await asyncio.sleep(0)
            return {"keys": state["keys"]}
        if url.endswith("/token"):
            if state.get("error"):
                return {"error": state["error"]}
            return {"id_token": token(state["exchange_changes"]), "refresh_token": state["refresh_token"]}
        assert url.endswith("/revoke")
        return {}

    return AppleGateway(config, request=request, now=lambda: NOW), token, state, calls, config, client_key


async def test_authorize_verifies_both_tokens_and_signs_client_secret(apple):
    gateway, token, _, calls, config, client_key = apple
    result = await gateway.authorize(token(), "one-time-code", "challenge-nonce", "Person")
    assert (result.identity.issuer, result.identity.subject, result.identity.email) == (
        ISSUER,
        "apple-sub",
        "hidden@example.com",
    )
    assert result.identity.display_name == "Person"
    assert result.refresh_token == "private-refresh"
    assert "private-refresh" not in repr(result)
    assert result.client_id == CLIENT
    assert len(calls) == 2
    method, url, data = calls[-1]
    assert (method, url) == ("POST", ISSUER + "/auth/token")
    assert data["code"] == "one-time-code" and data["grant_type"] == "authorization_code"
    secret = jwt.decode(
        data["client_secret"],
        client_key.public_key(),
        algorithms=["ES256"],
        audience=ISSUER,
        issuer=config.team_id,
        options={"verify_exp": False},
    )
    assert secret["sub"] == CLIENT and secret["iat"] == NOW
    assert 0 < secret["exp"] - NOW <= 600


@pytest.mark.parametrize(
    "changes",
    [
        {"aud": "com.other.app"},
        {"aud": [CLIENT, "com.other.app"]},
        {"iss": "https://evil.example"},
        {"exp": NOW},
        {"iat": NOW + 1},
        {"exp": None},
        {"iat": True},
        {"sub": ""},
        {"nonce": "old-nonce"},
        {"nonce": None},
        {"sub": "contains space"},
    ],
)
async def test_authorize_rejects_invalid_claims_before_exchange(apple, changes):
    gateway, token, _, calls, *_ = apple
    with pytest.raises(AuthError) as caught:
        await gateway.authorize(token(changes), "private-code", "challenge-nonce")
    assert caught.value.status_code == 401
    assert not any(url.endswith("/token") for _, url, _ in calls)
    assert "private-code" not in str(caught.value)


async def test_rejects_wrong_algorithm_and_tampering(apple):
    gateway, token, _, _, *_ = apple
    for invalid in [token(key="shared-secret", algorithm="HS256"), token()[:-8] + "tampered"]:
        with pytest.raises(AuthError):
            await gateway.authorize(invalid, "code", "challenge-nonce")


@pytest.mark.parametrize("changes", [{"sub": "other-person"}, {"nonce": "other-nonce"}, {"aud": "other"}])
async def test_exchange_identity_must_match_authorization(apple, changes):
    gateway, token, state, *_ = apple
    state["exchange_changes"] = changes
    with pytest.raises(AuthError):
        await gateway.authorize(token(), "code", "challenge-nonce")


async def test_invalid_exchange_revokes_already_obtained_refresh(apple):
    gateway, token, state, calls, *_ = apple
    state["exchange_changes"] = {"sub": "other-person"}
    with pytest.raises(AuthError):
        await gateway.authorize(token(), "code", "challenge-nonce")
    assert calls[-1][1] == ISSUER + "/auth/revoke"
    assert calls[-1][2]["token"] == "private-refresh"


async def test_failed_exchange_compensation_preserves_secret_for_durable_retry(apple):
    gateway, token, state, _, *_ = apple
    state["exchange_changes"] = {"nonce": "other-nonce"}
    transport = gateway._request

    async def revoke_unavailable(method, url, data):
        if url.endswith("/revoke"):
            raise TimeoutError("private-refresh")
        return await transport(method, url, data)

    gateway._request = revoke_unavailable
    with pytest.raises(AuthError) as caught:
        await gateway.authorize(token(), "code", "challenge-nonce")
    assert caught.value.code == "APPLE_REVOCATION_REQUIRED"
    assert caught.value.revocation_token.get_secret_value() == "private-refresh"
    assert caught.value.client_id == CLIENT
    assert "private-refresh" not in str(caught.value)
    assert "private-refresh" not in repr(caught.value)
    assert "private-refresh" not in repr(vars(caught.value))


async def test_cancellation_after_exchange_compensates_obtained_refresh(apple):
    from dwy_auth.apple import AppleGateway

    gateway, token, _, calls, config, _ = apple
    transport = gateway._request
    verifying_exchange = asyncio.Event()
    key_requests = 0

    async def request(method, url, data):
        nonlocal key_requests
        if url.endswith("/keys"):
            key_requests += 1
            if key_requests > 1:
                verifying_exchange.set()
                await asyncio.Event().wait()
        if url.endswith("/token"):
            return {"id_token": token(kid="new-key"), "refresh_token": "private-refresh"}
        return await transport(method, url, data)

    gateway = AppleGateway(config, request=request, now=lambda: NOW)
    pending = asyncio.create_task(gateway.authorize(token(), "code", "challenge-nonce"))
    await asyncio.wait_for(verifying_exchange.wait(), timeout=1)
    pending.cancel()
    with pytest.raises(asyncio.CancelledError):
        await pending
    assert calls[-1][1] == ISSUER + "/auth/revoke"
    assert calls[-1][2]["token"] == "private-refresh"


async def test_unverified_email_and_missing_name_are_optional(apple):
    gateway, token, state, *_ = apple
    state["exchange_changes"] = {"email_verified": False}
    result = await gateway.authorize(token({"email_verified": False}), "code", "challenge-nonce")
    assert result.identity.email is None and result.identity.display_name is None


async def test_unicode_nonce_and_untrusted_nested_event_type_are_sanitized(apple):
    gateway, token, *_ = apple
    with pytest.raises(AuthError):
        await gateway.authorize(token(), "code", "非本次挑战")
    with pytest.raises(AuthError):
        await gateway.verify_notification(
            token(
                {
                    "jti": "notification",
                    "events": {"type": [], "sub": "apple-sub", "event_time": NOW},
                }
            )
        )


async def test_numeric_email_verification_is_not_a_verified_profile(apple):
    gateway, token, state, *_ = apple
    state["exchange_changes"] = {"email_verified": 1}
    result = await gateway.authorize(token({"email_verified": 1}), "code", "challenge-nonce")
    assert result.identity.email is None


@pytest.mark.parametrize("refresh", [None, "", "x" * 16385])
async def test_missing_refresh_never_reports_success(apple, refresh):
    gateway, token, state, *_ = apple
    state["refresh_token"] = refresh
    with pytest.raises(AuthError):
        await gateway.authorize(token(), "code", "challenge-nonce")


async def test_jwks_cache_handles_rotation_and_bounds_unknown_key_fetches(apple):
    gateway, token, state, calls, *_ = apple
    await gateway.authorize(token(), "first", "challenge-nonce")
    new_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public = jwk.construct(new_key.public_key(), "RS256").to_dict()
    public.update(kid="rotated", alg="RS256", use="sig")
    state["keys"] = [public]
    state["exchange_changes"] = {}
    # Exchange still uses the old key, so only verify a rotated notification here.
    claims = {"jti": "notice", "events": {"type": "consent-revoked", "sub": "apple-sub", "event_time": NOW}}
    await gateway.verify_notification(token(claims, key=new_key, kid="rotated"))
    invalid = [gateway.verify_notification(token(claims, kid=f"unknown-{i}")) for i in range(20)]
    errors = await asyncio.gather(*invalid, return_exceptions=True)
    assert all(isinstance(error, AuthError) for error in errors)
    assert sum(url.endswith("/keys") for _, url, _ in calls) == 2


async def test_initial_jwks_fetch_is_single_flight(apple):
    gateway, token, _, calls, *_ = apple
    await asyncio.gather(*(gateway.authorize(token(), "code", "challenge-nonce") for _ in range(10)))
    assert sum(url.endswith("/keys") for _, url, _ in calls) == 1


async def test_timeout_and_remote_error_are_sanitized(apple):
    from dwy_auth.apple import AppleGateway

    gateway, token, state, _, config, _ = apple
    state["error"] = "private upstream data"
    with pytest.raises(AuthError) as caught:
        await gateway.authorize(token(), "private-code", "challenge-nonce")
    assert "private" not in str(caught.value)

    async def unavailable(*args):
        raise TimeoutError("private-token")

    with pytest.raises(AuthError) as caught:
        await AppleGateway(config, request=unavailable).authorize(token(), "code", "challenge-nonce")
    assert caught.value.status_code == 503 and "private" not in str(caught.value)


async def test_revoke_posts_refresh_token_and_rejects_other_client(apple):
    gateway, _, _, calls, *_ = apple
    await gateway.revoke("private-refresh")
    method, url, data = calls[-1]
    assert (method, url) == ("POST", ISSUER + "/auth/revoke")
    assert data["token"] == "private-refresh" and data["token_type_hint"] == "refresh_token"
    with pytest.raises(AuthError):
        await gateway.revoke("private-refresh", "other-app")
    assert len(calls) == 1


@pytest.mark.parametrize("string_events", [False, True])
async def test_notification_verifies_documented_event_without_exp(apple, string_events):
    gateway, token, *_ = apple
    event = {"type": "account-deleted", "sub": "apple-sub", "event_time": NOW - 2}
    value = {"jti": "notification-id", "events": json.dumps(event) if string_events else event}
    # The documented notification has no exp, unlike an identity token.
    signed = token({**value, "exp": None})
    result = await gateway.verify_notification(signed)
    assert result["events"] == event and result["jti"] == "notification-id"


@pytest.mark.parametrize(
    "changes",
    [
        {"aud": "other-app"},
        {"iss": "evil"},
        {"iat": NOW + 1},
        {"iat": NOW - 86401},
        {"exp": NOW - 1},
        {"jti": ""},
        {"events": "bad-json"},
        {"events": {"type": "unknown", "sub": "apple-sub", "event_time": NOW}},
        {"events": {"type": "account-deleted", "sub": "", "event_time": NOW}},
        {"events": {"type": "account-deleted", "sub": "apple-sub", "event_time": NOW + 1}},
    ],
)
async def test_notification_rejects_invalid_claims_and_events(apple, changes):
    gateway, token, *_ = apple
    value = {
        "jti": "notification-id",
        "events": {"type": "consent-revoked", "sub": "apple-sub", "event_time": NOW},
    }
    value.update(changes)
    with pytest.raises(AuthError):
        await gateway.verify_notification(token(value))


def test_config_rejects_bad_encryption_and_signing_keys_without_echoing_secrets(apple):
    from dwy_auth.apple import AppleSignInConfig

    *_, config, _ = apple
    for field in ["private_key", "token_encryption_key"]:
        values = config.model_dump()
        values[field] = "private-invalid-material"
        with pytest.raises(ValidationError) as caught:
            AppleSignInConfig(**values)
        assert "private-invalid-material" not in str(caught.value)
    assert "PRIVATE KEY" not in repr(config)


async def test_default_transport_rejects_redirect_and_oversized_body(apple, monkeypatch):
    from dwy_auth.apple import AppleGateway

    *_, config, _ = apple
    timeouts = []
    redirects = []

    class Reply:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def read(self, size):
            return b"x" * size

    class Opener:
        def open(self, request, timeout):
            timeouts.append(timeout)
            return Reply()

    def build_opener(*handlers):
        request = Request(ISSUER + "/auth/revoke", data=b"token=private-refresh")
        redirects.append(
            handlers[0].redirect_request(request, None, 302, "redirect", {}, "https://other.example/collect")
        )
        return Opener()

    monkeypatch.setattr("urllib.request.build_opener", build_opener)
    with pytest.raises(AuthError):
        await AppleGateway(config).revoke("private-refresh")
    assert timeouts == [5]
    assert redirects == [None]

    class RedirectOpener:
        def open(self, request, timeout):
            raise HTTPError(request.full_url, 302, "private", {}, None)

    monkeypatch.setattr("urllib.request.build_opener", lambda *args: RedirectOpener())
    with pytest.raises(AuthError):
        await AppleGateway(config).revoke("private-refresh")
