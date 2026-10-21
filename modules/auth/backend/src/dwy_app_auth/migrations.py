"""宿主Alembic revision调用的升级辅助；共享包不创建业务数据库。"""

from sqlalchemy import MetaData, inspect

from .storage import build_auth_tables


def upgrade_email_auth(op) -> None:
    """在宿主revision事务中升级已有Google表；仅由迁移调用，不能放入应用启动。

    op为宿主Alembic Operations对象，避免给认证运行时新增Alembic依赖。
    SQLite batch迁移需由宿主迁移环境按Alembic要求处理外键PRAGMA；生产PostgreSQL原位修改。
    """
    bind = op.get_bind()
    columns = inspect(bind).get_columns("auth_users")
    subject = next(column for column in columns if column["name"] == "google_subject")
    if not subject["nullable"]:
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("auth_users") as batch:
                batch.alter_column("google_subject", existing_type=subject["type"], nullable=True)
        else:
            op.alter_column("auth_users", "google_subject", existing_type=subject["type"], nullable=True)
    tables = build_auth_tables(MetaData())
    for table in (tables.password_credentials, tables.email_challenges, tables.auth_rate_limits):
        table.create(bind, checkfirst=True)
