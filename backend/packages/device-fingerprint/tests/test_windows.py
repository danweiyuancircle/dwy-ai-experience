"""Windows 原生注册表边界。不要求测试宿主运行 Windows。"""

import builtins
import importlib
import sys
from contextlib import nullcontext
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


@pytest.fixture
def registry(monkeypatch):
    """仅替代 OS API。保留 provider 的导入、选择视图与错误处理。"""
    native = SimpleNamespace(
        HKEY_LOCAL_MACHINE=1,
        KEY_READ=0x20019,
        KEY_WOW64_64KEY=0x100,
        REG_SZ=1,
        OpenKey=Mock(return_value=nullcontext("registry-handle")),
        QueryValueEx=Mock(return_value=("01234567-89AB-CDEF-0123-456789ABCDEF", 1)),
    )
    monkeypatch.setitem(sys.modules, "winreg", native)
    return native


def test_reads_machine_guid_from_64bit_view(registry):
    """32 位 Python 也必须使用同一注册表视图。"""
    provider = importlib.import_module("dwy_device.providers.windows")
    from dwy_device.models import DeviceSource

    value, source = provider.read_machine_id()

    assert value == "01234567-89AB-CDEF-0123-456789ABCDEF"
    assert source is DeviceSource.WINDOWS_MACHINE_GUID
    registry.OpenKey.assert_called_once_with(
        registry.HKEY_LOCAL_MACHINE,
        r"SOFTWARE\Microsoft\Cryptography",
        0,
        registry.KEY_READ | registry.KEY_WOW64_64KEY,
    )
    registry.QueryValueEx.assert_called_once_with("registry-handle", "MachineGuid")


@pytest.mark.parametrize(
    "value,value_type",
    [(123, 1), (b"raw-guid", 1), ("guid", 3), ("", 1), ("x" * 129, 1)],
)
def test_rejects_wrong_registry_type_or_size(registry, value, value_type):
    """注册表属于外部边界。不将任意类型或无限长值传入核心。"""
    provider = importlib.import_module("dwy_device.providers.windows")
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    registry.QueryValueEx.return_value = (value, value_type)
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id()
    assert failure.value.code is DeviceErrorCode.INVALID_VALUE


@pytest.mark.parametrize("operation", ["OpenKey", "QueryValueEx"])
@pytest.mark.parametrize(
    "error,code",
    [
        (FileNotFoundError("private-guid"), "NOT_FOUND"),
        (PermissionError("private-guid"), "PERMISSION_DENIED"),
        (OSError("private-guid"), "COMMAND_FAILED"),
    ],
)
def test_registry_errors_have_safe_codes(registry, operation, error, code):
    """缺失、权限和其他系统错误不得将底层内容带给调用者。"""
    provider = importlib.import_module("dwy_device.providers.windows")
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    getattr(registry, operation).side_effect = error
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id()
    assert failure.value.code is getattr(DeviceErrorCode, code)
    assert "private-guid" not in str(failure.value)
    assert failure.value.__suppress_context__


def test_import_does_not_require_winreg(monkeypatch):
    """非 Windows 导入时不访问平台专属注册表模块。"""
    provider = importlib.import_module("dwy_device.providers.windows")
    original = builtins.__import__

    def prohibit_winreg(name, *args, **kwargs):
        if name == "winreg":
            raise AssertionError("platform-specific import during module loading")
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", prohibit_winreg)
    importlib.reload(provider)
