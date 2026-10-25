"""会话表声明与业务 User 解耦；宿主通过 Alembic 显式执行迁移。"""

import re
from dataclasses import dataclass

from sqlalchemy import BigInteger, Column, MetaData, String, Table, UniqueConstraint


@dataclass(frozen=True)
class SessionTables:
    """一行 session 对应一个 refresh family，历史摘要保留用于重放撤销。"""

    sessions: Table
    refresh_history: Table


def register_session_tables(metadata: MetaData, prefix: str = "auth_runtime_") -> SessionTables:
    """仅注册表结构，不建表；前缀限制确保标识符安全且兼容 PostgreSQL 长度。"""
    if not isinstance(prefix, str) or not re.fullmatch(r"[a-z][a-z0-9_]{0,39}", prefix):
        raise ValueError("Invalid session table prefix")
    sessions = Table(
        prefix + "sessions",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("id", String(36), primary_key=True),
        Column("subject", String(255), nullable=False, index=True),
        Column("method", String(64), nullable=False),
        Column("device_id", String(36)),
        Column("access_jti", String(36), nullable=False),
        Column("refresh_hash", String(64), nullable=False),
        Column("created_at", BigInteger, nullable=False),
        Column("expires_at", BigInteger, nullable=False),
        Column("revoked_at", BigInteger),
        UniqueConstraint("app_id", "refresh_hash"),
    )
    # 无业务表外键；删除/清理策略由宿主迁移和运维任务显式管理。
    history = Table(
        prefix + "refresh_history",
        metadata,
        Column("app_id", String(32), primary_key=True),
        Column("refresh_hash", String(64), primary_key=True),
        Column("session_id", String(36), nullable=False, index=True),
        Column("expires_at", BigInteger, nullable=False),
    )
    return SessionTables(sessions, history)
