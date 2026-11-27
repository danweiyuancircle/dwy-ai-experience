"""业务层显式提供展示预设；公共发送与队列不按来源识别业务。"""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from sqlalchemy import select
from test_delivery_queue import storage as storage

from dwy_notify import NotificationAppearance, NotificationConfig, Notifier
from dwy_notify.delivery import NotificationDeliveryError
from dwy_notify.events import NotificationEvent
from dwy_notify.integration import DiscordUsername, NotificationSettings, configured_notifier
from dwy_notify.relay import NotificationRelay
from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue

DISCORD = "discord://123456789012345678/offline-integration-token"
WEBHOOK = "https://discord.com/api/webhooks/123456789012345678/offline-integration-token"


@pytest.fixture
def post(monkeypatch):
    response = requests.Response()
    response.status_code = 200
    response._content = b'{"id": "123456789012345679"}'
    mocked = Mock(return_value=response)
    monkeypatch.setattr("dwy_notify._transport.post", mocked)
    return mocked


async def test_relay_uses_explicit_preset_for_unknown_source_and_deduplicates(post):
    notifier = Notifier(NotificationConfig(targets={"discord": DISCORD}))
    relay = NotificationRelay(notifier, appearance=NotificationAppearance(username="自有模块通知"))
    event = NotificationEvent("custom.source", "app-1", "event-1", "changed", "验收内容")
    assert await relay(event)
    assert not await relay(event)
    assert post.call_count == 1
    assert post.call_args.kwargs["json"]["username"] == "自有模块通知"


async def test_relay_does_not_accept_failed_target_and_retries_only_that_target():
    calls = []

    class Sender:
        targets = ("a", "b")

        def target_fingerprint(self, name):
            return name

        async def send(self, body, *, targets, default_appearance):
            name = targets[0]
            calls.append((name, default_appearance.username))
            success = name == "a" or len(calls) == 3
            return SimpleNamespace(deliveries=(SimpleNamespace(
                success=success, error_code="network_error", retry_after=None, permanent=False,
            ),))

    relay = NotificationRelay(Sender(), appearance=NotificationAppearance(username="自有模块通知"))
    event = NotificationEvent("custom.source", "app-1", "event-1", "changed", "内容")
    with pytest.raises(NotificationDeliveryError, match="network_error"):
        await relay(event)
    assert await relay(event)
    assert calls == [("a", "自有模块通知"), ("b", "自有模块通知"), ("b", "自有模块通知")]


async def test_queue_snapshots_explicit_preset_without_source_lookup(storage, post):
    notifier = Notifier(NotificationConfig(targets={"discord": DISCORD}))
    queue = SQLAlchemyDeliveryQueue(
        *storage, notifier=notifier, source="custom.source",
        appearance=NotificationAppearance(username="自有队列通知", avatar_url=None),
    )
    assert await queue(NotificationEvent("custom.source", "app-1", "event-1", "changed", "内容"))
    assert await queue.process_pending() == 1
    sessions, table = storage
    async with sessions() as session:
        row = (await session.execute(select(table))).mappings().one()
    assert row["payload"]["appearance"] == {"username": "自有队列通知", "avatar_url": None}
    assert row["status"] == "sent"
    assert post.call_args.kwargs["json"]["username"] == "自有队列通知"


async def test_legacy_implicit_name_preserves_fingerprint_and_module_priority(post):
    class SourceSettings(NotificationSettings):
        discord_username: DiscordUsername | None = None

    implicit = configured_notifier(SourceSettings(discord_webhook_url=WEBHOOK))
    explicit = configured_notifier(SourceSettings(
        discord_webhook_url=WEBHOOK, discord_username="Apple 应用通知",
    ))
    assert implicit.target_fingerprint("discord") == explicit.target_fingerprint("discord")
    preset = NotificationAppearance(username="当前模块通知")
    await implicit.send("内容", default_appearance=preset)
    assert post.call_args.kwargs["json"]["username"] == "当前模块通知"
    await explicit.send("内容", default_appearance=preset)
    assert post.call_args.kwargs["json"]["username"] == "Apple 应用通知"


def test_legacy_target_selection_rejects_double_configuration():
    with pytest.raises(ValueError, match="Configure notifications or legacy Discord destination"):
        NotificationSettings(
            notifications=NotificationConfig(targets={"discord": DISCORD}),
            discord_webhook_url=WEBHOOK,
        )
