"""只声明认证凭据表；metadata、表前缀与迁移执行权归宿主。"""

import re
from dataclasses import dataclass

from sqlalchemy import BigInteger, Boolean, Column, MetaData, String, Table, UniqueConstraint


@dataclass(frozen=True)
class RuntimeTables:
    """全部唯一性和查询均包含 app_id，不关联具体业务 User。"""

    identifiers: Table
    password_credentials: Table
    external_identities: Table
    email_challenges: Table
    auth_rate_limits: Table
    authentication_proofs: Table


def build_runtime_tables(metadata: MetaData, prefix: str = "auth_runtime_") -> RuntimeTables:
    """注册通用认证表；重复注册应由宿主复用返回值，不在启动时执行迁移。"""
    # 与会话表共用前缀时也需留出最长后缀，避免超出 PostgreSQL 63 字符上限。
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", prefix):
        raise ValueError("Invalid authentication table prefix")
    identifiers = Table(
        prefix + "identifiers",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("kind", String(16), primary_key=True),
        Column("value", String(254), primary_key=True),
        Column("subject", String(255), nullable=False, index=True),
        Column("verified", Boolean, nullable=False),
        UniqueConstraint("app_id", "subject", "kind"),
    )
    passwords = Table(
        prefix + "password_credentials",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("subject", String(255), primary_key=True),
        Column("password_hash", String(128), nullable=False),
        Column("updated_at", BigInteger, nullable=False),
    )
    external = Table(
        prefix + "external_identities",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("provider", String(64), primary_key=True),
        Column("issuer", String(512), primary_key=True),
        Column("external_subject", String(255), primary_key=True),
        Column("subject", String(255), nullable=False, index=True),
        Column("generation", String(36), nullable=False),
    )
    # 保持既有 challenge/rate 表列契约，直接复用同一套 challenge 算法和原子查询。
    challenges = Table(
        prefix + "email_challenges",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("email", String(254), nullable=False, index=True),
        Column("purpose", String(32), nullable=False),
        Column("code_hash", String(64), nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
        Column("attempts", BigInteger, nullable=False, default=0),
        Column("delivered_at", BigInteger),
        Column("consumed_at", BigInteger),
    )
    rate_limits = Table(
        prefix + "rate_limits",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("key", String(64), primary_key=True),
        Column("count", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
    )
    proofs = Table(
        prefix + "authentication_proofs",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("subject", String(255), nullable=False, index=True),
        Column("method", String(64), nullable=False),
        Column("purpose", String(16), nullable=False),
        Column("credential_value", String(255), nullable=False),
        Column("issuer", String(512)),
        Column("credential_version", String(64), nullable=False),
        Column("created_at", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
        Column("consumed_at", BigInteger),
    )
    return RuntimeTables(identifiers, passwords, external, challenges, rate_limits, proofs)
