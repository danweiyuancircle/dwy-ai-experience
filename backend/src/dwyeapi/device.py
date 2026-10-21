"""设备指纹可选门面; 核心无需安装 FastAPI 即可供 Python 3.9+ 应用使用。"""

try:
    from dwy_device import (
        DeviceErrorCode,
        DeviceInfo,
        DeviceSource,
        DeviceStatus,
        SystemInfo,
        collect_device,
    )
except ModuleNotFoundError as error:
    if error.name != "dwy_device":
        raise
    raise ModuleNotFoundError(
        "设备能力需要 dwyeapi[device]; 请从私有 Release 安装匹配的 dwy-device-fingerprint wheel。",
        name="dwy_device",
    ) from None

__all__ = [
    "DeviceErrorCode",
    "DeviceInfo",
    "DeviceSource",
    "DeviceStatus",
    "SystemInfo",
    "collect_device",
]
