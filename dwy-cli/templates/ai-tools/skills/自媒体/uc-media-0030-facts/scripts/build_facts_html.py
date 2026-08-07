#!/usr/bin/env python3
"""Build a facts-only HTML viewer from 事实-*.md + sources.json.

- Renders only factual content (TOC + body + figures + references).
- Inline [[cite:S1]] / [[cite:S1,S2]] become hover markers showing
  site, authority, and URL from sources.json.
- Sections titled like 成片裁切备忘 are collapsed by default (author memo).

Usage:
  python3 build_facts_html.py \\
    --md path/to/事实-xxx.md \\
    --sources path/to/sources.json \\
    --out path/to/index.html
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


CITE_RE = re.compile(r"\[\[cite:([A-Za-z0-9_,\s]+)\]\]")
HEADING_RE = re.compile(r"^(#{1,4})\s+(.+)$", re.M)
IMG_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CODE_FENCE_RE = re.compile(r"```(\w*)\n(.*?)```", re.S)


def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff]+", "-", text.strip()).lower().strip("-")
    return re.sub(r"-+", "-", text)[:80] or "section"


def load_sources(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("sources", data if isinstance(data, list) else [])
    out = {}
    for s in items:
        sid = s["id"]
        if "site" not in s or not s["site"]:
            host = urlparse(s.get("url", "")).hostname or ""
            s = {**s, "site": host}
        if "authority_label_zh" not in s:
            s = {
                **s,
                "authority_label_zh": AUTHORITY_ZH.get(
                    s.get("authority", ""), s.get("authority", "未分级")
                ),
            }
        out[sid] = s
    return out


AUTHORITY_ZH = {
    "primary_official": "官方一手（一级）",
    "primary_academic": "学术论文（一级）",
    "secondary_edu": "教材/高校（二级）",
    "secondary_tech": "技术解读（二级·需交叉验证）",
    "media": "媒体（仅背景）",
}


def cite_html(ids: list[str], sources: dict[str, dict]) -> str:
    parts = []
    for sid in ids:
        s = sources.get(sid)
        if not s:
            parts.append(
                f'<sup class="cite missing" title="未知来源 {html.escape(sid)}">{html.escape(sid)}</sup>'
            )
            continue
        title = html.escape(s.get("title", sid))
        site = html.escape(s.get("site", ""))
        auth = html.escape(s.get("authority_label_zh", s.get("authority", "")))
        url = html.escape(s.get("url", "#"))
        tip = (
            f'<span class="cite-tip">'
            f"<strong>{title}</strong><br>"
            f"网站：{site}<br>"
            f"权威性：{auth}<br>"
            f'链接：<a href="{url}" target="_blank" rel="noopener">{url}</a>'
            f"</span>"
        )
        parts.append(
            f'<sup class="cite" tabindex="0" data-cite="{html.escape(sid)}">'
            f'<a href="#ref-{html.escape(sid)}">{html.escape(sid)}</a>{tip}</sup>'
        )
    return "".join(parts)


def replace_cites(text: str, sources: dict[str, dict]) -> str:
    def repl(m: re.Match) -> str:
        ids = [x.strip() for x in m.group(1).split(",") if x.strip()]
        return cite_html(ids, sources)

    return CITE_RE.sub(repl, text)


def inline_format(text: str, sources: dict[str, dict]) -> str:
    text = replace_cites(text, sources)
    # images first
    text = IMG_RE.sub(
        lambda m: (
            f'<figure class="fig"><img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}" loading="lazy"/>'
            f'<figcaption>{html.escape(m.group(1))}</figcaption></figure>'
        ),
        text,
    )
    # links
    text = LINK_RE.sub(
        lambda m: f'<a href="{html.escape(m.group(2))}" target="_blank" rel="noopener">{html.escape(m.group(1))}</a>',
        text,
    )
    # bold / italic / code
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def is_memo_heading(title: str) -> bool:
    t = title.strip()
    return any(k in t for k in ("成片裁切", "作者备忘", "口播", "给 0040", "给0040"))


def md_to_html(md: str, sources: dict[str, dict]) -> tuple[str, list[dict]]:
    # strip YAML-like status lines we don't need? keep body
    # remove leading blockquote meta if purely pipeline — keep for context lightly
    lines = md.splitlines()
    toc: list[dict] = []
    body: list[str] = []
    i = 0
    in_memo = False
    memo_buf: list[str] = []

    def flush_para(buf: list[str], sink: list[str]):
        if not buf:
            return
        para = "\n".join(buf).strip()
        buf.clear()
        if not para:
            return
        if para.startswith("|") and "\n|" in para + "\n":
            sink.append(table_html(para, sources))
        elif para.startswith(">"):
            quote = "\n".join(
                re.sub(r"^>\s?", "", ln) for ln in para.splitlines()
            )
            sink.append(f"<blockquote>{inline_format(quote, sources)}</blockquote>")
        else:
            # single newlines -> space for paragraphs
            p = inline_format(para.replace("\n", " "), sources)
            sink.append(f"<p>{p}</p>")

    para_buf: list[str] = []
    n = len(lines)
    while i < n:
        line = lines[i]
        # code fence
        if line.strip().startswith("```"):
            flush_para(para_buf, memo_buf if in_memo else body)
            lang = line.strip()[3:].strip()
            i += 1
            code_lines = []
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            if i < n:
                i += 1
            code = html.escape("\n".join(code_lines))
            block = f'<pre class="code"><code class="language-{html.escape(lang)}">{code}</code></pre>'
            (memo_buf if in_memo else body).append(block)
            continue

        hm = re.match(r"^(#{1,4})\s+(.+)$", line)
        if hm:
            flush_para(para_buf, memo_buf if in_memo else body)
            level = len(hm.group(1))
            title = hm.group(2).strip()
            # close previous memo
            if in_memo and level <= 2:
                body.append(wrap_memo(memo_buf))
                memo_buf = []
                in_memo = False
            if is_memo_heading(title):
                in_memo = True
                sid = slugify(title)
                memo_buf.append(f'<h{level} id="{sid}">{inline_format(title, sources)}</h{level}>')
                toc.append({"level": level, "id": sid, "title": re.sub(r"<[^>]+>", "", title), "memo": True})
                i += 1
                continue
            sid = slugify(title)
            title_html = inline_format(title, sources)
            # strip cites from toc text
            toc_title = CITE_RE.sub("", title)
            toc_title = re.sub(r"[#*`]", "", toc_title).strip()
            toc.append({"level": level, "id": sid, "title": toc_title, "memo": False})
            sink = memo_buf if in_memo else body
            sink.append(f'<h{level} id="{sid}">{title_html}</h{level}>')
            i += 1
            continue

        if line.strip() == "---":
            flush_para(para_buf, memo_buf if in_memo else body)
            (memo_buf if in_memo else body).append("<hr/>")
            i += 1
            continue

        if line.strip().startswith("- ") or line.strip().startswith("* "):
            flush_para(para_buf, memo_buf if in_memo else body)
            items = []
            while i < n and (lines[i].strip().startswith("- ") or lines[i].strip().startswith("* ")):
                items.append(lines[i].strip()[2:])
                i += 1
            lis = "".join(f"<li>{inline_format(it, sources)}</li>" for it in items)
            (memo_buf if in_memo else body).append(f"<ul>{lis}</ul>")
            continue

        if not line.strip():
            flush_para(para_buf, memo_buf if in_memo else body)
            i += 1
            continue

        para_buf.append(line)
        i += 1

    flush_para(para_buf, memo_buf if in_memo else body)
    if in_memo and memo_buf:
        body.append(wrap_memo(memo_buf))

    return "\n".join(body), toc


def wrap_memo(parts: list[str]) -> str:
    inner = "\n".join(parts)
    return (
        '<details class="memo"><summary>作者备忘（默认折叠 · 非正文事实主轴）</summary>'
        f'<div class="memo-body">{inner}</div></details>'
    )


def table_html(md_table: str, sources: dict[str, dict]) -> str:
    rows = [r.strip() for r in md_table.strip().splitlines() if r.strip()]
    if len(rows) < 2:
        return f"<p>{inline_format(md_table, sources)}</p>"
    def cells(row: str) -> list[str]:
        row = row.strip().strip("|")
        return [c.strip() for c in row.split("|")]

    header = cells(rows[0])
    # skip separator
    body_rows = rows[2:] if re.match(r"^\|?[\s:-]+\|", rows[1]) else rows[1:]
    th = "".join(f"<th>{inline_format(h, sources)}</th>" for h in header)
    trs = []
    for r in body_rows:
        cs = cells(r)
        trs.append("<tr>" + "".join(f"<td>{inline_format(c, sources)}</td>" for c in cs) + "</tr>")
    return f'<div class="table-wrap"><table><thead><tr>{th}</tr></thead><tbody>{"".join(trs)}</tbody></table></div>'


def refs_html(sources: dict[str, dict]) -> str:
    items = []
    for sid in sorted(sources.keys(), key=lambda x: (len(x), x)):
        s = sources[sid]
        items.append(
            f'<li id="ref-{html.escape(sid)}"><strong>{html.escape(sid)}</strong> '
            f'{html.escape(s.get("title", ""))} · '
            f'<span class="meta">{html.escape(s.get("site", ""))} · '
            f'{html.escape(s.get("authority_label_zh", ""))}</span><br>'
            f'<a href="{html.escape(s.get("url", "#"))}" target="_blank" rel="noopener">'
            f'{html.escape(s.get("url", ""))}</a></li>'
        )
    return '<section class="refs"><h2 id="references">参考资料</h2><ol class="ref-list">' + "".join(items) + "</ol></section>"


def toc_html(toc: list[dict]) -> str:
    lis = []
    for t in toc:
        if t.get("memo"):
            continue
        if t["level"] > 3:
            continue
        lis.append(
            f'<li class="toc-level-{t["level"]}"><a href="#{html.escape(t["id"])}">{html.escape(t["title"])}</a></li>'
        )
    lis.append('<li class="toc-level-1"><a href="#references">参考资料</a></li>')
    return f'<nav class="sidebar"><div class="sidebar-title">目录</div><ul class="toc-nav">{"".join(lis)}</ul></nav>'


HTML_SHELL = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>{title}</title>
<style>
:root {{
  --bg: #f7f8fa; --card: #fff; --text: #1a1a1a; --muted: #64748b;
  --border: #e2e8f0; --accent: #2563eb; --accent-soft: #dbeafe;
  --tip-bg: #0f172a; --tip-text: #f8fafc; --tip-link: #93c5fd;
  --code-bg: #f1f5f9; --sidebar-w: 240px;
}}
@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0b1220; --card: #111827; --text: #e5e7eb; --muted: #94a3b8;
    --border: #1f2937; --accent: #60a5fa; --accent-soft: #1e3a5f;
    --tip-bg: #020617; --tip-text: #f1f5f9; --tip-link: #93c5fd;
    --code-bg: #0f172a;
  }}
}}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Segoe UI", "PingFang SC", "Noto Sans SC", system-ui, sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.75; }}
.layout {{ display: flex; max-width: 1100px; margin: 0 auto; min-height: 100vh; }}
.sidebar {{ width: var(--sidebar-w); position: sticky; top: 0; height: 100vh; overflow: auto;
  padding: 1.5rem 1rem; border-right: 1px solid var(--border); flex-shrink: 0; }}
.sidebar-title {{ font-size: .75rem; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); margin-bottom: .75rem; }}
.toc-nav {{ list-style: none; padding: 0; margin: 0; }}
.toc-nav a {{ display: block; padding: .35rem .5rem; color: var(--muted); text-decoration: none;
  border-radius: 6px; border-left: 2px solid transparent; font-size: .85rem; }}
.toc-nav a:hover {{ background: var(--accent-soft); color: var(--text); }}
.toc-level-1 a {{ font-weight: 600; color: var(--text); }}
.toc-level-2 a {{ padding-left: 1rem; }}
.toc-level-3 a {{ padding-left: 1.5rem; font-size: .8rem; }}
.main {{ flex: 1; padding: 2rem 2.5rem 4rem; max-width: 820px; }}
h1 {{ font-size: 1.75rem; line-height: 1.3; margin: 0 0 1rem; }}
h2 {{ font-size: 1.35rem; margin: 2rem 0 .75rem; padding-top: .5rem; border-top: 1px solid var(--border); }}
h3 {{ font-size: 1.1rem; margin: 1.5rem 0 .5rem; }}
h4 {{ font-size: 1rem; margin: 1.25rem 0 .4rem; color: var(--muted); }}
p {{ margin: .65rem 0; }}
a {{ color: var(--accent); }}
hr {{ border: 0; border-top: 1px solid var(--border); margin: 1.5rem 0; }}
ul {{ padding-left: 1.25rem; }}
code {{ background: var(--code-bg); padding: .1em .35em; border-radius: 4px; font-size: .9em; }}
pre.code {{ background: var(--code-bg); padding: 1rem; border-radius: 8px; overflow: auto; font-size: .85rem; }}
.table-wrap {{ overflow-x: auto; margin: 1rem 0; }}
table {{ border-collapse: collapse; width: 100%; font-size: .9rem; }}
th, td {{ border: 1px solid var(--border); padding: .5rem .65rem; vertical-align: top; }}
th {{ background: var(--accent-soft); text-align: left; }}
blockquote {{ margin: .75rem 0; padding: .5rem 1rem; border-left: 3px solid var(--accent); color: var(--muted); background: var(--card); }}
figure.fig {{ margin: 1.25rem 0; padding: .75rem; background: var(--card); border: 1px solid var(--border); border-radius: 10px; }}
figure.fig img {{ max-width: 100%; height: auto; display: block; margin: 0 auto; border-radius: 6px; }}
figcaption {{ font-size: .85rem; color: var(--muted); margin-top: .5rem; text-align: center; }}
sup.cite {{ position: relative; display: inline-block; margin: 0 1px; cursor: help; font-weight: 600; }}
sup.cite > a {{ color: var(--accent); text-decoration: none; font-size: .75em; padding: 0 .2em; border-radius: 3px; background: var(--accent-soft); }}
sup.cite .cite-tip {{
  display: none; position: absolute; z-index: 50; left: 50%; transform: translateX(-50%);
  bottom: calc(100% + 8px); width: min(320px, 70vw); padding: .75rem .85rem;
  background: var(--tip-bg); color: var(--tip-text); border-radius: 8px; font-size: .8rem;
  line-height: 1.45; box-shadow: 0 8px 24px rgba(0,0,0,.25); font-weight: 400; text-align: left;
}}
sup.cite .cite-tip a {{ color: var(--tip-link); word-break: break-all; }}
sup.cite:hover .cite-tip, sup.cite:focus .cite-tip, sup.cite:focus-within .cite-tip, sup.cite.open .cite-tip {{ display: block; }}
sup.cite.missing > a {{ background: #fee2e2; color: #b91c1c; }}
.memo {{ margin: 2rem 0; border: 1px dashed var(--border); border-radius: 8px; padding: .5rem 1rem; color: var(--muted); }}
.memo summary {{ cursor: pointer; font-weight: 600; }}
.refs {{ margin-top: 3rem; }}
.ref-list {{ padding-left: 1.25rem; }}
.ref-list li {{ margin: .75rem 0; }}
.ref-list .meta {{ color: var(--muted); font-size: .9em; }}
.page-note {{ font-size: .85rem; color: var(--muted); margin-bottom: 1.5rem; }}
@media (max-width: 900px) {{
  .sidebar {{ display: none; }}
  .main {{ padding: 1.25rem; }}
}}
</style>
</head>
<body>
<div class="layout">
{toc}
<main class="main">
<p class="page-note">事实资料库 · 仅展示可溯源技术内容 · 悬停引用标记可查看来源网站 / 权威性 / 链接</p>
{body}
{refs}
</main>
</div>
<script>
document.querySelectorAll('sup.cite').forEach(function(el) {{
  el.addEventListener('click', function(e) {{
    if (window.matchMedia('(hover: none)').matches) {{
      e.preventDefault();
      document.querySelectorAll('sup.cite.open').forEach(function(x) {{ if (x !== el) x.classList.remove('open'); }});
      el.classList.toggle('open');
    }}
  }});
}});
document.addEventListener('click', function(e) {{
  if (!e.target.closest('sup.cite')) document.querySelectorAll('sup.cite.open').forEach(function(x) {{ x.classList.remove('open'); }});
}});
</script>
</body>
</html>
"""


def extract_title(md: str) -> str:
    m = re.search(r"^#\s+(.+)$", md, re.M)
    return m.group(1).strip() if m else "事实资料库"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, type=Path)
    ap.add_argument("--sources", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    md = args.md.read_text(encoding="utf-8")
    sources = load_sources(args.sources)
    body, toc = md_to_html(md, sources)
    title = extract_title(md)
    # strip pipeline meta blockquotes at very top from title display — body already has them
    page = HTML_SHELL.format(
        title=html.escape(CITE_RE.sub("", title)),
        toc=toc_html(toc),
        body=body,
        refs=refs_html(sources),
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(page, encoding="utf-8")
    print(f"wrote {args.out} ({len(page)} bytes, {len(sources)} sources)")


if __name__ == "__main__":
    main()
