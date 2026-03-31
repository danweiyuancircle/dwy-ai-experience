"""Tests for danweiyuan_base.cache."""

import pytest

import danweiyuan_base.cache as cache_mod
from danweiyuan_base.cache import close_redis, configure, get_redis


class TestCacheConfiguration:
    @pytest.fixture(autouse=True)
    async def cleanup(self):
        yield
        cache_mod._redis_url = None
        cache_mod._redis = None

    async def test_get_redis_without_configure_raises(self):
        cache_mod._redis_url = None
        cache_mod._redis = None
        with pytest.raises(RuntimeError, match="not configured"):
            await get_redis()

    async def test_configure_sets_url(self):
        configure("redis://localhost:6379/15")
        assert cache_mod._redis_url == "redis://localhost:6379/15"

    async def test_close_redis_is_safe_when_not_connected(self):
        cache_mod._redis = None
        await close_redis()  # should not raise
