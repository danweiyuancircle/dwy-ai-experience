"""Linux 仅使用系统 machine-id; 主来源损坏或不可读时不隐式改变身份来源。"""

from pathlib import Path

from ..models import DeviceErrorCode, DeviceSource
from ._errors import CollectionError

_PRIMARY_PATH = Path("/etc/machine-id")
_DBUS_PATH = Path("/var/lib/dbus/machine-id")
_MAX_ID_BYTES = 128


def read_machine_id() -> tuple[str, DeviceSource]:
    """读取最多 128 字节, 仅主文件不存在时使用 D-Bus 路径; 格式交由核心统一校验。"""
    try:
        return _read_path(_PRIMARY_PATH), DeviceSource.LINUX_MACHINE_ID
    except FileNotFoundError:
        try:
            return _read_path(_DBUS_PATH), DeviceSource.LINUX_DBUS_MACHINE_ID
        except FileNotFoundError:
            raise CollectionError(DeviceErrorCode.NOT_FOUND) from None


def _read_path(path: Path) -> str:
    try:
        with path.open("rb") as handle:
            content = handle.read(_MAX_ID_BYTES + 1)
    except FileNotFoundError:
        raise
    except PermissionError:
        raise CollectionError(DeviceErrorCode.PERMISSION_DENIED) from None
    except OSError:
        raise CollectionError(DeviceErrorCode.COMMAND_FAILED) from None
    if len(content) > _MAX_ID_BYTES:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    try:
        return content.decode("ascii")
    except UnicodeDecodeError:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE) from None
