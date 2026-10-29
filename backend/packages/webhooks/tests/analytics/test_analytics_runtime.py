"""运行时只关闭自有客户端，先停止任务再释放宿主数据库。"""

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI

from dwy_webhooks.analytics.runtime import install_analytics_monitor


@pytest.mark.parametrize("owned", [False, True])
async def test_lifespan_ownership_shutdown_order_and_public_state(monkeypatch, owned):
    import dwy_webhooks.analytics.runtime as module

    order, started = [], [asyncio.Event(), asyncio.Event()]

    async def worker(index):
        started[index].set()
        try:
            await asyncio.Event().wait()
        finally:
            order.append(f"stop-{index}")

    @asynccontextmanager
    async def host(app):
        yield
        order.append("dispose")

    client = SimpleNamespace(aclose=AsyncMock())
    monkeypatch.setattr(module, "AppleAnalyticsClient", lambda config: client)
    monkeypatch.setattr(module, "AnalyticsStore", lambda *a: object())
    monkeypatch.setattr(module, "AnalyticsMonitor", lambda *a, **kw: SimpleNamespace(run=lambda: worker(0)))
    monkeypatch.setattr(
        module, "SQLAlchemyDeliveryQueue", lambda *a, **kw: SimpleNamespace(run=lambda: worker(1))
    )
    app = FastAPI(lifespan=host)
    runtime = install_analytics_monitor(
        app,
        SimpleNamespace(discord_webhook_url=None, apps={"1234567890": object()}, issuer_id="issuer"),
        object(),
        SimpleNamespace(deliveries=object()),
        client=None if owned else client,
        sender=AsyncMock(),
    )
    assert app.state.dwy_analytics_monitor is runtime
    async with app.router.lifespan_context(app):
        await asyncio.wait_for(asyncio.gather(*(e.wait() for e in started)), 1)
    assert order[-1] == "dispose" and set(order[:2]) == {"stop-0", "stop-1"}
    assert client.aclose.await_count == int(owned)
    with pytest.raises(ValueError, match="already installed"):
        install_analytics_monitor(app, object(), object(), object())


def test_install_requires_destination_before_creating_resources():
    with pytest.raises(ValueError, match="destination"):
        install_analytics_monitor(FastAPI(), SimpleNamespace(discord_webhook_url=None), object(), object())
