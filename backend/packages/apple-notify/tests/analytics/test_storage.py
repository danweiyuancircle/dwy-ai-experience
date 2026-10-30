"""经营快照、租约与 outbox 必须由同一事务保护。"""

import asyncio
from datetime import date
from decimal import Decimal

import pytest
from dwyeapi.database import create_async_engine_factory, create_session_factory
from sqlalchemy import MetaData, event, select

from dwy_apple_notify.analytics.models import AnalyticsValue, AppleBusinessSnapshot
from dwy_apple_notify.analytics.storage import AnalyticsStore, build_analytics_tables


@pytest.fixture
async def storage(tmp_path):
    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'analytics.db'}")
    metadata = MetaData()
    tables = build_analytics_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    yield create_session_factory(engine), tables, engine
    await engine.dispose()


def snapshot(day=date(2026, 10, 25), value="3"):
    return AppleBusinessSnapshot(
        app_id="123",
        report_date=day,
        metrics={
            "sales_usd": AnalyticsValue(
                value=Decimal(value), status="available", currency="USD", source="Purchases"
            ),
        },
    )


async def rows(storage, name):
    async with storage[0]() as db:
        return (await db.execute(select(getattr(storage[1], name)))).mappings().all()


async def finish(store, token, *, issuer="issuer", day=date(2026, 10, 25), value="3"):
    return await store.complete(
        issuer,
        "123",
        token,
        [snapshot(day, value)],
        report_date=day,
        messages=[("daily", day, day, ["content"])],
        next_poll_at=2000,
    )


def test_table_definitions_are_injected_and_names_bounded():
    tables = build_analytics_tables(MetaData())
    assert tables.state.primary_key.columns.keys() == ["issuer_id", "app_id"]
    assert tables.snapshots.primary_key.columns.keys() == ["issuer_id", "app_id", "report_date"]
    assert tables.deliveries.c.app_id.type.length == 255
    with pytest.raises(ValueError):
        build_analytics_tables(MetaData(), "a" * 52)


async def test_snapshot_roundtrip_account_isolation_and_restart_dedup(storage):
    store = AnalyticsStore(*storage[:2], clock=lambda: 1000)
    token = await store.claim("issuer", "123", date(2026, 10, 25))
    assert await finish(store, token)
    assert (
        await AnalyticsStore(*storage[:2], clock=lambda: 1001).claim("issuer", "123", date(2026, 10, 25))
        is None
    )
    loaded = await store.load("issuer", "123", date(2026, 10, 25), date(2026, 10, 25))
    assert loaded == [snapshot()]
    assert await store.load("other", "123", date(2026, 10, 25), date(2026, 10, 25)) == []
    other = await store.claim("other", "123", date(2026, 10, 25))
    assert await finish(store, other, issuer="other")
    assert len(await rows(storage, "snapshots")) == 2
    assert len({r["app_id"] for r in await rows(storage, "deliveries")}) == 2


async def test_takeover_fences_complete_release_and_corrected_versions_replace(storage):
    clock = [1000]
    store = AnalyticsStore(*storage[:2], clock=lambda: clock[0])
    old = await store.claim("issuer", "123", date(2026, 10, 25), lease_seconds=10)
    assert await store.claim("issuer", "123", date(2026, 10, 25)) is None
    clock[0] += 10
    assert not await finish(store, old)
    new = await store.claim("issuer", "123", date(2026, 10, 25))
    await store.release("issuer", "123", old)
    assert (await rows(storage, "state"))[0]["lease_token"] == new
    assert await finish(store, new)
    clock[0] = 2000
    token = await store.claim("issuer", "123", date(2026, 10, 26))
    assert await finish(store, token, day=date(2026, 10, 26))
    assert len(await rows(storage, "deliveries")) == 2
    # 同一期间的重查可以修正快照，但不能重复入队。
    clock[0] = 3000
    token = await store.claim("issuer", "123", date(2026, 10, 27))
    assert await store.complete(
        "issuer",
        "123",
        token,
        [snapshot(value="4")],
        report_date=date(2026, 10, 27),
        messages=[("daily", date(2026, 10, 25), date(2026, 10, 25), ["changed"])],
        next_poll_at=4000,
    )
    assert len(await rows(storage, "deliveries")) == 2
    assert (await store.load("issuer", "123", date(2026, 10, 25), date(2026, 10, 25)))[0].metrics[
        "sales_usd"
    ].value == 4


async def test_outbox_failure_rolls_back_snapshot_and_schedule(storage):
    store = AnalyticsStore(*storage[:2], clock=lambda: 1000)
    token = await store.claim("issuer", "123", date(2026, 10, 25))

    def reject(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO app_store_analytics_deliveries"):
            raise RuntimeError("injected failure")

    event.listen(storage[2].sync_engine, "before_cursor_execute", reject)
    try:
        with pytest.raises(RuntimeError, match="injected failure"):
            await finish(store, token)
    finally:
        event.remove(storage[2].sync_engine, "before_cursor_execute", reject)
    assert await rows(storage, "snapshots") == []
    assert (await rows(storage, "state"))[0]["last_report_date"] is None


async def test_concurrent_workers_claim_once_and_cleanup_is_account_scoped(storage):
    store = AnalyticsStore(*storage[:2], clock=lambda: 1000)
    claims = await asyncio.gather(*(store.claim("issuer", "123", date(2026, 10, 25)) for _ in range(5)))
    assert sum(token is not None for token in claims) == 1
    assert await finish(store, next(token for token in claims if token))
    token = await store.claim("other", "123", date(2026, 10, 25))
    assert await finish(store, token, issuer="other")
    store.clock = lambda: 1000 + 401 * 86400
    assert await store.cleanup("issuer", 400) == 2
    assert len(await rows(storage, "snapshots")) == 1
    assert len(await rows(storage, "deliveries")) == 1


async def test_queue_orders_deterministic_message_parts(storage):
    from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue

    store = AnalyticsStore(*storage[:2], clock=lambda: 1000)
    token = await store.claim("issuer", "123", date(2026, 10, 25))
    assert await store.complete(
        "issuer",
        "123",
        token,
        [snapshot()],
        report_date=date(2026, 10, 25),
        messages=[("daily", date(2026, 10, 25), date(2026, 10, 25), ["first", "second", "third"])],
        next_poll_at=2000,
    )
    received = []

    async def sender(content):
        received.append(content)
        return "message-1"

    queue = SQLAlchemyDeliveryQueue(
        storage[0], storage[1].deliveries, sender, source="app_store_analytics", clock=lambda: 1000
    )
    assert await queue.process_pending() == 3
    assert received == ["first", "second", "third"]


async def test_failure_alert_is_fenced_deduplicated_and_does_not_block_success(storage):
    clock = [1000]
    store = AnalyticsStore(*storage[:2], clock=lambda: clock[0])
    day = date(2026, 10, 25)
    token = await store.claim("issuer", "123", day)
    assert await store.fail("issuer", "123", token, day, app_name="工具")
    assert await store.claim("issuer", "123", day) is None
    clock[0] += 60
    token = await store.claim("issuer", "123", day)
    assert await store.fail("issuer", "123", token, day, app_name="工具")
    alerts = await rows(storage, "deliveries")
    assert len(alerts) == 1 and alerts[0]["event_type"] == "analytics.collection_failed"
    assert (
        "ANALYTICS_COLLECTION_FAILED" in alerts[0]["payload"]["content"]
        and "2026-10-25" in alerts[0]["payload"]["content"]
    )
    clock[0] += 60
    old = await store.claim("issuer", "123", day, lease_seconds=1)
    clock[0] += 1
    token = await store.claim("issuer", "123", day)
    assert not await store.fail("issuer", "123", old, day, app_name="工具")
    assert await finish(store, token)
    assert sorted(r["event_type"] for r in await rows(storage, "deliveries")) == [
        "analytics.collection_failed",
        "analytics.daily",
    ]


async def test_failure_outbox_error_keeps_owned_lease_and_does_not_advance_schedule(storage):
    store = AnalyticsStore(*storage[:2], clock=lambda: 1000)
    day = date(2026, 10, 25)
    token = await store.claim("issuer", "123", day)

    def reject(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO app_store_analytics_deliveries"):
            raise RuntimeError("injected failure")

    event.listen(storage[2].sync_engine, "before_cursor_execute", reject)
    try:
        with pytest.raises(RuntimeError):
            await store.fail("issuer", "123", token, day, app_name="工具")
    finally:
        event.remove(storage[2].sync_engine, "before_cursor_execute", reject)
    row = (await rows(storage, "state"))[0]
    assert row["lease_token"] == token and row["next_poll_at"] == 0 and row["last_report_date"] is None
