"""Linux 固定来源及有界读取, 不以备用来源掩盖损坏或权限错误。"""

from pathlib import Path

import pytest

from dwy_device import DeviceErrorCode, DeviceSource, DeviceStatus, collect_device
from dwy_device.providers import linux
from dwy_device.providers._errors import CollectionError


@pytest.fixture
def machine_paths(monkeypatch, tmp_path):
    """测试只读取临时目录, 不接触宿主身份。"""
    primary, dbus = tmp_path / "machine-id", tmp_path / "dbus-machine-id"
    monkeypatch.setattr(linux, "_PRIMARY_PATH", primary)
    monkeypatch.setattr(linux, "_DBUS_PATH", dbus)
    return primary, dbus


def test_primary_has_priority(machine_paths):
    primary, dbus = machine_paths
    primary.write_text("a" * 32 + "\n")
    dbus.write_text("b" * 32)
    assert linux.read_machine_id() == ("a" * 32 + "\n", DeviceSource.LINUX_MACHINE_ID)


def test_fallback_only_when_primary_missing(machine_paths):
    _, dbus = machine_paths
    dbus.write_text("b" * 32)
    assert linux.read_machine_id() == ("b" * 32, DeviceSource.LINUX_DBUS_MACHINE_ID)


@pytest.mark.parametrize("content", ["invalid", "0" * 32, ""])
def test_invalid_primary_never_falls_back(machine_paths, monkeypatch, content):
    primary, dbus = machine_paths
    primary.write_text(content)
    dbus.write_text("b" * 32)
    monkeypatch.setattr("dwy_device.collector.platform.system", lambda: "Linux")
    result = collect_device("quantzone")
    assert result.status is DeviceStatus.UNAVAILABLE
    assert result.error_code is DeviceErrorCode.INVALID_VALUE
    assert result.source is DeviceSource.LINUX_MACHINE_ID


def test_missing_paths_are_safe(machine_paths):
    with pytest.raises(CollectionError) as caught:
        linux.read_machine_id()
    assert caught.value.code is DeviceErrorCode.NOT_FOUND


def test_permissions_do_not_trigger_fallback(machine_paths, monkeypatch):
    primary, dbus = machine_paths
    dbus.write_text("b" * 32)
    original = Path.open

    def fail(path, *args, **kwargs):
        if path == primary:
            raise PermissionError("raw host details")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(CollectionError) as caught:
        linux.read_machine_id()
    assert caught.value.code is DeviceErrorCode.PERMISSION_DENIED
    assert "raw host details" not in str(caught.value)


@pytest.mark.parametrize("content", [b"a" * 129, b"\xff" * 32])
def test_bounded_ascii_read(machine_paths, content):
    primary, _ = machine_paths
    primary.write_bytes(content)
    with pytest.raises(CollectionError) as caught:
        linux.read_machine_id()
    assert caught.value.code is DeviceErrorCode.INVALID_VALUE


def test_io_error_is_safe(machine_paths, monkeypatch):
    def fail(*args, **kwargs):
        raise OSError("raw mount details")

    monkeypatch.setattr(Path, "open", fail)
    with pytest.raises(CollectionError) as caught:
        linux.read_machine_id()
    assert caught.value.code is DeviceErrorCode.COMMAND_FAILED
    assert "raw mount details" not in str(caught.value)
