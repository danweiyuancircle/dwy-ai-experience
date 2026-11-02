"""微信 SDK 异常只能以脱敏渠道错误返回，任务取消必须向上传播。"""

import asyncio
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from dwy_payment.config import WechatPayConfig
from dwy_payment.errors import PaymentChannelError
from dwy_payment.gateways.wechat_native import WechatNativeGateway


async def invoke_sdk_failure(monkeypatch, operation, error):
    """替换 SDK 上下文和三个网络方法，禁止测试访问商户接口。"""
    client = SimpleNamespace(
        pay=AsyncMock(side_effect=error),
        query=AsyncMock(side_effect=error),
        close=AsyncMock(side_effect=error),
    )
    context = AsyncMock()
    context.__aenter__.return_value = client
    gateway = WechatNativeGateway(WechatPayConfig())
    monkeypatch.setattr(gateway, "_client", lambda: context)
    arguments = {"order_no": "review123"}
    if operation == "create_native":
        arguments.update(description="测试商品", amount_fen=1000, time_expire=datetime(2026, 11, 2))
    return await getattr(gateway, operation)(**arguments)


@pytest.mark.parametrize("operation", ["create_native", "query", "close"])
@pytest.mark.parametrize("error_type", [TimeoutError, Exception])
async def test_sdk_failures_are_safe_channel_errors(monkeypatch, operation, error_type):
    """SDK 超时和通用验签异常不能绕过服务的渠道恢复分支或泄露原文。"""
    marker = "sdk-sensitive-response-test-only"
    logger = Mock()
    monkeypatch.setattr("dwy_payment.gateways.wechat_native.logger", logger)
    with pytest.raises(PaymentChannelError) as caught:
        await invoke_sdk_failure(monkeypatch, operation, error_type(marker))
    assert marker not in str(caught.value)
    assert marker not in repr(logger.mock_calls)
    assert caught.value.__suppress_context__


@pytest.mark.parametrize("operation", ["create_native", "query", "close"])
async def test_sdk_cancellation_is_not_converted(monkeypatch, operation):
    """停机取消不是可重试的渠道错误，不能被异常归一化吞掉。"""
    with pytest.raises(asyncio.CancelledError):
        await invoke_sdk_failure(monkeypatch, operation, asyncio.CancelledError())
