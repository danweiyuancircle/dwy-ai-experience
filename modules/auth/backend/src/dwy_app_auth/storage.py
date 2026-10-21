"""应用自己拥有 metadata 与迁移，不引入进程全局数据库。"""

from dataclasses import dataclass

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKeyConstraint,
    MetaData,
    String,
    Table,
    UniqueConstraint,
)


@dataclass(frozen=True)
class AuthTables:
    users: Table
    sessions: Table
    refresh_history: Table


def build_auth_tables(metadata: MetaData) -> AuthTables:
    users = Table(
        "auth_users",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("google_subject", String(255), nullable=False),
        Column("email", String(320)),
        Column("display_name", String(255)),
        Column("disabled", Boolean, nullable=False, default=False),
        Column("created_at", BigInteger, nullable=False),
        Column("deleted_at", BigInteger),
        UniqueConstraint("app_id", "google_subject"),
    )
    sessions = Table(
        "auth_sessions",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("user_id", String(36), nullable=False, index=True),
        Column("device_id", String(36), nullable=False),
        Column("access_hash", String(64), nullable=False),
        Column("refresh_hash", String(64), nullable=False),
        Column("access_expires_at", BigInteger, nullable=False),
        Column("refresh_expires_at", BigInteger, nullable=False),
        Column("created_at", BigInteger, nullable=False),
        Column("revoked_at", BigInteger),
        ForeignKeyConstraint(["app_id", "user_id"], ["auth_users.app_id", "auth_users.id"]),
        UniqueConstraint("app_id", "access_hash"),
        UniqueConstraint("app_id", "refresh_hash"),
    )
    # 一个 session 行即一个 refresh family；旧摘要保留到该 family 的绝对到期时间。
    refresh_history = Table(
        "auth_refresh_history",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("refresh_hash", String(64), primary_key=True),
        Column("session_id", String(36), nullable=False, index=True),
        Column("expires_at", BigInteger, nullable=False),
        ForeignKeyConstraint(["app_id", "session_id"], ["auth_sessions.app_id", "auth_sessions.id"]),
    )
    return AuthTables(users, sessions, refresh_history)
