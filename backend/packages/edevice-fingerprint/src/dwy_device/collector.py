"""固定原生来源和 HMAC 协议; 不缓存、不写盘、不代替宿主决定失败策略。"""

import hashlib
import hmac
import math
import platform
import re

from .models import DeviceErrorCode, DeviceInfo, DeviceSource, DeviceStatus, SystemInfo
from .providers._errors import CollectionError


def collect_device(namespace: str, *, command_timeout: float = 2.0) -> DeviceInfo:
    """采集产品域内的稳定指纹; 只支持 Windows、macOS、Linux 固定系统来源。

    Args:
        namespace: 产品固定域, 1..128 个小写 ASCII 字母、数字、点、下划线或连字符;
            禁止混入账号、API Key、项目路径或 SDK 版本。
        command_timeout: macOS 原生命令超时秒数, 必须是 (0, 30] 内有限数值。

    Returns:
        不可变结果, fingerprint 为 64 位十六进制派生值; 预期采集失败以 status/error_code 表示。
        原始系统身份不进入结果、日志或磁盘; 系统版本与架构不参与派生。

    Raises:
        ValueError: namespace 或 command_timeout 不满足约束, 错误不回显输入值。
    """
    if not isinstance(namespace, str) or re.fullmatch(r"[a-z0-9._-]{1,128}", namespace) is None:
        raise ValueError("namespace must contain 1..128 lowercase ASCII product-domain characters")
    if (
        isinstance(command_timeout, bool)
        or not isinstance(command_timeout, (int, float))
        or not 0 < command_timeout <= 30
        or not math.isfinite(command_timeout)
    ):
        raise ValueError("command_timeout must be a finite number in (0, 30]")

    name = platform.system()
    system = SystemInfo(
        system_name=name[:32],
        system_release=platform.release()[:128],
        system_version=platform.version()[:128],
        architecture=platform.machine()[:32],
    )
    source = None
    try:
        raw, source = _read_machine_id(name, command_timeout)
        normalized = _normalize_machine_id(raw, source)
    except CollectionError as exc:
        status = (
            DeviceStatus.UNSUPPORTED if exc.code is DeviceErrorCode.UNSUPPORTED_PLATFORM else DeviceStatus.UNAVAILABLE
        )
        return DeviceInfo(None, 1, source, status, exc.code, system)

    fingerprint = hmac.new(
        normalized.encode("ascii"), ("dwy.device.v1:" + namespace).encode("utf-8"), hashlib.sha256
    ).hexdigest()
    return DeviceInfo(fingerprint, 1, source, DeviceStatus.AVAILABLE, None, system)


def _read_machine_id(name: str, command_timeout: float) -> tuple[str, DeviceSource]:
    if name == "Windows":
        from .providers.windows import read_machine_id

        return read_machine_id()
    if name == "Darwin":
        from .providers.macos import read_machine_id

        return read_machine_id(command_timeout)
    if name == "Linux":
        from .providers.linux import read_machine_id

        return read_machine_id()
    raise CollectionError(DeviceErrorCode.UNSUPPORTED_PLATFORM)


def _normalize_machine_id(raw: str, source: DeviceSource) -> str:
    value = raw.strip()
    uuid_source = source in (DeviceSource.WINDOWS_MACHINE_GUID, DeviceSource.MACOS_PLATFORM_UUID)
    pattern = r"(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{8}(?:-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12})"
    if re.fullmatch(pattern if uuid_source else r"[0-9a-fA-F]{32}", value) is None:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    normalized = value.replace("-", "").lower()
    if normalized == "0" * 32:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    return normalized
