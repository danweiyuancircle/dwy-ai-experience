"""公共 Webhook 传输契约：真实 SDK 请求、受限目标和安全的失败信息。"""

import asyncio
import json
import logging

import httpx
import pytest

from dwy_webhooks.discord import DiscordWebhookSender
from dwy_webhooks.errors import WebhookDeliveryError

URL = "https://discord.com/api/webhooks/123456789/shared-test-secret"


@pytest.fixture
def transport(monkeypatch):
    """只模拟 HTTP 网络，保留 SDK 的序列化、查询参数和客户端选项。"""
    original = httpx.AsyncClient
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

    def client(**kwargs):
        """仅替换传输；超时、重定向和 headers 都取生产配置。"""
        return original(transport=httpx.MockTransport(receive), **kwargs)

    monkeypatch.setattr(httpx, "AsyncClient", client)
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
    assert request.headers["user-agent"] == "dwy-webhooks/0.4.0"
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
    outcomes.append(httpx.ConnectError(URL))
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


async def test_cancellation_closes_the_http_client(monkeypatch):
    """停机取消发送时也释放连接，不能留下后台网络任务或自动重试。"""
    from dwy_webhooks import discord

    started = asyncio.Event()
    clients = []

    async def receive(request):
        """在取消前保持请求挂起；此传输永远不会访问外部网络。"""
        started.set()
        await asyncio.Future()

    def client():
        """保留实际 HTTPX 上下文生命周期以验证 aclose 行为。"""
        value = httpx.AsyncClient(transport=httpx.MockTransport(receive))
        clients.append(value)
        return value

    monkeypatch.setattr(discord, "discord_client", client)
    task = asyncio.create_task(DiscordWebhookSender(URL)("event"))
    await asyncio.wait_for(started.wait(), timeout=1)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(clients) == 1
    assert clients[0].is_closed
