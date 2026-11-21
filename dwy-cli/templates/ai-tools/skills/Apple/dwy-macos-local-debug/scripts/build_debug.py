#!/usr/bin/env python3
"""构建并更新当前用户固定路径的 macOS Debug 应用。"""

import argparse
import ctypes
import fcntl
import json
import os
from pathlib import Path
import plistlib
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing


def command(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def debug_bundle(app, bundle_id, team_id):
    """核对身份、开发签名与调试权利，防止覆盖同名正式安装。"""
    with (app / "Contents/Info.plist").open("rb") as info:
        identifier = plistlib.load(info)["CFBundleIdentifier"]
    if identifier != bundle_id:
        raise RuntimeError(f"应用 Bundle ID 与目标不符：{app}")
    signature = command("/usr/bin/codesign", "-dv", "--verbose=4", app,
                        stderr=subprocess.PIPE, text=True).stderr
    if "Authority=Apple Development:" not in signature or f"TeamIdentifier={team_id}" not in signature.splitlines():
        raise RuntimeError(f"应用缺少指定团队的 Apple Development 签名：{app}")
    entitlements = command("/usr/bin/codesign", "-d", "--entitlements", ":-", app,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    if not entitlements or plistlib.loads(entitlements).get("com.apple.security.get-task-allow") is not True:
        raise RuntimeError(f"应用缺少 Debug 签名权利 com.apple.security.get-task-allow：{app}")
    command("/usr/bin/codesign", "--verify", "--deep", "--strict", app)


def running_apps(bundle_id):
    result = command("/usr/bin/osascript", "-l", "JavaScript", "-e", """
        ObjC.import("AppKit");
        function run(args) {
            const apps = $.NSRunningApplication.runningApplicationsWithBundleIdentifier(args[0]);
            const results = [];
            for (let index = 0; index < apps.count; index++) {
                const app = apps.objectAtIndex(index);
                results.push([app.processIdentifier, ObjC.unwrap(app.bundleURL.path)]);
            }
            return JSON.stringify(results);
        }
    """, bundle_id, stdout=subprocess.PIPE, text=True, timeout=10).stdout
    return {pid: Path(path).resolve() for pid, path in json.loads(result)}


def stop_installed(app, bundle_id):
    processes = running_apps(bundle_id)
    if any(path != app for path in processes.values()):
        paths = "\n".join(str(path) for path in processes.values() if path != app)
        raise RuntimeError(f"相同 Bundle ID 的其他应用实例正在运行，请先退出：\n{paths}")
    if processes:
        # 走原生退出请求，让应用有机会提交偏好和数据库写入。
        command("/usr/bin/osascript", "-l", "JavaScript", "-e", """
            ObjC.import("AppKit");
            function run(args) {
                for (const pid of args.slice(1)) {
                    const target = $.NSRunningApplication.runningApplicationWithProcessIdentifier(Number(pid));
                    if (target.isNil()) continue;
                    if (ObjC.unwrap(target.bundleURL.path) !== args[0] || !target.terminate) {
                        throw new Error("无法请求旧应用正常退出");
                    }
                }
            }
        """, app, *(str(pid) for pid in processes), timeout=20)
    deadline = time.monotonic() + 20
    while running_apps(bundle_id):
        if time.monotonic() >= deadline:
            raise RuntimeError("等待旧应用退出超时。")
        time.sleep(0.25)


def verify_database(file, options):
    with closing(sqlite3.connect(file.as_uri() + options, uri=True)) as database:
        if database.execute("PRAGMA integrity_check").fetchall() != [("ok",)]:
            raise RuntimeError(f"备份 SQLite 完整性校验失败：{file.name}")


def verify_backup(container, backup):
    """对照文件字节、目录和符号链接，并检查目录副本中的 SQLite 数据库。"""
    if container.is_file():
        if container.read_bytes() != backup.read_bytes():
            raise RuntimeError("文件备份与原数据不一致。")
        return
    changes = command("/usr/bin/rsync", "-rlDcin", "--delete", f"{container}/", f"{backup}/",
                      stdout=subprocess.PIPE, text=True, timeout=120).stdout
    if changes:
        raise RuntimeError("容器备份与原数据不一致。")
    for file in backup.rglob("*"):
        if file.is_symlink() or not file.is_file():
            continue
        with file.open("rb") as handle:
            if handle.read(16) != b"SQLite format 3\x00":
                continue
        wal = file.with_name(file.name + "-wal")
        if not wal.is_file():
            verify_database(file, "?mode=ro&immutable=1")
            continue
        # SQLite 读取 WAL 时会写共享内存文件，校验使用临时副本以保留原备份。
        with tempfile.TemporaryDirectory(dir=backup.parent) as temporary:
            copied = Path(temporary) / file.name
            shutil.copyfile(file, copied)
            shutil.copyfile(wal, copied.with_name(wal.name))
            verify_database(copied, "?mode=ro")


def replace(source, destination):
    """同一文件系统上把完整签名包一次换入；失败时目的路径仍保留旧包。"""
    if not destination.exists():
        source.rename(destination)
        return
    rename = ctypes.CDLL(None, use_errno=True).renamex_np
    rename.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint)
    rename.restype = ctypes.c_int
    if rename(os.fsencode(source), os.fsencode(destination), 0x00000002) != 0:  # RENAME_SWAP
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error), str(destination))


def launch(app, bundle_id):
    command("/usr/bin/open", "-a", app)
    deadline = time.monotonic() + 20
    while time.monotonic() < deadline:
        if list(running_apps(bundle_id).values()) == [app]:
            time.sleep(1)
            if list(running_apps(bundle_id).values()) == [app]:
                return
        time.sleep(0.25)
    raise RuntimeError(f"未确认唯一进程从该路径启动：{app}")


def install(candidate, installed, bundle_id):
    """保留原包直到新进程稳定启动；回滚受阻时保留现场。"""
    had_install = installed.exists()
    replace(candidate, installed)
    try:
        launch(installed, bundle_id)
    except (OSError, subprocess.SubprocessError, RuntimeError, ValueError, KeyError, KeyboardInterrupt):
        stop_installed(installed, bundle_id)
        if had_install:
            replace(candidate, installed)
        else:
            installed.rename(candidate)
        raise


def backup_data(paths, state, bundle_id):
    """校验本轮全部备份后原子替换上次快照。"""
    with tempfile.TemporaryDirectory(prefix=".backup-", dir=state) as temporary:
        snapshot = Path(temporary) / "Data"
        snapshot.mkdir()
        for index, source in enumerate(paths, start=1):
            target = snapshot / f"{index}-{source.name}"
            command("/usr/bin/ditto", source, target, timeout=120)
            verify_backup(source, target)
        if running_apps(bundle_id):
            raise RuntimeError("备份期间应用已被启动，请退出后重试。")
        (snapshot / "sources.json").write_text(
            json.dumps([str(path) for path in paths], ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        replace(snapshot, state / "Data")
    print(f"已校验数据备份 {state / 'Data'}", flush=True)


def build_and_install(args):
    """在整个构建和安装事务中持有按 Bundle ID 划分的锁。"""
    home = Path.home().resolve()
    installed = (home / "Applications").resolve() / args.app
    product_path = args.product.expanduser()
    product = product_path.resolve()
    state = home / "Library/Application Support/DWY Debug Build" / args.bundle_id
    paths = [path.expanduser().resolve() for path in args.data]
    if (product_path.is_symlink() or product.suffix != ".app"
            or product == installed.resolve() or installed in product.parents):
        raise RuntimeError("构建产物必须是独立于安装路径的 .app。")
    for path in paths:
        if path == state or path in state.parents or state in path.parents:
            raise RuntimeError(f"备份来源不可与备份目录重叠：{path}")
        if not path.exists() and installed.exists():
            raise RuntimeError(f"现有安装的预期数据路径未找到：{path}")
        if path.is_file() and path.suffix != ".plist":
            raise RuntimeError(f"单文件数据仅接受 plist；数据库应配置其所在目录：{path}")
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    with (state / "build.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if installed.is_symlink():
            raise RuntimeError(f"安装路径为符号链接：{installed}")
        previous_inode = None
        if installed.exists():
            debug_bundle(installed, args.bundle_id, args.team_id)
            previous_inode = installed.stat().st_ino
        stop_installed(installed, args.bundle_id)
        command(*args.build)
        if product_path.is_symlink() or product_path.resolve() != product:
            raise RuntimeError("构建产物路径已变化，停止安装。")
        debug_bundle(product, args.bundle_id, args.team_id)

        installed.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".adbox-debug-", dir=installed.parent))
        # 交换后的旧包仅作回滚数据，避免在启动阶段出现第二个 .app 入口。
        candidate = staging / "Bundle"
        preserve_staging = False
        try:
            command("/usr/bin/ditto", product, candidate, timeout=120)
            debug_bundle(candidate, args.bundle_id, args.team_id)
            if running_apps(args.bundle_id):
                raise RuntimeError("构建期间应用已被启动，请退出后重试。")
            current_paths = [path for path in paths if path.exists()]
            if previous_inode is not None and current_paths != paths:
                raise RuntimeError("构建期间预期数据路径已变化，停止覆盖。")
            if current_paths:
                backup_data(current_paths, state, args.bundle_id)
            if installed.is_symlink() or (installed.stat().st_ino if installed.exists() else None) != previous_inode:
                raise RuntimeError("构建期间安装路径已变化，停止覆盖。")
            try:
                install(candidate, installed, args.bundle_id)
            except BaseException:
                preserve_staging = (previous_inode is not None and candidate.exists()
                                    and candidate.stat().st_ino == previous_inode)
                if preserve_staging:
                    print(f"自动恢复受阻，旧包保存在 {candidate}", file=sys.stderr)
                raise
        finally:
            if not preserve_staging:
                shutil.rmtree(staging)
        shutil.rmtree(product)
        print(f"已安装并启动 {installed}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--app", required=True, help="固定安装的 .app 文件名")
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--team-id", required=True)
    parser.add_argument("--product", required=True, type=Path, help="项目专用构建目录中的 .app；成功后由脚本清理")
    storage = parser.add_mutually_exclusive_group(required=True)
    storage.add_argument("--data", action="append", type=Path, default=[], help="数据目录或偏好 plist，可重复")
    storage.add_argument("--stateless", action="store_true", help="仅用于已确认无持久化用户数据的应用")
    parser.add_argument("build", nargs=argparse.REMAINDER, help="-- 之后的项目 Debug 构建命令")
    args = parser.parse_args()
    if Path(args.app).name != args.app or not args.app.endswith(".app"):
        parser.error("--app 必须是 .app 文件名")
    if not args.bundle_id or not all(part and part.isascii() and part.replace("-", "").isalnum()
                                    for part in args.bundle_id.split(".")):
        parser.error("--bundle-id 包含非法字符")
    if not args.team_id.isascii() or not args.team_id.isalnum():
        parser.error("--team-id 必须为字母数字")
    if len(args.build) < 2 or args.build[0] != "--":
        parser.error("必须用 -- 引出构建命令")
    args.build = args.build[1:]
    try:
        build_and_install(args)
    except subprocess.CalledProcessError as error:
        print(f"macOS Debug 命令失败（退出码 {error.returncode}）：{Path(error.cmd[0]).name}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    except (OSError, subprocess.SubprocessError, sqlite3.Error, RuntimeError, ValueError, KeyError,
            plistlib.InvalidFileException) as error:
        print(f"macOS Debug 更新失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
