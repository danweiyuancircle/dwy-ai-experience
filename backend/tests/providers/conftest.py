"""providers 测试共享 fixtures -- 用 fakeredis 替代真实 Redis。"""

import fakeredis.aioredis
import pytest

from dwyeapi.config import set_current_environment


@pytest.fixture(autouse=True)
def _default_dev_environment():
    """provider 测试默认在 dev 环境下执行(等价于业务 Settings() 加载 ENVIRONMENT=dev)。

    专门校验 prod 行为的测试用例,在用例内自行调用 ``set_current_environment("prod")`` 覆盖。
    """
    set_current_environment("dev")
    yield
    set_current_environment("prod")


@pytest.fixture
async def fake_redis():
    """fakeredis 实例,每个测试独立,解码响应与真实 Redis 对齐。"""
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    yield client
    await client.flushall()
    await client.aclose()
