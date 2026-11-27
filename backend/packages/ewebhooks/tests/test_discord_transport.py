"""公共 Webhook 传输契约：真实 SDK 请求、受限目标和安全的失败信息。"""

import asyncio
import json
import logging
import threading

import httpx
import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError

from dwy_webhooks.discord import DiscordWebhookSender
from dwy_webhooks.errors import WebhookDeliveryError

URL = "https://discord.com/api/webhooks/123456789/shared-test-secret"


@pytest.fixture
def transport(capture_notification_http):
    """只模拟 HTTP 网络，保留 SDK 的序列化、查询参数和客户端选项。"""
    calls, outcomes = [], []

    def receive(request):
        """一次发送只允许消费一个结果，隐式重试将直接让测试失败。"""
        calls.append(request)
        result = outcomes.pop(0)
        if isinstance(result, Exception):
            raise result
        headers = result[2] if len(result) > 2 else {}
        if isinstance(result[1], bytes):
            return httpx.Response(result[0], content=result[1], headers=headers)
        return httpx.Response(result[0], json=result[1], headers=headers)

    capture_notification_http(receive)
    return calls, outcomes


async def test_single_request_preserves_safe_payload_and_redacts_credentials(transport, caplog):
    """多个来源共用相同的发送和脱敏规则，禁止提及及链接预览。"""
    calls, outcomes = transport
    outcomes.append((200, {"id": "987654321"}))
    caplog.set_level(logging.INFO, logger="httpx")
    result = await DiscordWebhookSender(URL)("event @everyone", suppress_embeds=True)
    assert result == "987654321"
    assert len(calls) == 1
    request = calls[0]
    assert request.url.params["wait"] == "true"
    assert request.headers["user-agent"]
    assert request.extensions["timeout"]["read"] == 10
    payload = json.loads(request.content)
    assert payload["content"] == "event @everyone"
    assert payload["allowed_mentions"] == {"parse": []}
    assert payload["flags"] == 4
    assert "shared-test-secret" not in caplog.text


@pytest.mark.parametrize("status,permanent", [(302, True), (400, True), (403, True), (503, False)])
async def test_http_failures_do_not_follow_redirects_retry_or_leak_secrets(transport, status, permanent):
    """重试由外层账本或上游负责，重定向一律不能继续发送 token。"""
    calls, outcomes = transport
    outcomes.append((status, {"message": URL}, {"Location": "https://evil.example/collect"}))
    with pytest.raises(WebhookDeliveryError) as caught:
        await DiscordWebhookSender(URL)("event")
    assert caught.value.permanent is permanent
    assert caught.value.code == "discord_http_error"
    assert URL not in str(caught.value)
    assert len(calls) == 1


@pytest.mark.parametrize("delay,expected", [
    (12.5, 12.5), (True, None), (-1, None), ("nan", None), ("inf", None), ({}, None),
])
async def test_rate_limit_is_reported_without_sleeping(transport, delay, expected):
    """布尔值、负值和非有限数不能成为调度延迟。"""
    calls, outcomes = transport
    outcomes.append((429, {"retry_after": delay}))
    with pytest.raises(WebhookDeliveryError) as caught:
        await DiscordWebhookSender(URL)("event")
    assert caught.value.code == "discord_rate_limited"
    assert caught.value.retry_after == expected
    assert caught.value.permanent is False
    assert len(calls) == 1


async def test_rate_limit_uses_header_when_body_does_not_provide_delay(transport):
    """不同 Discord 限流响应形态共享同一回退规则。"""
    _, outcomes = transport
    outcomes.append((429, b"not-json", {"Retry-After": "7.25"}))
    with pytest.raises(WebhookDeliveryError) as caught:
        await DiscordWebhookSender(URL)("event")
    assert caught.value.retry_after == 7.25


@pytest.mark.parametrize("message_id", [None, 123, "", "not-an-id", "１２３", "1" * 129])
async def test_success_requires_a_bounded_ascii_message_id(transport, message_id):
    """统一确认契约，任何来源都不能把畸形响应当成已发送。"""
    _, outcomes = transport
    outcomes.append((200, {"id": message_id}))
    with pytest.raises(WebhookDeliveryError, match="discord_invalid_response"):
        await DiscordWebhookSender(URL)("event")


async def test_network_error_does_not_chain_the_credential_url(transport):
    """异常链和错误消息都不能公开客户端原始带 token 的异常。"""
    _, outcomes = transport
    outcomes.append(RequestsConnectionError(URL))
    with pytest.raises(WebhookDeliveryError) as caught:
        await DiscordWebhookSender(URL)("event")
    assert caught.value.code == "discord_network_error"
    assert URL not in str(caught.value)
    assert caught.value.__suppress_context__ is True


@pytest.mark.parametrize("url", [
    "https://evil.example/webhooks/123/token",
    "http://discord.com/api/webhooks/123/token",
    URL + "?redirect=1",
    URL + "\n",
])
def test_reusable_sender_enforces_the_official_target(url):
    """公共包不能依赖宿主先校验，独立调用也必须禁止任意目标。"""
    with pytest.raises(ValueError):
        DiscordWebhookSender(url)


async def test_cancellation_propagates_without_retrying(monkeypatch):
    """取消调用不吞异常；已进入线程的请求由自身超时收敛，不宣称立即撤销。"""
    started, release = threading.Event(), threading.Event()
    calls = []

    def post(url, **kwargs):
        calls.append(url)
        started.set()
        release.wait(timeout=2)
        raise RequestsConnectionError("cancelled-test")

    monkeypatch.setattr("dwy_notify._transport.post", post)
    task = asyncio.create_task(DiscordWebhookSender(URL)("event"))
    try:
        assert await asyncio.to_thread(started.wait, 1)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        assert len(calls) == 1
    finally:
        release.set()
