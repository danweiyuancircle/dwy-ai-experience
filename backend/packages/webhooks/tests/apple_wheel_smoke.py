"""在全新实际 wheel 环境验收其他项目的 Apple→Discord 链路，不需要 App Cloud。"""

import asyncio
import importlib.metadata
import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import httpx
import requests
from appstoreserverlibrary.models.Data import Data
from appstoreserverlibrary.models.JWSTransactionDecodedPayload import JWSTransactionDecodedPayload
from appstoreserverlibrary.models.ResponseBodyV2DecodedPayload import ResponseBodyV2DecodedPayload
from dwy_notify import NotificationConfig
from fastapi import FastAPI

from dwy_webhooks import WebhookConfig, install_webhooks
from dwy_webhooks.apple import AppleTransactionDetails, apple_notification_content
from dwy_webhooks.config import AppleNotificationApp, AppleNotificationsConfig


async def main(expected_version: str):
    """仅在官方 SDK 验签方法边界注入离线对象，其余装配、映射和 HTTP JSON 均真实执行。"""
    assert importlib.metadata.version("dwy-webhooks") == expected_version
    assert Path(sys.modules[AppleTransactionDetails.__module__].__file__).resolve().is_relative_to(
        Path(sys.prefix).resolve()
    )
    for name in ("app_cloud", "apple_iap", "cloud_kernel", "resend", "discord_webhook"):
        assert importlib.util.find_spec(name) is None, name
    now = 1793059200000
    transaction = JWSTransactionDecodedPayload(
        transactionId="tx", originalTransactionId="original", bundleId="com.example.other",
        rawEnvironment="Sandbox", productId="other.lifetime", price=14990, currency="AUD", storefront="AUS",
        purchaseDate=now,
    )
    notice = ResponseBodyV2DecodedPayload(
        rawNotificationType="CONSUMPTION_REQUEST", notificationUUID="portable-refund", signedDate=now,
        data=Data(bundleId="com.example.other", rawEnvironment="Sandbox", signedTransactionInfo="tx-jws",
                  rawConsumptionRequestReason="UNINTENDED_PURCHASE"),
    )

    class Verifier:
        """模拟 SDK 签名边界；库仍负责身份、字段及事件处理，不连接 Apple。"""

        def __init__(self, *args):
            """证书由调用方注入，离线边界不读取业务文件。"""

        def verify_and_decode_notification(self, signed):
            """返回已验签通知。"""
            assert signed == "notice-jws"
            return notice

        def verify_and_decode_signed_transaction(self, signed):
            """嵌套交易仍必须独立经过 SDK 方法。"""
            assert signed == "tx-jws"
            return transaction

    messages = []

    def receive(url, **kwargs):
        """捕获实际 Discord JSON，不发送真实消息。"""
        assert url.startswith("https://discord.com/api/webhooks/123456789/")
        assert kwargs["verify"] is True and kwargs["allow_redirects"] is False
        messages.append(kwargs["json"])
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({"id": "123456789"}).encode()
        return response

    original = httpx.AsyncClient
    with patch("appstoreserverlibrary.signed_data_verifier.SignedDataVerifier", Verifier), patch(
        "dwy_notify._transport.post", receive,
    ):
        app = FastAPI()
        config = WebhookConfig(
            notifications=NotificationConfig(targets={
                "apple": "discord://Other%20Apple@123456789/offline-token",
            }),
            apple_notifications=AppleNotificationsConfig(apps={
                "other": AppleNotificationApp(name="Other Project", bundle_id="com.example.other",
                                              environment="Sandbox", root_certificates=(b"offline-cert",)),
            }),
        )
        install_webhooks(app, config)
        async with app.router.lifespan_context(app), original(
            transport=httpx.ASGITransport(app=app), base_url="https://other",
        ) as client:
            response = await client.post("/webhooks/apple/other", json={"signedPayload": "notice-jws"})
            assert response.status_code == 200
        assert messages[0]["username"] == "Other Apple"
        assert "Other Project · 用户申请退款" in messages[0]["content"]
        assert "原交易金额：14.99 AUD" in messages[0]["content"] and "购买地区：AUS" in messages[0]["content"]
        assert "申请原因（用户选择分类）：误购" in messages[0]["content"]
        assert "ADBox" not in messages[0]["content"]
    assert callable(apple_notification_content)
    print("Apple wheel: independent project, verified mapping, branding and actual Discord JSON passed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apple_wheel_smoke.py EXPECTED_VERSION")
    asyncio.run(main(sys.argv[1]))
