"""FastAPI dependency factories."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


def create_get_db(session_factory: async_sessionmaker[AsyncSession]):
    """Create a get_db FastAPI dependency bound to a session factory."""

    async def get_db() -> AsyncGenerator[AsyncSession]:
        """Yield a database session, automatically closed after the request."""
        async with session_factory() as session:
            yield session

    return get_db
