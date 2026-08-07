#!/usr/bin/env python3
"""Generate a structured Markdown research report from sub-agent results."""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path


def slugify(text: str) -> str:
    """Convert topic to URL-safe slug."""
    import re
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text


def generate_report(topic: str, angles_data: list[dict]) -> str:
    """Generate the full Markdown report."""
    today = datetime.now().strftime('%Y-%m-%d')
    angles_list = '、'.join(a['angle'] for a in angles_data)

    lines = [
        f'# {topic}',
        '',
        f'> 生成时间：{today}',
        f'> 调研角度：{angles_list}',
        '',
        '---',
        '',
        '## 目录',
        '1. [概述](#概述)',
    ]

    for i, a in enumerate(angles_data, 2):
        anchor = a['angle'].replace(' ', '-').replace('/', '')
        lines.append(f'{i}. [{a["angle"]}](#{anchor})')

    lines.extend([
        f'{len(angles_data) + 2}. [参考来源](#参考来源)',
        '',
        '---',
        '',
        '## 概述',
        '',
    ])

    # Overview section: combine all summaries
    overview_parts = []
    for a in angles_data:
        overview_parts.append(f'**{a["angle"]}**：{a["summary"]}')
    lines.append('\n\n'.join(overview_parts))

    # Per-angle sections
    for a in angles_data:
        lines.extend([
            '',
            '---',
            '',
            f'## {a["angle"]}',
            '',
            a.get('details', a.get('summary', '（内容待补充）')),
            '',
        ])

        if a.get('key_points'):
            lines.extend(['### 关键要点', ''])
            for kp in a['key_points']:
                lines.append(f'- {kp}')
            lines.append('')

    # Images section
    all_images = []
    for a in angles_data:
        for img in a.get('images', []):
            all_images.append(img)

    if all_images:
        lines.extend([
            '---',
            '',
            '## 图片资料',
            '',
            '| 序号 | 说明 | 来源 |',
            '|------|------|------|',
        ])
        for i, img in enumerate(all_images, 1):
            desc = img.get('description', '—')
            src = img.get('source', img.get('url', '—'))
            lines.append(f'| {i} | {desc} | [查看]({src}) |')
        lines.append('')

    # Sources section
    academic_sources = []
    community_sources = []
    for a in angles_data:
        for src in a.get('sources', []):
            t = src.get('type', 'community')
            if t in ('official', 'academic', 'wikipedia'):
                academic_sources.append(src)
            else:
                community_sources.append(src)

    lines.extend([
        '---',
        '',
        '## 参考来源',
        '',
    ])

    if academic_sources:
        lines.append('### 官方与学术来源')
        lines.append('')
        for i, src in enumerate(academic_sources, 1):
            title = src.get('title', src.get('url', '未知'))
            url = src.get('url', '#')
            lines.append(f'{i}. [{title}]({url})')
        lines.append('')

    if community_sources:
        lines.append('### 社区与媒体来源')
        lines.append('')
        offset = len(academic_sources)
        for i, src in enumerate(community_sources, offset + 1):
            title = src.get('title', src.get('url', '未知'))
            url = src.get('url', '#')
            lines.append(f'{i}. [{title}]({url})')
        lines.append('')

    lines.extend([
        '---',
        '',
        '*本报告由 AI 助手调研生成，资料来源仅供参考，请自行验证准确性。*',
        '',
    ])

    return '\n'.join(lines)


def generate_sources_json(angles_data: list[dict]) -> dict:
    """Generate structured sources.json."""
    return {
        'generated_at': datetime.now().isoformat(),
        'angles': [
            {
                'angle': a['angle'],
                'sources': a.get('sources', []),
                'images': a.get('images', []),
            }
            for a in angles_data
        ],
    }


def main():
    parser = argparse.ArgumentParser(description='Generate topic research report')
    parser.add_argument('--topic', required=True, help='Research topic')
    parser.add_argument('--input', required=True, help='Path to JSON file with angle data')
    parser.add_argument('--output-dir', required=True, help='Output directory')
    args = parser.parse_args()

    with open(args.input, 'r', encoding='utf-8') as f:
        angles_data = json.load(f)

    # Handle both list format and {angles: [...]} format
    if isinstance(angles_data, dict):
        angles_data = angles_data.get('angles', angles_data.get('results', []))

    topic = args.topic
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Generate report
    report_md = generate_report(topic, angles_data)
    report_path = out_dir / 'README.md'
    report_path.write_text(report_md, encoding='utf-8')
    print(f'Report saved to: {report_path}')

    # Generate sources.json
    sources_data = generate_sources_json(angles_data)
    sources_path = out_dir / 'sources.json'
    sources_path.write_text(json.dumps(sources_data, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Sources saved to: {sources_path}')


if __name__ == '__main__':
    main()
