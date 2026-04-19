"""Tests for dwyeapi.config."""

import pytest
from pydantic import ValidationError

from dwyeapi.config import (
    BaseSettings,
    get_environment,
    is_dev,
    is_prod,
    set_current_environment,
)


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

    def test_debug_field_removed(self, monkeypatch):
        """debug 字段已废弃,请用 environment + is_dev()/is_prod() 代替。"""
        monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("SECRET_KEY", "s")
        s = BaseSettings()
        assert not hasattr(s, "debug")

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


def _set_required_env(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://u:p@localhost/db")
    monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setenv("SECRET_KEY", "s")


@pytest.fixture
def restore_environment():
    """每个测试跑完把全局 environment 复原为 prod,避免测试间相互污染。"""
    yield
    set_current_environment("prod")


class TestEnvironment:
    def test_environment_defaults_prod(self, monkeypatch, restore_environment):
        _set_required_env(monkeypatch)
        monkeypatch.delenv("ENVIRONMENT", raising=False)
        s = BaseSettings()
        assert s.environment == "prod"
        assert is_prod() is True
        assert is_dev() is False

    def test_environment_dev_from_env(self, monkeypatch, restore_environment):
        _set_required_env(monkeypatch)
        monkeypatch.setenv("ENVIRONMENT", "dev")
        s = BaseSettings()
        assert s.environment == "dev"
        assert is_dev() is True
        assert is_prod() is False

    def test_environment_invalid_raises(self, monkeypatch, restore_environment):
        _set_required_env(monkeypatch)
        monkeypatch.setenv("ENVIRONMENT", "staging")
        with pytest.raises(ValidationError):
            BaseSettings()

    def test_get_environment_returns_current(self, monkeypatch, restore_environment):
        _set_required_env(monkeypatch)
        monkeypatch.setenv("ENVIRONMENT", "dev")
        BaseSettings()
        assert get_environment() == "dev"

    def test_is_dev_is_prod_mutually_exclusive(self, restore_environment):
        set_current_environment("dev")
        assert is_dev() is True
        assert is_prod() is False
        set_current_environment("prod")
        assert is_prod() is True
        assert is_dev() is False

    def test_subclass_inherits_environment_sync(self, monkeypatch, restore_environment):
        _set_required_env(monkeypatch)
        monkeypatch.setenv("ENVIRONMENT", "dev")

        class MySettings(BaseSettings):
            custom_field: str = "default"

        MySettings()
        assert is_dev() is True

    def test_module_initial_environment_is_prod(self, restore_environment):
        """eapi 加载后、业务 Settings() 未实例化前,默认按 prod 处理(fail-safe)。"""
        set_current_environment("prod")
        assert get_environment() == "prod"
        assert is_prod() is True
