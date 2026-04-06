"""JWT token creation/verification and bcrypt password hashing.

All helpers are stateless — pass secrets and algorithm as parameters.
"""

from datetime import timedelta
from typing import Any

from danweiyuan_eapi import dt

import bcrypt
from jose import JWTError, jwt


def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Return True if *plain* matches *hashed*."""
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


def create_token(
    data: dict[str, Any],
    secret: str,
    expires_minutes: int,
    algorithm: str = "HS256",
) -> str:
    """Encode *data* as a signed JWT with the given expiration."""
    to_encode = data.copy()
    expire = dt.utc_now() + timedelta(minutes=expires_minutes)
    to_encode["exp"] = expire
    return jwt.encode(to_encode, secret, algorithm=algorithm)


def decode_token(
    token: str,
    secret: str,
    algorithm: str = "HS256",
) -> dict[str, Any] | None:
    """Decode and verify *token*. Returns None if invalid/expired."""
    try:
        return jwt.decode(token, secret, algorithms=[algorithm])
    except JWTError:
        return None
