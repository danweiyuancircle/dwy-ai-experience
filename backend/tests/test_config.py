"""Tests for danweiyuan_eapi.config."""

import pytest

from danweiyuan_eapi.config import BaseSettings


class TestBaseSettings:
    def test_required_fields_raise_without_env(self, monkeypatch):
        monkeypatch.delenv("DATABASE_URL", raising=False)
        monkeypatch.delenv("REDIS_URL", raising=False)
        monkeypatch.delenv("SECRET_KEY", raising=False)
        with pytest.raises(ValueError):
            BaseSettings()

    def test_construct_with_all_required(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "test-secret")
        s = BaseSettings()
        assert s.database_url == "postgresql+asyncpg://u:p@localhost/db"
        assert s.redis_url == "redis://localhost:6379/0"
        assert s.secret_key == "test-secret"

    def test_debug_defaults_false(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        s = BaseSettings()
        assert s.debug is False

    def test_allowed_origins_defaults_empty(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        s = BaseSettings()
        assert s.allowed_origins == []

    def test_allowed_origins_from_env(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        monkeypatch.setenv("ALLOWED_ORIGINS", '["http://localhost:5173","http://example.com"]')
        s = BaseSettings()
        assert s.allowed_origins == ["http://localhost:5173", "http://example.com"]

    def test_subclass_adds_fields(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        monkeypatch.setenv("CUSTOM_FIELD", "hello")

        class MySettings(BaseSettings):
            custom_field: str = "default"

        s = MySettings()
        assert s.custom_field == "hello"

    def test_jwt_defaults(self, monkeypatch):
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        s = BaseSettings()
        assert s.jwt_algorithm == "HS256"
        assert s.access_token_expire_minutes == 30
