"""macOS 原生命令适配。真实子进程验证输出限额与超时回收。"""

import importlib
import plistlib
import subprocess
import sys
import time

import pytest


@pytest.fixture
def launch(monkeypatch):
    """仅替换 ioreg 可执行边界。子进程、管道与计时仍使用真实系统。"""
    if sys.platform == "win32":
        pytest.skip("macOS 管道 selector 行为仅在 POSIX 宿主验证")
    original = subprocess.Popen
    children = []
    calls = []

    def install(script):
        provider = importlib.import_module("dwy_device.providers.macos")

        def spawn(command, **kwargs):
            calls.append((command, kwargs))
            process = original([sys.executable, "-c", script], **kwargs)
            children.append(process)
            return process

        monkeypatch.setattr(provider.subprocess, "Popen", spawn)
        return provider

    yield install, children, calls
    for child in children:
        if child.poll() is None:
            child.kill()
            child.wait()


def _output_script(payload):
    """将测试载荷写到子进程 stdout。避免绕过真实管道行为。"""
    return "import sys; sys.stdout.buffer.write(" + repr(payload) + ")"


def test_reads_uuid_from_bounded_plist_command(launch):
    """只运行固定参数、禁用 shell。舍弃不使用的标准输入与错误输出。"""
    install, children, calls = launch
    from dwy_device.models import DeviceSource

    uuid = "01234567-89AB-CDEF-0123-456789ABCDEF"
    provider = install(_output_script(plistlib.dumps([{"IOPlatformUUID": uuid}])))

    assert provider.read_machine_id(2.0) == (uuid, DeviceSource.MACOS_PLATFORM_UUID)
    command, options = calls[0]
    assert command[0] == "/usr/sbin/ioreg"
    assert "IOPlatformExpertDevice" in command
    assert "-a" in command
    assert options["shell"] is False
    assert options["stdin"] is subprocess.DEVNULL
    assert options["stderr"] is subprocess.DEVNULL
    assert children[0].poll() == 0


@pytest.mark.parametrize(
    "payload",
    [
        b"private-guid-not-a-plist",
        b'<?xml version="1.0"?><plist><array><dict>',
        plistlib.dumps({"IOPlatformUUID": "private-guid"}),
        plistlib.dumps([]),
        plistlib.dumps([{}]),
        plistlib.dumps([{"IOPlatformUUID": 123}]),
        plistlib.dumps([{"IOPlatformUUID": ""}]),
        plistlib.dumps([{"IOPlatformUUID": "x" * 129}]),
    ],
)
def test_rejects_invalid_plist_or_identity_without_leaking_output(launch, payload):
    """结构或字段无效时仅返回安全码。不将 plist 载荷放入异常。"""
    install, children, _ = launch
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    provider = install(_output_script(payload))
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(2.0)
    assert failure.value.code is DeviceErrorCode.INVALID_VALUE
    assert "private-guid" not in str(failure.value)
    assert children[0].poll() is not None


def test_nonzero_exit_has_safe_error_code(launch):
    """命令退出失败优先于载荷解析。不泄露 stderr。"""
    install, children, _ = launch
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    provider = install("import sys; sys.stderr.write('private-guid'); sys.exit(7)")
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(2.0)
    assert failure.value.code is DeviceErrorCode.COMMAND_FAILED
    assert "private-guid" not in str(failure.value)
    assert children[0].poll() == 7


def test_timeout_kills_and_reaps_child(launch):
    """无输出且不退出的命令也必须在总时限内回收。"""
    install, children, _ = launch
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    provider = install("import time; time.sleep(30)")
    started = time.monotonic()
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(0.1)
    assert failure.value.code is DeviceErrorCode.TIMEOUT
    assert time.monotonic() - started < 3
    assert children[0].poll() is not None


def test_timeout_applies_after_stdout_is_closed(launch):
    """管道 EOF 不能使仍在运行的子进程越过总时限。"""
    install, children, _ = launch
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    provider = install("import os,time; os.close(1); time.sleep(30)")
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(0.5)
    assert failure.value.code is DeviceErrorCode.TIMEOUT
    assert children[0].poll() is not None


def test_excess_output_is_stopped_before_child_finishes(launch):
    """输出上限在读取期间生效。不能先 communicate 全量收集。"""
    install, children, _ = launch
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    provider = install(
        "import sys,time; sys.stdout.buffer.write(b'x'*1048576); sys.stdout.buffer.flush(); time.sleep(30)"
    )
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(2.0)
    assert failure.value.code is DeviceErrorCode.INVALID_VALUE
    assert children[0].poll() is not None


@pytest.mark.parametrize(
    "error,code",
    [
        (FileNotFoundError("private-guid"), "NOT_FOUND"),
        (PermissionError("private-guid"), "PERMISSION_DENIED"),
        (OSError("private-guid"), "COMMAND_FAILED"),
    ],
)
def test_process_start_errors_have_safe_codes(monkeypatch, error, code):
    """原生命令不可启动时不传播带环境内容的 OSError。"""
    provider = importlib.import_module("dwy_device.providers.macos")
    from dwy_device.models import DeviceErrorCode
    from dwy_device.providers._errors import CollectionError

    def fail_start(*args, **kwargs):
        raise error

    monkeypatch.setattr(provider.subprocess, "Popen", fail_start)
    with pytest.raises(CollectionError) as failure:
        provider.read_machine_id(2.0)
    assert failure.value.code is getattr(DeviceErrorCode, code)
    assert "private-guid" not in str(failure.value)
    assert failure.value.__suppress_context__
