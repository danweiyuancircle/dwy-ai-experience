"""原生验收显式启用, 比较子进程结果但不向 CI 日志输出真实指纹。"""

import json
import os
import subprocess
import sys

import pytest

from dwy_device import DeviceStatus, collect_device


@pytest.mark.skipif(os.environ.get("DWY_DEVICE_NATIVE_TEST") != "1", reason="native OS acceptance is opt-in")
def test_native_fingerprint_stable_across_processes():
    """同运行环境的独立进程应取得相同产品指纹, 错误报告仅显示安全状态。"""
    info = collect_device("dwy.native.test")
    assert info.status is DeviceStatus.AVAILABLE, (info.status.value, info.error_code)
    script = """
import json
from dwy_device import collect_device
info = collect_device("dwy.native.test")
print(json.dumps({"status": info.status.value, "fingerprint": info.fingerprint}))
"""
    result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 0, "native child process failed"
    child = json.loads(result.stdout)
    matches = child["status"] == "available" and child["fingerprint"] == info.fingerprint
    assert matches, "native fingerprint changed across processes"
