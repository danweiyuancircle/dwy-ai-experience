"""读取固定 Windows 系统身份。不回退到不同语义的硬件标识。"""

from ..models import DeviceErrorCode, DeviceSource
from ._errors import CollectionError


def read_machine_id() -> tuple[str, DeviceSource]:
    """读取 64 位 MachineGuid。原始值仅交给内部核心校验与派生。"""
    # 非 Windows 也能安全导入包。只有明确分发到此平台时才加载原生模块。
    import winreg

    try:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            winreg.KEY_READ | winreg.KEY_WOW64_64KEY,
        ) as key:
            value, value_type = winreg.QueryValueEx(key, "MachineGuid")
    except FileNotFoundError:
        raise CollectionError(DeviceErrorCode.NOT_FOUND) from None
    except PermissionError:
        raise CollectionError(DeviceErrorCode.PERMISSION_DENIED) from None
    except OSError:
        raise CollectionError(DeviceErrorCode.COMMAND_FAILED) from None

    # 只接收有界字符串。UUID 规范化由三平台共用的核心完成。
    if value_type != winreg.REG_SZ or not isinstance(value, str) or not 1 <= len(value) <= 128:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    return value, DeviceSource.WINDOWS_MACHINE_GUID
