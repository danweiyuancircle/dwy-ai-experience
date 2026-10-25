"""官方 Google 验签适配器：使用本地 RSA 密钥测试真实签名/声明校验，不联网。"""

import time

import pytest

from dwy_auth import AuthError, GoogleConfig, OfficialGoogleVerifier

CLIENT_ID = "12345-sample.apps.googleusercontent.com"


@pytest.fixture
def signed_token(monkeypatch):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from google.auth import crypt, jwt
    from google.oauth2 import id_token

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    private_pem = key.private_bytes(
        serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()
    )
    public_pem = key.public_key().public_bytes(
        serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    monkeypatch.setattr(id_token, "_fetch_certs", lambda request, certs_url: {"test-key": public_pem})
    signer = crypt.RSASigner.from_string(private_pem, key_id="test-key")

    def encode(**changes):
        claims = {
            "iss": "https://accounts.google.com",
            "aud": CLIENT_ID,
            "sub": "google-stable-subject",
            "iat": int(time.time()) - 1,
            "exp": int(time.time()) + 300,
            "email": "person@example.com",
            "email_verified": True,
            "name": "Person",
        }
        claims.update(changes)
        return jwt.encode(signer, claims).decode()

    return encode


async def test_official_signature_verifier_accepts_expected_audience(signed_token):
    identity = await OfficialGoogleVerifier(GoogleConfig(client_id=CLIENT_ID)).verify(signed_token())
    assert identity.subject == "google-stable-subject"
    assert identity.email == "person@example.com"


@pytest.mark.parametrize(
    "changes",
    [
        {"aud": "99999-other.apps.googleusercontent.com"},
        {"iss": "https://attacker.example"},
        {"iat": int(time.time()) - 600, "exp": int(time.time()) - 300},
        {"iat": int(time.time()) + 300},
        {"sub": None},
        {"sub": ""},
    ],
)
async def test_official_verifier_rejects_wrong_claims(signed_token, changes):
    with pytest.raises(AuthError) as error:
        await OfficialGoogleVerifier(GoogleConfig(client_id=CLIENT_ID)).verify(signed_token(**changes))
    assert error.value.status_code == 401


async def test_official_verifier_rejects_tampered_signature(signed_token):
    original = signed_token()
    header, payload, signature = original.split(".")
    signature = ("A" if signature[0] != "A" else "B") + signature[1:]
    with pytest.raises(AuthError):
        await OfficialGoogleVerifier(GoogleConfig(client_id=CLIENT_ID)).verify(
            ".".join([header, payload, signature])
        )


async def test_unverified_email_is_not_stored_as_verified_profile(signed_token):
    identity = await OfficialGoogleVerifier(GoogleConfig(client_id=CLIENT_ID)).verify(
        signed_token(email_verified=False),
    )
    assert identity.email is None


async def test_network_failure_is_retryable_sanitized_error(monkeypatch):
    from google.auth.exceptions import TransportError
    from google.oauth2 import id_token

    def unavailable(*args, **kwargs):
        raise TransportError("secret remote details")

    monkeypatch.setattr(id_token, "verify_oauth2_token", unavailable)
    with pytest.raises(AuthError) as error:
        await OfficialGoogleVerifier(GoogleConfig(client_id=CLIENT_ID)).verify("secret-token")
    assert error.value.status_code == 503
    assert "secret" not in str(error.value)
