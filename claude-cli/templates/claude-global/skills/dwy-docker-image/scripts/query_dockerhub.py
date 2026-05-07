#!/usr/bin/env python3
"""
查询 DockerHub 上某镜像的版本列表，自动剔除 latest / rc / beta / alpha / preview / nightly
等不稳定标签和浮动 tag，并推荐使用「最新稳定 minor 的上一个 minor」（N-1）。

用法：
    python3 query_dockerhub.py <image> [--namespace library] [--top 20]

示例：
    python3 query_dockerhub.py nginx
    python3 query_dockerhub.py postgres
    python3 query_dockerhub.py mycompany/api --namespace mycompany
"""

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime
from urllib.error import HTTPError, URLError

DOCKERHUB_API = "https://hub.docker.com/v2/repositories/{namespace}/{image}/tags"

UNSTABLE_KEYWORDS = (
    "rc", "beta", "alpha", "preview", "nightly", "dev", "snapshot",
    "experimental", "edge", "canary", "next", "unstable",
)

FLOATING_TAGS = {
    "latest", "stable", "mainline", "current", "release",
    "lts", "rolling", "main", "master", "head",
}

SEMVER_RE = re.compile(r"^(\d+)(?:\.(\d+))?(?:\.(\d+))?(?:[.\-+](.+))?$")


def fetch_tags(namespace: str, image: str, page_size: int = 100, max_pages: int = 5):
    """从 DockerHub API 拉取 tags，返回原始列表。"""
    url = DOCKERHUB_API.format(namespace=namespace, image=image) + f"?page_size={page_size}"
    tags = []
    page = 1
    while url and page <= max_pages:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "dwy-docker-image-skill/1.0"})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            if e.code == 404:
                print(f"错误：DockerHub 上找不到 {namespace}/{image}", file=sys.stderr)
                sys.exit(2)
            raise
        except URLError as e:
            print(f"错误：访问 DockerHub 失败：{e}", file=sys.stderr)
            sys.exit(3)

        tags.extend(data.get("results", []))
        url = data.get("next")
        page += 1
    return tags


def parse_version(tag: str):
    """
    解析 tag 中的版本号（major, minor, patch, suffix）。

    返回 None 表示这个 tag 不能解析为版本号（比如 'alpine'、'bookworm'）。
    """
    cleaned = tag.lstrip("v")
    m = SEMVER_RE.match(cleaned)
    if not m:
        return None
    major = int(m.group(1))
    minor = int(m.group(2)) if m.group(2) else 0
    patch = int(m.group(3)) if m.group(3) else 0
    suffix = m.group(4) or ""
    return (major, minor, patch, suffix)


def is_stable(tag_name: str) -> bool:
    """判断 tag 是否为稳定版本。"""
    name = tag_name.lower()
    if name in FLOATING_TAGS:
        return False
    for kw in UNSTABLE_KEYWORDS:
        if re.search(rf"[\-._]{kw}\b", name) or name.endswith(kw) or name.startswith(kw + "-"):
            return False
    return True


def has_only_version(tag_name: str) -> bool:
    """
    tag 是否仅包含版本号且至少包含 major.minor 两段。

    单段数字 tag（如 '1'、'17'）虽然看起来固定，实际是浮动 tag（指向该 major
    系列最新 patch），不能用作固定版本，必须排除。
    """
    return bool(re.match(r"^v?\d+\.\d+(\.\d+)?$", tag_name))


def main():
    parser = argparse.ArgumentParser(description="查询 DockerHub 镜像版本，推荐 N-1 minor")
    parser.add_argument("image", help="镜像名，如 nginx、postgres")
    parser.add_argument("--namespace", default="library", help="DockerHub 命名空间，默认 library")
    parser.add_argument("--top", type=int, default=20, help="显示最近 N 个 tag，默认 20")
    args = parser.parse_args()

    print(f"查询 DockerHub: {args.namespace}/{args.image} ...\n", file=sys.stderr)
    tags = fetch_tags(args.namespace, args.image)
    if not tags:
        print(f"未找到 {args.namespace}/{args.image} 的任何 tag", file=sys.stderr)
        sys.exit(1)

    # 过滤：稳定 + 纯版本号
    pure_version_tags = []
    for t in tags:
        name = t.get("name", "")
        if not is_stable(name):
            continue
        if not has_only_version(name):
            continue
        ver = parse_version(name)
        if ver is None:
            continue
        pure_version_tags.append({
            "name": name,
            "version": ver,
            "last_updated": t.get("last_updated", ""),
        })

    if not pure_version_tags:
        print("未找到符合规范的稳定版本 tag。请手动确认。", file=sys.stderr)
        sys.exit(1)

    # 按 (major, minor) 分组，每组取最大 patch
    minor_groups = defaultdict(list)
    for item in pure_version_tags:
        major, minor, _patch, _suffix = item["version"]
        minor_groups[(major, minor)].append(item)

    # 每组按版本号排序，取最大 patch 作为该 minor 的代表
    minor_latest = {}
    for key, items in minor_groups.items():
        items.sort(key=lambda x: x["version"], reverse=True)
        minor_latest[key] = items[0]

    # 按 (major, minor) 倒序排列
    sorted_minors = sorted(minor_latest.keys(), reverse=True)

    if not sorted_minors:
        print("无法识别任何 (major, minor) 系列", file=sys.stderr)
        sys.exit(1)

    latest_minor = sorted_minors[0]
    latest_item = minor_latest[latest_minor]

    # N-1：跳过仅有少量 patch 的快速被弃用版本，找真正的"上一个 minor"
    n_minus_1_item = None
    if len(sorted_minors) >= 2:
        n_minus_1_minor = sorted_minors[1]
        n_minus_1_item = minor_latest[n_minus_1_minor]

    # 输出
    print("=" * 60)
    print(f"镜像: {args.namespace}/{args.image}")
    print("=" * 60)
    major, minor, patch, _ = latest_item["version"]
    print(f"最新稳定 minor: {major}.{minor}")
    print(f"  最新 patch: {latest_item['name']}  ({format_date(latest_item['last_updated'])})")
    print()

    if n_minus_1_item:
        n_major, n_minor, n_patch, _ = n_minus_1_item["version"]
        print(f"✅ 推荐 (N-1 minor): {args.image}:{n_minus_1_item['name']}")
        print(f"   {n_major}.{n_minor} 系列最新 patch，发布于 {format_date(n_minus_1_item['last_updated'])}")
    else:
        print("⚠️  仅找到一个 minor 系列，无法推荐 N-1，请手动确认是否可降级 major")
    print()

    print(f"最近 {args.top} 个稳定 tag（每个 minor 取最新 patch）:")
    n_minus_1_key = sorted_minors[1] if len(sorted_minors) >= 2 else None
    for key in sorted_minors[:args.top]:
        item = minor_latest[key]
        marker = ""
        if key == latest_minor:
            marker = "  ← 最新"
        elif key == n_minus_1_key:
            marker = "  ← 推荐 (N-1)"
        print(f"  {item['name']:20s}  {format_date(item['last_updated'])}{marker}")


def format_date(iso: str) -> str:
    if not iso:
        return "-"
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        return iso[:10]


if __name__ == "__main__":
    main()
