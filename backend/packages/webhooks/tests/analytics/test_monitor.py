"""北京时间发送边界、七天重查、周报和取消的编排验收。"""

import asyncio
from datetime import date, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import pytest

from dwy_webhooks.analytics.models import AppleBusinessSnapshot
from dwy_webhooks.analytics.service import AnalyticsMonitor


def monitor(day="2026-10-26T08:30:00"):
    now = datetime.fromisoformat(day).replace(tzinfo=ZoneInfo("Asia/Shanghai")).timestamp()
    store = SimpleNamespace(
        clock=lambda: now,
        cleanup=AsyncMock(),
        claim=AsyncMock(return_value="lease"),
        load=AsyncMock(return_value=[]),
        complete=AsyncMock(return_value=True),
        release=AsyncMock(),
        fail=AsyncMock(),
    )
    client = SimpleNamespace(
        collect=AsyncMock(
            side_effect=lambda app, day: AppleBusinessSnapshot(app_id=app, report_date=day, metrics={})
        )
    )
    config = SimpleNamespace(
        apps={"123": SimpleNamespace(name="工具")},
        issuer_id="issuer",
        timezone="Asia/Shanghai",
        send_hour=8,
        send_minute=30,
        retention_days=400,
    )
    return AnalyticsMonitor(config, store, client), store, client


async def test_boundary_yesterday_seven_day_refresh_and_monday_weekly_without_history_flood():
    worker, store, client = monitor("2026-10-26T08:29:59")
    assert await worker.run_once() == 0
    client.collect.assert_not_awaited()
    worker, store, client = monitor()
    assert await worker.run_once() == 1
    assert [call.args[1] for call in client.collect.await_args_list] == [
        date(2026, 10, 19) + timedelta(days=i) for i in range(7)
    ]
    messages = store.complete.call_args.kwargs["messages"]
    assert [message[0] for message in messages] == ["daily", "weekly"]
    assert messages[0][1:3] == (date(2026, 10, 25), date(2026, 10, 25))
    assert messages[1][1:3] == (date(2026, 10, 19), date(2026, 10, 25))
    assert store.complete.call_args.kwargs["next_poll_at"] == int(
        datetime(2026, 10, 27, 8, 30, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp()
    )


async def test_historical_comparison_feedback_and_non_monday_daily_only():
    worker, store, client = monitor("2026-10-27T08:30:00")
    feedback = AsyncMock(return_value={"review_count": 2, "low_star_reviews": 1})
    worker.feedback = feedback
    assert await worker.run_once() == 1
    messages = store.complete.call_args.kwargs["messages"]
    assert len(messages) == 1 and messages[0][0] == "daily"
    assert "UTC" in "\n".join(messages[0][3])
    assert len(feedback.await_args_list) == 7
    assert store.load.await_count >= 1


@pytest.mark.parametrize("failure", [RuntimeError("secret"), asyncio.CancelledError()])
async def test_failed_or_cancelled_collection_releases_without_partial_writes(failure):
    worker, store, client = monitor()
    client.collect.side_effect = failure
    if isinstance(failure, asyncio.CancelledError):
        with pytest.raises(asyncio.CancelledError):
            await worker.run_once()
    else:
        assert await worker.run_once() == 0
    if isinstance(failure, asyncio.CancelledError):
        store.release.assert_awaited_once_with("issuer", "123", "lease")
        store.fail.assert_not_awaited()
    else:
        store.fail.assert_awaited_once_with("issuer", "123", "lease", date(2026, 10, 25), app_name="工具")
    store.complete.assert_not_awaited()


async def test_busy_or_completed_database_schedule_skips_collection():
    worker, store, client = monitor()
    store.claim.return_value = None
    assert await worker.run_once() == 0
    client.collect.assert_not_awaited()


async def test_optional_feedback_failure_does_not_block_core_analytics():
    worker, store, client = monitor()
    worker.feedback = AsyncMock(side_effect=RuntimeError("secret"))
    assert await worker.run_once() == 1
    snapshots = store.complete.call_args.args[3]
    assert all(s.metrics["review_count"].status == "unavailable" for s in snapshots)


async def test_daily_week_comparison_reads_persisted_history_without_extra_requests():
    from dwy_webhooks.analytics.models import AnalyticsValue

    worker, store, client = monitor("2026-10-27T08:30:00")
    store.load.return_value = [
        AppleBusinessSnapshot(
            app_id="123",
            report_date=date(2026, 10, 19),
            metrics={
                "first_downloads": AnalyticsValue(value=2, status="available", source="Apple"),
            },
        )
    ]
    client.collect.side_effect = lambda app, day: AppleBusinessSnapshot(
        app_id=app,
        report_date=day,
        metrics={
            "first_downloads": AnalyticsValue(value=3, status="available", source="Apple"),
        },
    )
    assert await worker.run_once() == 1
    assert client.collect.await_count == 7
    rendered = "\n".join(store.complete.call_args.kwargs["messages"][0][3])
    assert "较上周同日 +50.0%" in rendered


async def test_real_store_restart_refreshes_corrections_without_historical_send_flood(tmp_path):
    from dwyeapi.database import create_async_engine_factory, create_session_factory
    from sqlalchemy import MetaData, select

    from dwy_webhooks.analytics.storage import AnalyticsStore, build_analytics_tables

    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'real.db'}")
    metadata, clock = (
        MetaData(),
        [datetime(2026, 10, 26, 8, 30, tzinfo=ZoneInfo("Asia/Shanghai")).timestamp()],
    )
    tables = build_analytics_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = create_session_factory(engine)
    worker, fake_store, client = monitor()
    worker.store = AnalyticsStore(sessions, tables, clock=lambda: clock[0])
    try:
        assert await worker.run_once() == 1
        count = client.collect.await_count
        worker.store = AnalyticsStore(sessions, tables, clock=lambda: clock[0])
        assert await worker.run_once() == 0
        assert client.collect.await_count == count
        clock[0] += 86400
        assert await worker.run_once() == 1
        async with sessions() as db:
            stored = (await db.execute(select(tables.snapshots))).all()
            queued = (await db.execute(select(tables.deliveries))).mappings().all()
        assert len(stored) == 8  # Seven-day replacement window, one new day.
        assert sorted(row["event_type"] for row in queued) == [
            "analytics.daily",
            "analytics.daily",
            "analytics.weekly",
        ]
    finally:
        await engine.dispose()
