"""非共享队列表结构的调用方也能复用同一逐目标算法和租约检查点。"""

from copy import deepcopy
from types import SimpleNamespace

import pytest
from test_target_delivery import FakeNotifier, delivery

from dwy_notify.delivery import DeliveryPolicy, deliver_notifications, delivery_failure
from dwy_notify.delivery import NotificationDeliveryError as WebhookDeliveryError


def checkpoint_for(persisted, *, fail_at=None):
    calls = []

    async def checkpoint(**values):
        calls.append(deepcopy(values))
        if len(calls) == fail_at:
            return False
        persisted.update(deepcopy(values))
        return True

    return checkpoint, calls


async def test_helper_checkpoints_targets_before_sending_and_preserves_host_payload():
    persisted = {"payload": {"content": "notice", "host_notice": {"id": "event"}}}
    checkpoint, checkpoints = checkpoint_for(persisted)
    calls = []

    async def send(target):
        assert persisted["payload"]["notifications"][target]["status"] == "pending"
        assert persisted["lease_until"] == 160
        calls.append(target)
        return delivery(target)

    result = await deliver_notifications(
        FakeNotifier({"a": "fingerprint-a", "b": "fingerprint-b"}, send),
        deepcopy(persisted["payload"]), policy=DeliveryPolicy(), clock=lambda: 100,
        checkpoint=checkpoint,
    )
    assert result["status"] == "sent" and result["attempts"] == 1
    assert calls == ["a", "b"]
    assert checkpoints[0]["payload"]["notifications"]["a"]["fingerprint"] == "fingerprint-a"
    assert result["payload"]["host_notice"] == {"id": "event"}
    assert all(state["status"] == "sent" for state in result["payload"]["notifications"].values())


async def test_helper_keeps_partial_success_and_safe_independent_failures():
    persisted = {"payload": {"content": "notice"}}
    checkpoint, _ = checkpoint_for(persisted)

    async def send(target):
        if target == "ok":
            return delivery(target)
        return SimpleNamespace(target=target, success=False, error_code="unsafe https://secret",
                               retry_after=15.5, permanent=target == "gone")

    result = await deliver_notifications(
        FakeNotifier({"ok": "a", "slow": "b", "gone": "c"}, send),
        deepcopy(persisted["payload"]), policy=DeliveryPolicy(), clock=lambda: 100,
        checkpoint=checkpoint,
    )
    states = result["payload"]["notifications"]
    assert result["status"] == "retry" and result["next_attempt_at"] == 116
    assert states["ok"]["status"] == "sent"
    assert states["slow"]["status"] == "retry"
    assert states["gone"]["status"] == "dead"
    assert result["error_code"] == "webhook_delivery_error"
    assert "secret" not in str(result)


async def test_helper_restart_retries_only_due_failed_target_without_adding_recipients():
    persisted = {"payload": {"content": "notice"}}
    checkpoint, _ = checkpoint_for(persisted)
    calls = []

    async def fail_once(target):
        calls.append(target)
        if target == "slow":
            raise WebhookDeliveryError("rate_limited", retry_after=20)
        return delivery(target)

    result = await deliver_notifications(
        FakeNotifier({"ok": "a", "slow": "b"}, fail_once), deepcopy(persisted["payload"]),
        policy=DeliveryPolicy(), clock=lambda: 100, checkpoint=checkpoint,
    )
    assert result["next_attempt_at"] == 120

    async def recover(target):
        calls.append(target)
        return delivery(target)

    notifier = FakeNotifier({"ok": "a", "slow": "b", "new": "c"}, recover)
    early = await deliver_notifications(
        notifier, deepcopy(persisted["payload"]), policy=DeliveryPolicy(), clock=lambda: 119,
        checkpoint=checkpoint,
    )
    assert early["status"] == "retry" and calls == ["ok", "slow"]
    resumed = await deliver_notifications(
        notifier, deepcopy(persisted["payload"]), policy=DeliveryPolicy(), clock=lambda: 120,
        checkpoint=checkpoint,
    )
    assert resumed["status"] == "sent" and calls == ["ok", "slow", "slow"]
    assert set(resumed["payload"]["notifications"]) == {"ok", "slow"}


@pytest.mark.parametrize("fail_at,expected_calls", [(1, []), (2, []), (3, ["a"])])
async def test_helper_lost_lease_stops_before_sending_or_recording_next_target(fail_at, expected_calls):
    persisted = {"payload": {"content": "notice"}}
    checkpoint, _ = checkpoint_for(persisted, fail_at=fail_at)
    calls = []

    async def send(target):
        calls.append(target)
        return delivery(target)

    result = await deliver_notifications(
        FakeNotifier({"a": "a", "b": "b"}, send), deepcopy(persisted["payload"]),
        policy=DeliveryPolicy(), clock=lambda: 100, checkpoint=checkpoint,
    )
    assert result == {"status": "processing"}
    assert calls == expected_calls
    if fail_at > 1:
        assert persisted["payload"]["notifications"]["a"]["status"] == "pending"


def test_delivery_failure_preserves_bounded_retry_and_fixed_error_codes():
    result = delivery_failure(
        1, WebhookDeliveryError("unsafe https://secret", retry_after=9999),
        policy=DeliveryPolicy(max_attempts=2, provider_retry_cap_seconds=60), clock=lambda: 100,
    )
    assert result == {"status": "dead", "attempts": 2, "next_attempt_at": 160,
                      "error_code": "webhook_delivery_error"}
