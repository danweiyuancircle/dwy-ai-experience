"""资金迁移独立于宿主：首建、严格升级、保留旧数据及受控降级。"""

import subprocess
import sys
from datetime import datetime

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

from dwy_payment.events import PaymentEvent
from dwy_payment.migrations import (
    create_payment_tables,
    downgrade_payment_tables,
    upgrade_payment_tables,
    validate_payment_tables,
)
from dwy_payment.models import PaymentOrder
from dwy_payment.refunds.models import RefundRecord

_ORDER_NO = "a" * 32
_NOW = datetime(2026, 11, 2, 12)


@pytest.fixture
def database():
    """只提供迁移连接，不导入应用或建立全局ORM metadata中的其他表。"""
    engine = sa.create_engine("sqlite://")
    with engine.begin() as connection:
        yield connection, Operations(MigrationContext.configure(connection))
    engine.dispose()


def _legacy_tables(connection, *, omit_order: str | None = None, user_id_type=None) -> None:
    """0.2夹具独立构建，不通过待测降级函数制造旧库；兼容旧宿主唯一索引。"""
    metadata = sa.MetaData()
    for original in (PaymentOrder.__table__, RefundRecord.__table__):
        omitted = {"idempotency_key", "expires_at", omit_order} if original.name == "payment_orders" else set()
        columns = [
            sa.Column(
                column.name,
                user_id_type if column.name == "user_id" and user_id_type is not None else column.type,
                primary_key=column.primary_key,
                nullable=column.nullable,
                server_default=column.server_default.arg if column.server_default is not None else None,
            )
            for column in original.columns if column.name not in omitted
        ]
        table = sa.Table(original.name, metadata, *columns)
        for constraint in original.constraints:
            if isinstance(constraint, sa.CheckConstraint):
                table.append_constraint(sa.CheckConstraint(str(constraint.sqltext), name=constraint.name))
            if isinstance(constraint, sa.UniqueConstraint) and not omitted.intersection(constraint.columns.keys()):
                names = tuple(constraint.columns.keys())
                sa.Index(f"ix_{table.name}_{'_'.join(names)}", *(table.c[name] for name in names), unique=True)
        for index in original.indexes:
            sa.Index(index.name, *(table.c[name] for name in index.columns.keys()), unique=index.unique)
    metadata.create_all(connection)


def _order_row() -> dict:
    return {
        "id": 1, "uuid": "1" * 36, "user_id": "customer_1", "order_no": _ORDER_NO,
        "amount_fen": 1000, "channel": "wechat", "channel_trade_no": "transaction_1",
        "status": "success", "description": "original order", "refunded_fen": 100,
        "refund_no": "refund_1", "is_deleted": False, "created_at": _NOW, "updated_at": _NOW,
    }


def _refund_row() -> dict:
    return {
        "id": 1, "order_no": _ORDER_NO, "refund_no": "refund_1", "transaction_id": "transaction_1",
        "amount_fen": 1000, "refund_fen": 100, "source": "app", "provider_status": "SUCCESS",
        "verified_status": "SUCCESS", "business_processed": True, "manual_required": False,
        "version": 1, "created_at": _NOW, "updated_at": _NOW,
    }


def _table(connection, name: str) -> sa.Table:
    return sa.Table(name, sa.MetaData(), autoload_with=connection)


def test_fresh_install_creates_only_three_payment_tables(database):
    connection, op = database
    create_payment_tables(op)
    create_payment_tables(op)
    validate_payment_tables(connection)
    assert set(sa.inspect(connection).get_table_names()) == {"payment_orders", "payment_refunds", "payment_events"}


def test_migration_snapshot_matches_current_orm_metadata(database):
    connection, _op = database
    metadata = sa.MetaData()
    for model in (PaymentOrder, RefundRecord, PaymentEvent):
        model.__table__.to_metadata(metadata)
    metadata.create_all(connection)
    validate_payment_tables(connection)


def test_legacy_upgrade_preserves_records_then_downgrades_and_upgrades_again(database):
    connection, op = database
    business = sa.Table("host_orders", sa.MetaData(), sa.Column("id", sa.Integer(), primary_key=True))
    business.create(connection)
    connection.execute(business.insert().values(id=7))
    _legacy_tables(connection)
    connection.execute(_table(connection, "payment_orders").insert(), _order_row())
    connection.execute(_table(connection, "payment_refunds").insert(), _refund_row())
    before_order = dict(connection.execute(sa.select(_table(connection, "payment_orders"))).mappings().one())
    before_refund = dict(connection.execute(sa.select(_table(connection, "payment_refunds"))).mappings().one())

    upgrade_payment_tables(op)
    validate_payment_tables(connection)
    orders = _table(connection, "payment_orders")
    upgraded = dict(connection.execute(sa.select(orders)).mappings().one())
    assert upgraded.pop("idempotency_key") is None
    assert upgraded.pop("expires_at") is None
    assert upgraded == before_order
    assert dict(connection.execute(sa.select(_table(connection, "payment_refunds"))).mappings().one()) == before_refund
    connection.execute(orders.update().values(idempotency_key="stable-intent", expires_at=_NOW))
    connection.execute(_table(connection, "payment_events").insert().values(
        event_id="a" * 64, order_no=_ORDER_NO, payload={"event_type": "PAYMENT.SUCCESS"},
        created_at=_NOW, updated_at=_NOW,
    ))

    downgrade_payment_tables(op)
    assert "payment_events" not in sa.inspect(connection).get_table_names()
    assert not {"idempotency_key", "expires_at"}.intersection(
        column["name"] for column in sa.inspect(connection).get_columns("payment_orders")
    )
    assert dict(connection.execute(sa.select(_table(connection, "payment_orders"))).mappings().one()) == before_order
    assert dict(connection.execute(sa.select(_table(connection, "payment_refunds"))).mappings().one()) == before_refund
    assert connection.scalar(sa.select(business.c.id)) == 7

    upgrade_payment_tables(op)
    validate_payment_tables(connection)
    upgraded = dict(connection.execute(sa.select(_table(connection, "payment_orders"))).mappings().one())
    assert upgraded.pop("idempotency_key") is None
    assert upgraded.pop("expires_at") is None
    assert upgraded == before_order
    assert connection.scalar(sa.select(sa.func.count()).select_from(_table(connection, "payment_events"))) == 0
    assert connection.scalar(sa.select(business.c.id)) == 7


def test_upgraded_idempotency_is_unique_but_nullable(database):
    connection, op = database
    _legacy_tables(connection)
    upgrade_payment_tables(op)
    orders = _table(connection, "payment_orders")
    connection.execute(orders.insert(), {**_order_row(), "idempotency_key": "intent"})
    with pytest.raises(sa.exc.IntegrityError), connection.begin_nested():
        connection.execute(orders.insert(), {**_order_row(), "id": 2, "uuid": "2" * 36,
                                            "order_no": "b" * 32, "idempotency_key": "intent"})
    for number in (3, 4):
        connection.execute(orders.insert(), {**_order_row(), "id": number, "uuid": str(number) * 36,
                                            "order_no": str(number) * 32, "refund_no": None})


@pytest.mark.parametrize("operation", [create_payment_tables, upgrade_payment_tables])
def test_partial_existing_schema_is_not_silently_completed(database, operation):
    connection, op = database
    _legacy_tables(connection)
    _table(connection, "payment_refunds").drop(connection)
    with pytest.raises(RuntimeError):
        operation(op)
    assert set(sa.inspect(connection).get_table_names()) == {"payment_orders"}
    assert not {"idempotency_key", "expires_at"}.intersection(
        column["name"] for column in sa.inspect(connection).get_columns("payment_orders")
    )


def test_missing_legacy_column_fails_before_any_upgrade_ddl(database):
    connection, op = database
    _legacy_tables(connection, omit_order="channel_trade_no")
    with pytest.raises(RuntimeError, match="incompatible columns"):
        upgrade_payment_tables(op)
    assert "payment_events" not in sa.inspect(connection).get_table_names()
    assert not {"idempotency_key", "expires_at"}.intersection(
        column["name"] for column in sa.inspect(connection).get_columns("payment_orders")
    )


def test_incompatible_existing_type_is_not_silently_accepted(database):
    connection, op = database
    _legacy_tables(connection, user_id_type=sa.String(32))
    with pytest.raises(RuntimeError, match="payment_orders.user_id"):
        upgrade_payment_tables(op)


def test_incompatible_existing_nullability_is_rejected(database):
    connection, op = database
    _legacy_tables(connection)
    with op.batch_alter_table("payment_orders") as batch:
        batch.alter_column("channel_trade_no", existing_type=sa.String(64), nullable=False)
    with pytest.raises(RuntimeError, match="payment_orders.channel_trade_no"):
        upgrade_payment_tables(op)


def test_missing_unique_key_and_index_are_rejected(database):
    connection, op = database
    _legacy_tables(connection)
    op.drop_index("ix_payment_orders_order_no", table_name="payment_orders")
    with pytest.raises(RuntimeError, match="unique keys"):
        upgrade_payment_tables(op)
    assert "payment_events" not in sa.inspect(connection).get_table_names()


def test_fresh_install_does_not_hide_a_missing_existing_index(database):
    connection, op = database
    create_payment_tables(op)
    op.drop_index("ix_payment_events_order_no", table_name="payment_events")
    with pytest.raises(RuntimeError, match="required index"):
        create_payment_tables(op)


def test_downgrade_also_supports_orm_named_or_unnamed_unique_constraints(database):
    connection, op = database
    metadata = sa.MetaData()
    for model in (PaymentOrder, RefundRecord, PaymentEvent):
        model.__table__.to_metadata(metadata)
    metadata.create_all(connection)
    downgrade_payment_tables(op)
    upgrade_payment_tables(op)
    validate_payment_tables(connection)


@pytest.mark.parametrize("operation", [create_payment_tables, upgrade_payment_tables, downgrade_payment_tables])
def test_offline_mode_is_explicitly_rejected(operation):
    op = Operations(MigrationContext.configure(url="sqlite://", opts={"as_sql": True}))
    with pytest.raises(RuntimeError, match="online connection"):
        operation(op)


def test_migrations_work_when_host_modules_are_unavailable():
    code = """
import importlib.abc
import sys
class NoHost(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {'app', 'quant_billing', 'dwy_shared', 'dwy_auth'}:
            raise ImportError('host modules are unavailable')
sys.meta_path.insert(0, NoHost())
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations
from dwy_payment.migrations import create_payment_tables, validate_payment_tables
engine = sa.create_engine('sqlite://')
with engine.begin() as connection:
    create_payment_tables(Operations(MigrationContext.configure(connection)))
    validate_payment_tables(connection)
    assert set(sa.inspect(connection).get_table_names()) == {'payment_orders', 'payment_refunds', 'payment_events'}
"""
    result = subprocess.run([sys.executable, "-I", "-c", code], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
