"""仓库外运行的 ratings wheel 验收；只安装 ratings extra 和 SQLite 测试驱动。"""

import asyncio
import importlib.metadata
import importlib.util
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory

import httpx
from dwy_notify.delivery import NotificationDeliveryError
from dwyeapi.database import create_async_engine_factory, create_session_factory
from fastapi import FastAPI
from sqlalchemy import MetaData, insert, select

import dwy_apple_notify.ratings as ratings
from dwy_apple_notify.ratings import (
    AppleRatingClient,
    AppleRatingsConfig,
    RatingApp,
    build_rating_tables,
    install_rating_monitor,
)


async def main(expected_version: str) -> None:
    """验证安装来源、09:30 调度、完整变化日报和持久重试，不访问外部网络。"""
    assert importlib.metadata.version("dwy-apple-notify") == expected_version
    assert Path(ratings.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    for name in (
        "app_cloud",
        "apple_iap",
        "cloud_kernel",
        "adbox_server",
        "dwy_webhooks",
        "resend",
        "appstoreserverlibrary",
        "discord_webhook",
    ):
        assert importlib.util.find_spec(name) is None, name
    config = AppleRatingsConfig(
        apps={"1234567890": RatingApp(name="Ratings Wheel Test")},
        territories=("cn", "us"),
        timezone="Asia/Shanghai",
        send_hour=9,
        send_minute=30,
    )
    assert (config.send_hour, config.send_minute) == (9, 30)
    clock = [datetime(2026, 11, 6, 1, 29, 59, tzinfo=UTC).timestamp()]
    requests, sent = [], []

    def lookup(request):
        assert request.method == "GET" and request.url.host == "itunes.apple.com"
        assert request.url.path == "/lookup" and request.url.params["id"] == "1234567890"
        territory = request.url.params["country"]
        assert territory in config.territories
        requests.append(territory)
        return httpx.Response(
            200,
            json={
                "resultCount": 1,
                "results": [
                    {
                        "trackId": 1234567890,
                        "userRatingCount": 12 if territory == "cn" else 0,
                        "averageUserRating": 4.700000001 if territory == "cn" else 0,
                    }
                ],
            },
        )

    async def send(content):
        sent.append(content)
        if len(sent) == 1:
            raise NotificationDeliveryError("ratings_smoke_retry")
        return "ratings-wheel-message"

    with TemporaryDirectory(prefix="ratings-wheel-") as temporary:
        engine = create_async_engine_factory(f"sqlite+aiosqlite:///{Path(temporary) / 'ratings.db'}")
        metadata = MetaData()
        tables = build_rating_tables(metadata)
        assert set(metadata.tables) == {
            "app_store_ratings_state",
            "app_store_ratings_snapshots",
            "app_store_ratings_deliveries",
        }
        try:
            async with engine.begin() as connection:
                await connection.run_sync(metadata.create_all)
            sessions = create_session_factory(engine)
            async with sessions.begin() as db:
                for day, count, average in (
                    ("2026-11-05", 10, 4.5),
                    ("2026-10-30", 8, 4.3),
                    ("2026-10-06", 6, 4.0),
                ):
                    for territory in config.territories:
                        await db.execute(
                            insert(tables.snapshots).values(
                                timezone=config.timezone,
                                app_id="1234567890",
                                territory=territory,
                                day=day,
                                count=count if territory == "cn" else 0,
                                average=average if territory == "cn" else 0,
                                status="ok",
                                collected_at=int(clock[0]),
                            )
                        )
            async with httpx.AsyncClient(transport=httpx.MockTransport(lookup)) as http:
                collector = AppleRatingClient(config, client=http)
                app = FastAPI()
                runtime = install_rating_monitor(
                    app,
                    config,
                    sessions,
                    tables,
                    client=collector,
                    sender=send,
                    clock=lambda: clock[0],
                )
                assert app.state.dwy_rating_monitor is runtime
                assert await runtime.monitor.run_once() == 0 and not requests
                clock[0] += 1
                assert await runtime.monitor.run_once() == 1
                assert await runtime.monitor.run_once() == 0 and requests == ["cn", "us"]
                async with sessions() as db:
                    deliveries = (await db.execute(select(tables.deliveries))).mappings().all()
                    assert len(deliveries) == 1 and deliveries[0]["status"] == "pending"
                    content = deliveries[0]["payload"]["content"]
                    assert deliveries[0]["payload"]["app_ids"] == ["1234567890"]
                    snapshot = (
                        (
                            await db.execute(
                                select(tables.snapshots).where(
                                    tables.snapshots.c.day == "2026-11-06",
                                    tables.snapshots.c.territory == "cn",
                                )
                            )
                        )
                        .mappings()
                        .one()
                    )
                    assert snapshot["average"] == 4.700000001 and snapshot["count"] == 12
                assert "日变化：评分数净变化 +2，均分 +0.20" in content
                assert "周变化：评分数净变化 +4，均分 +0.40" in content
                assert "月变化：评分数净变化 +6，均分 +0.70" in content
                assert "当前评分总数：0，平均评分：0.00" in content
                assert "09:30:00+08:00" in content
                assert await runtime.queue.process_pending() == 0
                async with sessions() as db:
                    failed = (await db.execute(select(tables.deliveries))).mappings().one()
                    assert failed["status"] == "retry" and failed["attempts"] == 1
                    assert failed["error_code"] == "ratings_smoke_retry"
                clock[0] += 3600
                assert await runtime.monitor.run_once() == 0 and requests == ["cn", "us"]
                assert await runtime.queue.process_pending() == 1
                assert sent == [content, content]
                async with sessions() as db:
                    delivered = (await db.execute(select(tables.deliveries))).mappings().one()
                    assert delivered["status"] == "sent" and delivered["attempts"] == 1
                    assert delivered["message_id"] == "ratings-wheel-message"
                await collector.aclose()
                assert not http.is_closed
        finally:
            await engine.dispose()
    print(
        f"ratings wheel {expected_version}: Beijing 09:30, isolated imports, "
        "Lookup, day/week/month digest, SQLite outbox and fixed-content retry passed"
    )


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1]))
