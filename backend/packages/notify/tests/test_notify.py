import asyncio
import json
import logging
import threading
from unittest.mock import Mock

import pytest
import requests
from pydantic import SecretStr, ValidationError

from dwy_notify import NotificationConfig, NotificationDelivery, NotificationResult, Notifier

DISCORD = "discord://123456789012345678/" + "secret-token-" * 6
WECOM = "wecombot://secret-wecom-key"


def notification_config(**values):
    return NotificationConfig(**{
        "appearance": {"username": "测试通知"}, **values,
    })


def response(status=200, payload=None, headers=None):
    result = requests.Response()
    result.status_code = status
    result._content = json.dumps(payload).encode() if payload is not None else b""
    result.headers.update(headers or {})
    return result


@pytest.fixture
def post(monkeypatch):
    mocked = Mock(return_value=response(payload={"id": "123456789012345679"}))
    monkeypatch.setattr("dwy_notify._transport.post", mocked)
    return mocked


def test_config_and_results_are_public_owned_and_frozen():
    config = notification_config(targets={"ops": SecretStr(DISCORD)})
    assert DISCORD not in repr(config)
    with pytest.raises(ValidationError):
        config.timeout_seconds = 1
    for data in (
        {"targets": {}},
        {"targets": {"": DISCORD}},
        {"targets": {"a": ""}},
        {"targets": {"a": DISCORD}, "timeout_seconds": float("inf")},
        {"targets": {"a": DISCORD}, "timeout_seconds": 0},
    ):
        with pytest.raises(ValidationError):
            notification_config(**data)
    delivered = NotificationDelivery(target="ops", success=True, message_id="123")
    failed = NotificationDelivery(target="audit", success=False, error_code="network_error")
    result = NotificationResult(deliveries=(delivered, failed))
    assert not result.success
    assert result.succeeded == ("ops",)
    assert result.failed == ("audit",)
    assert not NotificationResult(deliveries=()).success


async def test_discord_sends_once_without_mentions_embeds_redirect_retry_or_insecure_tls(post):
    notifier = Notifier(
        notification_config(
            targets={"ops": DISCORD + "?verify=no&redirect=yes&retry=8&optional=yes"}, timeout_seconds=3
        )
    )
    result = await notifier.send("@everyone <@123> private body", title="private title")
    assert result.success
    assert result.deliveries[0].message_id == "123456789012345679"
    assert post.call_count == 1
    args, kwargs = post.call_args
    assert args[0].startswith("https://discord.com/api/webhooks/")
    assert kwargs["verify"] is True
    assert kwargs["allow_redirects"] is False
    assert kwargs["timeout"] == 3
    assert kwargs["params"]["wait"] == "true"
    assert kwargs["json"]["allowed_mentions"] == {"parse": []}
    assert "allow_mentions" not in kwargs["json"]
    assert kwargs["json"]["flags"] & 4


@pytest.mark.parametrize("payload", [{"errcode": 40013}, {"errcode": "0"}, {"errcode": False}, {}, None])
async def test_wecom_requires_integer_zero_business_result(post, payload):
    post.return_value = response(payload=payload)
    result = await Notifier(notification_config(targets={"ops": WECOM})).send("body")
    assert result.deliveries[0].error_code == "provider_error"
    assert not result.success


async def test_wecom_success_and_target_selection(post):
    post.return_value = response(payload={"errcode": 0, "errmsg": "ok"})
    notifier = Notifier(notification_config(targets={"ops": DISCORD, "audit": WECOM}))
    result = await notifier.send("body", title="title", targets=["audit"])
    assert result.success
    assert tuple(d.target for d in result.deliveries) == ("audit",)
    assert post.call_count == 1
    assert "body" in post.call_args.kwargs["json"]["text"]["content"]
    assert notifier.targets == ("ops", "audit")
    assert len(notifier.target_fingerprint("ops")) == 64
    assert notifier.target_fingerprint("ops") != notifier.target_fingerprint("audit")
    with pytest.raises(ValueError, match="unknown_target"):
        await notifier.send("body", targets=["missing"])
    with pytest.raises(ValueError, match="duplicate_target"):
        await notifier.send("body", targets=["ops", "ops"])


@pytest.mark.parametrize(
    "status,payload,code,permanent,retry",
    [
        (429, {"retry_after": 2.5}, "rate_limited", False, 2.5),
        (429, {"retry_after": "nan"}, "rate_limited", False, None),
        (401, {}, "http_error", True, None),
        (408, {}, "http_error", False, None),
        (302, {}, "redirect_rejected", True, None),
        (503, {}, "http_error", False, None),
        (200, {}, "invalid_response", False, None),
        (204, None, "invalid_response", False, None),
    ],
)
async def test_http_failures_are_safe_structured_results(post, status, payload, code, permanent, retry):
    post.return_value = response(status, payload)
    delivery = (await Notifier(notification_config(targets={"ops": DISCORD})).send("body")).deliveries[0]
    assert not delivery.success
    assert delivery.error_code == code
    assert delivery.permanent is permanent
    assert delivery.retry_after == retry
    assert post.call_count == 1


@pytest.mark.parametrize(
    "exception,code",
    [
        (requests.Timeout("private body " + DISCORD), "timeout"),
        (requests.ConnectionError(DISCORD), "network_error"),
    ],
)
async def test_network_error_and_logs_never_expose_url_or_body(post, caplog, exception, code):
    caplog.set_level(logging.DEBUG)
    post.side_effect = exception
    notifier = Notifier(notification_config(targets={"ops": DISCORD}))
    delivery = (await notifier.send("private body")).deliveries[0]
    assert delivery.error_code == code
    assert DISCORD not in caplog.text
    assert "private body" not in caplog.text
    assert "secret-token" not in caplog.text


async def test_cancel_propagates_and_target_lock_covers_inflight_thread(post):
    started = threading.Event()
    release = threading.Event()
    calls = 0

    def blocked(*args, **kwargs):
        nonlocal calls
        calls += 1
        started.set()
        release.wait(3)
        return response(payload={"id": "123456789012345679"})

    post.side_effect = blocked
    notifier = Notifier(notification_config(targets={"ops": DISCORD}))
    task = asyncio.create_task(notifier.send("first"))
    assert await asyncio.to_thread(started.wait, 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    second = asyncio.create_task(notifier.send("second"))
    await asyncio.sleep(0.03)
    assert calls == 1
    release.set()
    assert (await second).success
    assert calls == 2


def test_invalid_config_error_never_exposes_secret(caplog):
    caplog.set_level(logging.DEBUG)
    with pytest.raises(ValueError, match="invalid_target"):
        Notifier(notification_config(targets={"ops": "invalid://secret-token/private"}))
    assert "secret-token" not in caplog.text


@pytest.mark.parametrize(
    "url,module",
    [
        (
            "dingtalk://" + "a" * 64 + "/?verify=no&redirect=yes&retry=8&optional=yes&cto=999&rto=999",
            "dingtalk",
        ),
        (
            "feishu://00000000-0000-0000-0000-000000000000/?verify=no&redirect=yes&retry=8&optional=yes",
            "feishu",
        ),
    ],
)
async def test_standard_apprise_http_channels_force_safety_and_isolate_logger(
    monkeypatch, caplog, url, module
):
    upstream_logger = logging.getLogger("apprise")
    original = (upstream_logger.level, upstream_logger.disabled, list(upstream_logger.handlers))
    caplog.set_level(logging.DEBUG)
    post = Mock(return_value=response(503, {"message": "secret response"}))
    monkeypatch.setattr(f"apprise.plugins.{module}.requests.post", post)
    notifier = Notifier(notification_config(targets={"ops": url}, timeout_seconds=2))
    result = await notifier.send("private body", title="private title")
    assert not result.success
    assert result.deliveries[0].error_code == "send_failed"
    assert post.call_count == 1
    kwargs = post.call_args.kwargs
    assert kwargs["verify"] is True
    assert kwargs["allow_redirects"] is False
    assert kwargs["timeout"] == (2, 2)
    assert "private body" not in caplog.text
    assert "private title" not in caplog.text
    assert url not in caplog.text
    assert "secret response" not in caplog.text
    assert (upstream_logger.level, upstream_logger.disabled, list(upstream_logger.handlers)) == original


@pytest.mark.parametrize(
    "url", ["mailto://user:secret-token@example.com", "json://user:secret-token@example.com/path"]
)
def test_non_http_or_insecure_protocol_is_rejected(url):
    with pytest.raises(ValueError, match="unsupported_transport"):
        Notifier(notification_config(targets={"ops": url}))


async def test_native_discord_url_and_second_message_keep_real_confirmation(post):
    native = "https://discord.com/api/webhooks/123456789012345678/" + "secret-token-" * 6
    notifier = Notifier(notification_config(targets={"ops": native}))
    assert (await notifier.send("first")).success
    assert (await notifier.send("second")).success
    assert post.call_count == 2


async def test_different_targets_send_concurrently_and_preserve_config_order(post):
    both_started = threading.Barrier(2, timeout=2)

    def send(*args, **kwargs):
        both_started.wait()
        return (
            response(payload={"errcode": 0})
            if "weixin.qq.com" in args[0]
            else response(payload={"id": "123"})
        )

    post.side_effect = send
    notifier = Notifier(notification_config(targets={"ops": DISCORD, "audit": WECOM}))
    result = await notifier.send("body")
    assert result.success
    assert result.succeeded == ("ops", "audit")


async def test_unexpected_sdk_response_errors_are_safe_delivery_failures(monkeypatch, post):
    monkeypatch.setattr(
        "dwy_notify._plugins._Discord.notify", Mock(side_effect=ValueError("private " + DISCORD))
    )
    result = await Notifier(notification_config(targets={"ops": DISCORD})).send("body")
    assert not result.success
    assert result.deliveries[0].error_code == "provider_error"


async def test_discord_split_stops_after_first_failure_and_retains_its_error(post):
    post.side_effect = [response(429, {"retry_after": 3}), response(payload={"id": "123"})]
    notifier = Notifier(notification_config(targets={"ops": DISCORD + "?overflow=split"}))
    delivery = (await notifier.send("x" * 5000)).deliveries[0]
    assert not delivery.success
    assert delivery.error_code == "rate_limited"
    assert delivery.retry_after == 3
    assert post.call_count == 1


@pytest.mark.parametrize(
    "url",
    [
        "fluxer://123/secret-token",
        "revolt://secret-token/channel",
        "matrixs://user:secret-token@matrix.org/room",
        "sparkpost://secret-token/notify@example.com",
        "sendpulse://user:secret-token/notify@example.com",
    ],
)
def test_plugins_with_internal_retries_are_rejected(url):
    with pytest.raises(ValueError, match="unsupported_transport"):
        Notifier(notification_config(targets={"ops": url}))


@pytest.mark.parametrize("message_id", ["１２３", "١٢٣", "1" * 129])
async def test_discord_response_id_must_be_bounded_ascii_digits(post, message_id):
    post.return_value = response(payload={"id": message_id})
    delivery = (await Notifier(notification_config(targets={"ops": DISCORD})).send("body")).deliveries[0]
    assert not delivery.success
    assert delivery.error_code == "invalid_response"
    assert delivery.message_id is None


@pytest.mark.parametrize("timeout", [True, False, 31, float("nan")])
def test_timeout_rejects_boolean_nonfinite_and_unbounded_values(timeout):
    with pytest.raises(ValidationError):
        notification_config(targets={"ops": DISCORD}, timeout_seconds=timeout)


@pytest.mark.parametrize(
    "body,title,targets,error",
    [
        ("", "", None, "invalid_body"),
        (" \n ", "", None, "invalid_body"),
        (123, "", None, "invalid_body"),
        ("body", None, None, "invalid_title"),
        ("body", "", [], "invalid_targets"),
        ("body", "", "ops", "invalid_targets"),
        ("body", "", [None], "invalid_targets"),
    ],
)
async def test_invalid_send_input_is_rejected_before_http(post, body, title, targets, error):
    with pytest.raises(ValueError, match=error):
        await Notifier(notification_config(targets={"ops": DISCORD})).send(body, title=title, targets=targets)
    post.assert_not_called()


async def test_http_debug_logging_is_suppressed_only_in_notification_thread(post, caplog):
    caplog.set_level(logging.DEBUG)
    http_logger = logging.getLogger("urllib3.connectionpool")
    retry_logger = logging.getLogger("urllib3.util.retry")
    ordinary_logger = logging.getLogger("host.application")

    def send(*args, **kwargs):
        http_logger.debug("POST %s private body", DISCORD)
        retry_logger.debug("Retry %s private body", DISCORD)
        ordinary_logger.info("ordinary host log")
        return response(payload={"id": "123"})

    post.side_effect = send
    await Notifier(notification_config(targets={"ops": DISCORD})).send("private body")
    http_logger.debug("host HTTP outside notification")
    retry_logger.debug("host retry outside notification")
    assert DISCORD not in caplog.text
    assert "private body" not in caplog.text
    assert "ordinary host log" in caplog.text
    assert "host HTTP outside notification" in caplog.text
    assert "host retry outside notification" in caplog.text
