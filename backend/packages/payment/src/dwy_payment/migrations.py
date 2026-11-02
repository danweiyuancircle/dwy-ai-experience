"""0.3.0资金表的显式Alembic集成；导入和应用启动均不执行DDL。

表定义是版本固定的迁移快照，不引用未来可能变化的ORM模型。宿主revision传入op，
因此Alembic不是支付运行时依赖；只支持有真实连接的SQLite/PostgreSQL在线迁移。
"""

import sqlalchemy as sa
from sqlalchemy.engine import Connection

_METADATA = sa.MetaData()
_IDEMPOTENCY_UNIQUE = "uq_payment_orders_idempotency_key"
_NEW_ORDER_COLUMNS = frozenset({"idempotency_key", "expires_at"})


def _timestamps() -> tuple[sa.Column, sa.Column]:
    return (
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


_ORDERS = sa.Table(
    "payment_orders", _METADATA,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("uuid", sa.String(36), nullable=False, unique=True, index=True),
    sa.Column("user_id", sa.String(64), nullable=False, index=True),
    sa.Column("idempotency_key", sa.String(64), nullable=True),
    sa.Column("expires_at", sa.DateTime(), nullable=True),
    sa.Column("order_no", sa.String(32), nullable=False, unique=True, index=True),
    sa.Column("amount_fen", sa.Integer(), nullable=False),
    sa.Column("channel", sa.String(16), nullable=False),
    sa.Column("channel_trade_no", sa.String(64), nullable=True),
    sa.Column("status", sa.String(16), nullable=False),
    sa.Column("description", sa.String(127), nullable=False),
    sa.Column("code_url", sa.String(512), nullable=True),
    sa.Column("refunded_fen", sa.Integer(), nullable=False, server_default="0"),
    sa.Column("refund_no", sa.String(64), nullable=True, unique=True),
    sa.Column("notify_payload", sa.Text(), nullable=True),
    sa.Column("is_deleted", sa.Boolean(), nullable=False),
    sa.Column("deleted_at", sa.DateTime(), nullable=True),
    *_timestamps(),
    sa.UniqueConstraint("idempotency_key", name=_IDEMPOTENCY_UNIQUE),
    sa.CheckConstraint("status IN ('pending', 'success', 'failed', 'refund')", name="ck_payment_orders_status"),
    sa.CheckConstraint("amount_fen >= 1 AND amount_fen <= 100000000", name="ck_payment_orders_amount"),
)
_REFUNDS = sa.Table(
    "payment_refunds", _METADATA,
    sa.Column("id", sa.Integer(), primary_key=True),
    sa.Column("order_no", sa.String(32), nullable=False, index=True),
    sa.Column("refund_no", sa.String(64), nullable=False, unique=True),
    sa.Column("transaction_id", sa.String(64), nullable=False),
    sa.Column("provider_refund_id", sa.String(64), nullable=True),
    sa.Column("amount_fen", sa.Integer(), nullable=False),
    sa.Column("refund_fen", sa.Integer(), nullable=False),
    sa.Column("source", sa.String(16), nullable=False),
    sa.Column("provider_status", sa.String(16), nullable=False),
    sa.Column("verified_status", sa.String(16), nullable=True),
    sa.Column("business_processed", sa.Boolean(), nullable=False),
    sa.Column("next_query_at", sa.DateTime(), nullable=True),
    sa.Column("last_query_at", sa.DateTime(), nullable=True, index=True),
    sa.Column("manual_required", sa.Boolean(), nullable=False),
    sa.Column("version", sa.Integer(), nullable=False),
    *_timestamps(),
    sa.CheckConstraint("refund_fen > 0 AND refund_fen <= amount_fen", name="ck_payment_refunds_amount"),
    sa.CheckConstraint("source IN ('app', 'external')", name="ck_payment_refunds_source"),
    sa.Index("ix_payment_refunds_due", "next_query_at"),
)
_EVENTS = sa.Table(
    "payment_events", _METADATA,
    sa.Column("event_id", sa.String(64), primary_key=True),
    sa.Column("order_no", sa.String(32), nullable=False, index=True),
    sa.Column("payload", sa.JSON(), nullable=False),
    sa.Column("acknowledged_at", sa.DateTime(), nullable=True, index=True),
    *_timestamps(),
)
_TABLES = (_ORDERS, _REFUNDS, _EVENTS)


def _connection(op) -> Connection:
    if op.get_context().as_sql:
        raise RuntimeError("payment migrations require an online connection; offline SQL is unsupported")
    bind = op.get_bind()
    if bind.dialect.name not in {"sqlite", "postgresql"}:
        raise RuntimeError("payment migrations support SQLite and PostgreSQL only")
    return bind


def _column_names(columns) -> tuple[str, ...]:
    return tuple(column.name for column in columns)


def _validate_table(bind: Connection, table: sa.Table, *, exclude: frozenset[str] = frozenset()) -> None:
    inspector = sa.inspect(bind)
    if not inspector.has_table(table.name):
        raise RuntimeError(f"payment schema missing table: {table.name}")
    actual = {column["name"]: column for column in inspector.get_columns(table.name)}
    expected = {column.name: column for column in table.columns if column.name not in exclude}
    if actual.keys() != expected.keys():
        raise RuntimeError(f"payment schema incompatible columns: {table.name}")
    for name, column in expected.items():
        found = actual[name]
        if (found["type"].compile(dialect=bind.dialect).upper() != column.type.compile(dialect=bind.dialect).upper()
                or found["nullable"] != column.nullable):
            raise RuntimeError(f"payment schema incompatible column: {table.name}.{name}")
    primary_key = tuple(inspector.get_pk_constraint(table.name)["constrained_columns"])
    if primary_key != _column_names(table.primary_key.columns):
        raise RuntimeError(f"payment schema incompatible primary key: {table.name}")

    indexes = inspector.get_indexes(table.name)
    # 唯一索引与唯一约束语义相同，兼容旧宿主的索引命名，但部分索引不能替代全局唯一。
    actual_unique = {tuple(item["column_names"]) for item in inspector.get_unique_constraints(table.name)}
    usable_indexes = [item for item in indexes if all(item["column_names"])
                      and not any(key.endswith("_where") and value is not None
                                  for key, value in item.get("dialect_options", {}).items())]
    actual_unique.update(tuple(item["column_names"]) for item in usable_indexes if item["unique"])
    expected_unique = {_column_names(item.columns) for item in table.constraints
                       if isinstance(item, sa.UniqueConstraint) and not exclude.intersection(item.columns.keys())}
    expected_unique.update(_column_names(item.columns) for item in table.indexes if item.unique)
    if actual_unique != expected_unique:
        raise RuntimeError(f"payment schema incompatible unique keys: {table.name}")
    actual_indexes = {(tuple(item["column_names"]), bool(item["unique"])) for item in usable_indexes}
    if not {(_column_names(item.columns), bool(item.unique)) for item in table.indexes} <= actual_indexes:
        raise RuntimeError(f"payment schema missing required index: {table.name}")
    checks = {item["name"] for item in inspector.get_check_constraints(table.name)}
    if not {item.name for item in table.constraints if isinstance(item, sa.CheckConstraint)} <= checks:
        raise RuntimeError(f"payment schema missing required check constraint: {table.name}")


def validate_payment_tables(bind: Connection) -> None:
    """核对0.3.0三张资金表的列、类型、空值和关键约束；不执行任何修复或DDL。

    默认表达式及数据库自动生成的唯一约束名不参与比较，避免跨方言的等价表达误报。
    业务表即使已进入同一ORM metadata，也不会被检查或创建。
    """
    for table in _TABLES:
        _validate_table(bind, table)


def create_payment_tables(op) -> None:
    """在宿主Alembic事务中首建0.3.0三张资金表；已有表必须完整且兼容才允许无操作。

    部分旧表或缺列必须使用明确的升级路径，不能通过checkfirst掩盖不完整schema。
    """
    bind = _connection(op)
    if any(sa.inspect(bind).has_table(table.name) for table in _TABLES):
        validate_payment_tables(bind)
        return
    for table in _TABLES:
        table.create(bind)
    validate_payment_tables(bind)


def upgrade_payment_tables(op) -> None:
    """显式将完整0.2资金表升级到0.3.0，或为新宿主首建；不触碰其他表。

    修改前先核对旧支付/退款表，新增幂等键和截止时间为NULL，不回填历史事件。
    旧付款截止未知，不能按当前配置重新计算并改变原渠道请求参数。
    """
    bind = _connection(op)
    present = {table.name for table in _TABLES if sa.inspect(bind).has_table(table.name)}
    if not present:
        create_payment_tables(op)
        return
    if present == {table.name for table in _TABLES}:
        validate_payment_tables(bind)
        return
    if present != {_ORDERS.name, _REFUNDS.name}:
        raise RuntimeError("payment schema is incomplete; refusing an implicit repair")
    _validate_table(bind, _ORDERS, exclude=_NEW_ORDER_COLUMNS)
    _validate_table(bind, _REFUNDS)
    with op.batch_alter_table("payment_orders") as batch:
        batch.add_column(sa.Column("idempotency_key", sa.String(64), nullable=True))
        batch.add_column(sa.Column("expires_at", sa.DateTime(), nullable=True))
        batch.create_unique_constraint(_IDEMPOTENCY_UNIQUE, ["idempotency_key"])
    _EVENTS.create(bind)
    validate_payment_tables(bind)


def downgrade_payment_tables(op) -> None:
    """显式退回0.2资金表，删除新增事件表、幂等键和截止时间，保留原支付/退款记录。

    此操作会移除事件、幂等键和截止时间证据；只供隔离验收或数据审核后的受控降级。
    """
    bind = _connection(op)
    validate_payment_tables(bind)
    inspector = sa.inspect(bind)
    keys = [key for key in inspector.get_unique_constraints("payment_orders")
            if key["column_names"] == ["idempotency_key"]]
    indexes = [index for index in inspector.get_indexes("payment_orders")
               if index["unique"] and index["column_names"] == ["idempotency_key"]]
    # SQLite可能来自ORM的未命名约束，batch命名规则只用于定位并移除该列的唯一性。
    naming = {"uq": "uq_%(table_name)s_%(column_0_name)s"}
    with op.batch_alter_table("payment_orders", naming_convention=naming) as batch:
        for key in keys:
            batch.drop_constraint(key["name"] or _IDEMPOTENCY_UNIQUE, type_="unique")
        for index in indexes:
            if not index.get("duplicates_constraint"):
                batch.drop_index(index["name"])
        batch.drop_column("idempotency_key")
        batch.drop_column("expires_at")
    _EVENTS.drop(bind)
    _validate_table(bind, _ORDERS, exclude=_NEW_ORDER_COLUMNS)
    _validate_table(bind, _REFUNDS)
