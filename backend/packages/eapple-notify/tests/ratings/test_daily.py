"""真实 SQLite 验证每日持久调度、历史与 outbox 原子性。"""

import asyncio
from datetime import UTC, date, datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from zoneinfo import ZoneInfo

import httpx
import pytest
from fastapi import FastAPI
from sqlalchemy import MetaData, event, insert, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_apple_notify.ratings import (
    AppleRating,
    AppleRatingClient,
    AppleRatingsConfig,
    RatingApp,
    RatingCollectionError,
    RatingMonitor,
    RatingStore,
    build_rating_tables,
    install_rating_monitor,
)
from dwy_apple_notify.ratings.formatting import comparison_dates, digest_content, split_content


@pytest.fixture
async def storage(tmp_path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'ratings.db'}")
    metadata = MetaData()
    tables = build_rating_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    clock = SimpleNamespace(value=datetime(2026, 11, 6, 0, 30, tzinfo=UTC).timestamp())
    sessions = async_sessionmaker(engine)
    yield sessions, tables, clock
    await engine.dispose()


def setup(storage, **changes):
    sessions, tables, clock = storage
    config = AppleRatingsConfig(apps={"123": RatingApp(name="Demo")}, **changes)
    client = SimpleNamespace(get_rating=AsyncMock(return_value=AppleRating(count=12, average=4.7)))
    store = RatingStore(sessions, tables, clock=lambda: clock.value)
    monitor = RatingMonitor(config, store, client, clock=lambda: clock.value)
    return config, client, store, monitor


async def rows(storage, table):
    async with storage[0]() as db:
        return (await db.execute(select(table))).mappings().all()


async def test_first_daily_digest_waits_until_due_and_restart_deduplicates(storage):
    config, client, store, monitor = setup(storage)
    storage[2].value -= 1
    assert await monitor.run_once() == 0
    client.get_rating.assert_not_awaited()
    storage[2].value += 1
    assert await monitor.run_once() == 1
    assert client.get_rating.await_count == 2
    deliveries = await rows(storage, storage[1].deliveries)
    assert len(deliveries) == 1
    content = deliveries[0]["payload"]["content"]
    assert "2026-11-06" in content and "cn" in content and "us" in content
    assert "首次采集" in content and "含仅打星和文字评价附带的星级" in content
    restart = RatingMonitor(config, store, client, clock=lambda: storage[2].value)
    assert await restart.run_once() == 0
    assert client.get_rating.await_count == 2
    snapshots = await rows(storage, storage[1].snapshots)
    assert len(snapshots) == 2 and all(row["count"] == 12 for row in snapshots)


async def test_failed_item_is_finalized_once_without_destroying_history(storage):
    _, client, _, monitor = setup(storage)
    assert await monitor.run_once() == 1
    storage[2].value += 86400
    client.get_rating.side_effect = [
        RatingCollectionError("rating_request_error"),
        AppleRating(count=13, average=4.8),
    ]
    assert await monitor.run_once() == 1
    assert await monitor.run_once() == 0
    assert client.get_rating.await_count == 4
    snapshots = await rows(storage, storage[1].snapshots)
    failed = [row for row in snapshots if row["status"] == "error"]
    assert len(failed) == 1 and failed[0]["count"] is None and failed[0]["average"] is None
    content = (await rows(storage, storage[1].deliveries))[-1]["payload"]["content"]
    assert "数据暂不可用" in content and "评分数净变化 +1" in content and "secret" not in content
    storage[2].value += 86400
    client.get_rating.side_effect = None
    assert await monitor.run_once() == 1
    content = (await rows(storage, storage[1].deliveries))[-1]["payload"]["content"]
    assert "基准日采集失败" in content


async def test_deep_json_failure_finalizes_once_and_other_apps_continue(storage):
    config = AppleRatingsConfig(
        apps={"123": {"name": "Invalid"}, "456": {"name": "Valid"}}, territories=("cn",)
    )
    requests = []

    def handler(request):
        requests.append(request)
        if request.url.params["id"] == "123":
            return httpx.Response(200, content="[" * 2000 + "0" + "]" * 2000)
        return httpx.Response(
            200,
            json={
                "resultCount": 1,
                "results": [{"trackId": 456, "userRatingCount": 12, "averageUserRating": 4.7}],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as http:
        client = AppleRatingClient(config, client=http)
        store = RatingStore(storage[0], storage[1], clock=lambda: storage[2].value)
        monitor = RatingMonitor(config, store, client, clock=lambda: storage[2].value)
        assert await monitor.run_once() == 1
        assert await monitor.run_once() == 0
    assert len(requests) == 2
    snapshots = await rows(storage, storage[1].snapshots)
    assert {row["app_id"]: row["status"] for row in snapshots} == {"123": "error", "456": "ok"}
    deliveries = await rows(storage, storage[1].deliveries)
    assert len(deliveries) == 1
    content = deliveries[0]["payload"]["content"]
    assert "数据暂不可用" in content and "当前评分总数：12" in content


@pytest.mark.parametrize(
    "day,month",
    [
        (date(2024, 3, 31), date(2024, 2, 29)),
        (date(2025, 3, 31), date(2025, 2, 28)),
        (date(2026, 1, 31), date(2025, 12, 31)),
        (date(2026, 5, 30), date(2026, 4, 30)),
    ],
)
def test_comparison_calendar_clamps_previous_month(day, month):
    assert comparison_dates(day)["月"] == month
    assert (day - comparison_dates(day)["日"]).days == 1
    assert (day - comparison_dates(day)["周"]).days == 7


async def test_exact_day_week_month_history_raw_precision_and_negative_changes(storage):
    config, client, _, monitor = setup(storage, territories=("cn",))
    snapshots = storage[1].snapshots
    async with storage[0].begin() as db:
        for day, count, average in [
            ("2026-11-05", 13, 4.6),
            ("2026-10-30", 10, 4.5),
            ("2026-10-06", 8, 4.7),
            ("2026-10-29", 99, 1),
        ]:
            await db.execute(
                insert(snapshots).values(
                    timezone=config.timezone,
                    app_id="123",
                    territory="cn",
                    day=day,
                    count=count,
                    average=average,
                    status="ok",
                    collected_at=int(storage[2].value),
                )
            )
    client.get_rating.return_value = AppleRating(count=12, average=4.7)
    assert await monitor.run_once() == 1
    content = (await rows(storage, storage[1].deliveries))[0]["payload"]["content"]
    assert "日变化：评分数净变化 -1，均分 +0.10" in content
    assert "周变化：评分数净变化 +2，均分 +0.20" in content
    assert "月变化：评分数净变化 +4，均分 +0.00" in content
    assert "0.199999" not in content and "2026-10-29" not in content


async def test_concurrent_workers_only_collect_once(storage):
    config, client, store, monitor = setup(storage)
    other = RatingMonitor(config, store, client, clock=lambda: storage[2].value)
    assert sorted(await asyncio.gather(monitor.run_once(), other.run_once())) == [0, 1]
    assert client.get_rating.await_count == 2


async def test_expired_and_replaced_lease_cannot_write_any_history_or_outbox(storage):
    config, _, store, _ = setup(storage)
    day = date(2026, 11, 6)
    token = await store.claim(config.timezone, day)
    storage[2].value += 301
    assert not await store.complete(config, day, token, {("123", "cn"): AppleRating(count=1, average=5)})
    replacement = await store.claim(config.timezone, day)
    await store.release(config.timezone, day, token)
    assert await store.renew(config.timezone, day, replacement)
    assert not await store.complete(config, day, token, {})
    assert await rows(storage, storage[1].snapshots) == []
    assert await rows(storage, storage[1].deliveries) == []


async def test_cancellation_releases_lease_and_new_monitor_recovers(storage):
    config, client, store, monitor = setup(storage)
    client.get_rating.side_effect = asyncio.CancelledError
    with pytest.raises(asyncio.CancelledError):
        await monitor.run_once()
    client.get_rating.side_effect = None
    recovered = RatingMonitor(config, store, client, clock=lambda: storage[2].value)
    assert await recovered.run_once() == 1


async def test_queue_retries_fixed_report_without_collecting(storage):
    sessions, tables, clock = storage
    config, client, _, _ = setup(storage)
    sender = AsyncMock(side_effect=[RuntimeError("secret"), "message-id"])
    runtime = install_rating_monitor(
        FastAPI(), config, sessions, tables, client=client, sender=sender, clock=lambda: clock.value
    )
    assert await runtime.monitor.run_once() == 1
    assert await runtime.queue.process_pending() == 0
    content = sender.call_args.args[0]
    clock.value += 10000
    assert await runtime.monitor.run_once() == 0
    assert await runtime.queue.process_pending() == 1
    assert sender.call_args.args[0] == content and client.get_rating.await_count == 2


async def test_timezone_change_isolates_history_and_downtime_does_not_backfill(storage):
    _, client, _, monitor = setup(storage, timezone="UTC", send_hour=0, send_minute=0)
    assert await monitor.run_once() == 1
    storage[2].value += 3 * 86400
    assert await monitor.run_once() == 1
    assert len(await rows(storage, storage[1].snapshots)) == 4
    _, other_client, _, other = setup(storage, timezone="Asia/Shanghai")
    assert await other.run_once() == 1
    content = (await rows(storage, storage[1].deliveries))[-1]["payload"]["content"]
    assert "首次采集" in content and other_client.get_rating.await_count == 2
    assert client.get_rating.await_count == 4


async def test_lifespan_preserves_host_state_and_external_client(storage):
    sessions, tables, clock = storage
    config, client, _, _ = setup(storage)
    client.aclose = AsyncMock()
    app = FastAPI()
    runtime = install_rating_monitor(
        app, config, sessions, tables, client=client, sender=AsyncMock(), clock=lambda: clock.value
    )
    assert app.state.dwy_rating_monitor is runtime
    with pytest.raises(ValueError, match="already installed"):
        install_rating_monitor(app, config, sessions, tables, client=client, sender=AsyncMock())
    async with app.router.lifespan_context(app):
        await asyncio.sleep(0.05)
    client.aclose.assert_not_awaited()


def test_prefix_and_utf16_chunking_keep_all_content():
    metadata = MetaData()
    assert build_rating_tables(metadata).snapshots.name == "app_store_ratings_snapshots"
    assert build_rating_tables(metadata, prefix="second").state.name == "second_state"
    with pytest.raises(ValueError):
        build_rating_tables(metadata, prefix="x; DROP")
    content = "长文😀\n" * 2000
    chunks = split_content(content)
    assert "".join(chunks) == content
    assert all(len(chunk.encode("utf-16-le")) // 2 <= 2000 for chunk in chunks)


def test_small_average_change_is_not_fabricated_or_lost():
    config = AppleRatingsConfig(apps={"123": {"name": "Demo"}}, territories=("cn",))
    today = date(2026, 11, 6)
    current = {("123", "cn"): AppleRating(count=10, average=4.7000001)}
    history = {("123", "cn", "2026-11-05"): {"status": "ok", "count": 10, "average": 4.7}}
    content = digest_content(config, today, 1793925000, current, history, {("123", "cn")})
    assert "变化小于显示精度" in content


async def test_retention_keeps_monthly_baseline_and_other_timezone(storage):
    config, _, store, _ = setup(storage, retention_days=32)
    async with storage[0].begin() as db:
        for zone, day in [
            (config.timezone, "2026-10-04"),
            (config.timezone, "2026-10-05"),
            (config.timezone, "2026-10-06"),
            ("UTC", "2026-10-01"),
        ]:
            await db.execute(
                insert(storage[1].snapshots).values(
                    timezone=zone,
                    day=day,
                    app_id="123",
                    territory="cn",
                    status="ok",
                    count=1,
                    average=5,
                    collected_at=1,
                )
            )
    await store.cleanup(config, date(2026, 11, 6))
    history = await rows(storage, storage[1].snapshots)
    assert {(row["timezone"], row["day"]) for row in history} == {
        (config.timezone, "2026-10-05"),
        (config.timezone, "2026-10-06"),
        ("UTC", "2026-10-01"),
    }


async def test_failed_outbox_insert_rolls_back_daily_state_and_snapshots(storage):
    config, client, _, monitor = setup(storage)
    engine = storage[0].kw["bind"]

    def reject_outbox(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO app_store_ratings_deliveries"):
            raise RuntimeError("simulated database write failure")

    event.listen(engine.sync_engine, "before_cursor_execute", reject_outbox)
    try:
        with pytest.raises(RuntimeError, match="simulated"):
            await monitor.run_once()
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", reject_outbox)
    assert await rows(storage, storage[1].snapshots) == []
    assert await rows(storage, storage[1].deliveries) == []
    state = (await rows(storage, storage[1].state))[0]
    assert not state["completed"] and state["lease_token"] is None
    assert await monitor.run_once() == 1
    assert client.get_rating.await_count == 4


async def test_two_late_daily_runs_finalize_cross_midnight_failures_once(storage):
    config, client, store, monitor = setup(storage, send_hour=23, send_minute=59)

    async def collect(app_id, territory):
        storage[2].value += 20
        return AppleRating(count=10, average=5)

    client.get_rating.side_effect = collect
    for index, day in enumerate((6, 7), start=1):
        storage[2].value = datetime(2026, 11, day, 15, 59, 50, tzinfo=UTC).timestamp()
        assert await monitor.run_once() == 1
        assert client.get_rating.await_count == index  # 跨日后 us 不再请求。
        assert await monitor.run_once() == 0  # 次日尚未到配置时间。
        assert await store.claim(config.timezone, date(2026, 11, day)) is None
    snapshots = await rows(storage, storage[1].snapshots)
    assert len(snapshots) == 4
    assert all(
        row["status"] == "error" and row["count"] is None and row["average"] is None for row in snapshots
    )
    assert {row["day"] for row in snapshots} == {"2026-11-06", "2026-11-07"}
    assert all(
        datetime.fromtimestamp(row["collected_at"], ZoneInfo(config.timezone)).day == int(row["day"][-2:]) + 1
        for row in snapshots
    )
    deliveries = await rows(storage, storage[1].deliveries)
    assert len(deliveries) == 2
    for row in deliveries:
        assert "采集跨日，本轮数据不可用" in row["payload"]["content"]
        assert "00:00:10+08:00" in row["payload"]["content"]
    assert all(row["completed"] for row in await rows(storage, storage[1].state))


async def test_cross_midnight_partial_success_is_discarded_before_late_failure_commit(storage):
    _, client, _, monitor = setup(storage, territories=("cn", "us", "jp"), send_hour=23, send_minute=59)
    storage[2].value = datetime(2026, 11, 6, 15, 59, 50, tzinfo=UTC).timestamp()
    durations = iter((5, 10, 0))

    async def collect(app_id, territory):
        storage[2].value += next(durations)
        return AppleRating(count=10, average=5)

    client.get_rating.side_effect = collect
    assert await monitor.run_once() == 1
    assert client.get_rating.await_count == 2
    snapshots = await rows(storage, storage[1].snapshots)
    assert len(snapshots) == 3
    assert all(row["status"] == "error" and row["count"] is None for row in snapshots)


async def test_store_rejects_cross_day_success_future_day_and_expired_late_failure(storage):
    config, _, store, _ = setup(storage)
    storage[2].value = datetime(2026, 11, 6, 15, 59, 50, tzinfo=UTC).timestamp()
    planned = date(2026, 11, 6)
    token = await store.claim(config.timezone, planned)
    storage[2].value += 20
    assert not await store.complete(config, planned, token, {("123", "cn"): AppleRating(count=1, average=5)})
    future = date(2026, 11, 8)
    future_token = await store.claim(config.timezone, future)
    assert not await store.complete(config, future, future_token, {("123", "cn"): None})
    storage[2].value += 301
    assert not await store.complete(config, planned, token, {("123", "cn"): None})
    assert await rows(storage, storage[1].snapshots) == []
    assert await rows(storage, storage[1].deliveries) == []


async def test_timezone_change_keeps_previously_generated_outbox_deliverable(storage):
    config, _, _, monitor = setup(storage)
    assert await monitor.run_once() == 1
    other_config = config.model_copy(update={"timezone": "UTC"})
    sender = AsyncMock(return_value="sent")
    runtime = install_rating_monitor(FastAPI(), other_config, storage[0], storage[1], sender=sender)
    try:
        assert await runtime.queue.process_pending() == 1
        sender.assert_awaited_once()
    finally:
        await runtime.monitor.client.aclose()


@pytest.mark.parametrize("disabled_days", [0, 3], ids=["partial-removal", "disabled-then-subset"])
async def test_revoked_app_suppresses_the_whole_fixed_digest(storage, disabled_days):
    sessions, tables, clock = storage
    original = AppleRatingsConfig(
        apps={"123": {"name": "Keep"}, "456": {"name": "Revoke"}}, territories=("cn",)
    )
    collector = SimpleNamespace(get_rating=AsyncMock(return_value=AppleRating(count=1, average=5)))
    prior_runtime = install_rating_monitor(
        FastAPI(), original, sessions, tables, client=collector, sender=AsyncMock(), clock=lambda: clock.value
    )
    assert await prior_runtime.monitor.run_once() == 1
    # 完全停用时不安装监控器，已有 outbox 保持到重新启用子集时再消费。
    clock.value += disabled_days * 86400
    current = original.model_copy(update={"apps": {"123": original.apps["123"]}})
    sender = AsyncMock(return_value="must-not-send")
    runtime = install_rating_monitor(
        FastAPI(), current, sessions, tables, client=collector, sender=sender, clock=lambda: clock.value
    )
    assert await runtime.queue.process_pending() == 0
    sender.assert_not_awaited()
    assert collector.get_rating.await_count == 2
    deliveries = await rows(storage, tables.deliveries)
    assert len(deliveries) == 1
    assert deliveries[0]["status"] == "suppressed" and deliveries[0]["payload"] == {}


async def test_multi_segment_digest_is_one_collection_with_all_apps(storage):
    sessions, tables, clock = storage
    apps = {str(index + 100): {"name": "演示😀" * 20 + str(index)} for index in range(20)}
    config = AppleRatingsConfig(apps=apps)
    client = SimpleNamespace(get_rating=AsyncMock(return_value=AppleRating(count=0, average=0)))
    runtime = install_rating_monitor(
        FastAPI(), config, sessions, tables, client=client, sender=AsyncMock(), clock=lambda: clock.value
    )
    assert await runtime.monitor.run_once() == 1
    deliveries = await rows(storage, tables.deliveries)
    content = "".join(row["payload"]["content"] for row in sorted(deliveries, key=lambda row: row["id"]))
    assert len(deliveries) > 1 and content.count("每日评分日报") == 1
    assert all(application.name in content for application in config.apps.values())
    assert len({row["id"].split(":")[0] for row in deliveries}) == 1
    assert client.get_rating.await_count == 40
    assert all(len(row["payload"]["content"].encode("utf-16-le")) // 2 <= 2000 for row in deliveries)
    assert all(set(row["payload"]["app_ids"]) == set(config.apps) for row in deliveries)


async def test_runtime_requires_a_destination_and_closes_owned_client(storage, monkeypatch):
    config, client, _, _ = setup(storage)
    with pytest.raises(ValueError, match="requires notifications"):
        install_rating_monitor(FastAPI(), config, storage[0], storage[1])
    client.aclose = AsyncMock()
    monkeypatch.setattr("dwy_apple_notify.ratings.runtime.AppleRatingClient", lambda options: client)
    app = FastAPI()
    runtime = install_rating_monitor(
        app, config, storage[0], storage[1], sender=AsyncMock(), clock=lambda: storage[2].value
    )
    async with app.router.lifespan_context(app):
        await asyncio.sleep(0.05)
    client.aclose.assert_awaited_once()
    assert runtime.queue.source == "app_store_ratings"


async def test_unexpected_collector_bug_propagates_without_finalizing_failure_digest(storage):
    _, client, _, monitor = setup(storage)
    client.get_rating.side_effect = TypeError("programming bug")
    with pytest.raises(TypeError, match="programming bug"):
        await monitor.run_once()
    assert await rows(storage, storage[1].snapshots) == []
    assert await rows(storage, storage[1].deliveries) == []
    assert (await rows(storage, storage[1].state))[0]["lease_token"] is None


async def test_old_history_does_not_masquerade_as_first_collection(storage):
    config, _, _, monitor = setup(storage)
    async with storage[0].begin() as db:
        await db.execute(
            insert(storage[1].snapshots).values(
                timezone=config.timezone,
                day="2026-10-20",
                app_id="123",
                territory="cn",
                status="ok",
                count=1,
                average=5,
                collected_at=1,
            )
        )
    assert await monitor.run_once() == 1
    content = (await rows(storage, storage[1].deliveries))[0]["payload"]["content"]
    assert content.count("首次采集") == 1  # us 首次，cn 已有历史但三个精确基准日均缺失。
    assert content.count("暂无历史数据") == 6
