"""仓库外运行的实际 analytics wheel 验收；网络仅使用离线 Discord transport。"""

import asyncio
import importlib.metadata
import importlib.util
import json
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import requests
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec
from dwy_notify import NotificationConfig, Notifier
from dwyeapi.database import create_async_engine_factory, create_session_factory
from sqlalchemy import MetaData, select

import dwy_webhooks.analytics as analytics
from dwy_webhooks.analytics import (
    AnalyticsStore,
    AnalyticsValue,
    AppleAnalyticsClient,
    AppleAnalyticsConfig,
    AppleBusinessSnapshot,
    apple_business_digest_content,
    build_analytics_tables,
)
from dwy_webhooks.delivery import SQLAlchemyDeliveryQueue


async def main(expected_version: str) -> None:
    """检查实际导入来源、默认时间、独立存储和真实发送器的离线链路。"""
    assert importlib.metadata.version("dwy-webhooks") == expected_version
    assert Path(analytics.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    for name in (
        "app_cloud", "apple_iap", "cloud_kernel", "adbox_server", "resend", "appstoreserverlibrary",
        "discord_webhook",
    ):
        assert importlib.util.find_spec(name) is None, name
    key = ec.generate_private_key(ec.SECP256R1())
    config = AppleAnalyticsConfig(
        apps={"1234567890": {"name": "Wheel Test"}},
        issuer_id="12345678-1234-1234-1234-123456789012", key_id="ABCDEFGHIJ",
        private_key=key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8,
                                      serialization.NoEncryption()).decode(),
    )
    assert (config.timezone, config.send_hour, config.send_minute) == ("Asia/Shanghai", 8, 30)
    client = AppleAnalyticsClient(config)
    await client.aclose()
    snapshot = AppleBusinessSnapshot(app_id="1234567890", report_date=date(2026, 10, 25), metrics={
        "first_downloads": AnalyticsValue(value=Decimal(9), status="available", source="Downloads Standard"),
        "sales_usd": AnalyticsValue(value=Decimal("1.25"), status="available", currency="USD",
                                    source="App Store Purchases Standard"),
    })
    parts = apple_business_digest_content("Wheel Test", [snapshot])
    assert "首次下载：9" in "\n".join(parts) and "USD 1.25" in "\n".join(parts)
    assert all(len(part.encode("utf-16-le")) <= 4000 for part in parts)
    calls = []

    def receive(url, **kwargs):
        assert url.startswith("https://discord.com/api/webhooks/123456789/")
        assert kwargs["verify"] is True and kwargs["allow_redirects"] is False
        payload = kwargs["json"]
        assert payload["allowed_mentions"] == {"parse": []}
        assert payload["username"] == "经营报表"
        assert payload["avatar_url"].endswith("/report.png")
        calls.append(payload["content"])
        response = requests.Response()
        response.status_code = 200
        response._content = json.dumps({"id": str(123456789 + len(calls))}).encode()
        return response

    with TemporaryDirectory(prefix="analytics-wheel-") as temporary:
        engine = create_async_engine_factory(f"sqlite+aiosqlite:///{Path(temporary) / 'analytics.db'}")
        metadata = MetaData()
        tables = build_analytics_tables(metadata)
        assert set(metadata.tables) == {
            "app_store_analytics_state", "app_store_analytics_snapshots", "app_store_analytics_deliveries",
        }
        try:
            async with engine.begin() as connection:
                await connection.run_sync(metadata.create_all)
            sessions = create_session_factory(engine)
            store = AnalyticsStore(sessions, tables, clock=lambda: 1800000000)
            token = await store.claim(config.issuer_id, snapshot.app_id, snapshot.report_date)
            assert token is not None
            assert await store.complete(config.issuer_id, snapshot.app_id, token, [snapshot],
                report_date=snapshot.report_date, messages=[("daily", snapshot.report_date,
                    snapshot.report_date, parts)], next_poll_at=1800086400)
            assert await store.claim(config.issuer_id, snapshot.app_id, snapshot.report_date) is None
            queue = SQLAlchemyDeliveryQueue(sessions, tables.deliveries,
                notifier=Notifier(NotificationConfig(targets={"daily": "discord://123456789/wheel-test-token"})),
                source="app_store_analytics", clock=lambda: 1800000000)
            with patch("dwy_notify._transport.post", receive):
                assert await queue.process_pending() == len(parts)
            async with sessions() as db:
                assert set((await db.execute(select(tables.deliveries.c.status))).scalars()) == {"sent"}
            assert calls == parts
        finally:
            await engine.dispose()
    print(f"analytics wheel {expected_version}: Beijing 08:30, "
          "isolated imports, persistent outbox and Discord passed")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
