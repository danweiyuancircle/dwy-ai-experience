"""仓库外验收实际安装的 wheel、轻量导入及显式展示的持久化合同。"""

import asyncio
import importlib.metadata
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory


async def check_queue(directory: Path) -> None:
    """以离线发送器驱动真实 SQLite，验证发送前快照和重启后的成功状态。"""
    from dwyeapi.database import create_async_engine_factory, create_session_factory
    from sqlalchemy import MetaData, select

    from dwy_notify import NotificationAppearance, NotificationDelivery, NotificationResult
    from dwy_notify.events import NotificationEvent
    from dwy_notify.sqlalchemy import SQLAlchemyDeliveryQueue, build_delivery_table

    calls = []

    class Sender:
        """只实现公开发送合同；验收不访问任何外部通知服务。"""

        targets = ("offline",)

        def target_fingerprint(self, name):
            return "stable-offline-fingerprint"

        async def send(self, body, *, targets, default_appearance):
            calls.append((body, targets, default_appearance))
            return NotificationResult((NotificationDelivery(targets[0], True, message_id="smoke-message"),))

    engine = create_async_engine_factory(f"sqlite+aiosqlite:///{directory / 'smoke.db'}")
    metadata = MetaData()
    table = build_delivery_table(metadata, "notification_smoke")
    try:
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        sessions = create_session_factory(engine)
        preset = NotificationAppearance(username="验收通知", avatar_url=None)
        queue = SQLAlchemyDeliveryQueue(
            sessions, table, notifier=Sender(), source="wheel.smoke", appearance=preset,
        )
        event = NotificationEvent("wheel.smoke", "app", "event", "test", "offline content")
        assert await queue(event)
        assert await queue.process_pending() == 1
        async with sessions() as session:
            row = (await session.execute(select(table))).mappings().one()
        assert row["payload"]["appearance"] == {"username": "验收通知", "avatar_url": None}
        assert row["payload"]["notifications"]["offline"]["status"] == "sent"
        assert calls == [("offline content", ("offline",), preset)]
        restarted = SQLAlchemyDeliveryQueue(
            sessions, table, notifier=Sender(), source="wheel.smoke", appearance=preset,
        )
        assert not await restarted(event)
        assert await restarted.process_pending() == 0
        assert len(calls) == 1
    finally:
        await engine.dispose()


def main() -> None:
    """预期版本由发布任务注入，拒绝用源码环境或旧安装元数据代替产物验收。"""
    assert importlib.metadata.version("dwy-notify") == sys.argv[1]
    subprocess.run([
        sys.executable, "-c",
        "import sys, dwy_notify; "
        "assert 'sqlalchemy' not in sys.modules; "
        "assert 'fastapi' not in sys.modules; "
        "assert 'dwy_webhooks' not in sys.modules; "
        "assert dwy_notify.__file__ and 'site-packages' in dwy_notify.__file__",
    ], check=True)
    with TemporaryDirectory(prefix="notify-wheel-smoke-") as temporary:
        asyncio.run(check_queue(Path(temporary)))
    print("notify wheel import and durable appearance smoke passed")


if __name__ == "__main__":
    main()
