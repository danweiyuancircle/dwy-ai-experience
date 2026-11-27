"""后台轮询与投递任务的生命周期必须早于宿主资源释放结束。"""

from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from dwy_apple_notify.reviews.runtime import install_review_monitor


async def test_runtime_stops_tasks_before_host_database_is_disposed(monkeypatch):
    """关闭顺序错误会让仍在发送的任务使用已释放会话。"""
    import asyncio

    import dwy_apple_notify.reviews.runtime as module

    order = []
    started = [asyncio.Event(), asyncio.Event()]

    async def worker(index):
        """停止时记录次序，不访问网络或真实数据库。"""
        started[index].set()
        try:
            await asyncio.Event().wait()
        finally:
            order.append(f"stop-{index}")

    @asynccontextmanager
    async def host_lifespan(app):
        """模拟宿主引擎只在所有后台消费者停止后才能关闭。"""
        yield
        order.append("dispose")

    app = FastAPI(lifespan=host_lifespan)
    client = SimpleNamespace(aclose=AsyncMock())
    monkeypatch.setattr(module, "ReviewStore", lambda *a, **kw: object())
    monkeypatch.setattr(module, "ReviewMonitor", lambda *a: SimpleNamespace(run=lambda: worker(0)))
    monkeypatch.setattr(
        module, "ReviewDeliveryQueue", lambda *a, **kw: SimpleNamespace(run=lambda: worker(1))
    )
    config = SimpleNamespace(discord_webhook_url=None, retention_days=30, apps={"1234567890": object()})
    tables = SimpleNamespace(deliveries=object())
    runtime = install_review_monitor(app, config, object(), tables, client=client, sender=AsyncMock())
    assert app.state.dwy_review_monitor is runtime
    async with app.router.lifespan_context(app):
        await asyncio.wait_for(asyncio.gather(*(event.wait() for event in started)), timeout=1)
    assert order[-1] == "dispose"
    assert set(order[:2]) == {"stop-0", "stop-1"}
    client.aclose.assert_not_awaited()
    with pytest.raises(ValueError, match="already installed"):
        install_review_monitor(app, config, object(), tables, client=client, sender=AsyncMock())
