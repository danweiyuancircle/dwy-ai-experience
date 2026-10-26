"""可选设备门面必须保持核心类型一致, 并隔离缺失依赖。"""

import subprocess
import sys


def test_device_facade_reuses_core_contract():
    """门面复用唯一实现, 避免后端与 SDK 各自派生不同指纹。"""
    import dwy_device

    from dwyeapi import device

    for name in (
        "collect_device",
        "DeviceInfo",
        "SystemInfo",
        "DeviceSource",
        "DeviceStatus",
        "DeviceErrorCode",
    ):
        assert getattr(device, name) is getattr(dwy_device, name)


def test_base_import_does_not_require_device_extra():
    """缺设备 extra 不影响已有 eapi 用户; 显式使用时才提示 PyPI 安装。"""
    script = """
import importlib.abc
import sys

class MissingDevice(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "dwy_device":
            raise ModuleNotFoundError("not installed", name="dwy_device")

sys.meta_path.insert(0, MissingDevice())
import dwyeapi
assert "dwyeapi.device" not in sys.modules
try:
    import dwyeapi.device
except ModuleNotFoundError as error:
    assert error.name == "dwy_device"
    assert "dwyeapi[device]" in str(error)
    assert "PyPI" in str(error)
    assert "私有" not in str(error)
else:
    raise AssertionError("missing optional package must be reported")
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr


def test_facade_preserves_unrelated_import_failure():
    """核心内部导入错误不能被伪装成缺少设备 extra。"""
    script = """
import importlib.abc
import sys

class BrokenDevice(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname == "dwy_device":
            raise ModuleNotFoundError("broken internal import", name="broken_internal")

sys.meta_path.insert(0, BrokenDevice())
try:
    import dwyeapi.device
except ModuleNotFoundError as error:
    assert error.name == "broken_internal"
    assert "dwyeapi[device]" not in str(error)
else:
    raise AssertionError("internal import error must propagate")
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
