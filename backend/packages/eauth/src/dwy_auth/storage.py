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
    """旧 Google 产品可以保留三表；邮箱表仅在宿主明确迁移后注册。"""

    users: Table
    sessions: Table
    refresh_history: Table
    password_credentials: Table | None
    email_challenges: Table | None
    auth_rate_limits: Table | None


def build_auth_tables(metadata: MetaData, *, include_email_auth: bool = True) -> AuthTables:
    """注册宿主实际采用的 legacy schema；关闭邮箱能力不会升级旧产品数据库。"""
    users = Table(
        "auth_users",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("google_subject", String(255), nullable=include_email_auth),
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
    if not include_email_auth:
        return AuthTables(users, sessions, refresh_history, None, None, None)
    password_credentials = Table(
        "auth_password_credentials",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("email", String(254), primary_key=True),
        Column("user_id", String(36), nullable=False),
        Column("password_hash", String(128), nullable=False),
        Column("updated_at", BigInteger, nullable=False),
        ForeignKeyConstraint(["app_id", "user_id"], ["auth_users.app_id", "auth_users.id"]),
        UniqueConstraint("app_id", "user_id"),
    )
    email_challenges = Table(
        "auth_email_challenges",
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
    auth_rate_limits = Table(
        "auth_rate_limits",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("key", String(64), primary_key=True),
        Column("count", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False, index=True),
    )
    return AuthTables(
        users, sessions, refresh_history, password_credentials, email_challenges, auth_rate_limits
    )
