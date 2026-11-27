"""独立资金数据库，不导入任何宿主项目或认证模型。"""

import pytest_asyncio
from dwyeapi.database import Base
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from dwy_payment.events import PaymentEvent  # noqa: F401
from dwy_payment.models import PaymentOrder  # noqa: F401
from dwy_payment.refunds.models import RefundRecord  # noqa: F401


@pytest_asyncio.fixture
async def payment_db(tmp_path):
    """使用文件SQLite支持独立session；生产并发另由PostgreSQL验收。"""
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'payments.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        yield factory
    finally:
        await engine.dispose()
