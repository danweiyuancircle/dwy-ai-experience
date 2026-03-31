"""Tests for danweiyuan_base.database."""

import pytest
from sqlalchemy import String, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column

from danweiyuan_base.database import Base, TimestampMixin, create_async_engine_factory, create_session_factory


class FakeModel(Base, TimestampMixin):
    __tablename__ = "fake_items"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))


class TestDatabaseFactory:
    @pytest.fixture()
    async def session(self):
        engine = create_async_engine_factory("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        session_factory = create_session_factory(engine)
        async with session_factory() as session:
            yield session
        await engine.dispose()

    async def test_insert_and_query(self, session: AsyncSession):
        item = FakeModel(id=1, name="test-item")
        session.add(item)
        await session.commit()
        result = await session.execute(select(FakeModel).where(FakeModel.id == 1))
        found = result.scalar_one()
        assert found.name == "test-item"

    async def test_timestamp_mixin_has_columns(self):
        assert hasattr(FakeModel, "created_at")
        assert hasattr(FakeModel, "updated_at")

    async def test_base_is_declarative(self):
        assert hasattr(Base, "metadata")
        assert "fake_items" in Base.metadata.tables
