"""通用投递队列使用外部资源，保持租约、失败重试与来源隔离。"""

import pytest
from dwyeapi.database import create_async_engine_factory, create_session_factory
from sqlalchemy import MetaData, select, update

from dwy_webhooks.delivery import DeliveryPolicy, SQLAlchemyDeliveryQueue, build_delivery_table
from dwy_webhooks.errors import WebhookDeliveryError
from dwy_webhooks.events import WebhookEvent


@pytest.fixture
async def storage(tmp_path):
    """测试独立数据库只由调用方创建；队列不能初始化或关闭共享引擎。"""
    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{tmp_path / 'delivery.db'}")
    metadata = MetaData()
    table = build_delivery_table(metadata, "events")
    async with engine.begin() as connection:
        await connection.run_sync(metadata.create_all)
    sessions = create_session_factory(engine)
    yield sessions, table
    await engine.dispose()


def event(source="app_store_connect", scope="app-1", event_id="event-1"):
    """提供与具体平台 SDK 无关的已验签事件。"""
    return WebhookEvent(source, scope, event_id, "state.changed", "safe content")


async def read(storage):
    """通过实际数据库观察状态，避免以模拟调用代替投递事实。"""
    sessions, table = storage
    async with sessions() as session:
        return [dict(row) for row in (await session.execute(select(table))).mappings()]


async def test_injected_queue_deduplicates_and_isolates_applications(storage):
    calls = []

    async def sender(content):
        calls.append(content)
        return "123456"

    queue = SQLAlchemyDeliveryQueue(*storage, sender, source="app_store_connect", clock=lambda: 100)
    assert await queue(event()) is True
    assert await queue(event()) is False
    assert await queue(event(scope="app-2")) is True
    assert await queue.process_pending() == 2
    assert len(calls) == 2 and {row["status"] for row in await read(storage)} == {"sent"}
    with pytest.raises(ValueError, match="source"):
        await queue(event(source="resend"))


async def test_retry_after_and_safe_failure_survive_a_new_consumer(storage):
    async def failed(content):
        raise WebhookDeliveryError("discord_rate_limited", retry_after=15.5)

    queue = SQLAlchemyDeliveryQueue(*storage, failed, source="app_store_connect", clock=lambda: 100)
    await queue(event())
    assert await queue.process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "retry" and row["next_attempt_at"] == 116 and row["attempts"] == 1

    async def sent(content):
        return "123456"

    fresh = SQLAlchemyDeliveryQueue(*storage, sent, source="app_store_connect", clock=lambda: 116)
    assert await fresh.process_pending() == 1
    assert (await read(storage))[0]["status"] == "sent"


async def test_app_selection_also_suppresses_previously_queued_messages(storage):
    calls = []

    async def sender(content):
        calls.append(content)
        return "123456"

    old = SQLAlchemyDeliveryQueue(*storage, sender, source="app_store_connect")
    await old(event(scope="selected"))
    await old(event(scope="removed"))
    queue = SQLAlchemyDeliveryQueue(
        *storage, sender, source="app_store_connect", allowed_scopes={"selected"}
    )
    assert await queue.process_pending() == 1
    rows = {row["app_id"]: row for row in await read(storage)}
    assert rows["selected"]["status"] == "sent"
    assert rows["removed"]["status"] == "suppressed"
    assert rows["removed"]["payload"] == {}
    assert len(calls) == 1
    assert await queue.process_pending() == 0


async def test_active_lease_is_not_stolen_and_expiry_recovers(storage):
    async def sender(content):
        return "123456"

    queue = SQLAlchemyDeliveryQueue(*storage, sender, source="app_store_connect", clock=lambda: 100)
    await queue(event())
    sessions, table = storage
    async with sessions.begin() as session:
        await session.execute(update(table).values(status="processing", lease_token="old", lease_until=101))
    assert await queue.process_pending() == 0
    queue.clock = lambda: 102
    assert await queue.process_pending() == 1


async def test_stale_sender_cannot_complete_a_new_lease(storage):
    sessions, table = storage

    async def sender(content):
        async with sessions.begin() as session:
            await session.execute(update(table).values(lease_token="replacement"))
        return "123456"

    queue = SQLAlchemyDeliveryQueue(*storage, sender, source="app_store_connect", clock=lambda: 100)
    await queue(event())
    assert await queue.process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "processing" and row["lease_token"] == "replacement"


async def test_permanent_failure_stops_retrying_and_policy_is_injected(storage):
    async def failed(content):
        raise WebhookDeliveryError("discord_http_error", permanent=True)

    queue = SQLAlchemyDeliveryQueue(*storage, failed, source="app_store_connect",
                                   policy=DeliveryPolicy(max_attempts=2), clock=lambda: 100)
    await queue(event())
    await queue.process_pending()
    assert (await read(storage))[0]["status"] == "dead"
    assert await queue.process_pending() == 0


async def test_unexpected_sender_failure_is_bounded_and_never_persisted_raw(storage):
    async def failed(content):
        raise RuntimeError("https://discord.com/api/webhooks/123/not-a-real-secret")

    queue = SQLAlchemyDeliveryQueue(*storage, failed, source="app_store_connect",
                                   policy=DeliveryPolicy(max_attempts=1), clock=lambda: 100)
    await queue(event())
    assert await queue.process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "dead" and row["attempts"] == 1
    assert row["error_code"] == "webhook_delivery_error"
    assert "not-a-real-secret" not in str(row)


def test_legacy_asc_table_shape_is_preserved_without_registration_side_effects():
    metadata = MetaData()
    table = build_delivery_table(metadata, "asc_notification_deliveries", scope_length=20)
    assert set(metadata.tables) == {"asc_notification_deliveries"}
    assert tuple(table.c.keys()) == (
        "app_id", "id", "event_type", "payload", "status", "attempts", "next_attempt_at",
        "lease_until", "lease_token", "error_code", "message_id",
    )
    assert table.c.app_id.type.length == 20 and table.c.id.type.length == 128
