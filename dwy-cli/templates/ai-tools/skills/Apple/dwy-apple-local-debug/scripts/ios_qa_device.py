"""查找或创建指定 iOS 大版本的共享 QA 模拟器，输出 UDID。"""

import argparse
import fcntl
import json
import re
import subprocess
import sys
from pathlib import Path
from uuid import UUID


def _simctl(*args):
    return subprocess.check_output(["xcrun", "simctl", *args], text=True).strip()


def _inventory():
    return json.loads(_simctl("list", "-j"))


def resolve_device(major):
    """返回 UDID、runtime 版本和是否新建。调用方需串行执行查询和创建。"""
    name = f"IOS{major}-QA"
    inventory = _inventory()
    runtime_pattern = re.compile(rf"^com\.apple\.CoreSimulator\.SimRuntime\.iOS-{major}(?:-|$)")
    runtimes = {
        runtime["identifier"]: runtime for runtime in inventory["runtimes"]
        if runtime_pattern.match(runtime["identifier"]) and runtime["isAvailable"]
    }
    matches = [
        (runtime_id, device) for runtime_id, devices in inventory["devices"].items()
        for device in devices if device["name"] == name
    ]
    if len(matches) > 1:
        details = ", ".join(f"{runtime_id} ({device['udid']})" for runtime_id, device in matches)
        raise ValueError(f"存在多个同名模拟器 {name}：{details}")
    if matches:
        runtime_id, device = matches[0]
        if not runtime_pattern.match(runtime_id):
            raise ValueError(f"{name} 当前的 runtime 不属于 iOS {major}：{runtime_id}")
        if runtime_id not in runtimes or not device["isAvailable"]:
            raise ValueError(f"{name} 或其 runtime 不可用：{runtime_id}")
        return device["udid"], runtimes[runtime_id]["version"], False

    if not runtimes:
        raise ValueError(f"缺少可用的 iOS {major} runtime，请核对当前 Xcode 的已安装组件。")

    def version(runtime):
        return tuple(map(int, runtime["version"].split(".")))

    for runtime in sorted(runtimes.values(), key=version, reverse=True):
        models = [
            (int(match[1]), device_type["identifier"])
            for device_type in runtime["supportedDeviceTypes"]
            if (match := re.fullmatch(r"iPhone (\d+)", device_type["name"]))
        ]
        if models:
            _, device_type_id = max(models, key=lambda model: (model[0] == 16, model[0]))
            udid = _simctl("create", name, device_type_id, runtime["identifier"])
            return udid, runtime["version"], True
    raise ValueError(f"已安装的 iOS {major} runtime 没有兼容的标准版 iPhone。")


def main():
    """仅将有效 UDID 写入 stdout，供后续构建、安装和启动使用。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("major", type=int, choices=(18, 26, 27))
    args = parser.parse_args()
    lock_dir = Path.home() / "Library" / "Caches" / "DWY iOS QA"
    try:
        lock_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        with (lock_dir / f"ios-{args.major}.lock").open("a") as lock:
            # 多个项目会共用设备，锁必须覆盖查询和创建。
            fcntl.flock(lock, fcntl.LOCK_EX)
            udid, version, created = resolve_device(args.major)
            UUID(udid)
        action = "已创建" if created else "已复用"
        print(f"{action} IOS{args.major}-QA（iOS {version}）", file=sys.stderr)
        print(udid)
    except (OSError, subprocess.CalledProcessError, KeyError, TypeError, ValueError) as error:
        print(f"iOS QA 设备选择失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
