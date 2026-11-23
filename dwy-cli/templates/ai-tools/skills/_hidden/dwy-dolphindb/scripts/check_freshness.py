# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
列出 references/url-manifest.json 中 fetched_at 距今超过阈值天数的页面。

用法：
    uv run scripts/check_freshness.py             # 默认阈值 90 天
    uv run scripts/check_freshness.py --days 30   # 指定阈值
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "references" / "url-manifest.json"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=90, help="过期阈值天数，默认 90")
    args = ap.parse_args()

    if not MANIFEST.exists():
        print(f"❌ 未找到 {MANIFEST}", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text("utf-8"))
    now = datetime.now(timezone.utc)
    stale: list[tuple[int, str]] = []
    for url, info in manifest.items():
        ts = datetime.strptime(info["fetched_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age = (now - ts).days
        if age >= args.days:
            stale.append((age, url))

    if not stale:
        print(f"✅ 全部 {len(manifest)} 个页面 fetched_at < {args.days} 天，无需刷新")
        return 0

    stale.sort(reverse=True)
    print(f"⚠️  {len(stale)} 个页面 fetched_at ≥ {args.days} 天：\n")
    for age, url in stale:
        print(f"  [{age:>4} 天] {url}")
    print(f"\n刷新建议：")
    print(f"  uv run scripts/refresh_docs.py --all                  # 全量增量更新")
    print(f"  uv run scripts/refresh_docs.py --section funcs        # 按章节")
    return 0


if __name__ == "__main__":
    sys.exit(main())
