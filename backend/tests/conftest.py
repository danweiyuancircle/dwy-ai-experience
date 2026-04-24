"""tests 根级 fixtures。

提供跨测试文件的通用清理逻辑,避免单个测试改动全局状态后污染后续测试。
"""

import pytest

from dwyeapi.config import set_current_environment


@pytest.fixture(autouse=True)
def _restore_environment_after_test():
    """每个测试结束后把全局 environment 复原为 ``"prod"``。

    背景:``dwyeapi.config._current_environment`` 是模块级全局,部分测试
    (如 ``test_exceptions.py`` 的 dev/prod 切换、``test_config.py`` 的
    Environment 系列)会在测试中调用 ``set_current_environment("dev")``。
    若不强制复原,一旦测试 body 在恢复前异常退出或忘记 ``finally``,后续
    测试会在错误的 environment 下跑,可能误判 dev/prod 行为差异。

    测试默认环境为 ``"prod"``,与 ``BaseSettings.environment`` 默认值一致。
    """
    yield
    set_current_environment("prod")
