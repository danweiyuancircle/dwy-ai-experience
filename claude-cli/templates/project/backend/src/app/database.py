"""Database engine and session factory."""

from danweiyuan_eapi.database import create_async_engine_factory, create_session_factory
from danweiyuan_eapi.dependencies import create_get_db

from app.config import settings

engine = create_async_engine_factory(settings.database_url)
session_factory = create_session_factory(engine)
get_db = create_get_db(session_factory)
