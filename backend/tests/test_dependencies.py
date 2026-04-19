"""Tests for dwyeapi.dependencies."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column

from dwyeapi.database import Base, create_async_engine_factory, create_session_factory
from dwyeapi.dependencies import create_get_db


class Item(Base):
    __tablename__ = "dep_test_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class TestGetDb:
    @pytest.fixture()
    def app(self, tmp_path):
        db_path = tmp_path / "test.db"
        engine = create_async_engine_factory(f"sqlite+aiosqlite:///{db_path}")
        session_factory = create_session_factory(engine)
        get_db = create_get_db(session_factory)

        from collections.abc import AsyncGenerator
        from contextlib import asynccontextmanager

        @asynccontextmanager
        async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            yield
            await engine.dispose()

        app = FastAPI(lifespan=lifespan)

        @app.post("/items")
        async def create_item(session=Depends(get_db)):  # noqa: B008
            item = Item(id=1, name="test")
            session.add(item)
            await session.commit()
            return {"id": 1}

        @app.get("/items/{item_id}")
        async def get_item(item_id: int, session=Depends(get_db)):  # noqa: B008
            result = await session.execute(select(Item).where(Item.id == item_id))
            item = result.scalar_one_or_none()
            if item is None:
                return {"error": "not found"}
            return {"id": item.id, "name": item.name}

        return app

    @pytest.fixture()
    def client(self, app):
        with TestClient(app) as c:
            yield c

    def test_create_and_get_via_dependency(self, client):
        resp = client.post("/items")
        assert resp.status_code == 200
        resp = client.get("/items/1")
        assert resp.status_code == 200
        assert resp.json() == {"id": 1, "name": "test"}

    def test_get_nonexistent_returns_not_found(self, client):
        resp = client.get("/items/999")
        assert resp.json() == {"error": "not found"}
