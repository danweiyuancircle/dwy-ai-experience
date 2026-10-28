"""App Store Connect account-key validation shared by reviews and analytics."""

import jwt
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


def asc_private_key(secret):
    """只接受 P-256 账号私钥；错误中不携带底层密钥材料。"""
    try:
        key = serialization.load_pem_private_key(secret.get_secret_value().encode(), password=None)
        if not isinstance(key, ec.EllipticCurvePrivateKey) or not isinstance(key.curve, ec.SECP256R1):
            raise ValueError
        return key
    except (ValueError, TypeError, AttributeError, UnsupportedAlgorithm):
        raise ValueError("Invalid ASC credentials") from None


def asc_token(config, key, clock) -> str:
    """为当前宿主凭据签发五分钟 ASC token，不缓存或记录签名结果。"""
    try:
        issued = int(clock())
        return jwt.encode(
            {"iss": config.issuer_id, "iat": issued, "exp": issued + 300, "aud": "appstoreconnect-v1"},
            key,
            algorithm="ES256",
            headers={"kid": config.key_id, "typ": "JWT"},
        )
    except (ValueError, TypeError, jwt.PyJWTError):
        raise ValueError("Invalid ASC credentials") from None
