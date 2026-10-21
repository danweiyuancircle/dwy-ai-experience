"""通过固定 ioreg 查询获取 macOS 平台 UUID。限制总耗时和输出内存。"""

import os
import plistlib
import selectors
import subprocess
import time
from xml.parsers.expat import ExpatError

from ..models import DeviceErrorCode, DeviceSource
from ._errors import CollectionError

# 查询限定单层设备。上限仍在读取期间执行。不能先捕获所有输出再截断。
_MAX_OUTPUT_BYTES = 65536
_COMMAND = ("/usr/sbin/ioreg", "-a", "-r", "-d", "1", "-c", "IOPlatformExpertDevice")


def _read_output(process: subprocess.Popen, deadline: float) -> bytes:
    assert process.stdout is not None
    output = bytearray()
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise CollectionError(DeviceErrorCode.TIMEOUT)
            chunk = os.read(process.stdout.fileno(), min(4096, _MAX_OUTPUT_BYTES + 1 - len(output)))
            if not chunk:
                break
            output.extend(chunk)
            if len(output) > _MAX_OUTPUT_BYTES:
                raise CollectionError(DeviceErrorCode.INVALID_VALUE)

    process.wait(timeout=max(0.0, deadline - time.monotonic()))
    if process.returncode != 0:
        raise CollectionError(DeviceErrorCode.COMMAND_FAILED)
    return bytes(output)


def _query_ioreg(command_timeout: float) -> bytes:
    deadline = time.monotonic() + command_timeout
    try:
        process = subprocess.Popen(
            _COMMAND,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            shell=False,
            bufsize=0,
        )
    except FileNotFoundError:
        raise CollectionError(DeviceErrorCode.NOT_FOUND) from None
    except PermissionError:
        raise CollectionError(DeviceErrorCode.PERMISSION_DENIED) from None
    except OSError:
        raise CollectionError(DeviceErrorCode.COMMAND_FAILED) from None

    try:
        return _read_output(process, deadline)
    except subprocess.TimeoutExpired:
        raise CollectionError(DeviceErrorCode.TIMEOUT) from None
    except OSError:
        raise CollectionError(DeviceErrorCode.COMMAND_FAILED) from None
    finally:
        # 超时和超限都必须回收子进程。不能留下持有管道的 ioreg。
        if process.poll() is None:
            process.kill()
        process.wait()
        assert process.stdout is not None
        process.stdout.close()


def read_machine_id(command_timeout: float) -> tuple[str, DeviceSource]:
    """读取有界 plist。调用者已校验超时。原始 UUID 不进入错误信息。"""
    output = _query_ioreg(command_timeout)
    try:
        devices = plistlib.loads(output)
    except (plistlib.InvalidFileException, ExpatError, ValueError, TypeError, OverflowError):
        raise CollectionError(DeviceErrorCode.INVALID_VALUE) from None

    if not isinstance(devices, list) or len(devices) != 1 or not isinstance(devices[0], dict):
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    value = devices[0].get("IOPlatformUUID")
    if not isinstance(value, str) or not 1 <= len(value) <= 128:
        raise CollectionError(DeviceErrorCode.INVALID_VALUE)
    return value, DeviceSource.MACOS_PLATFORM_UUID
