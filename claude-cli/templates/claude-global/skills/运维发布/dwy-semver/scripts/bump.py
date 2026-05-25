#!/usr/bin/env python3
"""SemVer 2.0.0 版本号递增计算器。

给定当前版本号 + 递增级别，输出下一个版本号，严格遵循 SemVer 归零规则
与 node-semver 的预发布递增语义。纯标准库，无外部依赖。

为什么需要这个脚本：归零（minor+1 → patch 归零）和预发布递增（rc.0 → rc.1）
是 LLM 手算高频出错点，交给确定性代码避免算错。

用法:
    bump.py 1.2.3 minor                 -> 1.3.0
    bump.py 1.2.3 major                 -> 2.0.0
    bump.py 0.9.1 minor                 -> 0.10.0
    bump.py 1.0.0 prerelease --preid rc -> 1.0.1-rc.0
    bump.py 1.0.0 preminor --preid rc   -> 1.1.0-rc.0
    bump.py 1.1.0-rc.0 prerelease       -> 1.1.0-rc.1

级别: major | minor | patch | premajor | preminor | prepatch | prerelease
"""

import argparse
import re
import sys

# 不含 build metadata 的解析；bump 时 build metadata（+xxx）按 SemVer 一律丢弃
_VERSION_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
    r"(?:-(?P<prerelease>[0-9A-Za-z.-]+))?"
    r"(?:\+(?P<build>[0-9A-Za-z.-]+))?$"
)


def parse(version: str) -> tuple[int, int, int, list]:
    """解析版本号为 (major, minor, patch, prerelease 标识符列表)。

    prerelease 中纯数字段转 int（便于递增与比较），其余保留字符串。
    无效格式直接抛 ValueError，让调用方感知，不静默兜底。
    """
    m = _VERSION_RE.match(version.strip())
    if not m:
        raise ValueError(f"非法 SemVer 版本号: {version!r}")
    pre_raw = m.group("prerelease")
    prerelease = []
    if pre_raw:
        for part in pre_raw.split("."):
            prerelease.append(int(part) if part.isdigit() else part)
    return int(m.group("major")), int(m.group("minor")), int(m.group("patch")), prerelease


def _format(major: int, minor: int, patch: int, prerelease: list) -> str:
    base = f"{major}.{minor}.{patch}"
    if prerelease:
        base += "-" + ".".join(str(p) for p in prerelease)
    return base


def _bump_prerelease(prerelease: list, preid: str | None) -> list:
    """递增已有的预发布标识符列表（node-semver 语义）。

    - 指定了 preid 且与当前不同 -> 切到新 preid，从 0 开始
    - 否则递增最后一个数字段；末位非数字则追加 0
    """
    if preid and (not prerelease or prerelease[0] != preid):
        return [preid, 0]
    bumped = list(prerelease)
    for i in range(len(bumped) - 1, -1, -1):
        if isinstance(bumped[i], int):
            bumped[i] += 1
            return bumped
    bumped.append(0)
    return bumped


def inc(version: str, release: str, preid: str | None = None) -> str:
    """按 release 级别递增版本号，返回新版本字符串。"""
    major, minor, patch, prerelease = parse(version)

    if release == "major":
        # 已是 x.0.0 的预发布（如 2.0.0-rc.1）升 major 只需转正式版
        if prerelease and minor == 0 and patch == 0:
            return _format(major, 0, 0, [])
        return _format(major + 1, 0, 0, [])

    if release == "minor":
        if prerelease and patch == 0:
            return _format(major, minor, 0, [])
        return _format(major, minor + 1, 0, [])

    if release == "patch":
        # 预发布转正式版时 patch 不再 +1（1.2.3-rc.1 -> 1.2.3）
        if prerelease:
            return _format(major, minor, patch, [])
        return _format(major, minor, patch + 1, [])

    pre_start = [preid, 0] if preid else [0]

    if release == "premajor":
        return _format(major + 1, 0, 0, pre_start)
    if release == "preminor":
        return _format(major, minor + 1, 0, pre_start)
    if release == "prepatch":
        return _format(major, minor, patch + 1, pre_start)

    if release == "prerelease":
        # 当前无预发布 -> 等价 prepatch 后加预发布
        if not prerelease:
            return _format(major, minor, patch + 1, pre_start)
        return _format(major, minor, patch, _bump_prerelease(prerelease, preid))

    raise ValueError(f"未知级别: {release!r}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="SemVer 2.0.0 版本号递增计算器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("version", help="当前版本号，如 1.2.3 或 1.2.3-rc.0")
    parser.add_argument(
        "release",
        choices=["major", "minor", "patch", "premajor", "preminor", "prepatch", "prerelease"],
        help="递增级别",
    )
    parser.add_argument("--preid", default=None, help="预发布标识符，如 alpha / beta / rc")
    args = parser.parse_args()

    try:
        print(inc(args.version, args.release, args.preid))
    except ValueError as e:
        print(f"错误: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
