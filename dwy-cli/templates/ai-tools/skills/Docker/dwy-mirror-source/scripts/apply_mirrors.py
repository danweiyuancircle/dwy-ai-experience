#!/usr/bin/env python3
"""
应用镜像源加速到本地配置文件。

强制原则：
  1. 默认 --dry-run，只输出 diff，必须显式去掉才会落盘
  2. 检测到企业私服时跳过，不覆盖
  3. 不重启 Docker daemon / 不 source rc，仅给提示

用法：
    python3 apply_mirrors.py [选项]

选项：
    --tools T1,T2,...      逗号分隔的工具列表（默认全部）
    --scope {user,project,both}  默认 user（项目级请显式指定）
    --provider {aliyun,tsinghua,ustc}  推荐源，默认读 preference.json
    --project-path PATH    默认 cwd
    --dry-run              只输出 diff，不写文件（默认开启，必须 --apply 才落盘）
    --apply                显式确认落盘（与 --dry-run 互斥）
    --backup               写文件前备份原文件为 .bak.<timestamp>
"""

import argparse
import datetime
import difflib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("错误：需要 Python 3.11+", file=sys.stderr)
    sys.exit(2)

# 复用 check 脚本里的常量
sys.path.insert(0, str(Path(__file__).parent))
from check_mirrors import (  # noqa: E402
    MIRRORS, KNOWN_GOOD, PRIVATE_PATTERNS, PUBLIC_MIRROR_DOMAINS,
    is_private_registry, classify_url, is_installed, home, is_macos,
    read_text_safe, parse_npmrc, load_preference,
)


# ============================================================
# 数据结构
# ============================================================

@dataclass
class Change:
    tool: str
    scope: str          # user / project
    config_path: str
    action: str         # create / modify / skip
    old_content: str = ""
    new_content: str = ""
    note: str = ""
    is_json: bool = False  # JSON 类配置文件需要保留缩进格式


# ============================================================
# 工具函数
# ============================================================

def make_diff(old: str, new: str, path: str) -> str:
    if old == new:
        return ""
    diff = difflib.unified_diff(
        old.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile=f"a/{path}",
        tofile=f"b/{path}",
        n=3,
    )
    return "".join(diff)


def write_with_backup(path: Path, content: str, backup: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    if backup and path.exists():
        ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = path.with_suffix(path.suffix + f".bak.{ts}")
        shutil.copy2(path, backup_path)
    path.write_text(content, encoding="utf-8")


def replace_or_add_ini_line(content: str, key: str, value: str, section: str | None = None) -> str:
    """
    在 INI 风格内容中替换或添加 key=value。

    section 为 None 时表示无 section（如 .npmrc）。
    存在则替换，不存在则在 section 末尾或文件末尾追加。
    """
    pattern = rf"^(\s*){re.escape(key)}\s*=.*$"
    new_line = f"{key} = {value}"
    if re.search(pattern, content, re.MULTILINE | re.IGNORECASE):
        return re.sub(pattern, new_line, content, count=1, flags=re.MULTILINE | re.IGNORECASE)

    if section:
        section_pat = rf"^\[{re.escape(section)}\]\s*$"
        if re.search(section_pat, content, re.MULTILINE | re.IGNORECASE):
            # 在 section 下追加
            lines = content.splitlines()
            out = []
            in_section = False
            inserted = False
            for line in lines:
                out.append(line)
                if not inserted:
                    if re.match(section_pat, line, re.IGNORECASE):
                        in_section = True
                        out.append(new_line)
                        inserted = True
            return "\n".join(out) + ("\n" if not content.endswith("\n") else "")
        # 没有 section，添加 section + line
        prefix = "\n" if content and not content.endswith("\n") else ""
        return content + f"{prefix}[{section}]\n{new_line}\n"

    # 无 section
    prefix = "\n" if content and not content.endswith("\n") else ""
    return content + f"{prefix}{new_line}\n"


# ============================================================
# 各工具的 apply 函数（返回 Change 列表）
# ============================================================

def apply_pip(provider: str, _project: Path) -> list[Change]:
    if not (is_installed("pip") or is_installed("pip3")):
        return []

    target = MIRRORS[provider]["pip"]
    host = re.sub(r"^https?://", "", target).split("/")[0]

    # 候选路径，优先选已存在的
    candidates = []
    if is_macos():
        candidates.append(home() / "Library/Application Support/pip/pip.conf")
    candidates.extend([
        home() / ".config/pip/pip.conf",
        home() / ".pip/pip.conf",
    ])
    path = next((p for p in candidates if p.exists()), candidates[0])
    old = read_text_safe(path) if path.exists() else ""

    m = re.search(r"^\s*index[-_]url\s*=\s*(.+)$", old, re.MULTILINE | re.IGNORECASE)
    current = m.group(1).strip() if m else ""
    if is_private_registry(current):
        return [Change("pip", "user", str(path), "skip", note="检测到私服，跳过")]
    if classify_url("pip", current) == "ok":
        return []

    new = replace_or_add_ini_line(old, "index-url", target, section="global")
    new = replace_or_add_ini_line(new, "trusted-host", host, section="install")
    if old == new:
        return []
    return [Change("pip", "user", str(path),
                   "create" if not old else "modify", old, new)]


def apply_uv(provider: str, project: Path) -> list[Change]:
    if not is_installed("uv"):
        return []

    changes: list[Change] = []
    target_index = MIRRORS[provider]["uv"]
    target_python = MIRRORS[provider]["uv_python_install"]
    user_uv = home() / ".config/uv/uv.toml"

    old = read_text_safe(user_uv) if user_uv.exists() else ""

    # 解析现有内容
    existing_index = ""
    existing_python_mirror = ""
    if old:
        try:
            data = tomllib.loads(old)
            indexes = data.get("index", []) or []
            urls = [i.get("url", "") for i in indexes if isinstance(i, dict)]
            existing_index = urls[0] if urls else ""
            existing_python_mirror = data.get("python-install-mirror", "")
        except tomllib.TOMLDecodeError:
            return [Change("uv", "user", str(user_uv), "skip",
                           note="uv.toml 解析失败，请手动修复")]

    # 私服跳过
    if existing_index and is_private_registry(existing_index):
        return [Change("uv", "user", str(user_uv), "skip", note="PyPI 索引是私服，跳过")]

    # 计算新内容：python-install-mirror 总是放最前，再放 [[index]]
    need_index = classify_url("pip", existing_index) != "ok"
    need_python = "npmmirror.com" not in existing_python_mirror

    if not need_index and not need_python:
        return []

    # 重新生成整个 uv.toml（用结构化方式更可靠）
    new_lines = []
    new_lines.append(f'python-install-mirror = "{target_python}"')
    new_lines.append("")
    new_lines.append("[[index]]")
    new_lines.append(f'url = "{target_index}"')
    new_lines.append("default = true")
    new_content = "\n".join(new_lines) + "\n"

    # 保留原 uv.toml 中其他字段（如 cache-dir、resolution 等）
    if old:
        try:
            data = tomllib.loads(old)
            preserved = {k: v for k, v in data.items()
                         if k not in ("python-install-mirror", "index")}
            if preserved:
                # 简单序列化保留字段（仅基础类型，复杂结构保持原样附加）
                extra_lines = []
                for k, v in preserved.items():
                    if isinstance(v, str):
                        extra_lines.append(f'{k} = "{v}"')
                    elif isinstance(v, bool):
                        extra_lines.append(f'{k} = {"true" if v else "false"}')
                    elif isinstance(v, (int, float)):
                        extra_lines.append(f"{k} = {v}")
                    # 其他复杂类型（dict/list）跳过，提示用户手动迁移
                if extra_lines:
                    new_content = "\n".join(extra_lines) + "\n\n" + new_content
        except tomllib.TOMLDecodeError:
            pass

    if old == new_content:
        return []
    note = "包含两套源：PyPI 包索引 + Python 解释器下载（python-install-mirror）"
    changes.append(Change("uv", "user", str(user_uv),
                          "create" if not old else "modify", old, new_content, note=note))

    # 项目级 pyproject.toml — 不自动改
    pyproject = project / "pyproject.toml"
    if pyproject.exists():
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            indexes = data.get("tool", {}).get("uv", {}).get("index", []) or []
            urls = [i.get("url", "") for i in indexes if isinstance(i, dict)]
            if not indexes:
                changes.append(Change("uv", "project", str(pyproject), "skip",
                                      note="pyproject.toml 由项目维护，不自动改。建议手动添加 [[tool.uv.index]]"))
            elif urls and is_private_registry(urls[0]):
                changes.append(Change("uv", "project", str(pyproject), "skip",
                                      note="项目使用私服，跳过"))
        except tomllib.TOMLDecodeError:
            pass

    return changes


def apply_npm(provider: str, project: Path, scope: str) -> list[Change]:
    if not is_installed("npm"):
        return []

    target = MIRRORS[provider]["npm"]
    changes: list[Change] = []

    paths = []
    if scope in ("user", "both"):
        paths.append((home() / ".npmrc", "user"))
    if scope in ("project", "both"):
        proj = project / ".npmrc"
        if proj.exists() or scope == "project":
            paths.append((proj, "project"))

    for path, scp in paths:
        old = read_text_safe(path) if path.exists() else ""
        cfg = parse_npmrc(old)
        existing = cfg.get("registry", "")
        if existing and is_private_registry(existing):
            changes.append(Change("npm", scp, str(path), "skip", note="私服跳过"))
            continue
        if classify_url("npm", existing) == "ok":
            continue
        new = replace_or_add_ini_line(old, "registry", target)
        if old == new:
            continue
        changes.append(Change("npm", scp, str(path),
                              "create" if not old else "modify", old, new))
    return changes


def apply_pnpm(provider: str, project: Path, scope: str) -> list[Change]:
    # pnpm 共用 .npmrc，不重复修改，但需告知
    if is_installed("pnpm"):
        return [Change("pnpm", "user", str(home() / ".npmrc"), "skip",
                       note="pnpm 与 npm 共用 .npmrc，已被 npm 修改覆盖")]
    return []


def apply_yarn(provider: str, _project: Path, _scope: str) -> list[Change]:
    if not is_installed("yarn"):
        return []
    target = MIRRORS[provider]["npm"]
    yarnrc_v2 = home() / ".yarnrc.yml"
    yarnrc_v1 = home() / ".yarnrc"

    if yarnrc_v2.exists():
        old = read_text_safe(yarnrc_v2)
        if re.search(r"^\s*npmRegistryServer:", old, re.MULTILINE):
            new = re.sub(r"^\s*npmRegistryServer:.*$",
                         f'npmRegistryServer: "{target}"',
                         old, count=1, flags=re.MULTILINE)
        else:
            new = old.rstrip() + f'\nnpmRegistryServer: "{target}"\n'
        if old != new:
            return [Change("yarn", "user", str(yarnrc_v2), "modify", old, new)]
    elif yarnrc_v1.exists():
        old = read_text_safe(yarnrc_v1)
        if re.search(r"^\s*registry\s+", old, re.MULTILINE):
            new = re.sub(r"^\s*registry\s+.*$",
                         f'registry "{target}"',
                         old, count=1, flags=re.MULTILINE)
        else:
            new = old.rstrip() + f'\nregistry "{target}"\n'
        if old != new:
            return [Change("yarn", "user", str(yarnrc_v1), "modify", old, new)]
    else:
        # 默认创建 v2 格式
        new = f'npmRegistryServer: "{target}"\n'
        return [Change("yarn", "user", str(yarnrc_v2), "create", "", new)]
    return []


def apply_docker(provider: str, _project: Path) -> list[Change]:
    if not is_installed("docker"):
        return []

    mirrors = MIRRORS[provider]["docker"]
    if is_macos():
        path = home() / ".docker/daemon.json"
    else:
        path = Path("/etc/docker/daemon.json")
        if not path.exists() and not os.access(str(path.parent), os.W_OK):
            # Linux 上无写权限退到用户级
            path = home() / ".docker/daemon.json"

    old = read_text_safe(path) if path.exists() else ""
    try:
        data = json.loads(old) if old else {}
    except json.JSONDecodeError:
        return [Change("docker", "user", str(path), "skip", note="daemon.json 解析失败，请手动修复")]

    existing = data.get("registry-mirrors", []) or []
    if any(is_private_registry(u) for u in existing):
        return [Change("docker", "user", str(path), "skip", note="存在私服镜像，跳过")]

    # 合并：去重，保留 existing 中 known good 的
    merged = []
    for u in mirrors + existing:
        if u not in merged:
            merged.append(u)

    if data.get("registry-mirrors") == merged:
        return []

    data["registry-mirrors"] = merged
    new = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    note = "改完后请手动重启 Docker（macOS: 退出 Docker Desktop 重开；Linux: sudo systemctl restart docker）"
    return [Change("docker", "user", str(path),
                   "create" if not old else "modify", old, new, note=note, is_json=True)]


def apply_go(provider: str, _project: Path) -> list[Change]:
    if not is_installed("go"):
        return []
    target = MIRRORS[provider]["go"]
    if is_macos():
        env_file = home() / "Library/Application Support/go/env"
    else:
        env_file = home() / ".config/go/env"
    old = read_text_safe(env_file) if env_file.exists() else ""

    if re.search(r"^GOPROXY=.*", old, re.MULTILINE):
        new = re.sub(r"^GOPROXY=.*", f"GOPROXY={target}", old, count=1, flags=re.MULTILINE)
    else:
        new = old.rstrip() + ("\n" if old else "") + f"GOPROXY={target}\n"

    if old == new:
        return []
    note = "可改用 go env -w GOPROXY=... 命令同等效果"
    return [Change("go", "user", str(env_file),
                   "create" if not old else "modify", old, new, note=note)]


def apply_cargo(provider: str, _project: Path) -> list[Change]:
    if not is_installed("cargo"):
        return []
    name = MIRRORS[provider]["cargo_replace_with"]
    url = MIRRORS[provider]["cargo_url"]
    path = home() / ".cargo/config.toml"
    old = read_text_safe(path) if path.exists() else ""

    block = (
        f'[source.crates-io]\n'
        f'replace-with = "{name}"\n\n'
        f'[source.{name}]\n'
        f'registry = "{url}"\n'
    )

    if old:
        # 已有 [source.crates-io] 段就替换 replace-with 行；否则追加
        if re.search(r"\[source\.crates-io\]", old):
            new = re.sub(r"replace-with\s*=\s*\".*?\"",
                         f'replace-with = "{name}"', old, count=1)
            # 确保对应 source 块存在，如果没有就追加
            if not re.search(rf"\[source\.{re.escape(name)}\]", new):
                new = new.rstrip() + f'\n\n[source.{name}]\nregistry = "{url}"\n'
        else:
            new = old.rstrip() + "\n\n" + block
    else:
        new = block

    if old == new:
        return []
    return [Change("cargo", "user", str(path),
                   "create" if not old else "modify", old, new)]


def apply_maven(provider: str, _project: Path) -> list[Change]:
    if not (is_installed("mvn") or (home() / ".m2").exists()):
        return []
    target = MIRRORS[provider]["maven"]
    path = home() / ".m2/settings.xml"
    old = read_text_safe(path) if path.exists() else ""

    mirror_block = f"""    <mirror>
      <id>aliyun</id>
      <name>aliyun maven</name>
      <mirrorOf>*,!internal</mirrorOf>
      <url>{target}</url>
    </mirror>"""

    if not old.strip():
        new = f"""<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0 http://maven.apache.org/xsd/settings-1.0.0.xsd">
  <mirrors>
{mirror_block}
  </mirrors>
</settings>
"""
        return [Change("maven", "user", str(path), "create", "", new)]

    # 已有内容：检查是否已配
    if re.search(r"<mirror>.*?<url>\s*" + re.escape(target),
                 old, re.DOTALL | re.IGNORECASE):
        return []
    if re.search(r"<mirrors>", old, re.IGNORECASE):
        new = re.sub(r"(<mirrors>)", r"\1\n" + mirror_block, old, count=1, flags=re.IGNORECASE)
    else:
        # 在 </settings> 前插入
        new = re.sub(r"(</settings>)",
                     f"  <mirrors>\n{mirror_block}\n  </mirrors>\n\\1",
                     old, count=1, flags=re.IGNORECASE)
    return [Change("maven", "user", str(path), "modify", old, new)]


def apply_gradle(provider: str, _project: Path) -> list[Change]:
    has_gradle = is_installed("gradle") or (home() / ".gradle").exists()
    if not has_gradle:
        return []
    target_main = MIRRORS[provider]["maven"]
    target_plugin = MIRRORS[provider]["gradle_plugin"]
    path = home() / ".gradle/init.gradle.kts"
    old = read_text_safe(path) if path.exists() else ""

    new_content = f'''// Gradle 全局镜像源（由 dwy-mirror-source 生成）
allprojects {{
    repositories {{
        maven {{ url = uri("{target_main}") }}
        mavenCentral()
    }}
}}

settingsEvaluated {{
    pluginManagement {{
        repositories {{
            maven {{ url = uri("{target_plugin}") }}
            gradlePluginPortal()
        }}
    }}
}}
'''
    if old == new_content:
        return []
    return [Change("gradle", "user", str(path),
                   "create" if not old else "modify", old, new_content)]


def apply_homebrew(provider: str, _project: Path) -> list[Change]:
    if not is_installed("brew"):
        return []

    brew_url = MIRRORS[provider]["homebrew_brew"]
    core_url = MIRRORS[provider]["homebrew_core"]
    bottles_url = MIRRORS[provider]["homebrew_bottles"]

    # Homebrew 不通过单一文件配置，而是通过 git remote + 环境变量。
    # 这里输出操作指令而不是 diff，让用户手动执行（涉及多个仓库 git 操作）。
    note = (
        "Homebrew 镜像配置需多步手动执行：\n"
        f"  1. brew_repo=$(brew --repo)\n"
        f"  2. git -C \"$brew_repo\" remote set-url origin {brew_url}\n"
        f"  3. core=\"$brew_repo/Library/Taps/homebrew/homebrew-core\"\n"
        f"  4. [ -d \"$core\" ] && git -C \"$core\" remote set-url origin {core_url}\n"
        f"  5. 在 ~/.zshrc 添加: export HOMEBREW_BOTTLE_DOMAIN={bottles_url}\n"
        f"  6. brew update\n"
        "本 skill 不直接 git remote set-url，避免覆盖你的 brew tap 配置。"
    )
    return [Change("homebrew", "user", "brew --repo + ~/.zshrc", "skip", note=note)]


def apply_flutter(provider: str, _project: Path) -> list[Change]:
    if not is_installed("flutter"):
        return []
    pub_url = MIRRORS[provider]["flutter_pub"]
    storage_url = MIRRORS[provider]["flutter_storage"]

    # 选 zsh 优先，然后 bash
    zshrc = home() / ".zshrc"
    bashrc = home() / ".bashrc"
    target_rc = zshrc if zshrc.exists() else bashrc
    if not target_rc.exists():
        target_rc = zshrc  # 创建 .zshrc

    old = read_text_safe(target_rc) if target_rc.exists() else ""

    # 移除已有的 PUB_HOSTED_URL / FLUTTER_STORAGE_BASE_URL 行
    new = re.sub(r"^export\s+PUB_HOSTED_URL=.*$", "", old, flags=re.MULTILINE)
    new = re.sub(r"^export\s+FLUTTER_STORAGE_BASE_URL=.*$", "", new, flags=re.MULTILINE)
    new = new.rstrip() + (
        "\n\n# Flutter 国内镜像（由 dwy-mirror-source 添加）\n"
        f"export PUB_HOSTED_URL={pub_url}\n"
        f"export FLUTTER_STORAGE_BASE_URL={storage_url}\n"
    )
    if old == new:
        return []
    note = f"修改后需 source {target_rc} 或重开终端生效"
    return [Change("flutter", "user", str(target_rc),
                   "create" if not old else "modify", old, new, note=note)]


# ============================================================
# 主流程
# ============================================================

ALL_APPLIES = [
    ("pip", apply_pip),
    ("uv", apply_uv),
    ("npm", apply_npm),
    ("pnpm", apply_pnpm),
    ("yarn", apply_yarn),
    ("docker", apply_docker),
    ("go", apply_go),
    ("cargo", apply_cargo),
    ("maven", apply_maven),
    ("gradle", apply_gradle),
    ("homebrew", apply_homebrew),
    ("flutter", apply_flutter),
]


def main():
    parser = argparse.ArgumentParser(description="应用国内镜像源加速")
    parser.add_argument("--tools", default="",
                        help="逗号分隔的工具列表，默认全部")
    parser.add_argument("--scope", choices=["user", "project", "both"], default="user")
    parser.add_argument("--provider", choices=["aliyun", "tsinghua", "ustc"], default=None)
    parser.add_argument("--project-path", type=Path, default=Path("."))
    parser.add_argument("--apply", action="store_true",
                        help="实际写入（默认只 dry-run 输出 diff）")
    parser.add_argument("--backup", action="store_true",
                        help="写文件前备份原文件")
    parser.add_argument("--dry-run", action="store_true",
                        help="（默认行为）只输出 diff，不落盘")
    args = parser.parse_args()

    provider = args.provider or load_preference()
    project = args.project_path.resolve()
    only = [t.strip() for t in args.tools.split(",") if t.strip()] if args.tools else []

    # 默认 dry-run，必须 --apply 才落盘
    dry_run = not args.apply

    all_changes: list[Change] = []
    for name, fn in ALL_APPLIES:
        if only and name not in only:
            continue
        try:
            sig = fn.__code__.co_varnames[: fn.__code__.co_argcount]
            if "scope" in sig:
                changes = fn(provider, project, args.scope)
            else:
                changes = fn(provider, project)
        except Exception as e:
            changes = [Change(name, "user", "-", "skip", note=f"apply 异常: {e}")]
        all_changes.extend(changes)

    if not all_changes:
        print("✅ 所有工具已加速或无需修改")
        return

    print("=" * 60)
    print(f"修复计划（provider={provider}, dry_run={dry_run}）")
    print("=" * 60)
    print()

    notes_after = []
    for c in all_changes:
        prefix = {
            "create": "📝 CREATE",
            "modify": "✏️  MODIFY",
            "skip": "⏭️  SKIP",
        }.get(c.action, c.action)
        print(f"--- {prefix}  [{c.tool}/{c.scope}]  {c.config_path}")
        if c.note:
            print(f"    备注: {c.note}")
        if c.action != "skip" and c.old_content != c.new_content:
            diff = make_diff(c.old_content, c.new_content, c.config_path)
            if diff:
                print(diff)
        print()
        if c.action != "skip" and c.note:
            notes_after.append(f"  • {c.tool}: {c.note}")

    if dry_run:
        print("=" * 60)
        print("以上为 dry-run 输出。确认无误后加 --apply 真正落盘。")
        print("=" * 60)
        return

    # 真正落盘
    print("=" * 60)
    print("开始写入...")
    print("=" * 60)
    for c in all_changes:
        if c.action == "skip":
            print(f"  ⏭️  {c.tool}: {c.note}")
            continue
        if c.old_content == c.new_content:
            continue
        try:
            write_with_backup(Path(c.config_path), c.new_content, args.backup)
            print(f"  ✅ {c.tool}: {c.config_path}")
        except OSError as e:
            print(f"  💥 {c.tool}: 写入失败 — {e}")

    if notes_after:
        print()
        print("⚠️  操作后续步骤：")
        for n in notes_after:
            print(n)


if __name__ == "__main__":
    main()
