# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "httpx>=0.27",
#     "selectolax>=0.3",
#     "markdownify>=0.13",
# ]
# ///
"""
DolphinDB 官方中文文档全量爬取脚本。

数据源：
- 主站 sitemap.xml：https://docs.dolphindb.cn/zh/sitemap.xml （2700+ URL）
- pydoc 子站：BFS 抓 https://docs.dolphindb.cn/zh/pydoc/ 下页面（sitemap 未含）

用法：
    uv run scripts/scrape_docs.py --all                  # 全量爬
    uv run scripts/scrape_docs.py --limit 10             # 抽样 10 页
    uv run scripts/scrape_docs.py --section funcs        # 只爬 funcs 章节
    uv run scripts/scrape_docs.py --rebuild              # 忽略 manifest 强制重爬

输出：
    references/official/{section}/{path}.md      每页一个 markdown，头部含 frontmatter
    references/url-manifest.json                 {url → {local_path, fetched_at, sha1}}
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse
from xml.etree import ElementTree as ET

import httpx
from markdownify import markdownify
from selectolax.parser import HTMLParser

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "references"
OFFICIAL = REFS / "official"
MANIFEST = REFS / "url-manifest.json"

SITEMAP_URL = "https://docs.dolphindb.cn/zh/sitemap.xml"
PYDOC_SEEDS = [
    "https://docs.dolphindb.cn/zh/pydoc/py.html",
    "https://docs.dolphindb.cn/zh/pydoc/basic_oper.html",
    "https://docs.dolphindb.cn/zh/pydoc/adv_oper.html",
    "https://docs.dolphindb.cn/zh/pydoc/py_vamos.html",
    "https://docs.dolphindb.cn/zh/pydoc/py_api_inst_offline.html",
    "https://docs.dolphindb.cn/zh/pydoc/release_notes/rn_py.html",
]
PYDOC_PREFIX = "https://docs.dolphindb.cn/zh/pydoc/"
DOMAIN_PREFIX = "https://docs.dolphindb.cn/zh/"
USER_AGENT = "Mozilla/5.0 (dwy-dolphindb scrape_docs.py)"
RATE_DELAY = 1.0  # 1 req/s


@dataclass
class Page:
    url: str
    section: str
    local_path: Path  # relative to REFS


def url_to_page(url: str) -> Page:
    """https://docs.dolphindb.cn/zh/funcs/aggregate/avg.html → Page(section='funcs', local_path='official/funcs/aggregate/avg.md')"""
    path = urlparse(url).path  # /zh/funcs/aggregate/avg.html
    rel = path.removeprefix("/zh/").removesuffix(".html")
    parts = rel.split("/")
    section = parts[0] if len(parts) > 1 else "_root"
    local = OFFICIAL.joinpath(*parts).with_suffix(".md").relative_to(REFS)
    return Page(url=url, section=section, local_path=local)


def load_manifest() -> dict[str, dict]:
    if MANIFEST.exists():
        return json.loads(MANIFEST.read_text("utf-8"))
    return {}


def save_manifest(manifest: dict[str, dict]) -> None:
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


async def fetch_sitemap_urls(client: httpx.AsyncClient) -> list[str]:
    r = await client.get(SITEMAP_URL)
    r.raise_for_status()
    root = ET.fromstring(r.text)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return [loc.text.strip() for loc in root.iterfind(".//sm:loc", ns) if loc.text]


def extract_pydoc_links(html: str, base_url: str) -> list[str]:
    """从 pydoc 页面 HTML 提取域内 .html 链接（同目录或子目录）"""
    parser = HTMLParser(html)
    urls = set()
    for a in parser.css("a[href]"):
        href = a.attributes.get("href", "").split("#")[0]
        if not href or not href.endswith(".html"):
            continue
        absolute = urljoin(base_url, href)
        if absolute.startswith(PYDOC_PREFIX):
            urls.add(absolute)
    return sorted(urls)


def extract_content_md(html: str) -> tuple[str, str]:
    """从 DITA-OT 页面 HTML 提取正文 article → markdown。返回 (title, markdown)"""
    parser = HTMLParser(html)
    title_node = parser.css_first("title")
    title = title_node.text(strip=True) if title_node else ""
    title = re.sub(r"\s*-\s*DolphinDB.*$", "", title).strip()

    article = parser.css_first("main[role=main] article") or parser.css_first("main article")
    if not article:
        # pydoc 页面可能没有 main role；退到最大 article
        articles = parser.css("article")
        article = max(articles, key=lambda n: len(n.html or ""), default=None)
    if not article:
        return title, ""

    md = markdownify(
        article.html,
        heading_style="ATX",
        code_language="dolphindb",  # 默认代码块语言，无法识别的统一标 dolphindb
        bullets="-",
        strip=["script", "style"],
    )
    # 压缩多余空行
    md = re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"
    return title, md


def write_page(page: Page, html: str, manifest: dict[str, dict]) -> bool:
    """写入页面 markdown + 更新 manifest。返回是否实际写入（False 表示 sha1 未变跳过）"""
    sha1 = hashlib.sha1(html.encode("utf-8")).hexdigest()
    existing = manifest.get(page.url)
    if existing and existing.get("sha1") == sha1 and (REFS / page.local_path).exists():
        return False

    title, md = extract_content_md(html)
    if not md:
        print(f"  ⚠️  无正文：{page.url}", file=sys.stderr)
        return False

    fm = (
        "---\n"
        f"source_url: {page.url}\n"
        f"fetched_at: {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n"
        f"category: {page.section}\n"
        f"title: {title}\n"
        f"sha1: {sha1}\n"
        "---\n\n"
    )
    out = REFS / page.local_path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(fm + md, encoding="utf-8")

    manifest[page.url] = {
        "local_path": str(page.local_path),
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha1": sha1,
    }
    return True


async def fetch_html(client: httpx.AsyncClient, url: str) -> str:
    r = await client.get(url, follow_redirects=True)
    r.raise_for_status()
    return r.text


async def scrape_pydoc(client: httpx.AsyncClient) -> list[str]:
    """BFS 抓 pydoc 子站所有 URL（不下载，只返回 URL 列表）"""
    seen: set[str] = set()
    queue: list[str] = list(PYDOC_SEEDS)
    discovered_html: dict[str, str] = {}

    while queue:
        url = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        try:
            html = await fetch_html(client, url)
        except httpx.HTTPError as e:
            print(f"  ⚠️  抓 pydoc 失败 {url}: {e}", file=sys.stderr)
            continue
        discovered_html[url] = html
        await asyncio.sleep(RATE_DELAY)
        for link in extract_pydoc_links(html, url):
            if link not in seen:
                queue.append(link)
    # 缓存到全局，主循环复用
    _PYDOC_CACHE.update(discovered_html)
    return sorted(seen)


_PYDOC_CACHE: dict[str, str] = {}


async def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="爬全量")
    ap.add_argument("--limit", type=int, help="只抓前 N 个 URL（抽样用）")
    ap.add_argument("--section", help="只抓指定章节（about/funcs/pydoc/...）")
    ap.add_argument("--rebuild", action="store_true", help="忽略 manifest 强制重爬")
    args = ap.parse_args()

    if not (args.all or args.limit or args.section):
        ap.print_help()
        return 1

    OFFICIAL.mkdir(parents=True, exist_ok=True)
    manifest = {} if args.rebuild else load_manifest()
    headers = {"User-Agent": USER_AGENT}

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        print("→ 读 sitemap.xml ...", file=sys.stderr)
        sitemap_urls = await fetch_sitemap_urls(client)
        print(f"  sitemap 含 {len(sitemap_urls)} 个 URL", file=sys.stderr)

        print("→ BFS 抓 pydoc 子站 URL（同时下载 HTML 缓存）...", file=sys.stderr)
        pydoc_urls = await scrape_pydoc(client)
        print(f"  pydoc 含 {len(pydoc_urls)} 个 URL", file=sys.stderr)

        all_urls = sitemap_urls + pydoc_urls

        if args.section:
            all_urls = [u for u in all_urls if f"/zh/{args.section}/" in u or u.endswith(f"/{args.section}.html")]
            print(f"  过滤 section={args.section} 后剩 {len(all_urls)} 个 URL", file=sys.stderr)

        if args.limit:
            # 抽样：每个 section 取几个
            seen_sections: dict[str, int] = {}
            sampled: list[str] = []
            for u in all_urls:
                page = url_to_page(u)
                if seen_sections.get(page.section, 0) >= max(1, args.limit // 8):
                    continue
                sampled.append(u)
                seen_sections[page.section] = seen_sections.get(page.section, 0) + 1
                if len(sampled) >= args.limit:
                    break
            all_urls = sampled
            print(f"  抽样后 {len(all_urls)} 个 URL", file=sys.stderr)

        print(f"→ 开始下载（{RATE_DELAY}s/req，预估 {len(all_urls) * RATE_DELAY / 60:.1f} 分钟）", file=sys.stderr)
        start = time.time()
        wrote = 0
        skipped = 0
        failed = 0
        for i, url in enumerate(all_urls, 1):
            page = url_to_page(url)
            try:
                html = _PYDOC_CACHE.get(url) or await fetch_html(client, url)
                if url not in _PYDOC_CACHE:
                    await asyncio.sleep(RATE_DELAY)
                if write_page(page, html, manifest):
                    wrote += 1
                else:
                    skipped += 1
            except httpx.HTTPError as e:
                failed += 1
                print(f"  ❌ {url}: {e}", file=sys.stderr)

            if i % 50 == 0 or i == len(all_urls):
                save_manifest(manifest)
                elapsed = time.time() - start
                print(
                    f"  [{i}/{len(all_urls)}] wrote={wrote} skip={skipped} fail={failed} "
                    f"elapsed={elapsed:.0f}s",
                    file=sys.stderr,
                )

        save_manifest(manifest)
        print(f"\n✅ 完成：写入 {wrote}，跳过 {skipped}，失败 {failed}", file=sys.stderr)
        return 0 if failed == 0 else 2


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
