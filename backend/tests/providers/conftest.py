"""providers 测试共享 fixtures -- 用 fakeredis 替代真实 Redis。"""

import fakeredis.aioredis
import pytest


@pytest.fixture
async def fake_redis():
    """fakeredis 实例,每个测试独立,解码响应与真实 Redis 对齐。"""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()
