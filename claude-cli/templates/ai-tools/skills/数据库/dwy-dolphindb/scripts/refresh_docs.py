# /// script
# requires-python = ">=3.10"
# dependencies = ["httpx>=0.27", "selectolax>=0.3", "markdownify>=0.13"]
# ///
"""
增量更新 DolphinDB 官方文档：调 scrape_docs.py 的逻辑，默认按 sha1 跳过未变页面。

用法：
    uv run scripts/refresh_docs.py --all                  # 全量增量
    uv run scripts/refresh_docs.py --section funcs        # 仅 funcs 章节
    uv run scripts/refresh_docs.py --section pydoc        # 仅 Python SDK
    uv run scripts/refresh_docs.py --rebuild              # 忽略 manifest 强制重爬

注：直接 exec scripts/scrape_docs.py，参数透传。本脚本只为语义上区分"首次爬取"和"周期刷新"。
"""
from __future__ import annotations

import sys
from pathlib import Path

SCRAPE = Path(__file__).resolve().parent / "scrape_docs.py"


def main() -> int:
    # 透传所有参数给 scrape_docs.py，使用 runpy 而非 subprocess 避免依赖解析开销
    import runpy

    sys.argv = [str(SCRAPE), *sys.argv[1:]]
    if not any(a in sys.argv for a in ("--all", "--section", "--limit")):
        sys.argv.append("--all")
    runpy.run_path(str(SCRAPE), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
