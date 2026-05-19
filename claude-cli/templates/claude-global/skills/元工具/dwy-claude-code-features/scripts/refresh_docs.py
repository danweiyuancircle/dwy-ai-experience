#!/usr/bin/env python3
"""
dwy-claude-code-features 文档刷新工具。

功能：
  1. 读 references/url-manifest.json，列出所有已缓存文档与 source_url
  2. 检查每个 references/*.md 的 fetched_at 与今天的差值，给出"建议刷新"标记
  3. （可选）打印一份指导 Claude / 用户去 WebFetch 的命令清单

不直接调 WebFetch（脚本无 LLM 能力）。实际刷新通过：
  - 在 Claude Code 会话里说"刷新 dwy-claude-code-features 文档"，让 Claude 用 WebFetch
  - 或手动 curl 后用 LLM 摘要写回对应 references/*.md

这样设计的原因：
  - WebFetch 在 Claude Code 内置可用且能 LLM 后处理（生成结构化 markdown），脚本里无法复刻
  - 脚本只负责"判断要不要刷"和"列出要刷什么"，省得 Claude 主动去判断每个文件状态

用法：
  python3 refresh_docs.py                    # 列出所有文档状态
  python3 refresh_docs.py --check-only       # 仅返回需要刷新的数量（脚本/CI 用）
  python3 refresh_docs.py --only A           # 仅看 A 类（slash-commands）
  python3 refresh_docs.py --warn-days 90     # 自定义"过期"阈值
  python3 refresh_docs.py --update-date 2026-05-19 <ref-file>   # 手动更新某文件的 fetched_at

退出码：
  0 = 所有文档新鲜
  1 = 有文档需要刷新
  2 = 参数 / 文件错误
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
MANIFEST_PATH = SKILL_DIR / "references" / "url-manifest.json"

DEFAULT_WARN_DAYS = 90
DEFAULT_FORCE_DAYS = 180


def fail(msg: str) -> "None":
    print(f"refresh_docs.py: {msg}", file=sys.stderr)
    sys.exit(2)


def load_manifest() -> dict:
    if not MANIFEST_PATH.exists():
        fail(f"manifest 不存在: {MANIFEST_PATH}")
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def parse_fetched_at(text: str) -> "date | None":
    """从 markdown frontmatter 里抓 fetched_at 字段。返回 date 或 None。"""
    m = re.search(r"^fetched_at:\s*['\"]?(\d{4}-\d{2}-\d{2})['\"]?", text, re.MULTILINE)
    if not m:
        return None
    try:
        return datetime.strptime(m.group(1), "%Y-%m-%d").date()
    except ValueError:
        return None


def age_days(d: date) -> int:
    return (date.today() - d).days


def status_label(days: int, warn: int, force: int) -> str:
    if days >= force:
        return "expired"
    if days >= warn:
        return "stale"
    return "fresh"


def cmd_status(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    cats = manifest["categories"]
    if args.only:
        if args.only not in cats:
            fail(f"未知类别: {args.only}（可选: {list(cats.keys())}）")
        cats = {args.only: cats[args.only]}

    rows = []
    any_stale = False
    for key, cat in cats.items():
        ref_file = SKILL_DIR / cat["reference_file"]
        if not ref_file.exists():
            rows.append((key, cat["reference_file"], "missing", "-", cat["primary"]))
            any_stale = True
            continue
        text = ref_file.read_text(encoding="utf-8")
        fetched = parse_fetched_at(text)
        if fetched is None:
            rows.append((key, cat["reference_file"], "no-date", "-", cat["primary"]))
            any_stale = True
            continue
        days = age_days(fetched)
        st = status_label(days, args.warn_days, args.force_days)
        if st != "fresh":
            any_stale = True
        rows.append((key, cat["reference_file"], st, f"{days}d ({fetched})", cat["primary"]))

    if args.check_only:
        stale_count = sum(1 for r in rows if r[2] != "fresh")
        print(stale_count)
        return 0 if stale_count == 0 else 1

    print(f"{'类别':<6} {'状态':<10} {'年龄':<22} {'文件':<50} 主源 URL")
    print("-" * 120)
    for key, ref, st, age, url in rows:
        icon = {"fresh": "✓", "stale": "⚠", "expired": "✗", "missing": "✗", "no-date": "?"}[st]
        print(f"{key:<6} {icon} {st:<6} {age:<22} {ref:<50} {url}")
    print("-" * 120)
    print(f"warn ≥ {args.warn_days} 天，force ≥ {args.force_days} 天")

    stale_keys = [r[0] for r in rows if r[2] in {"stale", "expired", "no-date", "missing"}]
    if stale_keys:
        print("\n建议刷新：")
        for key in stale_keys:
            cat = manifest["categories"][key]
            print(f"  - {key}: WebFetch {cat['primary']} → 更新 {cat['reference_file']}")
            for sec in cat.get("secondary", []):
                print(f"      （次源 {sec}）")
        print("\n在 Claude Code 会话里说：『刷新 dwy-claude-code-features 文档 (类别 X)』即可")
    else:
        print("\n所有文档新鲜")

    return 1 if any_stale else 0


def cmd_update_date(args: argparse.Namespace) -> int:
    target = Path(args.update_date_file).resolve()
    if not target.exists():
        fail(f"文件不存在: {target}")
    if not args.update_date or not re.match(r"^\d{4}-\d{2}-\d{2}$", args.update_date):
        fail(f"日期格式应为 YYYY-MM-DD: {args.update_date}")
    text = target.read_text(encoding="utf-8")
    new_text, n = re.subn(
        r"^(fetched_at:\s*['\"]?)\d{4}-\d{2}-\d{2}(['\"]?\s*)$",
        rf"\g<1>{args.update_date}\g<2>",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if n == 0:
        fail(f"未在 {target} 找到 fetched_at 字段")
    target.write_text(new_text, encoding="utf-8")
    print(f"已更新 {target} fetched_at = {args.update_date}")
    return 0


def main(argv: "list[str]") -> int:
    p = argparse.ArgumentParser(description="检查 / 提示刷新 references/ 缓存文档")
    p.add_argument("--only", help="仅检查某类别（A/B/C/D/E）")
    p.add_argument("--check-only", action="store_true", help="仅打印 stale 数量")
    p.add_argument("--warn-days", type=int, default=DEFAULT_WARN_DAYS)
    p.add_argument("--force-days", type=int, default=DEFAULT_FORCE_DAYS)
    p.add_argument("--update-date", help="手动更新某文件的 fetched_at（配 --update-date-file）")
    p.add_argument("--update-date-file", help="--update-date 的目标文件")
    args = p.parse_args(argv)

    if args.update_date and args.update_date_file:
        return cmd_update_date(args)
    if args.update_date or args.update_date_file:
        fail("--update-date 和 --update-date-file 必须同时给出")

    return cmd_status(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
