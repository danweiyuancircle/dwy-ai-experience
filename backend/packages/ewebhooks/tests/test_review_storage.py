"""评论同步使用真实数据库验证租约、原子 outbox 与内容保留窗口。"""

import asyncio
from datetime import UTC, datetime

import pytest
from dwyeapi.database import create_async_engine_factory, create_session_factory
from sqlalchemy import MetaData, event, select

from dwy_webhooks.reviews.models import AppleReview
from dwy_webhooks.reviews.storage import ReviewStore, build_review_tables

DAY = 86400
NOW = 1800000000


@pytest.fixture
async def storage(tmp_path):
    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'reviews.db'}")
    metadata = MetaData()
    tables = build_review_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = create_session_factory(engine)
    yield sessions, tables, engine
    await engine.dispose()


def review(review_id="review-1", *, age=1, body="A", **values):
    return AppleReview(
        id=review_id,
        rating=5,
        title="评价标题",
        body=body,
        reviewer_nickname="昵称",
        created_at=datetime.fromtimestamp(NOW - age * DAY, UTC),
        territory="CHN",
        **values,
    )


async def rows(storage, name):
    sessions, tables, _ = storage
    async with sessions() as db:
        return [dict(row) for row in (await db.execute(select(getattr(tables, name)))).mappings()]


async def complete(store, app_id="123", reviews=None, **kwargs):
    token = await store.claim(app_id, poll_interval_seconds=kwargs.get("poll_interval_seconds", 3600))
    assert token is not None
    return await store.complete(
        app_id,
        token,
        reviews or [],
        app_name="测试应用",
        poll_interval_seconds=kwargs.get("poll_interval_seconds", 3600),
        retention_days=kwargs.get("retention_days", 30),
    )


def test_table_definition_is_injected_and_names_are_bounded():
    metadata = MetaData()
    tables = build_review_tables(metadata, prefix="test_reviews")
    assert set(metadata.tables) == {"test_reviews_state", "test_reviews_reviews", "test_reviews_deliveries"}
    assert tables.deliveries.c.created_at.nullable is False
    for prefix in ("x" * 53, "bad-name", "", "a;DROP"):
        with pytest.raises(ValueError):
            build_review_tables(MetaData(), prefix=prefix)


async def test_first_sync_only_records_recent_baseline_and_one_summary(storage):
    store = ReviewStore(*storage[:2], clock=lambda: NOW)
    assert await complete(store, reviews=[review(), review("old", age=31)])
    assert [row["id"] for row in await rows(storage, "reviews")] == ["review-1"]
    deliveries = await rows(storage, "deliveries")
    assert len(deliveries) == 1
    assert deliveries[0]["created_at"] == NOW
    assert "评价标题" not in deliveries[0]["payload"]["content"]
    state = (await rows(storage, "state"))[0]
    assert state["initialized"] is True and state["last_success_at"] == NOW
    assert state["retention_cutoff_at"] == NOW - 30 * DAY
    assert state["next_poll_at"] == NOW + 3600 and state["lease_token"] is None


async def test_new_and_changed_reviews_notify_once_and_a_b_a_is_not_lost(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    assert await complete(store, reviews=[review()])
    for batch in (
        [review(), review("new")],
        [review(), review("new")],
        [review(body="B"), review("new")],
        [review(), review("new")],
    ):
        clock[0] += 3600
        assert await complete(store, reviews=batch)
    deliveries = await rows(storage, "deliveries")
    assert len(deliveries) == 4
    assert len({row["id"] for row in deliveries}) == 4
    assert len(await rows(storage, "reviews")) == 2
    assert all(row["created_at"] == NOW - DAY for row in deliveries if row["created_at"] != NOW)


@pytest.mark.parametrize(
    "field,value",
    [
        ("rating", 3),
        ("title", "新标题"),
        ("body", "新正文"),
        ("reviewer_nickname", "新昵称"),
        ("territory", "USA"),
    ],
)
async def test_fingerprint_covers_all_observable_review_content(storage, field, value):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    original = review()
    assert await complete(store, reviews=[original])
    clock[0] += 3600
    assert await complete(store, reviews=[original.model_copy(update={field: value})])
    assert len(await rows(storage, "deliveries")) == 2


@pytest.mark.parametrize("days", [30, 60, 90])
async def test_cleanup_removes_expired_reviews_and_payloads_without_fetch(storage, days):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    assert await complete(store, reviews=[review(age=days - 1)], retention_days=days)
    clock[0] += 3600
    assert await complete(store, reviews=[review(age=days - 1, body="edited")], retention_days=days)
    clock[0] += 2 * DAY
    assert await store.cleanup(days) == 2  # One review and its review notification payload.
    assert await rows(storage, "reviews") == []
    assert len(await rows(storage, "deliveries")) == 1  # Baseline has no review content.
    state_before = await rows(storage, "state")
    assert await store.cleanup(days) == 0
    assert await rows(storage, "state") == state_before
    assert await complete(store, reviews=[review(age=days - 1, body="edited")], retention_days=days)
    assert await rows(storage, "reviews") == []
    assert len(await rows(storage, "deliveries")) == 1


async def test_cleanup_expires_baseline_summary_by_its_own_timestamp(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    assert await complete(store, reviews=[])
    clock[0] += 31 * DAY
    assert await store.cleanup(30) == 1
    assert await rows(storage, "deliveries") == []
    assert (await rows(storage, "state"))[0]["initialized"] is True


async def test_restart_keeps_schedule_and_interval_changes_recompute_due_time(storage):
    assert await complete(ReviewStore(*storage[:2], clock=lambda: NOW))
    fresh = ReviewStore(*storage[:2], clock=lambda: NOW + 100)
    assert await fresh.claim("123") is None
    fresh.clock = lambda: NOW + 1800
    assert await fresh.claim("123", poll_interval_seconds=7200) is None
    assert await fresh.claim("123", poll_interval_seconds=1800) is not None


async def test_longer_interval_does_not_poll_at_old_due_time(storage):
    assert await complete(ReviewStore(*storage[:2], clock=lambda: NOW))
    fresh = ReviewStore(*storage[:2], clock=lambda: NOW + 3600)
    assert await fresh.claim("123", poll_interval_seconds=7200) is None
    fresh.clock = lambda: NOW + 7200
    assert await fresh.claim("123", poll_interval_seconds=7200) is not None


async def test_lease_excludes_workers_and_stale_complete_or_release_cannot_mutate(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    old_token = await store.claim("123", lease_seconds=10)
    assert old_token is not None and await store.claim("123") is None
    clock[0] += 10
    assert (
        await store.complete(
            "123",
            old_token,
            [review()],
            app_name="应用",
            poll_interval_seconds=3600,
            retention_days=30,
        )
        is False
    )
    new_token = await store.claim("123")
    assert new_token is not None and new_token != old_token
    await store.release("123", old_token)
    assert (await rows(storage, "state"))[0]["lease_token"] == new_token
    assert (
        await store.complete(
            "123",
            old_token,
            [review()],
            app_name="应用",
            poll_interval_seconds=3600,
            retention_days=30,
        )
        is False
    )
    assert await rows(storage, "reviews") == [] and await rows(storage, "deliveries") == []


async def test_release_schedules_retry_without_resetting_baseline(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    token = await store.claim("123")
    await store.release("123", token, retry_seconds=60)
    clock[0] += 59
    assert await store.claim("123") is None
    clock[0] += 1
    assert await store.claim("123") is not None


async def test_outbox_insert_failure_rolls_back_review_and_success_state(storage):
    sessions, tables, engine = storage
    store = ReviewStore(sessions, tables, clock=lambda: NOW)
    token = await store.claim("123")

    def reject_outbox(connection, cursor, statement, parameters, context, executemany):
        if statement.startswith("INSERT INTO app_store_review_deliveries"):
            raise RuntimeError("injected database write failure")

    event.listen(engine.sync_engine, "before_cursor_execute", reject_outbox)
    try:
        with pytest.raises(RuntimeError, match="injected database write failure"):
            await store.complete(
                "123",
                token,
                [review()],
                app_name="应用",
                poll_interval_seconds=3600,
                retention_days=30,
            )
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", reject_outbox)
    assert await rows(storage, "reviews") == [] and await rows(storage, "deliveries") == []
    state = (await rows(storage, "state"))[0]
    assert state["initialized"] is False and state["last_success_at"] is None
    assert state["retention_cutoff_at"] is None
    assert state["lease_token"] == token


async def test_applications_have_independent_baselines_and_leases(storage):
    store = ReviewStore(*storage[:2], clock=lambda: NOW)
    assert await complete(store, "123", [review()])
    assert await complete(store, "456", [review()])
    assert len(await rows(storage, "reviews")) == 2
    assert len(await rows(storage, "deliveries")) == 2


async def test_concurrent_workers_obtain_exactly_one_lease(storage):
    workers = [ReviewStore(*storage[:2], clock=lambda: NOW) for _ in range(8)]
    claims = await asyncio.gather(*(worker.claim("123") for worker in workers))
    assert len([token for token in claims if token is not None]) == 1
    assert len(await rows(storage, "state")) == 1


async def test_review_at_retention_boundary_survives_until_next_second(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    assert await complete(store, reviews=[review(age=30)])
    assert len(await rows(storage, "reviews")) == 1
    assert await store.cleanup(30) == 0
    clock[0] += 1
    assert await store.cleanup(30) == 1
    assert await rows(storage, "reviews") == []


@pytest.mark.parametrize(
    "kwargs",
    [
        {"poll_interval_seconds": 0},
        {"poll_interval_seconds": True},
        {"poll_interval_seconds": 604801},
        {"lease_seconds": 0},
        {"lease_seconds": 3601},
    ],
)
async def test_invalid_schedule_budgets_are_rejected_before_database_changes(storage, kwargs):
    store = ReviewStore(*storage[:2], clock=lambda: NOW)
    with pytest.raises(ValueError):
        await store.claim("123", **kwargs)
    assert await rows(storage, "state") == []


async def test_expanding_retention_silently_backfills_history_and_keeps_new_and_edit_alerts(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    assert await complete(store, reviews=[review("known", age=10), review("history", age=60)])
    clock[0] += 3600
    assert await complete(
        store,
        reviews=[review("known", age=10, body="changed"), review("history", age=60), review("new", age=30)],
        retention_days=90,
    )
    assert {row["id"] for row in await rows(storage, "reviews")} == {"known", "history", "new"}
    deliveries = await rows(storage, "deliveries")
    assert sorted(row["event_type"] for row in deliveries) == [
        "review.created",
        "review.updated",
        "reviews.baseline",
    ]
    assert all("history" not in row["payload"]["content"] for row in deliveries)
    clock[0] += 3600
    assert await complete(store, reviews=[review("history", age=60, body="later edit")], retention_days=90)
    assert len(await rows(storage, "deliveries")) == 4
    assert (await rows(storage, "state"))[0]["retention_cutoff_at"] == NOW - 30 * DAY


async def test_expanding_retention_after_purge_rebuilds_history_without_new_notification(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    old_review = review("history", age=60)
    assert await complete(store, reviews=[old_review], retention_days=90)
    clock[0] += 3600
    assert await store.cleanup(30) == 1
    assert await complete(store, reviews=[old_review], retention_days=30)
    assert await rows(storage, "reviews") == []
    clock[0] += 3600
    assert await complete(store, reviews=[old_review], retention_days=90)
    assert len(await rows(storage, "reviews")) == 1
    assert len(await rows(storage, "deliveries")) == 1


async def test_independent_cleanup_preserves_notification_floor_when_fetch_fails(storage):
    clock = [NOW]
    store = ReviewStore(*storage[:2], clock=lambda: clock[0])
    old_review = review("history", age=60)
    assert await complete(store, reviews=[old_review], retention_days=90)
    clock[0] += 3600
    state_before = (await rows(storage, "state"))[0]
    assert await store.cleanup(30) == 1
    state_after = (await rows(storage, "state"))[0]
    assert state_after["last_success_at"] == state_before["last_success_at"]
    assert state_after["next_poll_at"] == state_before["next_poll_at"]
    assert state_after["retention_cutoff_at"] == clock[0] - 30 * DAY
    assert await complete(store, reviews=[old_review], retention_days=90)
    assert len(await rows(storage, "reviews")) == 1
    assert len(await rows(storage, "deliveries")) == 1
