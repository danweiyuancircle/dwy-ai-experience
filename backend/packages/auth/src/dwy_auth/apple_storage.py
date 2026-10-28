"""Apple 挑战、加密授权与可靠撤销；宿主负责 Alembic 迁移。"""

from dataclasses import dataclass

from sqlalchemy import BigInteger, Column, MetaData, String, Table, Text


@dataclass(frozen=True)
class AppleTables:
    """所有记录按应用隔离，撤销队列不依赖业务主体外键。"""

    challenges: Table
    grants: Table
    revocations: Table
    notifications: Table


def build_apple_tables(metadata: MetaData) -> AppleTables:
    """只声明结构，不建表或迁移；密文由服务端配置的 Fernet 密钥保护。"""
    challenges = Table(
        "auth_apple_challenges",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("nonce_hash", String(64), nullable=False),
        Column("nonce_ciphertext", Text, nullable=False),
        Column("purpose", String(16), nullable=False),
        Column("subject", String(255)),
        Column("created_at", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
        Column("claimed_at", BigInteger),
    )
    grants = Table(
        "auth_apple_grants",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("issuer", String(512), primary_key=True),
        Column("external_subject", String(255), primary_key=True),
        Column("subject", String(255), nullable=False, index=True),
        Column("client_id", String(255), nullable=False),
        Column("refresh_ciphertext", Text, nullable=False),
        Column("created_at", BigInteger, nullable=False),
    )
    revocations = Table(
        "auth_apple_revocations",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("client_id", String(255), nullable=False),
        Column("refresh_ciphertext", Text, nullable=False),
        Column("attempts", BigInteger, nullable=False, default=0),
        Column("next_attempt_at", BigInteger, nullable=False, index=True),
        Column("lease_id", String(36)),
        Column("lease_until", BigInteger, nullable=False, default=0),
    )
    notifications = Table(
        "auth_apple_notifications",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(255), primary_key=True),
        Column("issuer", String(512), nullable=False),
        Column("external_subject", String(255), nullable=False, index=True),
        Column("event", String(32), nullable=False),
        Column("received_at", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
    )
    return AppleTables(challenges, grants, revocations, notifications)
