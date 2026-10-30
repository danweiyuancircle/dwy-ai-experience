"""通知目标账本逐项持久化，重启和租约接管不重发已成功目标。"""

import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy import update
from test_delivery_queue import event, read
from test_delivery_queue import storage as storage

from dwy_notify.delivery import DeliveryPolicy
from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue


def delivery(target):
    return SimpleNamespace(target=target, success=True, message_id=None, error_code=None,
                           retry_after=None, permanent=False)


class FakeNotifier:
    """仅实现公开契约，不引入通知包或第三方 SDK。"""

    def __init__(self, targets, send):
        self.fingerprints, self.callback = targets, send
        self.targets = tuple(targets)

    def target_fingerprint(self, name):
        return self.fingerprints[name]

    async def send(self, body, *, targets, default_appearance=None):
        return SimpleNamespace(deliveries=(await self.callback(targets[0]),))


def queue(storage, notifier, *, now=100, **options):
    return SQLAlchemyDeliveryQueue(*storage, notifier=notifier, source="app_store_connect",
                                   clock=lambda: now, **options)


async def test_partial_success_restart_retries_only_due_failed_target(storage):
    calls = []

    async def send(target):
        calls.append(target)
        if target == "slow":
            return SimpleNamespace(target=target, success=False, message_id=None,
                                   error_code="notify_rate_limited", retry_after=15.5, permanent=False)
        return delivery(target)

    notifier = FakeNotifier({"ok": "a", "slow": "b"}, send)
    consumer = queue(storage, notifier)
    await consumer(event())
    assert await consumer.process_pending() == 0
    row = (await read(storage))[0]
    assert row["payload"]["notifications"]["ok"]["status"] == "sent"
    assert row["next_attempt_at"] == 116
    assert await queue(storage, notifier, now=115).process_pending() == 0

    async def recover(target):
        calls.append(target)
        return delivery(target)

    fresh = queue(storage, FakeNotifier({"ok": "a", "slow": "b"}, recover), now=116)
    assert await fresh.process_pending() == 1
    assert calls == ["ok", "slow", "slow"]


async def test_cancel_after_one_success_preserves_snapshot_before_network(storage):
    calls = []

    async def send(target):
        calls.append(target)
        states = (await read(storage))[0]["payload"]["notifications"]
        assert states[target]["fingerprint"] == target
        if target == "second":
            assert states["first"]["status"] == "sent"
            raise asyncio.CancelledError
        return delivery(target)

    notifier = FakeNotifier({"first": "first", "second": "second"}, send)
    consumer = queue(storage, notifier)
    await consumer(event())
    with pytest.raises(asyncio.CancelledError):
        await consumer.process_pending()

    async def recover(target):
        calls.append(target)
        return delivery(target)

    fresh = queue(
        storage, FakeNotifier({"first": "first", "second": "second", "new": "new"}, recover), now=161
    )
    assert await fresh.process_pending() == 1
    assert calls == ["first", "second", "second"]


@pytest.mark.parametrize("replacement,code", [({"a": "changed"}, "notification_target_changed"),
                                             ({"new": "new"}, "notification_target_missing")])
async def test_changed_or_removed_target_never_redirects_existing_message(storage, replacement, code):
    async def cancel(target):
        raise asyncio.CancelledError

    consumer = queue(storage, FakeNotifier({"a": "original"}, cancel))
    await consumer(event())
    with pytest.raises(asyncio.CancelledError):
        await consumer.process_pending()

    async def unexpected(target):
        pytest.fail("changed recipient must not receive existing notification")

    assert await queue(storage, FakeNotifier(replacement, unexpected), now=161).process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "dead"
    assert row["payload"]["notifications"]["a"]["error_code"] == code


async def test_lost_lease_cannot_record_success_or_send_next_target(storage):
    calls = []
    sessions, table = storage

    async def send(target):
        calls.append(target)
        async with sessions.begin() as db:
            await db.execute(update(table).values(lease_token="replacement"))
        return delivery(target)

    consumer = queue(storage, FakeNotifier({"a": "a", "b": "b"}, send))
    await consumer(event())
    assert await consumer.process_pending() == 0
    row = (await read(storage))[0]
    assert calls == ["a"]
    assert row["payload"]["notifications"]["a"]["status"] == "pending"
    assert row["lease_token"] == "replacement"


async def test_mixed_permanent_and_temporary_failures_finish_independently(storage):
    calls = []

    async def send(target):
        calls.append(target)
        return SimpleNamespace(target=target, success=False, message_id=None,
                               error_code="unsafe https://secret", retry_after=0, permanent=target == "gone")

    notifier = FakeNotifier({"gone": "a", "retry": "b"}, send)
    consumer = queue(storage, notifier, policy=DeliveryPolicy(max_attempts=2))
    await consumer(event())
    await consumer.process_pending()
    row = (await read(storage))[0]
    assert row["status"] == "retry" and "https://secret" not in str(row)
    await queue(storage, notifier, now=102, policy=DeliveryPolicy(max_attempts=2)).process_pending()
    row = (await read(storage))[0]
    assert row["status"] == "dead" and calls == ["gone", "retry", "retry"]


async def test_disallowed_scope_clears_content_without_initializing_targets(storage):
    async def unexpected(target):
        pytest.fail("suppressed scope must not send")

    consumer = queue(storage, FakeNotifier({"a": "a"}, unexpected), allowed_scopes={"other"})
    await consumer(event())
    assert await consumer.process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "suppressed" and row["payload"] == {}


def test_queue_requires_exactly_one_delivery_implementation(storage):
    with pytest.raises(ValueError, match="exactly one"):
        queue(storage, None)
    with pytest.raises(ValueError, match="exactly one"):
        SQLAlchemyDeliveryQueue(*storage, lambda content: None, notifier=object(), source="app_store_connect")


async def test_each_target_renews_parent_lease_before_network(storage):
    now, leases = [100], []

    async def send(target):
        leases.append((await read(storage))[0]["lease_until"])
        now[0] += 50
        return delivery(target)

    consumer = queue(storage, FakeNotifier({name: name for name in ("a", "b", "c")}, send))
    consumer.clock = lambda: now[0]
    await consumer(event())
    assert await consumer.process_pending() == 1
    assert leases == [160, 210, 260]


async def test_failed_targets_have_independent_due_times(storage):
    calls = []

    async def send(target):
        calls.append(target)
        return SimpleNamespace(target=target, success=False, message_id=None,
                               error_code="notify_rate_limited", retry_after=15 if target == "slow" else 0,
                               permanent=False)

    notifier = FakeNotifier({"fast": "a", "slow": "b"}, send)
    consumer = queue(storage, notifier)
    await consumer(event())
    await consumer.process_pending()
    await queue(storage, notifier, now=102).process_pending()
    row = (await read(storage))[0]
    assert calls == ["fast", "slow", "fast"]
    assert row["payload"]["notifications"]["fast"]["attempts"] == 2
    assert row["payload"]["notifications"]["slow"]["attempts"] == 1
    assert row["next_attempt_at"] == 106
