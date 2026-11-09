"""在全新实际 wheel 环境验收其他项目的 Apple→Discord 链路，不需要 App Cloud。"""

import asyncio
import importlib.metadata
import importlib.util
import json
import sys
from importlib.resources import files
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import requests
from appstoreserverlibrary.models.Data import Data
from appstoreserverlibrary.models.JWSTransactionDecodedPayload import JWSTransactionDecodedPayload
from appstoreserverlibrary.models.ResponseBodyV2DecodedPayload import ResponseBodyV2DecodedPayload
from dwy_notify import NotificationConfig
from fastapi import FastAPI

from dwy_apple_notify import AppleNotifyConfig, install_apple_notifications
from dwy_apple_notify.apple import (
    AppleTransactionDetails,
    VerifiedAppleNotification,
    apple_notification_appearance,
    apple_notification_content,
    apple_original_platform,
)
from dwy_apple_notify.config import AppleNotificationApp, AppleNotificationsConfig


async def main(expected_version: str):
    """仅在官方 SDK 验签方法边界注入离线对象，其余装配、映射和 HTTP JSON 均真实执行。"""
    assert importlib.metadata.version("dwy-apple-notify") == expected_version
    assert callable(apple_notification_appearance)
    for icon in ("subscription", "refund"):
        asset = files("dwy_apple_notify").joinpath("assets", icon + ".png").read_bytes()
        assert asset[:8] == b"\x89PNG\r\n\x1a\n"
    class Client:
        async def get_app_transaction_info(self, transaction_id):
            assert transaction_id == "tx"
            return SimpleNamespace(signedAppTransactionInfo="signed-app")

    async def verify(signed):
        assert signed == "signed-app"
        return SimpleNamespace(originalPlatform="macOS")

    platform = await apple_original_platform(Client(), verify, "tx")
    from datetime import UTC, datetime

    platform_notice = VerifiedAppleNotification(
        notification_id="n", bundle_id="com.example.other", environment="Sandbox",
        notification_type="ONE_TIME_CHARGE", signed_at=datetime.now(UTC), original_platform=platform,
    )
    assert "首次获取 App 平台：macOS" in apple_notification_content(platform_notice)
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
        config = AppleNotifyConfig(
            notifications=NotificationConfig(targets={
                "apple": "discord://Other%20Apple@123456789/offline-token",
            }),
            apple_notifications=AppleNotificationsConfig(apps={
                "other": AppleNotificationApp(name="Other Project", bundle_id="com.example.other",
                                              environment="Sandbox", root_certificates=(b"offline-cert",)),
            }),
        )
        install_apple_notifications(app, config)
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
        assert messages[0]["avatar_url"].endswith("/general.png")

        production = FastAPI()
        install_apple_notifications(production, AppleNotifyConfig(
            notifications=NotificationConfig(targets={
                "apple": "https://discord.com/api/webhooks/123456789/offline-token",
            }),
            apple_notifications=AppleNotificationsConfig(apps={
                "other": AppleNotificationApp(
                    name="Other Project", bundle_id="com.example.other", environment="Production",
                    app_apple_id=123, root_certificates=(b"offline-cert",),
                ),
            }),
        ))
        async with production.router.lifespan_context(production), original(
            transport=httpx.ASGITransport(app=production), base_url="https://other",
        ) as client:
            for index, (event, subtype, kind, username, icon) in enumerate((
                ("SUBSCRIBED", "INITIAL_BUY", "Auto-Renewable Subscription", "订阅购买", "subscription"),
                ("ONE_TIME_CHARGE", None, "Non-Consumable", "买断购买", "purchase"),
                ("REFUND", None, "Non-Consumable", "退款通知", "refund"),
                ("DID_CHANGE_RENEWAL_STATUS", "AUTO_RENEW_DISABLED",
                 "Auto-Renewable Subscription", "内购动态", "general"),
            )):
                transaction = JWSTransactionDecodedPayload(
                    transactionId=f"tx-{index}", originalTransactionId="original",
                    bundleId="com.example.other", rawEnvironment="Production", productId="pro",
                    rawType=kind, rawInAppOwnershipType="PURCHASED", price=22000,
                    currency="CNY", purchaseDate=now,
                )
                notice = ResponseBodyV2DecodedPayload(
                    rawNotificationType=event, rawSubtype=subtype,
                    notificationUUID=f"appearance-{index}", signedDate=now,
                    data=Data(bundleId="com.example.other", appAppleId=123, rawEnvironment="Production",
                              signedTransactionInfo="tx-jws"),
                )
                response = await client.post("/webhooks/apple/other", json={"signedPayload": "notice-jws"})
                assert response.status_code == 200
                assert messages[-1]["username"] == username
                assert messages[-1]["avatar_url"].endswith(f"/{icon}.png")
    assert callable(apple_notification_content)
    print("Apple wheel: independent project, four appearances, assets and actual Discord JSON passed.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: apple_wheel_smoke.py EXPECTED_VERSION")
    asyncio.run(main(sys.argv[1]))
