"""独立于后端框架的设备采集契约; 公开结果不包含原始系统身份。"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DeviceSource(str, Enum):
    """实际读取的固定来源; 标签不参与指纹派生。"""

    WINDOWS_MACHINE_GUID = "windows_machine_guid"
    MACOS_PLATFORM_UUID = "macos_platform_uuid"
    LINUX_MACHINE_ID = "linux_machine_id"
    LINUX_DBUS_MACHINE_ID = "linux_dbus_machine_id"


class DeviceStatus(str, Enum):
    """区分采集成功、系统身份不可读与平台不支持。"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    UNSUPPORTED = "unsupported"


class DeviceErrorCode(str, Enum):
    """可安全记录的失败分类, 不携带命令输出或系统原始值。"""

    UNSUPPORTED_PLATFORM = "unsupported_platform"
    NOT_FOUND = "not_found"
    PERMISSION_DENIED = "permission_denied"
    TIMEOUT = "timeout"
    INVALID_VALUE = "invalid_value"
    COMMAND_FAILED = "command_failed"


@dataclass(frozen=True)
class SystemInfo:
    """仅作辅助信息; 名称/架构最多 32 字符, release/version 最多 128 字符。"""

    system_name: str
    system_release: str
    system_version: str
    architecture: str


@dataclass(frozen=True)
class DeviceInfo:
    """产品域内的指纹结果; 失败返回 None, 调用方自行决定请求策略。"""

    fingerprint: Optional[str]
    scheme_version: int
    source: Optional[DeviceSource]
    status: DeviceStatus
    error_code: Optional[DeviceErrorCode]
    system: SystemInfo
