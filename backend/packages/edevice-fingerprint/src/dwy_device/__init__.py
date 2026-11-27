"""零运行时依赖的设备指纹采集; 导入时不读取系统身份或执行命令。"""

from .collector import collect_device
from .models import DeviceErrorCode, DeviceInfo, DeviceSource, DeviceStatus, SystemInfo

__all__ = ["DeviceErrorCode", "DeviceInfo", "DeviceSource", "DeviceStatus", "SystemInfo", "collect_device"]
