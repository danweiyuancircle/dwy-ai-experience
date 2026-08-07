#!/usr/bin/env python3
"""Generate a Markdown report + interactive HTML viewer.

Outputs:
  - README.md    (clean Markdown, single source of truth)
  - index.html   (self-contained viewer: CSS + JS + embedded MD content)
  - sources.json (structured source data)
"""

import json
import re
import sys
import argparse
from datetime import datetime
from pathlib import Path
from html import escape


def slugify(text):
    """Generate a URL-safe slug from heading text."""
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'`([^`]+)`', r'\1', text)
    text = re.sub(r'[^\w\u4e00-\u9fff]+', '-', text.strip()).lower().strip('-')
    text = re.sub(r'-+', '-', text)[:60]
    return text


def normalize_source(src):
    """Normalize source entries to {title, url, type, ...}.

    Supports alternate shapes like {project, urls:[...]} used by some angle
    research dumps. Missing fields must not break the HTML viewer.
    """
    if not isinstance(src, dict):
        return {'title': str(src), 'url': '#', 'type': 'community'}

    urls = src.get('urls') or []
    if not isinstance(urls, list):
        urls = [urls] if urls else []

    url = src.get('url') or (urls[0] if urls else '#') or '#'
    title = src.get('title') or src.get('project') or url or '未知'
    out = {
        'title': title,
        'url': url,
        'type': src.get('type') or ('primary' if src.get('project') else 'community'),
    }
    if src.get('note'):
        out['note'] = src['note']
    elif len(urls) > 1:
        out['note'] = '相关链接：' + ' · '.join(str(u) for u in urls[1:])
    return out


def format_project_details(projects):
    """Turn a list of project license research objects into readable Markdown."""
    lines = []
    for p in projects:
        if not isinstance(p, dict):
            lines.append(f'- {p}')
            continue
        name = p.get('project', '未知项目')
        lines += [f'### {name}', '']
        if p.get('repo_url'):
            lines.append(f'- **仓库**：[{p["repo_url"]}]({p["repo_url"]})')
        if p.get('license_name'):
            lines.append(f'- **协议**：{p["license_name"]}')
        meta = p.get('github_license_metadata') or {}
        if isinstance(meta, dict) and (meta.get('spdx_id') or meta.get('name')):
            spdx = meta.get('spdx_id', '')
            mname = meta.get('name', '')
            note = meta.get('note', '')
            meta_line = f'- **GitHub 元数据**：{mname}'
            if spdx:
                meta_line += f' (`{spdx}`)'
            if note:
                meta_line += f' — {note}'
            lines.append(meta_line)
        if 'is_osi_open_source' in p:
            lines.append(f'- **是否 OSI 开源**：{"是" if p["is_osi_open_source"] else "否"}')
        if p.get('license_file'):
            lines.append(f'- **LICENSE 文件**：[{p["license_file"]}]({p["license_file"]})')
        faq = p.get('official_faq_is_remotion_open_source')
        if isinstance(faq, dict):
            q = faq.get('question', '')
            a = faq.get('answer_verbatim_summary', '')
            lines.append(f'- **官方 FAQ**：{q} → {a}')
            if faq.get('source'):
                lines.append(f'  - 来源：[{faq["source"]}]({faq["source"]})')
        if p.get('verification_method'):
            lines.append(f'- **核实方式**：{p["verification_method"]}')
        points = p.get('license_points') or []
        if points:
            lines += ['', '**要点**：']
            for pt in points:
                lines.append(f'- {pt}')
        quotes = p.get('quotes') or []
        if quotes:
            lines += ['', '**原文摘录**：']
            for q in quotes:
                if not isinstance(q, dict):
                    lines.append(f'> {q}')
                    lines.append('')
                    continue
                text = (q.get('text') or '').replace('\n', ' ').strip()
                qurl = q.get('url') or ''
                lines.append(f'> {text}')
                if qurl:
                    lines.append('>')
                    lines.append(f'> — [{qurl}]({qurl})')
                lines.append('')
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def details_to_markdown(details):
    """Coerce angle details (str / list / dict / JSON string) into Markdown."""
    if details is None:
        return '（内容待补充）'

    if isinstance(details, str):
        s = details.strip()
        if s.startswith('[') or s.startswith('{'):
            try:
                return details_to_markdown(json.loads(s))
            except json.JSONDecodeError:
                return details
        return details

    if isinstance(details, list):
        if details and isinstance(details[0], dict) and 'project' in details[0]:
            return format_project_details(details)
        parts = []
        for item in details:
            if isinstance(item, str):
                parts.append(item)
            else:
                parts.append(json.dumps(item, ensure_ascii=False, indent=2))
        return '\n\n'.join(parts)

    if isinstance(details, dict):
        if 'project' in details:
            return format_project_details([details])
        return '```json\n' + json.dumps(details, ensure_ascii=False, indent=2) + '\n```'

    return str(details)


def generate_markdown(topic, angles_data):
    """Generate clean Markdown report (single source of truth)."""
    today = datetime.now().strftime('%Y-%m-%d')
    angles_list = '、'.join(a['angle'] for a in angles_data)

    lines = [
        f'# {topic}',
        '',
        f'> 整理时间：{today}',
        f'> 覆盖角度：{angles_list}',
        '',
        '---',
        '',
        '## 目录',
        '1. [概述](#概述)',
    ]
    for i, a in enumerate(angles_data, 2):
        anchor = slugify(a['angle'])
        lines.append(f'{i}. [{a["angle"]}](#{anchor})')
    lines.append(f'{len(angles_data) + 2}. [参考资料](#参考资料)')
    lines += ['', '---', '', '## 概述', '']

    for a in angles_data:
        lines.append(f'**{a["angle"]}**：{a.get("summary", "")}')
    lines.append('')

    for i, a in enumerate(angles_data, 1):
        lines += ['', '---', '', f'## {a["angle"]}', '']
        details = details_to_markdown(a.get('details', a.get('summary', '（内容待补充）')))
        # Remove leading H1 if present (it's the angle title)
        details = re.sub(r'^#\s+.+\s*', '', details, count=1, flags=re.MULTILINE)
        lines.append(details)
        lines.append('')
        if a.get('key_points'):
            lines.append('### 关键要点')
            lines.append('')
            for kp in a['key_points']:
                lines.append(f'- {kp}')
            lines.append('')

    # Sources (normalized so HTML citations never see missing title/url)
    all_sources = []
    for a in angles_data:
        for src in a.get('sources', []):
            all_sources.append(normalize_source(src))

    lines += ['', '---', '', '## 参考资料', '', '### 来源列表', '']
    for i, src in enumerate(all_sources, 1):
        t = src.get('type', 'community')
        title = src.get('title', src.get('url', '未知'))
        url = src.get('url', '#')
        lines.append(f'[{i}] [{title}]({url}) `[{t}]`')
    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('*本笔记由 AI 调研生成，所有事实均标注来源。建议独立验证关键信息。*')
    lines.append('')

    return '\n'.join(lines), all_sources


HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<style>
:root {{
  --bg: #fafafa;
  --card-bg: #ffffff;
  --text: #1a1a1a;
  --text-secondary: #666;
  --border: #e5e5e5;
  --accent: #2563eb;
  --accent-light: #dbeafe;
  --cite-bg: #f0f9ff;
  --cite-border: #93c5fd;
  --popup-bg: #1e293b;
  --popup-text: #f8fafc;
  --popup-link: #93c5fd;
  --code-bg: #f1f5f9;
  --table-stripe: #f8fafc;
  --sidebar-width: 240px;
}}

@media (prefers-color-scheme: dark) {{
  :root {{
    --bg: #0f172a;
    --card-bg: #1e293b;
    --text: #e2e8f0;
    --text-secondary: #94a3b8;
    --border: #334155;
    --accent: #60a5fa;
    --accent-light: #1e3a5f;
    --cite-bg: #1e3a5f;
    --cite-border: #3b82f6;
    --popup-bg: #0f172a;
    --popup-text: #f1f5f9;
    --popup-link: #60a5fa;
    --code-bg: #1e293b;
    --table-stripe: #1a2332;
  }}
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg);
  color: var(--text);
  line-height: 1.8;
}}

/* Layout: sidebar + main */
.layout {{
  display: flex;
  max-width: 1120px;
  margin: 0 auto;
}}

.sidebar {{
  width: var(--sidebar-width);
  flex-shrink: 0;
  position: sticky;
  top: 0;
  height: 100vh;
  overflow-y: auto;
  padding: 2rem 1rem 2rem 1.5rem;
  border-right: 1px solid var(--border);
}}

.main-content {{
  flex: 1;
  max-width: 800px;
  padding: 2rem 3rem;
}}

@media (max-width: 900px) {{
  .sidebar {{ display: none; }}
  .main-content {{ padding: 1.5rem; }}
}}

/* Sidebar TOC */
.sidebar-title {{
  font-size: 0.875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-secondary);
  margin-bottom: 1rem;
}}

.toc-nav {{
  list-style: none;
  padding: 0;
}}

.toc-nav li {{
  margin: 0;
}}

.toc-nav a {{
  display: block;
  padding: 0.4rem 0.5rem;
  font-size: 0.9375rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  border-left: 2px solid transparent;
  transition: all 0.15s ease;
  line-height: 1.5;
}}

.toc-nav a:hover {{
  color: var(--text);
  background: var(--accent-light);
}}

.toc-nav a.active {{
  color: var(--accent);
  border-left-color: var(--accent);
  font-weight: 500;
}}

/* TOC indentation levels */
.toc-level-1 a {{
  font-weight: 600;
  font-size: 1rem;
  padding-left: 0.5rem;
}}

.toc-level-2 a {{
  padding-left: 1.25rem;
  font-size: 0.9375rem;
}}

.toc-level-3 a {{
  padding-left: 2rem;
  font-size: 0.875rem;
  opacity: 0.85;
}}

.toc-level-4 a {{
  padding-left: 2.75rem;
  font-size: 0.8125rem;
  opacity: 0.7;
}}

.toc-nav {{
  list-style: none;
  padding: 0;
}}

.toc-nav li {{
  margin: 0;
}}

.toc-nav a {{
  display: block;
  padding: 0.3rem 0.5rem;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  text-decoration: none;
  border-radius: 4px;
  border-left: 2px solid transparent;
  transition: all 0.15s ease;
  line-height: 1.4;
}}

.toc-nav a:hover {{
  color: var(--text);
  background: var(--accent-light);
}}

.toc-nav a.active {{
  color: var(--accent);
  border-left-color: var(--accent);
  font-weight: 500;
}}

.toc-level-1 a {{
  font-weight: 600;
  font-size: 0.875rem;
  padding-left: 0.5rem;
}}

.toc-level-2 a {{
  padding-left: 1.25rem;
  font-size: 0.8125rem;
}}

.toc-level-3 a {{
  padding-left: 2rem;
  font-size: 0.75rem;
  opacity: 0.85;
}}

.toc-level-4 a {{
  padding-left: 2.75rem;
  font-size: 0.6875rem;
  opacity: 0.7;
}}

/* Typography */
h1 {{
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  line-height: 1.3;
}}

.meta {{
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid var(--border);
}}

h2 {{
  font-size: 1.5rem;
  font-weight: 600;
  margin: 2.5rem 0 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--accent-light);
}}

h3 {{
  font-size: 1.125rem;
  font-weight: 600;
  margin: 1.5rem 0 0.75rem;
}}

h4 {{
  font-size: 1rem;
  font-weight: 600;
  margin: 1.25rem 0 0.5rem;
  color: var(--text-secondary);
}}

h5 {{
  font-size: 0.9375rem;
  font-weight: 600;
  margin: 1rem 0 0.5rem;
  color: var(--text-secondary);
  opacity: 0.9;
}}

p {{
  margin-bottom: 1rem;
}}

a {{
  color: var(--accent);
  text-decoration: none;
}}
a:hover {{ text-decoration: underline; }}

blockquote {{
  border-left: 3px solid var(--accent);
  padding-left: 1rem;
  color: var(--text-secondary);
  margin: 1rem 0;
}}

table {{
  width: 100%;
  border-collapse: collapse;
  margin: 1rem 0;
  font-size: 0.9375rem;
}}

th, td {{
  padding: 0.75rem 1rem;
  border: 1px solid var(--border);
  text-align: left;
}}

th {{
  background: var(--accent-light);
  font-weight: 600;
}}

tr:nth-child(even) td {{
  background: var(--table-stripe);
}}

code {{
  background: var(--code-bg);
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-size: 0.875em;
  font-family: "SF Mono", "Fira Code", "Consolas", monospace;
}}

pre {{
  background: var(--code-bg);
  padding: 1rem 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
  border: 1px solid var(--border);
}}

pre code {{
  background: none;
  padding: 0;
}}

ul, ol {{
  padding-left: 1.5rem;
  margin-bottom: 1rem;
}}

li {{
  margin: 0.35rem 0;
}}

/* Citation link */
a.cit {{
  display: inline;
  color: var(--accent);
  background: var(--cite-bg);
  border-bottom: 1px dashed var(--cite-border);
  cursor: pointer;
  padding: 0 1px;
  text-decoration: none;
  border-radius: 2px;
}}

a.cit:hover {{
  background: var(--cite-border);
  color: var(--card-bg);
  text-decoration: none;
}}

/* Image zoom */
.content img {{
  cursor: zoom-in;
  transition: opacity 0.2s ease;
}}
.content img:hover {{
  opacity: 0.9;
}}

/* Image lightbox */
#img-lightbox {{
  display: none;
  position: fixed;
  z-index: 2000;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.85);
  justify-content: center;
  align-items: center;
  cursor: zoom-out;
}}
#img-lightbox.visible {{
  display: flex;
}}
#img-lightbox img {{
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  border-radius: 4px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}}

/* Source popup */
#source-popup {{
  display: none;
  position: fixed;
  z-index: 1000;
  background: var(--popup-bg);
  color: var(--popup-text);
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  line-height: 1.5;
  max-width: 320px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.15s ease;
}}

#source-popup.visible {{
  display: block;
  opacity: 1;
}}

#source-popup.pinned {{
  pointer-events: auto;
}}

#source-popup a {{
  color: var(--popup-link);
  text-decoration: underline;
}}

#source-popup .popup-title {{
  font-weight: 600;
  margin-bottom: 0.25rem;
}}

#source-popup .popup-url {{
  opacity: 0.7;
  font-size: 0.75rem;
  word-break: break-all;
}}

#source-popup .popup-hint {{
  margin-top: 0.35rem;
  opacity: 0.5;
  font-size: 0.6875rem;
}}

/* Sources section */
.sources-list {{
  padding-left: 1.25rem;
}}

.sources-list li {{
  margin: 0.5rem 0;
  font-size: 0.9375rem;
}}

.source-type {{
  display: inline-block;
  font-size: 0.6875rem;
  padding: 0.1rem 0.5rem;
  border-radius: 10px;
  margin-left: 0.5rem;
  vertical-align: middle;
  opacity: 0.7;
}}

.source-type.official {{ background: #dcfce7; color: #166534; }}
.source-type.wikipedia {{ background: #dbeafe; color: #1e40af; }}
.source-type.academic {{ background: #fef3c7; color: #92400e; }}
.source-type.community {{ background: #f3e8ff; color: #6b21a8; }}
.source-type.media {{ background: #ffe4e6; color: #9f1239; }}

.footer {{
  margin-top: 3rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.8125rem;
  text-align: center;
}}

::selection {{
  background: var(--accent-light);
}}
</style>
</head>
<body>

<div class="layout">

<!-- Sidebar TOC -->
<aside class="sidebar">
<div class="sidebar-title">目录</div>
<ol class="toc-nav">
{toc_html}
</ol>
</aside>

<!-- Main content -->
<main class="main-content" id="content">
<!-- Content rendered from Markdown -->
</main>

</div>

<!-- Source popup -->
<div id="source-popup">
  <div class="popup-title" id="popup-title"></div>
  <div class="popup-url" id="popup-url"></div>
  <div class="popup-hint">点击链接访问原文</div>
</div>

<!-- Image lightbox -->
<div id="img-lightbox">
  <img src="" alt="Zoomed image" id="lightbox-img">
</div>

<script>
// === Embedded Markdown content ===
const MARKDOWN_CONTENT = {md_content_json};

// === Source data ===
const sources = {sources_json};

function sourceTitle(s) {{
  if (!s) return '来源';
  return String(s.title || s.project || s.url || (s.urls && s.urls[0]) || '来源');
}}
function sourceUrl(s) {{
  if (!s) return '#';
  return s.url || (s.urls && s.urls[0]) || '#';
}}

// === Markdown parser ===
function parseMarkdown(md) {{
  const lines = md.split('\\n');
  let html = '';
  let inTable = false;
  let inCode = false;
  let inUl = false;
  let inOl = false;

  function escapeHtml(text) {{
    return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }}

  function slugify(text) {{
    text = text.replace(/\\*\\*([^*]+)\\*\\*/g, '$1');
    text = text.replace(/\\*([^*]+)\\*/g, '$1');
    text = text.replace(/`([^`]+)`/g, '$1');
    return text.replace(/[^\\w\\u4e00-\\u9fff]+/g, '-').toLowerCase().replace(/^-|-$/g, '').replace(/-+/g, '-').substring(0, 60);
  }}

  function renderInline(text) {{
    // Code
    text = text.replace(/`([^`]+)`/g, '<code>$1</code>');
    // Images: ![alt](url) → <img>
    text = text.replace(/!\\[([^\\]]*)\\]\\(([^)]+)\\)/g, function(m, alt, url) {{
      const isLocal = !url.startsWith('http');
      const src = url;
      return '<img src="' + src + '" alt="' + alt + '" style="max-width:100%;border-radius:8px;margin:1rem 0;border:1px solid var(--border)">';
    }});
    // Links
    text = text.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    // Bold
    text = text.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong>$1</strong>');
    // Italic
    text = text.replace(/\\*([^*]+)\\*/g, '<em>$1</em>');
    return text;
  }}

  function renderCitations(text) {{
    return text.replace(/\\[(\\d+)\\]/g, function(m, idx) {{
      const i = parseInt(idx) - 1;
      if (i >= 0 && i < sources.length) {{
        const s = sources[i];
        const title = sourceTitle(s).substring(0, 40).replace(/"/g, '&quot;');
        const url = sourceUrl(s);
        return '<a class="cit" href="' + url + '" target="_blank" rel="noopener" data-source-idx="' + i + '" title="' + title + '">[' + idx + ']</a>';
      }}
      return m;
    }});
  }}

  function closeLists() {{
    if (inUl) {{ html += '</ul>'; inUl = false; }}
    if (inOl) {{ html += '</ol>'; inOl = false; }}
    if (inTable) {{ html += '</table>'; inTable = false; }}
  }}

  for (let li = 0; li < lines.length; li++) {{
    const line = lines[li];
    const stripped = line.trim();

    // Code blocks
    if (stripped.startsWith('```')) {{
      closeLists();
      if (inCode) {{
        html += '</code></pre>';
        inCode = false;
      }} else {{
        const lang = stripped.substring(3).trim();
        html += '<pre><code' + (lang ? ' class="language-' + lang + '"' : '') + '>';
        inCode = true;
      }}
      continue;
    }}
    if (inCode) {{
      html += escapeHtml(line) + '\\n';
      continue;
    }}

    // Empty line
    if (!stripped) {{
      closeLists();
      continue;
    }}

    // Horizontal rule
    if (stripped === '---') {{
      closeLists();
      html += '<hr style="border:none;border-top:1px solid var(--border);margin:2rem 0">';
      continue;
    }}

    // Headings
    const h5Match = stripped.match(/^#####\\s+(.+)$/);
    const h4Match = stripped.match(/^####\\s+(.+)$/);
    const h3Match = stripped.match(/^###\\s+(.+)$/);
    const h2Match = stripped.match(/^##\\s+(.+)$/);
    const h1Match = stripped.match(/^#\\s+(.+)$/);

    if (h1Match) {{
      closeLists();
      const id = slugify(h1Match[1]);
      html += '<h1 id="' + id + '">' + renderCitations(renderInline(h1Match[1])) + '</h1>';
      continue;
    }}
    if (h2Match) {{
      closeLists();
      const id = slugify(h2Match[1]);
      html += '<h2 id="' + id + '">' + renderCitations(renderInline(h2Match[1])) + '</h2>';
      continue;
    }}
    if (h3Match) {{
      closeLists();
      const id = slugify(h3Match[1]);
      html += '<h3 id="' + id + '">' + renderCitations(renderInline(h3Match[1])) + '</h3>';
      continue;
    }}
    if (h4Match) {{
      closeLists();
      const id = slugify(h4Match[1]);
      html += '<h4 id="' + id + '">' + renderCitations(renderInline(h4Match[1])) + '</h4>';
      continue;
    }}
    if (h5Match) {{
      closeLists();
      const id = slugify(h5Match[1]);
      html += '<h5 id="' + id + '">' + renderCitations(renderInline(h5Match[1])) + '</h5>';
      continue;
    }}

    // Table
    if (stripped.includes('|') && stripped.startsWith('|')) {{
      const cells = stripped.replace(/^\\||\\|$/g, '').split('|').map(c => c.trim());
      if (cells.every(c => /^[-:]+$/.test(c))) continue; // skip separator
      if (!inTable) {{
        html += '<table><thead><tr>';
        cells.forEach(c => {{ html += '<th>' + renderCitations(renderInline(c)) + '</th>'; }});
        html += '</tr></thead><tbody>';
        inTable = true;
      }} else {{
        html += '<tr>';
        cells.forEach(c => {{ html += '<td>' + renderCitations(renderInline(c)) + '</td>'; }});
        html += '</tr>';
      }}
      continue;
    }} else {{
      if (inTable) {{ html += '</table>'; inTable = false; }}
    }}

    // Unordered list
    if (/^[-*]\\s+/.test(stripped)) {{
      if (!inUl) {{
        if (inOl) {{ html += '</ol>'; inOl = false; }}
        html += '<ul>';
        inUl = true;
      }}
      html += '<li>' + renderCitations(renderInline(stripped.replace(/^[-*]\\s+/, ''))) + '</li>';
      continue;
    }}

    // Ordered list
    if (/^\\d+\\.\\s+/.test(stripped)) {{
      if (!inOl) {{
        if (inUl) {{ html += '</ul>'; inUl = false; }}
        html += '<ol>';
        inOl = true;
      }}
      html += '<li>' + renderCitations(renderInline(stripped.replace(/^\\d+\\.\\s+/, ''))) + '</li>';
      continue;
    }}

    // Blockquote
    if (stripped.startsWith('> ')) {{
      closeLists();
      html += '<blockquote>' + renderCitations(renderInline(stripped.substring(2))) + '</blockquote>';
      continue;
    }}

    // Paragraph
    closeLists();
    html += '<p>' + renderCitations(renderInline(stripped)) + '</p>';
  }}
  closeLists();
  return html;
}}

// === Render content ===
document.getElementById('content').innerHTML = parseMarkdown(MARKDOWN_CONTENT);

// === Image lightbox ===
(function() {{
  const lightbox = document.getElementById('img-lightbox');
  const lightboxImg = document.getElementById('lightbox-img');
  document.addEventListener('click', function(evt) {{
    const img = evt.target.closest('.content img');
    if (img) {{
      lightboxImg.src = img.src;
      lightboxImg.alt = img.alt;
      lightbox.classList.add('visible');
    }} else if (evt.target.closest('#img-lightbox')) {{
      lightbox.classList.remove('visible');
      lightboxImg.src = '';
    }}
  }});
  document.addEventListener('keydown', function(evt) {{
    if (evt.key === 'Escape') lightbox.classList.remove('visible');
  }});
}})();

// === Popup interaction ===
(function() {{
  const popup = document.getElementById('source-popup');
  const popupTitle = document.getElementById('popup-title');
  const popupUrl = document.getElementById('popup-url');
  let pinnedSource = null;

  function showPopup(el) {{
    const idx = parseInt(el.dataset.sourceIdx);
    const s = sources[idx];
    if (!s) return;
    const title = sourceTitle(s);
    const url = sourceUrl(s);
    popupTitle.textContent = title;
    popupUrl.innerHTML = '<a href="' + url + '" target="_blank" rel="noopener">' + url + '</a>';
    const rect = el.getBoundingClientRect();
    let x = rect.left;
    let y = rect.bottom + 8;
    if (x + 320 > window.innerWidth) x = window.innerWidth - 330;
    if (y + 100 > window.innerHeight) y = rect.top - 100;
    popup.style.left = x + 'px';
    popup.style.top = y + 'px';
    popup.classList.add('visible');
    pinnedSource = idx;
  }}

  function hidePopup() {{
    popup.classList.remove('visible');
    popup.classList.remove('pinned');
    pinnedSource = null;
  }}

  // Click on citation: toggle pin
  document.addEventListener('click', function(evt) {{
    const cit = evt.target.closest('.cit');
    if (cit) {{
      evt.preventDefault();
      evt.stopPropagation();
      const idx = parseInt(cit.dataset.sourceIdx);
      if (pinnedSource === idx) {{
        hidePopup();
      }} else {{
        showPopup(cit);
        popup.classList.add('pinned');
      }}
      return;
    }}
    // Click inside pinned popup → allow link navigation
    if (evt.target.closest('#source-popup')) return;
    // Click elsewhere → close
    hidePopup();
  }});

  // Hover: preview (only when not pinned)
  document.addEventListener('mouseover', function(evt) {{
    const cit = evt.target.closest('.cit');
    if (cit && !pinnedSource) showPopup(cit);
  }});
  document.addEventListener('mouseout', function(evt) {{
    const cit = evt.target.closest('.cit');
    if (cit && !pinnedSource) hidePopup();
  }});

  // Selection: detect citation
  document.addEventListener('mouseup', function(evt) {{
    const sel = window.getSelection();
    if (sel.isCollapsed) return;
    const range = sel.getRangeAt(0);
    let node = range.startContainer;
    if (node.nodeType === 3) node = node.parentNode;
    const cit = node.closest('.cit');
    if (cit && !pinnedSource) showPopup(cit);
  }});

  // Escape closes
  document.addEventListener('keydown', function(evt) {{
    if (evt.key === 'Escape') hidePopup();
  }});
}})();

// === Scroll-spy ===
(function() {{
  const tocLinks = document.querySelectorAll('.toc-nav a');
  const headingElements = new Map();
  tocLinks.forEach(function(link) {{
    const targetId = link.getAttribute('href').slice(1);
    const el = document.getElementById(targetId);
    if (el) headingElements.set(targetId, el);
  }});

  function updateActiveHeading() {{
    let current = '';
    const scrollPos = window.scrollY + 100;
    headingElements.forEach(function(el, id) {{
      if (el.offsetTop <= scrollPos) current = id;
    }});
    tocLinks.forEach(function(link) {{
      link.classList.toggle('active', link.getAttribute('href') === '#' + current);
    }});
  }}

  window.addEventListener('scroll', updateActiveHeading, {{ passive: true }});
  updateActiveHeading();
}})();
</script>

</body>
</html>
"""


def extract_headings_for_toc(md_text):
    """Extract headings from markdown for hierarchical TOC."""
    headings = []
    in_code = False
    for line in md_text.split('\n'):
        stripped = line.strip()
        if stripped.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if stripped.startswith('##### '):
            headings.append((5, stripped[6:].strip()))
        elif stripped.startswith('#### '):
            headings.append((4, stripped[5:].strip()))
        elif stripped.startswith('### '):
            headings.append((3, stripped[4:].strip()))
        elif stripped.startswith('## '):
            headings.append((2, stripped[3:].strip()))
        elif stripped.startswith('# '):
            headings.append((1, stripped[2:].strip()))
    return headings


def generate_html(topic, angles_data, md_content=None):
    """Generate HTML template from angle data.
    If md_content is provided, uses it; otherwise generates from angles_data.
    Returns (html_content, all_sources).
    """
    if md_content is None:
        md_content, all_sources = generate_markdown(topic, angles_data)
    else:
        all_sources = []
        for a in angles_data:
            for src in a.get('sources', []):
                all_sources.append(normalize_source(src))

    # Extract headings for TOC
    headings = extract_headings_for_toc(md_content)

    # Build hierarchical TOC HTML
    toc_html = '<li class="toc-level-1"><a href="#概述">概述</a></li>\n'
    for level, title in headings:
        hid = slugify(title)
        toc_level = min(level + 1, 4)
        toc_html += f'<li class="toc-level-{toc_level}"><a href="#{hid}">{escape(title)}</a></li>\n'

    # Embed markdown as JSON string
    md_json = json.dumps(md_content, ensure_ascii=False)
    sources_json_str = json.dumps(all_sources, ensure_ascii=False)

    html = HTML_TEMPLATE.format(
        title=escape(topic),
        toc_html=toc_html,
        md_content_json=md_json,
        sources_json=sources_json_str,
    )

    return html, all_sources


def main():
    parser = argparse.ArgumentParser(description='Generate Markdown + interactive HTML report')
    parser.add_argument('--topic', required=True, help='Research topic')
    parser.add_argument('--input', required=True, help='Path to JSON file with angle data')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        angles_data = json.load(f)

    if isinstance(angles_data, dict):
        angles_data = angles_data.get('angles', angles_data.get('results', []))

    topic = args.topic
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate initial Markdown
    md_content, all_sources = generate_markdown(topic, angles_data)

    # Download images and insert into markdown
    print('Downloading images...')
    image_map = collect_and_download_images(angles_data, out_dir)
    local_count = sum(1 for v in image_map.values() if not v.startswith('http'))
    remote_count = sum(1 for v in image_map.values() if v.startswith('http'))
    print(f'Images: {local_count} local, {remote_count} remote')

    md_content = insert_images_into_markdown(md_content, angles_data, image_map, out_dir)

    # Write README.md
    md_path = out_dir / 'README.md'
    md_path.write_text(md_content, encoding='utf-8')
    print(f'Markdown saved to: {md_path}')

    # Generate HTML with updated markdown (including image references)
    html_content, all_sources = generate_html(topic, angles_data, md_content=md_content)

    # Write index.html
    html_path = out_dir / 'index.html'
    html_path.write_text(html_content, encoding='utf-8')
    print(f'HTML viewer saved to: {html_path}')

    # Write sources.json
    sources_data = {
        'generated_at': datetime.now().isoformat(),
        'sources': all_sources,
    }
    sources_path = out_dir / 'sources.json'
    sources_path.write_text(json.dumps(sources_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Sources saved to: {sources_path}')


def download_image(url, dest_path, timeout=10):
    """Download an image from URL to local path. Returns (success, local_path_or_url)."""
    try:
        import urllib.request
        import urllib.error
        # Set a user agent to avoid 403 errors
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read()
            content_type = response.headers.get('Content-Type', '')
            # Determine extension from content-type or URL
            ext = '.png'
            if 'svg' in content_type or url.endswith('.svg'):
                ext = '.svg'
            elif 'jpeg' in content_type or 'jpg' in content_type or url.endswith(('.jpg', '.jpeg')):
                ext = '.jpg'
            elif 'gif' in content_type or url.endswith('.gif'):
                ext = '.gif'
            elif 'webp' in content_type or url.endswith('.webp'):
                ext = '.webp'
            elif url.endswith(('.png', '.svg', '.jpg', '.jpeg', '.gif', '.webp')):
                ext = '.' + url.split('.')[-1].split('?')[0]

            dest_path = dest_path.with_suffix(ext)
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            dest_path.write_bytes(data)
            return True, str(dest_path)
    except Exception as e:
        return False, url


def collect_and_download_images(angles_data, out_dir):
    """Collect all image URLs from angles and download them.
    Returns (image_map, updated_md_insertions) where image_map is {url: local_path}."""
    images_dir = out_dir / 'images'
    images_dir.mkdir(exist_ok=True)

    image_map = {}  # url -> local_path or original url
    all_images = []  # list of (index, image_info)

    for a_idx, a in enumerate(angles_data):
        for img in a.get('images', []):
            url = img.get('url', '')
            if not url or url in image_map:
                continue
            all_images.append((a_idx, img))

    # Download images
    for idx, (a_idx, img) in enumerate(all_images):
        url = img['url']
        desc = img.get('description', f'Image {idx+1}')

        # SVG files: use original URL (works in browsers and markdown viewers)
        if url.endswith('.svg') or 'wikipedia.org/wiki/File:' in url:
            image_map[url] = url
            continue

        # Generate a filename
        safe_name = re.sub(r'[^\w]+', '-', desc.lower()).strip('-')[:50]
        if not safe_name:
            safe_name = f'image-{idx+1}'
        dest_path = images_dir / safe_name

        # Check if already downloaded (from a previous run)
        existing = list(images_dir.glob(f'{safe_name}.*'))
        if existing:
            image_map[url] = str(existing[0].relative_to(out_dir)).replace('\\', '/')
            continue

        success, result = download_image(url, dest_path)
        if success:
            image_map[url] = result.replace('\\', '/')
            print(f'  Downloaded: {desc[:40]} -> {result}')
        else:
            image_map[url] = url  # Fallback to original URL
            print(f'  Failed to download (using original URL)')

    return image_map


def insert_images_into_markdown(md_content, angles_data, image_map, out_dir):
    """Insert image references into markdown content at appropriate positions.
    Returns updated markdown content."""
    # Build a list of images per angle
    angle_image_refs = {}  # angle_index -> list of markdown image refs
    for a_idx, a in enumerate(angles_data):
        for img in a.get('images', []):
            url = img.get('url', '')
            if not url:
                continue
            local_path = image_map.get(url, url)
            desc = img.get('description', '')
            source = img.get('source', url)
            img_md = f'![{desc}]({local_path})\n\n*来源：[{source})]({source})*'
            angle_image_refs.setdefault(a_idx, []).append(img_md)

    # Insert images after the first paragraph of each angle section
    # We'll find each angle's section and insert images after its first paragraph
    lines = md_content.split('\n')
    result = []
    current_angle = -1
    angle_header_pattern = re.compile(r'^##\s+(.+)')
    first_para_done = set()

    for i, line in enumerate(lines):
        result.append(line)

        # Detect angle headers
        m = angle_header_pattern.match(line)
        if m:
            header_text = m.group(1)
            for a_idx, a in enumerate(angles_data):
                if a['angle'] == header_text:
                    current_angle = a_idx
                    break

        # After first paragraph in an angle section, insert images
        if current_angle >= 0 and current_angle not in angle_image_refs:
            continue
        if current_angle >= 0 and current_angle not in first_para_done:
            # Check if this is a paragraph (non-empty, non-header, non-table, non-list)
            if line and not line.startswith('#') and not line.startswith('|') and not line.startswith(('-', '*', '>', '```')) and not re.match(r'^\d+\.', line):
                # Check if next line is empty (end of paragraph)
                next_line = lines[i + 1] if i + 1 < len(lines) else ''
                if next_line.strip() == '':
                    # Insert images here
                    result.append('')
                    for img_ref in angle_image_refs.get(current_angle, []):
                        result.append(img_ref)
                        result.append('')
                    first_para_done.add(current_angle)

    return '\n'.join(result)


if __name__ == '__main__':
    main()
