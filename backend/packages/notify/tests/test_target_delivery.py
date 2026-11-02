"""通知目标账本逐项持久化，重启和租约接管不重发已成功目标。"""

import asyncio
from types import SimpleNamespace

import pytest
from sqlalchemy import update
from test_delivery_queue import event, read
from test_delivery_queue import storage as storage

from dwy_notify.delivery import DeliveryPolicy
from dwy_notify.models import NotificationAppearance
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


async def test_disallowed_scope_send_defense_suppresses_without_initializing_targets(storage):
    async def unexpected(target):
        pytest.fail("suppressed scope must not send")

    consumer = queue(storage, FakeNotifier({"a": "a"}, unexpected), allowed_scopes={"other"})
    await consumer(event())
    assert await consumer.process_pending() == 0
    row = (await read(storage))[0]
    assert row["status"] == "pending" and row["payload"] == {"content": "safe content"}
    assert await consumer._send(row) == dict(status="suppressed", payload={}, error_code=None)


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


async def failed_queue(storage, *, permanent=True):
    """经过真实消费者生成成功与失败目标快照，避免手工状态掩盖重放缺陷。"""
    async def send(target):
        if target == "ok":
            return delivery(target)
        return SimpleNamespace(target=target, success=False, message_id=None,
                               error_code="notify_failed", retry_after=15, permanent=permanent)

    consumer = queue(storage, FakeNotifier({"ok": "a", "failed": "b"}, send),
                     appearance=NotificationAppearance(username="原始展示"))
    await consumer(event())
    await consumer.process_pending()
    return consumer


async def test_requeue_dead_target_really_sends_only_failed_snapshot_target(storage):
    consumer = await failed_queue(storage)
    before = (await read(storage))[0]
    assert before["status"] == "dead"
    calls = []

    async def recover(target):
        calls.append(target)
        return delivery(target)

    consumer.notifier = FakeNotifier({"ok": "a", "failed": "b", "new": "c"}, recover)
    consumer.appearance = NotificationAppearance(username="新展示")
    sessions, _ = storage
    async with sessions.begin() as db:
        assert await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))
    row = (await read(storage))[0]
    assert row["status"] == "retry" and row["next_attempt_at"] == 100
    state = row["payload"]["notifications"]["failed"]
    assert state == dict(fingerprint="b", status="pending", attempts=0, next_attempt_at=100,
                         error_code=None, message_id=None)
    assert row["payload"]["content"] == before["payload"]["content"]
    assert row["payload"]["appearance"] == before["payload"]["appearance"]
    assert row["payload"]["notifications"]["ok"] == before["payload"]["notifications"]["ok"]
    assert await consumer.process_pending() == 1
    assert calls == ["failed"]
    assert (await read(storage))[0]["status"] == "sent"


async def test_requeue_changes_follow_outer_rollback_and_concurrent_replay_is_single(storage):
    consumer = await failed_queue(storage)
    sessions, _ = storage
    before = await read(storage)
    async with sessions() as db:
        assert await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))
        await db.rollback()
    assert await read(storage) == before

    async def replay():
        async with sessions.begin() as db:
            return await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))

    assert sorted(await asyncio.gather(replay(), replay())) == [False, True]


@pytest.mark.parametrize("case,code", [
    ("sent", "notification_target_sent"),
    ("new", "notification_target_not_in_snapshot"),
    ("unknown", "notification_target_not_in_snapshot"),
    ("changed", "notification_target_changed"),
    ("removed", "notification_target_missing"),
    ("lease", "notification_active_lease"),
])
async def test_requeue_rejects_unsafe_targets_without_changing_snapshot(storage, case, code):
    consumer = await failed_queue(storage)
    sessions, table = storage
    target = "failed"
    if case == "sent":
        target = "ok"
    elif case in ("new", "unknown"):
        target = case
        consumer.notifier.targets += ("new",)
    elif case == "changed":
        consumer.notifier.fingerprints["failed"] = "replacement"
    elif case == "removed":
        consumer.notifier.targets = ("ok",)
    elif case == "lease":
        async with sessions.begin() as db:
            await db.execute(update(table).values(lease_until=101, lease_token="active"))
    before = await read(storage)
    async with sessions.begin() as db:
        with pytest.raises(ValueError, match=f"^{code}$"):
            await consumer.requeue_failed_in_session(db, "app-1", "event-1", (target,))
    assert await read(storage) == before


async def test_requeue_retry_recomputes_parent_and_preserves_other_failed_targets(storage):
    consumer = await failed_queue(storage, permanent=False)
    sessions, table = storage
    async with sessions.begin() as db:
        row = (await read(storage))[0]
        payload = row["payload"]
        payload["notifications"]["other"] = dict(
            fingerprint="c", status="dead", attempts=4, next_attempt_at=90,
            error_code="other_failure", message_id=None,
        )
        await db.execute(update(table).values(payload=payload))
    async with sessions.begin() as db:
        assert await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))
    row = (await read(storage))[0]
    assert row["status"] == "retry" and row["attempts"] == 4 and row["next_attempt_at"] == 100
    assert row["error_code"] == "other_failure"
    assert row["payload"]["notifications"]["other"] == payload["notifications"]["other"]


async def test_requeue_mixed_sent_selection_is_atomic_and_expires_old_worker_token(storage):
    consumer = await failed_queue(storage)
    sessions, table = storage
    before = await read(storage)
    async with sessions.begin() as db:
        with pytest.raises(ValueError, match="^notification_target_sent$"):
            await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed", "ok"))
    assert await read(storage) == before
    async with sessions.begin() as db:
        await db.execute(update(table).values(lease_until=99, lease_token="expired"))
    async with sessions.begin() as db:
        assert await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))
    assert not await consumer._checkpoint(
        dict(app_id="app-1", id="event-1", lease_token="expired"), status="sent",
    )
    row = (await read(storage))[0]
    assert row["status"] == "retry" and row["lease_token"] is None and row["lease_until"] == 0


@pytest.mark.parametrize("targets", [(), ("failed", "failed"), (1,), "failed", ["failed"]])
async def test_requeue_validates_target_selection(storage, targets):
    consumer = await failed_queue(storage)
    sessions, _ = storage
    async with sessions.begin() as db:
        with pytest.raises(ValueError, match="^invalid_notification_targets$"):
            await consumer.requeue_failed_in_session(db, "app-1", "event-1", targets)


async def test_requeue_missing_or_uninitialized_record_returns_false(storage):
    async def unexpected(target):
        pytest.fail("requeue must never send directly")

    consumer = queue(storage, FakeNotifier({"failed": "b"}, unexpected))
    await consumer(event())
    sessions, _ = storage
    async with sessions.begin() as db:
        assert not await consumer.requeue_failed_in_session(db, "other", "event-1", ("failed",))
        assert not await consumer.requeue_failed_in_session(db, "app-1", "event-1", ("failed",))
