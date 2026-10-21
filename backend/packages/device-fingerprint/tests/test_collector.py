"""核心协议测试: 派生固定、平台失败可观察, 原始身份不进入公开结果。"""

import importlib
from dataclasses import FrozenInstanceError, asdict

import pytest

from dwy_device import DeviceErrorCode, DeviceSource, DeviceStatus, collect_device
from dwy_device.providers import linux
from dwy_device.providers._errors import CollectionError

MACHINE_ID = "0123456789abcdef0123456789abcdef"


@pytest.fixture
def linux_device(monkeypatch):
    """隔离宿主机器, 避免测试读取真实机器身份。"""
    monkeypatch.setattr("dwy_device.collector.platform.system", lambda: "Linux")
    monkeypatch.setattr(linux, "read_machine_id", lambda: (MACHINE_ID, DeviceSource.LINUX_MACHINE_ID))


def test_known_vector_and_public_result_do_not_expose_raw_identity(linux_device):
    result = collect_device("quantzone")
    expected = "f68e7cf3e5e580aef9c4ffe2b4f5a4fe97dea0dbb5679eee2905147a866a8f96"
    assert result.fingerprint == expected
    assert len(expected) == 64
    assert result.scheme_version == 1
    assert result.status is DeviceStatus.AVAILABLE
    assert result.source is DeviceSource.LINUX_MACHINE_ID
    assert result.error_code is None
    assert MACHINE_ID not in repr(asdict(result))
    with pytest.raises(FrozenInstanceError):
        result.fingerprint = None
    with pytest.raises(FrozenInstanceError):
        result.system.system_name = "other"


def test_namespace_and_system_metadata_are_separate(linux_device, monkeypatch):
    first = collect_device("quantzone")
    monkeypatch.setattr("dwy_device.collector.platform.release", lambda: "new-release")
    monkeypatch.setattr("dwy_device.collector.platform.version", lambda: "new-version")
    monkeypatch.setattr("dwy_device.collector.platform.machine", lambda: "other-architecture")
    assert collect_device("quantzone").fingerprint == first.fingerprint
    assert collect_device("other-product").fingerprint != first.fingerprint


@pytest.mark.parametrize("namespace", [None, True, 7, "", "A", "a b", "中文", "a\n", "a" * 129])
def test_invalid_namespace_rejected(namespace):
    with pytest.raises(ValueError, match="namespace"):
        collect_device(namespace)


@pytest.mark.parametrize("timeout", [None, True, False, "2", 0, -1, 31, float("nan"), float("inf"), 10**400])
def test_invalid_timeout_rejected(timeout):
    with pytest.raises(ValueError, match="command_timeout"):
        collect_device("quantzone", command_timeout=timeout)


def test_parameter_boundaries(linux_device):
    assert collect_device("a" * 128, command_timeout=30).status is DeviceStatus.AVAILABLE
    assert collect_device("a._-0", command_timeout=0.01).status is DeviceStatus.AVAILABLE


@pytest.mark.parametrize("code", [DeviceErrorCode.NOT_FOUND, DeviceErrorCode.PERMISSION_DENIED])
def test_expected_collection_failure_is_safe(linux_device, monkeypatch, code):
    def fail():
        raise CollectionError(code)

    monkeypatch.setattr(linux, "read_machine_id", fail)
    result = collect_device("quantzone")
    assert result.fingerprint is None
    assert result.status is DeviceStatus.UNAVAILABLE
    assert result.error_code is code
    assert str(CollectionError(code)) == code.value


def test_unsupported_platform_is_explicit(monkeypatch):
    monkeypatch.setattr("dwy_device.collector.platform.system", lambda: "Plan9")
    result = collect_device("quantzone")
    assert result.status is DeviceStatus.UNSUPPORTED
    assert result.error_code is DeviceErrorCode.UNSUPPORTED_PLATFORM
    assert result.fingerprint is None


@pytest.mark.parametrize("value", ["0" * 32, "g" * 32, "a" * 31, "a" * 33, "{01234567-89ab-cdef-0123-456789abcdef}"])
def test_invalid_native_identity_not_hashed(linux_device, monkeypatch, value):
    monkeypatch.setattr(linux, "read_machine_id", lambda: (value, DeviceSource.LINUX_MACHINE_ID))
    result = collect_device("quantzone")
    assert result.status is DeviceStatus.UNAVAILABLE
    assert result.error_code is DeviceErrorCode.INVALID_VALUE
    assert result.fingerprint is None


def test_identity_normalization_and_no_cache(linux_device, monkeypatch):
    original = collect_device("quantzone")
    monkeypatch.setattr(linux, "read_machine_id", lambda: (MACHINE_ID.upper() + "\n", DeviceSource.LINUX_MACHINE_ID))
    assert collect_device("quantzone").fingerprint == original.fingerprint
    monkeypatch.setattr(linux, "read_machine_id", lambda: ("1" * 32, DeviceSource.LINUX_MACHINE_ID))
    assert collect_device("quantzone").fingerprint != original.fingerprint


@pytest.mark.parametrize(
    ("platform_name", "module_name", "source"),
    [
        ("Windows", "windows", DeviceSource.WINDOWS_MACHINE_GUID),
        ("Darwin", "macos", DeviceSource.MACOS_PLATFORM_UUID),
    ],
)
def test_uuid_sources_share_normalization(platform_name, module_name, source, monkeypatch):
    module = importlib.import_module("dwy_device.providers." + module_name)
    monkeypatch.setattr("dwy_device.collector.platform.system", lambda: platform_name)
    calls = []

    def read(*args):
        calls.append(args)
        return "01234567-89AB-CDEF-0123-456789ABCDEF", source

    monkeypatch.setattr(module, "read_machine_id", read)
    result = collect_device("quantzone", command_timeout=3.5)
    assert result.fingerprint == "f68e7cf3e5e580aef9c4ffe2b4f5a4fe97dea0dbb5679eee2905147a866a8f96"
    assert result.source is source
    assert calls == ([(3.5,)] if platform_name == "Darwin" else [()])


def test_metadata_limits(linux_device, monkeypatch):
    monkeypatch.setattr("dwy_device.collector.platform.release", lambda: "r" * 500)
    monkeypatch.setattr("dwy_device.collector.platform.version", lambda: "v" * 500)
    monkeypatch.setattr("dwy_device.collector.platform.machine", lambda: "m" * 100)
    system = collect_device("quantzone").system
    assert len(system.system_name) <= 32
    assert len(system.system_release) == 128
    assert len(system.system_version) == 128
    assert len(system.architecture) == 32


def test_unexpected_programming_error_propagates(linux_device, monkeypatch):
    def fail():
        raise RuntimeError("implementation bug")

    monkeypatch.setattr(linux, "read_machine_id", fail)
    with pytest.raises(RuntimeError, match="implementation bug"):
        collect_device("quantzone")
