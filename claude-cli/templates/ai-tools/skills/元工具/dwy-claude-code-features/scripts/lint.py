#!/usr/bin/env python3
"""
dwy-claude-code-features lint：对 Claude Code 4 类扩展文件做格式硬检查。

支持类型：
  - slash-command   .claude/commands/*.md
  - skill           <dir>/SKILL.md
  - subagent        .claude/agents/*.md
  - claude-md       CLAUDE.md / CLAUDE.local.md / .claude/rules/*.md

不带 --type 时，按路径自动推断（命中 commands/、skills/、agents/、CLAUDE.md 等关键字）。

输出 JSON：
  {
    "target": "<path>",
    "type": "skill",
    "violations": [
      {"rule": "frontmatter.field.unknown", "severity": "error", "message": "...", "line": 4}
    ],
    "passed": true
  }

退出码：
  0 = passed=true（无 error 级 violation；warn 不算失败）
  1 = passed=false
  2 = 参数 / 文件错误

只用 Python 标准库；YAML 用最小自实现解析（避免外部依赖）。

约束来源：
  - https://code.claude.com/docs/zh-CN/skills
  - https://code.claude.com/docs/zh-CN/sub-agents
  - https://code.claude.com/docs/zh-CN/memory
  fetched_at: 2026-05-19
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

# ---------- 字段集 ----------

SKILL_ALLOWED_FIELDS = {
    "name",
    "description",
    "when_to_use",
    "argument-hint",
    "arguments",
    "disable-model-invocation",
    "user-invocable",
    "allowed-tools",
    "model",
    "effort",
    "context",
    "agent",
    "hooks",
    "paths",
    "shell",
}

# slash command 跟 skill 字段集相同
SLASH_COMMAND_ALLOWED_FIELDS = set(SKILL_ALLOWED_FIELDS)

SUBAGENT_ALLOWED_FIELDS = {
    "name",
    "description",
    "tools",
    "disallowedTools",
    "model",
    "permissionMode",
    "maxTurns",
    "skills",
    "mcpServers",
    "hooks",
    "memory",
    "background",
    "effort",
    "isolation",
    "color",
    "initialPrompt",
    # 兼容（CLI inline JSON 用的 prompt 字段不在 markdown 文件中出现）
}

SUBAGENT_REQUIRED_FIELDS = {"name", "description"}

VALID_MODELS_ALIAS = {"sonnet", "opus", "haiku", "inherit"}
VALID_MODELS_PREFIX = ("claude-",)

VALID_EFFORT = {"low", "medium", "high", "xhigh", "max"}

VALID_PERMISSION_MODES = {
    "default",
    "acceptEdits",
    "auto",
    "dontAsk",
    "bypassPermissions",
    "plan",
}

VALID_COLORS = {"red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan"}

VALID_MEMORY_SCOPES = {"user", "project", "local"}

VALID_ISOLATION = {"worktree"}

VALID_CONTEXT = {"fork"}

VALID_SHELL = {"bash", "powershell"}

# rules 文件 paths 字段无限制 glob，不校验

# ---------- 工具函数 ----------

KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MODEL_FULL_RE = re.compile(r"^claude-[a-z0-9.-]+$")


def fail(msg: str) -> "None":
    print(f"lint.py: {msg}", file=sys.stderr)
    sys.exit(2)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as e:
        fail(f"文件不是 UTF-8 编码: {path} ({e})")
    except FileNotFoundError:
        fail(f"文件不存在: {path}")


def detect_type(path: Path) -> "str | None":
    parts = path.as_posix().split("/")
    name = path.name

    if name in {"CLAUDE.md", "CLAUDE.local.md"}:
        return "claude-md"
    if ".claude/rules/" in path.as_posix() or "/rules/" in path.as_posix() and name.endswith(".md"):
        return "claude-md"

    if ".claude/commands/" in path.as_posix() or "/commands/" in path.as_posix() and name.endswith(".md"):
        return "slash-command"

    if name == "SKILL.md":
        return "skill"
    if ".claude/skills/" in path.as_posix() or "/skills/" in path.as_posix():
        return "skill"

    if ".claude/agents/" in path.as_posix() or "/agents/" in path.as_posix():
        return "subagent"

    return None


# ---------- frontmatter 解析（最小自实现）----------


def split_frontmatter(text: str) -> "tuple[dict | None, int, str]":
    """返回 (frontmatter_dict, frontmatter_end_line, body)。

    没有合规 frontmatter 时 frontmatter_dict=None。
    Frontmatter 必须从第一行 `---` 开始，到第二个 `---` 结束。
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, 0, text
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return None, 0, text
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :])
    fm = parse_yaml_simple(fm_lines)
    return fm, end_idx + 1, body


def parse_yaml_simple(lines: "list[str]") -> dict:
    """极简 YAML 解析：仅支持 key: value、key: [list]、多行字符串（`|` / `|-` / `:` 后空再多行缩进）、
    block 列表（- item）。够 frontmatter 用。

    解析失败时返回字段 dict 里包含 `_yaml_error: <line_no>: <msg>` 占位，让上层报错。
    """
    out: "dict[str, object]" = {}
    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            i += 1
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
        if not m:
            out["_yaml_error"] = f"line {i+1}: 不可解析的行 `{line}`"
            return out
        key, val = m.group(1), m.group(2).strip()
        if val == "":
            # 嵌套结构或 block 列表
            block_lines = []
            j = i + 1
            while j < n:
                nxt = lines[j]
                if not nxt.strip() or nxt.startswith(" ") or nxt.startswith("\t") or nxt.lstrip().startswith("-"):
                    block_lines.append(nxt)
                    j += 1
                else:
                    break
            # block list (- xxx) 优先识别
            if any(ln.lstrip().startswith("- ") for ln in block_lines):
                items: "list[object]" = []
                for ln in block_lines:
                    ls = ln.lstrip()
                    if ls.startswith("- "):
                        items.append(ls[2:].strip().strip('"').strip("'"))
                out[key] = items
            else:
                # 当作复杂 dict（如 hooks: 嵌套结构）。这里只标记存在，详细结构不校验
                out[key] = {"_complex": True}
            i = j
            continue
        # inline value
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            items_list = [
                s.strip().strip('"').strip("'") for s in inner.split(",") if s.strip()
            ] if inner else []
            out[key] = items_list
        elif val.lower() in {"true", "false"}:
            out[key] = val.lower() == "true"
        elif val.isdigit() or (val.startswith("-") and val[1:].isdigit()):
            out[key] = int(val)
        else:
            v = val
            if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
                v = v[1:-1]
            out[key] = v
        i += 1
    return out


# ---------- violation 收集 ----------


class Violations:
    def __init__(self) -> None:
        self.items: "list[dict]" = []

    def add(self, rule: str, severity: str, message: str, line: "int | None" = None) -> None:
        d = {"rule": rule, "severity": severity, "message": message}
        if line is not None:
            d["line"] = line
        self.items.append(d)

    @property
    def has_error(self) -> bool:
        return any(v["severity"] == "error" for v in self.items)


# ---------- 通用校验 ----------


def check_utf8_bom(text: str, v: Violations) -> None:
    if text.startswith("﻿"):
        v.add(
            "encoding.bom",
            "warn",
            "文件包含 UTF-8 BOM，建议去掉（部分工具不兼容）",
            line=1,
        )


def check_filename_kebab(path: Path, v: Violations, stem_only: bool = True) -> None:
    name = path.stem if stem_only else path.name
    # SKILL.md 文件名固定为 SKILL，不参与 kebab 检查
    if name == "SKILL":
        return
    if not KEBAB_RE.match(name):
        v.add(
            "filename.kebab-case",
            "warn",
            f"文件名 `{path.name}` 不是 kebab-case（建议小写字母+连字符）",
        )


def check_model_value(val: str, v: Violations, field: str = "model") -> None:
    if val in VALID_MODELS_ALIAS:
        return
    if MODEL_FULL_RE.match(val):
        return
    v.add(
        f"{field}.value.invalid",
        "warn",
        f"`{field}: {val}` 不在已知集合（{', '.join(sorted(VALID_MODELS_ALIAS))} 或 claude-* 完整 ID）",
    )


# ---------- 各类型 lint ----------


def lint_skill(path: Path, fm: "dict | None", body: str, v: Violations) -> None:
    if fm is None:
        v.add("frontmatter.missing", "warn", "SKILL.md 没有 YAML frontmatter（description 字段强烈推荐）")
        return
    if "_yaml_error" in fm:
        v.add("frontmatter.yaml.parse", "error", str(fm["_yaml_error"]))
        return

    # 已知"字段错配"（subagent 字段误用到 skill 里）→ error；其他自定义字段 → warn
    SUBAGENT_ONLY = {"tools", "disallowedTools", "permissionMode", "mcpServers",
                     "maxTurns", "memory", "background", "isolation", "color",
                     "initialPrompt", "skills"}
    unknown = [k for k in fm if k not in SKILL_ALLOWED_FIELDS and not k.startswith("_")]
    for k in unknown:
        if k in SUBAGENT_ONLY:
            hint_map = {
                "tools": "subagent 才用 `tools`，skill / command 用 `allowed-tools`",
                "permissionMode": "`permissionMode` 是 subagent 字段，skill 不支持",
                "mcpServers": "`mcpServers` 是 subagent 字段",
                "disallowedTools": "`disallowedTools` 是 subagent 字段",
            }
            hint = hint_map.get(k, f"`{k}` 是 subagent 字段，skill 不支持")
            v.add(
                "frontmatter.field.misplaced",
                "error",
                f"字段 `{k}` 应该在 subagent，不在 skill：{hint}",
            )
        else:
            v.add(
                "frontmatter.field.custom",
                "warn",
                f"字段 `{k}` 不在官方 skill 字段集，Claude Code 会忽略（自定义元数据可保留）",
            )

    if "description" not in fm:
        v.add(
            "frontmatter.field.missing",
            "warn",
            "缺 `description` 字段；Claude 无法主动调用此 skill",
        )

    if "name" in fm:
        nm = fm["name"]
        if not isinstance(nm, str) or not KEBAB_RE.match(nm) or len(nm) > 64:
            v.add(
                "frontmatter.name.invalid",
                "error",
                f"`name: {nm!r}` 不合规：仅小写字母/数字/连字符，最多 64 字符",
            )

    if "model" in fm and isinstance(fm["model"], str):
        check_model_value(fm["model"], v)

    if "effort" in fm and fm["effort"] not in VALID_EFFORT:
        v.add("frontmatter.effort.invalid", "error",
              f"`effort: {fm['effort']}` 不在 {sorted(VALID_EFFORT)}")

    if "context" in fm and fm["context"] not in VALID_CONTEXT:
        v.add("frontmatter.context.invalid", "error",
              f"`context: {fm['context']}` 仅支持 `fork`")

    if "shell" in fm and fm["shell"] not in VALID_SHELL:
        v.add("frontmatter.shell.invalid", "error",
              f"`shell: {fm['shell']}` 仅支持 `bash` 或 `powershell`")

    # description 长度软检查
    desc = fm.get("description")
    if isinstance(desc, str):
        if len(desc.strip()) < 20:
            v.add("description.too-short", "warn",
                  f"description 仅 {len(desc.strip())} 字符，过短不利于触发；建议加触发关键词")
        if len(desc) > 1536:
            v.add("description.too-long", "warn",
                  f"description {len(desc)} 字符超 1536 上限，会被截断")

    # 行数提示（progressive disclosure）
    total_lines = body.count("\n") + 1
    if total_lines > 500:
        v.add("body.too-long", "warn",
              f"SKILL.md 正文 {total_lines} 行 > 500，建议把详细资料拆到 references/")

    # 资源引用实存性：只查 markdown link [text](path) 形式，避免误伤示例文本
    skill_dir = path.parent
    seen: "set[str]" = set()
    for m in re.finditer(r"\]\((references/[A-Za-z0-9_\-./]+\.md|scripts/[A-Za-z0-9_\-./]+)\)", body):
        rel = m.group(1)
        if rel in seen:
            continue
        seen.add(rel)
        if not (skill_dir / rel).exists():
            v.add(
                "resource.missing",
                "warn",
                f"markdown link 引用了 `{rel}` 但文件不存在",
            )


def lint_slash_command(path: Path, fm: "dict | None", body: str, v: Violations) -> None:
    # 文件名 kebab-case
    check_filename_kebab(path, v)

    if fm is None:
        # 兼容：纯 markdown 也允许
        v.add(
            "frontmatter.missing",
            "warn",
            "无 frontmatter（兼容运行，但建议至少加 description 让 Claude 知道何时调用）",
        )
        return
    if "_yaml_error" in fm:
        v.add("frontmatter.yaml.parse", "error", str(fm["_yaml_error"]))
        return

    SUBAGENT_ONLY = {"tools", "disallowedTools", "permissionMode", "mcpServers",
                     "maxTurns", "memory", "background", "isolation", "color",
                     "initialPrompt", "skills"}
    unknown = [k for k in fm if k not in SLASH_COMMAND_ALLOWED_FIELDS and not k.startswith("_")]
    for k in unknown:
        if k in SUBAGENT_ONLY:
            v.add(
                "frontmatter.field.misplaced",
                "error",
                f"字段 `{k}` 是 subagent 字段，slash command / skill 不支持",
            )
        else:
            v.add(
                "frontmatter.field.custom",
                "warn",
                f"字段 `{k}` 不在官方 slash command 字段集，Claude Code 会忽略（自定义元数据可保留）",
            )

    # 引导迁移
    v.add(
        "deprecation.suggest-migrate",
        "info" if False else "warn",
        ".claude/commands/ 已合并到 skills；建议迁移到 .claude/skills/<name>/SKILL.md 获得 supporting files 能力",
    )


def lint_subagent(path: Path, fm: "dict | None", body: str, v: Violations) -> None:
    check_filename_kebab(path, v)

    if fm is None:
        v.add("frontmatter.missing", "error",
              "subagent 文件必须有 YAML frontmatter（name + description 必填）")
        return
    if "_yaml_error" in fm:
        v.add("frontmatter.yaml.parse", "error", str(fm["_yaml_error"]))
        return

    # 必填
    for req in SUBAGENT_REQUIRED_FIELDS:
        if req not in fm:
            v.add(
                "frontmatter.field.missing",
                "error",
                f"subagent 必填字段缺失：`{req}`",
            )

    # 字段集
    SKILL_ONLY = {"allowed-tools", "when_to_use", "argument-hint", "arguments",
                  "disable-model-invocation", "user-invocable", "context", "agent",
                  "paths", "shell"}
    unknown = [k for k in fm if k not in SUBAGENT_ALLOWED_FIELDS and not k.startswith("_")]
    for k in unknown:
        if k in SKILL_ONLY:
            hint_map = {
                "allowed-tools": "subagent 用 `tools` 不是 `allowed-tools`",
                "when_to_use": "`when_to_use` 是 skill 字段，subagent 把信息写进 `description`",
                "argument-hint": "`argument-hint` 是 skill 字段",
                "context": "`context: fork` 是 skill 字段",
            }
            hint = hint_map.get(k, f"`{k}` 是 skill 字段，subagent 不支持")
            v.add(
                "frontmatter.field.misplaced",
                "error",
                f"字段 `{k}` 应该在 skill，不在 subagent：{hint}",
            )
        else:
            v.add(
                "frontmatter.field.custom",
                "warn",
                f"字段 `{k}` 不在官方 subagent 字段集，Claude Code 会忽略（自定义元数据可保留）",
            )

    # name 校验
    nm = fm.get("name")
    if isinstance(nm, str) and (not KEBAB_RE.match(nm) or len(nm) > 64):
        v.add(
            "frontmatter.name.invalid",
            "error",
            f"`name: {nm!r}` 不合规：仅小写字母/数字/连字符，最多 64 字符",
        )

    # 取值校验
    if "model" in fm and isinstance(fm["model"], str):
        check_model_value(fm["model"], v)

    if "effort" in fm and fm["effort"] not in VALID_EFFORT:
        v.add("frontmatter.effort.invalid", "error",
              f"`effort: {fm['effort']}` 不在 {sorted(VALID_EFFORT)}")

    if "permissionMode" in fm and fm["permissionMode"] not in VALID_PERMISSION_MODES:
        v.add(
            "frontmatter.permissionMode.invalid",
            "error",
            f"`permissionMode: {fm['permissionMode']}` 不在 {sorted(VALID_PERMISSION_MODES)}",
        )

    if "color" in fm and fm["color"] not in VALID_COLORS:
        v.add("frontmatter.color.invalid", "error",
              f"`color: {fm['color']}` 不在 {sorted(VALID_COLORS)}")

    if "memory" in fm and fm["memory"] not in VALID_MEMORY_SCOPES:
        v.add("frontmatter.memory.invalid", "error",
              f"`memory: {fm['memory']}` 不在 {sorted(VALID_MEMORY_SCOPES)}")

    if "isolation" in fm and fm["isolation"] not in VALID_ISOLATION:
        v.add("frontmatter.isolation.invalid", "error",
              f"`isolation: {fm['isolation']}` 仅支持 `worktree`")

    if "background" in fm and not isinstance(fm["background"], bool):
        v.add("frontmatter.background.invalid", "error",
              "`background` 必须为布尔值 true/false")

    # body 是 system prompt，空 body 没意义
    if not body.strip():
        v.add("body.empty", "warn", "subagent body 为空；body 是 system prompt，建议至少写角色和工作流程")


def lint_claude_md(path: Path, fm: "dict | None", body: str, v: Violations) -> None:
    # CLAUDE.md 本身无 frontmatter；但 .claude/rules/*.md 可以有 paths
    is_rule = "/rules/" in path.as_posix() or "\\rules\\" in str(path)

    if fm is not None and not is_rule:
        v.add(
            "frontmatter.unexpected",
            "warn",
            "CLAUDE.md 不应有 YAML frontmatter（仅 .claude/rules/*.md 可有 `paths`）",
        )

    if is_rule and fm is not None and "paths" in fm:
        paths_val = fm["paths"]
        if not isinstance(paths_val, list) or not all(isinstance(p, str) for p in paths_val):
            v.add("frontmatter.paths.invalid", "error",
                  "`.claude/rules/*.md` 的 `paths` 应为字符串数组")

    # 大小
    line_count = body.count("\n") + 1
    if line_count > 500:
        v.add("body.too-long", "warn",
              f"{path.name} {line_count} 行 > 500，强烈建议拆 .claude/rules/")
    elif line_count > 200 and not is_rule:
        v.add("body.large", "warn",
              f"{path.name} {line_count} 行 > 200，建议拆 .claude/rules/ 或用 paths 限定范围")

    # @path import 实存性（仅相对 / `~/` / 绝对路径）
    for m in re.finditer(r"@([A-Za-z0-9_\-./~][A-Za-z0-9_\-./~]+)", body):
        raw = m.group(1)
        # 排除 email、@-mention 这些常见非 import
        if raw.startswith("agent-") or ".com" in raw or "@" in raw:
            continue
        # 解析路径
        if raw.startswith("~/"):
            target = Path(os.path.expanduser(raw))
        elif raw.startswith("/"):
            target = Path(raw)
        else:
            target = path.parent / raw
        if not target.exists():
            v.add(
                "import.target.missing",
                "warn",
                f"`@{raw}` import 目标不存在",
            )


# ---------- 入口 ----------


LINTER = {
    "skill": lint_skill,
    "slash-command": lint_slash_command,
    "subagent": lint_subagent,
    "claude-md": lint_claude_md,
}


def main(argv: "list[str]") -> int:
    p = argparse.ArgumentParser(
        description="Lint Claude Code 扩展文件（slash-command / skill / subagent / CLAUDE.md）",
    )
    p.add_argument("--target", required=True, help="要检查的文件路径")
    p.add_argument(
        "--type",
        choices=sorted(LINTER.keys()),
        help="文件类型；不传则按路径推断",
    )
    p.add_argument("--format", choices=["json", "table"], default="json")
    args = p.parse_args(argv)

    target = Path(args.target).resolve()
    if not target.exists():
        fail(f"目标不存在: {target}")
    if target.is_dir():
        fail(f"目标是目录，请指定具体文件: {target}")

    typ = args.type or detect_type(target)
    if typ is None:
        fail(
            f"无法从路径推断类型，请显式 --type: {target}\n"
            f"提示：.claude/commands/*.md=slash-command，.claude/agents/*.md=subagent，"
            f"<dir>/SKILL.md=skill，CLAUDE.md/.claude/rules/*.md=claude-md"
        )

    text = read_text(target)
    v = Violations()

    check_utf8_bom(text, v)
    fm, _, body = split_frontmatter(text)
    LINTER[typ](target, fm, body, v)

    report = {
        "target": str(target),
        "type": typ,
        "violations": v.items,
        "passed": not v.has_error,
    }

    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"# {target}  ({typ})")
        if not v.items:
            print("  ✅ no violations")
        for it in v.items:
            line = f" line {it['line']}" if "line" in it else ""
            print(f"  [{it['severity']}] {it['rule']}{line}: {it['message']}")
        print(f"  passed = {report['passed']}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
