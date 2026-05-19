# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""
从 references/url-manifest.json + 各 .md 文件 frontmatter 生成索引：
- references/INDEX.md：主导航，按章节列每个 reference 的 title + 1 句摘要 + 路径
- references/official/funcs/_INDEX.md：函数参考二级索引，按子目录扁平列函数

用法：uv run scripts/build_index.py
"""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
OFFICIAL = REFS / "official"
MANIFEST = REFS / "url-manifest.json"
INDEX = REFS / "INDEX.md"
FUNCS_INDEX = OFFICIAL / "funcs" / "_INDEX.md"

SECTION_TITLES = {
    "about": "关于 DolphinDB",
    "getstarted": "快速上手",
    "deploy": "部署",
    "progr": "编程语言（含 SQL）",
    "db_distr_comp": "数据库 / 分布式存储 / 引擎",
    "stream": "流数据",
    "sys_man": "系统运维",
    "error_codes": "故障排查 / 错误码",
    "funcs": "函数参考（细目见 official/funcs/_INDEX.md）",
    "api": "连接器 & API（多语言）",
    "pydoc": "Python SDK 文档",
    "plugins": "插件",
    "backtest": "回测与模拟撮合",
    "mcp": "MCP",
    "tutorials": "教程",
    "rn": "版本说明",
    "tools": "工具",
    "modules": "模块库",
    "omc": "OMC",
    "_root": "顶层零散文档",
}


def parse_frontmatter(md_path: Path) -> dict:
    """读 .md 文件头的 YAML frontmatter，返回 dict。失败返回空 dict。"""
    try:
        text = md_path.read_text("utf-8")
    except OSError:
        return {}
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^(\w+):\s*(.+)$", line)
        if m:
            fm[m.group(1)] = m.group(2).strip()
    return fm


def first_paragraph(md_path: Path) -> str:
    """提取首段非标题、非空行作为摘要，截断到 80 字符。"""
    text = md_path.read_text("utf-8")
    body = text.split("\n---\n", 1)[-1] if text.startswith("---\n") else text
    for line in body.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("![") or s.startswith("|"):
            continue
        # 去 markdown 链接语法
        s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
        s = re.sub(r"[*`]", "", s)
        return s[:80] + ("…" if len(s) > 80 else "")
    return ""


def build_main_index(manifest: dict) -> None:
    by_section: dict[str, list[tuple[str, Path, str]]] = defaultdict(list)
    for url, info in manifest.items():
        local = REFS / info["local_path"]
        if not local.exists():
            continue
        fm = parse_frontmatter(local)
        section = fm.get("category", "_root").split("/")[0]
        title = fm.get("title", local.stem)
        summary = first_paragraph(local)
        rel = local.relative_to(REFS)
        by_section[section].append((title, rel, summary))

    # 扫描 digest/ 目录（提炼后的核心点，LLM 优先读）
    digest_dir = REFS / "digest"
    digest_items: list[tuple[str, Path, str]] = []
    if digest_dir.exists():
        for md in sorted(digest_dir.glob("*.md")):
            fm = parse_frontmatter(md)
            title = fm.get("title") or md.stem
            summary = first_paragraph(md)
            digest_items.append((title, md.relative_to(REFS), summary))

    lines = [
        "# DolphinDB Skill — 文档主索引",
        "",
        "> 自动生成，请勿手改。重新生成：`uv run scripts/build_index.py`",
        "",
        "## 优先：核心点摘要（digest/，LLM 第一站）",
        "",
    ]
    for t, rel, summary in digest_items:
        line = f"- `{rel}` — **{t}**"
        if summary:
            line += f" — {summary}"
        lines.append(line)
    lines += [
        "",
        "## 审查规则（skill 自带，非官方文档）",
        "",
        "- `review-rules/lethal-violations.md` — 10 条致命违规清单",
        "- `review-rules/anti-patterns.md` — 反模式与最佳实践（类型/SQL/库表/写入/运维）",
        "- `review-rules/perf-baselines.md` — 2 核 8G 性能基线 + 配置调优",
        "- `review-rules/change-checklist.md` — 17 项变更前自检 + 5 分钟慢查询排查",
        "- `project-schema-protocol.md` — 真实环境 DDL/SQL 接入协议",
        "",
        "## 官方文档（official/，按章节，下钻用）",
        "",
    ]

    section_order = list(SECTION_TITLES.keys())
    extras = sorted(set(by_section) - set(section_order))
    for section in section_order + extras:
        items = by_section.get(section, [])
        if not items:
            continue
        items.sort(key=lambda x: str(x[1]))
        title = SECTION_TITLES.get(section, section)
        lines.append(f"### {section} — {title}（{len(items)} 篇）")
        lines.append("")
        for t, rel, summary in items:
            line = f"- `{rel}` — **{t}**"
            if summary:
                line += f" — {summary}"
            lines.append(line)
        lines.append("")

    INDEX.write_text("\n".join(lines), encoding="utf-8")
    print(f"✅ 写 {INDEX} ({sum(len(v) for v in by_section.values())} 篇)")


def build_funcs_index(manifest: dict) -> None:
    """函数参考二级索引：按子目录（funcs/aggregate/ ... funcs/temporal/ ...）扁平列函数"""
    funcs_dir = OFFICIAL / "funcs"
    if not funcs_dir.exists():
        return
    by_subdir: dict[str, list[tuple[str, Path, str]]] = defaultdict(list)
    for md in funcs_dir.rglob("*.md"):
        if md.name == "_INDEX.md":
            continue
        rel_to_funcs = md.relative_to(funcs_dir)
        # subdir 取第一段；若直挂 funcs/ 下，归到 _root
        subdir = rel_to_funcs.parts[0] if len(rel_to_funcs.parts) > 1 else "_root"
        fm = parse_frontmatter(md)
        title = fm.get("title", md.stem)
        summary = first_paragraph(md)
        rel_to_official_funcs = md.relative_to(funcs_dir)
        by_subdir[subdir].append((title, rel_to_official_funcs, summary))

    lines = [
        "# 函数参考索引（official/funcs/）",
        "",
        "> 自动生成，请勿手改。重新生成：`uv run scripts/build_index.py`",
        "> 路径相对本目录（official/funcs/）",
        "",
    ]
    subdirs = sorted(by_subdir.keys())
    for sub in subdirs:
        items = sorted(by_subdir[sub], key=lambda x: str(x[1]).lower())
        lines.append(f"## {sub}（{len(items)} 个）")
        lines.append("")
        for t, rel, summary in items:
            line = f"- `{rel}` — **{t}**"
            if summary:
                line += f" — {summary}"
            lines.append(line)
        lines.append("")

    FUNCS_INDEX.parent.mkdir(parents=True, exist_ok=True)
    FUNCS_INDEX.write_text("\n".join(lines), encoding="utf-8")
    total = sum(len(v) for v in by_subdir.values())
    print(f"✅ 写 {FUNCS_INDEX} ({total} 个函数)")


def main() -> int:
    if not MANIFEST.exists():
        print(f"❌ 未找到 {MANIFEST}，先跑 scripts/scrape_docs.py", file=sys.stderr)
        return 1
    manifest = json.loads(MANIFEST.read_text("utf-8"))
    build_main_index(manifest)
    build_funcs_index(manifest)
    return 0


if __name__ == "__main__":
    sys.exit(main())
