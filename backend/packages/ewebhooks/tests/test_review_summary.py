"""摘要不导出评论正文，缺少完整采集基线时不伪造零评论。"""

from datetime import UTC, date, datetime

import pytest
from dwyeapi.database import create_async_engine_factory, create_session_factory
from sqlalchemy import MetaData

from dwy_webhooks.reviews.models import AppleReview
from dwy_webhooks.reviews.storage import ReviewStore, build_review_tables


@pytest.fixture
async def summary_store(tmp_path):
    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'summary.db'}")
    metadata = MetaData()
    tables = build_review_tables(metadata)
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    now = datetime(2026, 10, 28, tzinfo=UTC).timestamp()
    store = ReviewStore(create_session_factory(engine), tables, clock=lambda: now)
    yield store
    await engine.dispose()


async def test_summary_is_unavailable_without_completed_baseline(summary_store):
    assert await summary_store.summary("123", date(2026, 10, 25)) == {}


async def test_summary_counts_only_requested_app_and_utc_creation_day(summary_store):
    store = summary_store
    reviews = [AppleReview(
        id=identifier, rating=rating, title="private title", body="private body",
        reviewer_nickname="private name", territory="CHN", created_at=created,
    ) for identifier, rating, created in [
        ("first", 2, datetime(2026, 10, 25, tzinfo=UTC)),
        ("second", 5, datetime(2026, 10, 25, 23, 59, tzinfo=UTC)),
        ("next-day", 1, datetime(2026, 10, 26, tzinfo=UTC)),
    ]]
    token = await store.claim("123")
    await store.complete("123", token, reviews, app_name="Test", poll_interval_seconds=3600,
                         retention_days=30)
    assert await store.summary("123", date(2026, 10, 25)) == {"review_count": 2, "low_star_reviews": 1}
    assert await store.summary("123", date(2026, 10, 24)) == {"review_count": 0, "low_star_reviews": 0}
    assert await store.summary("456", date(2026, 10, 25)) == {}


async def test_summary_does_not_call_purged_or_future_days_zero(summary_store):
    store = summary_store
    token = await store.claim("123")
    await store.complete("123", token, [], app_name="Test", poll_interval_seconds=3600, retention_days=30)
    assert await store.summary("123", date(2026, 1, 1)) == {}
    assert await store.summary("123", date(2026, 10, 28)) == {}
