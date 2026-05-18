#!/usr/bin/env python3
"""扫 Python docstring 与 JS/TS JSDoc 中的敏感模式。

用法:
    check_comments.py <root> [--sdk-paths <json>] [--format text|json]

退出码:
    0 = 无违规
    1 = 有违规
    2 = 用法错误
"""
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable


# 敏感模式表，与 references/sensitive-patterns.md 对齐
PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("internal-domain", re.compile(r"\b[\w-]+\.(internal|corp|local|intranet)\b", re.I)),
    ("private-ip", re.compile(
        r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
        r"|192\.168\.\d{1,3}\.\d{1,3}"
        r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
    )),
    ("sql-statement", re.compile(
        r"\b(SELECT|UPDATE|DELETE|INSERT)\b[^.\n]{0,80}\b(FROM|WHERE|SET|INTO)\b", re.I
    )),
    ("redis-key-pattern", re.compile(r"\b(cache|redis|fmt|lock|queue):[a-z_]+:")),
    ("jira-ticket", re.compile(r"\b[A-Z]{2,6}-\d{2,6}\b")),
    ("internal-service", re.compile(
        r"\b[a-z_]+_(?:service|server|grpc|rpc)_(?:v\d|prod|stg|stage|dev)\b"
    )),
    ("aws-arn", re.compile(r"arn:aws:[a-z0-9-]+:[a-z0-9-]*:\d+:[a-zA-Z0-9-_/:]+")),
    ("aws-key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("cred-keyword", re.compile(
        r"\b(API_KEY|TOKEN|SECRET|PASSWORD|PRIVATE_KEY)\s*[=:]\s*['\"][\w\-./+]{6,}['\"]"
    )),
]

# 弱模式（仅在行内有上下文关键字时命中，降误报）
PORT_PATTERN = re.compile(r":(\d{4,5})\b")
PORT_CONTEXT = re.compile(r"\b(connect|server|host|endpoint|address|listen|bind)\b", re.I)

EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w.-]+\.[a-z]{2,}")
PUBLIC_EMAIL_DOMAINS = {
    "example.com", "example.org", "example.net",
    "gmail.com", "outlook.com", "hotmail.com", "qq.com", "163.com",
    "yourdomain.com", "your-domain.com", "domain.com",
}

# 行内示例 / 占位关键字 → 整行视为示例不告警
EXAMPLE_HINTS = re.compile(r"\b(example|示例|e\.g\.|placeholder|占位|your[- ]?domain|<.*>)\b", re.I)

# 行内豁免
IGNORE_MARKER = re.compile(r"#\s*sdk-spec:\s*ignore|//\s*sdk-spec:\s*ignore")


@dataclass
class Violation:
    file: str
    line: int
    pattern: str
    match: str
    context: str


def scan_text(file_rel: str, text: str, start_line_offset: int = 0) -> list[Violation]:
    """扫一段连续文本（docstring 或注释块），返回违规列表。

    `text` 内部带换行，`start_line_offset` 是该文本第一行在文件中的实际行号。
    """
    out: list[Violation] = []
    for i, line in enumerate(text.splitlines(), start=start_line_offset):
        if IGNORE_MARKER.search(line):
            continue
        line_stripped = line.strip()
        if not line_stripped:
            continue

        is_example = bool(EXAMPLE_HINTS.search(line))

        # 主模式
        for pat_name, pat in PATTERNS:
            for m in pat.finditer(line):
                if is_example and pat_name in {"sql-statement", "internal-domain", "jira-ticket"}:
                    continue
                out.append(Violation(
                    file=file_rel, line=i,
                    pattern=pat_name, match=m.group(0),
                    context=line_stripped[:160],
                ))

        # 端口（弱模式）
        if not is_example and PORT_CONTEXT.search(line):
            for m in PORT_PATTERN.finditer(line):
                port = int(m.group(1))
                if port in {8080, 8000, 3000, 5000, 5173, 5432, 6379, 9000}:
                    # 常见示例端口，跳过
                    continue
                out.append(Violation(
                    file=file_rel, line=i,
                    pattern="service-port", match=m.group(0),
                    context=line_stripped[:160],
                ))

        # 邮箱（弱模式）
        if not is_example:
            for m in EMAIL_PATTERN.finditer(line):
                email = m.group(0)
                domain = email.split("@", 1)[1].lower()
                if domain in PUBLIC_EMAIL_DOMAINS:
                    continue
                out.append(Violation(
                    file=file_rel, line=i,
                    pattern="internal-email", match=email,
                    context=line_stripped[:160],
                ))
    return out


def scan_python_file(path: Path, root: Path) -> list[Violation]:
    rel = str(path.relative_to(root))
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    out: list[Violation] = []
    # 模块、函数、类、异步函数的 docstring
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        doc = ast.get_docstring(node, clean=False)
        if not doc:
            continue
        # docstring 首行在 node.body[0].lineno（第一条 Expr 是字符串）
        first_stmt = node.body[0] if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) else node.body[0]
        start_line = getattr(first_stmt, "lineno", 1)
        out.extend(scan_text(rel, doc, start_line_offset=start_line))
    return out


# 匹配 JS/TS 的 /** ... */ JSDoc 块（不含其他 /* */ 注释）
JSDOC_BLOCK = re.compile(r"/\*\*(.*?)\*/", re.DOTALL)
# 行注释 //
LINE_COMMENT = re.compile(r"^\s*//\s?(.*)$")


def scan_js_file(path: Path, root: Path) -> list[Violation]:
    rel = str(path.relative_to(root))
    try:
        source = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    out: list[Violation] = []

    # JSDoc 块
    for m in JSDOC_BLOCK.finditer(source):
        block_text = m.group(1)
        # 起始行号
        start_line = source.count("\n", 0, m.start()) + 1
        # 去掉每行的 leading * 和空白
        cleaned_lines = []
        for line in block_text.splitlines():
            cleaned_lines.append(re.sub(r"^\s*\*\s?", "", line))
        out.extend(scan_text(rel, "\n".join(cleaned_lines), start_line_offset=start_line))

    # 行内注释（只扫描，因为商业 SDK 内部实现的行注释虽然不打包但开发期能看到）
    # 注：源文件其实是否打包取决于配置，行注释泄露主要看是否打包 src/
    # 跨边界谨慎起见也扫
    for i, line in enumerate(source.splitlines(), start=1):
        lm = LINE_COMMENT.match(line)
        if not lm:
            continue
        comment = lm.group(1)
        out.extend(scan_text(rel, comment, start_line_offset=i))

    return out


def iter_target_files(root: Path, sdk_paths: list[str] | None) -> Iterable[Path]:
    """枚举要扫的文件。sdk_paths 为 None 时全扫；否则只扫指定路径。"""
    excludes = {
        "node_modules", ".venv", "venv", "dist", "build",
        ".git", "__pycache__", ".mypy_cache", ".pytest_cache",
        ".ruff_cache", ".tox", "egg-info", "site-packages",
    }
    bases = [root / p for p in sdk_paths] if sdk_paths else [root]
    for base in bases:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if not p.is_file():
                continue
            if any(part in excludes or part.endswith(".egg-info") for part in p.parts):
                continue
            suf = p.suffix.lower()
            if suf in {".py", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs"}:
                yield p


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan SDK comments for sensitive patterns.")
    parser.add_argument("root", help="Project root directory (absolute path)")
    parser.add_argument("--sdk-paths", default=None,
                        help='JSON {"python":[...], "js":[...]} relative to root. Omit to scan all.')
    parser.add_argument("--format", choices=["text", "json"], default="text")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"ERROR: not a directory: {root}", file=sys.stderr)
        return 2

    target_paths: list[str] | None = None
    if args.sdk_paths:
        try:
            sdk_spec = json.loads(args.sdk_paths)
        except json.JSONDecodeError as e:
            print(f"ERROR: invalid --sdk-paths JSON: {e}", file=sys.stderr)
            return 2
        target_paths = []
        for key in ("python", "js"):
            target_paths.extend(sdk_spec.get(key, []))

    violations: list[Violation] = []
    for fp in iter_target_files(root, target_paths):
        if fp.suffix == ".py":
            violations.extend(scan_python_file(fp, root))
        else:
            violations.extend(scan_js_file(fp, root))

    if args.format == "json":
        print(json.dumps([asdict(v) for v in violations], ensure_ascii=False, indent=2))
    else:
        if not violations:
            print("OK: no sensitive patterns found")
        else:
            print(f"FAIL: {len(violations)} violation(s) found:\n")
            for v in violations:
                print(f"  {v.file}:{v.line}  [{v.pattern}]  match={v.match!r}")
                print(f"    > {v.context}")

    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
