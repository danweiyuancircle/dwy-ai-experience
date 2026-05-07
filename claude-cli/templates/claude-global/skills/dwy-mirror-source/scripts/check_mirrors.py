#!/usr/bin/env python3
"""
检查 13 类工具的镜像源配置：pip / uv / poetry / npm / pnpm / yarn /
docker / go / cargo / maven / gradle / homebrew / flutter

用法：
    python3 check_mirrors.py [选项]

选项：
    --scope {user,project,both}   扫描范围，默认 both
    --project-path PATH           项目根目录，默认 cwd
    --provider {aliyun,tsinghua,ustc}  推荐源，默认读 preference.json，再回退 aliyun
    --only TOOL                   只检查指定工具（可多次或用逗号）
    --verbose                     输出更多调试信息
    --json                        输出 JSON 格式（脚本间集成用）

退出码：
    0  全部已加速或仅 not_installed
    1  存在 warn / missing / deprecated / private（人工干预）
    2  脚本本身出错
"""

import argparse
import json
import os
import re
import shutil
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

try:
    import tomllib
except ImportError:
    print("错误：本脚本需要 Python 3.11+（标准库 tomllib）", file=sys.stderr)
    sys.exit(2)


# ============================================================
# 镜像源 URL 表（与 references/mirror-providers.md 对应）
# ============================================================

MIRRORS = {
    "aliyun": {
        "pip": "https://mirrors.aliyun.com/pypi/simple/",
        "uv": "https://mirrors.aliyun.com/pypi/simple/",
        "poetry": "https://mirrors.aliyun.com/pypi/simple/",
        "npm": "https://registry.npmmirror.com",
        "docker": ["https://docker.m.daocloud.io", "https://docker.mirrors.ustc.edu.cn"],
        "go": "https://goproxy.cn,direct",
        "cargo_url": "sparse+https://rsproxy.cn/index/",
        "cargo_replace_with": "rsproxy-sparse",
        "maven": "https://maven.aliyun.com/repository/public",
        "gradle_plugin": "https://maven.aliyun.com/repository/gradle-plugin",
        "homebrew_brew": "https://mirrors.aliyun.com/homebrew/brew.git",
        "homebrew_core": "https://mirrors.aliyun.com/homebrew/homebrew-core.git",
        "homebrew_bottles": "https://mirrors.aliyun.com/homebrew/homebrew-bottles",
        "flutter_pub": "https://pub.flutter-io.cn",
        "flutter_storage": "https://storage.flutter-io.cn",
    },
    "tsinghua": {
        "pip": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "uv": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "poetry": "https://pypi.tuna.tsinghua.edu.cn/simple",
        "npm": "https://registry.npmmirror.com",
        "docker": ["https://docker.m.daocloud.io"],
        "go": "https://goproxy.cn,direct",
        "cargo_url": "sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/",
        "cargo_replace_with": "tuna-sparse",
        "maven": "https://maven.aliyun.com/repository/public",
        "gradle_plugin": "https://maven.aliyun.com/repository/gradle-plugin",
        "homebrew_brew": "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/brew.git",
        "homebrew_core": "https://mirrors.tuna.tsinghua.edu.cn/git/homebrew/homebrew-core.git",
        "homebrew_bottles": "https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles",
        "flutter_pub": "https://pub.flutter-io.cn",
        "flutter_storage": "https://storage.flutter-io.cn",
    },
    "ustc": {
        "pip": "https://mirrors.ustc.edu.cn/pypi/simple/",
        "uv": "https://mirrors.ustc.edu.cn/pypi/simple/",
        "poetry": "https://mirrors.ustc.edu.cn/pypi/simple/",
        "npm": "https://registry.npmmirror.com",
        "docker": ["https://docker.m.daocloud.io"],
        "go": "https://goproxy.cn,direct",
        "cargo_url": "sparse+https://mirrors.ustc.edu.cn/crates.io-index/",
        "cargo_replace_with": "ustc-sparse",
        "maven": "https://maven.aliyun.com/repository/public",
        "gradle_plugin": "https://maven.aliyun.com/repository/gradle-plugin",
        "homebrew_brew": "https://mirrors.ustc.edu.cn/brew.git",
        "homebrew_core": "https://mirrors.ustc.edu.cn/homebrew-core.git",
        "homebrew_bottles": "https://mirrors.ustc.edu.cn/homebrew-bottles",
        "flutter_pub": "https://pub.flutter-io.cn",
        "flutter_storage": "https://storage.flutter-io.cn",
    },
}

# 已知国内加速源（任一匹配即视为 ok）
KNOWN_GOOD = {
    "pip": [
        r"mirrors\.aliyun\.com/pypi",
        r"pypi\.tuna\.tsinghua\.edu\.cn",
        r"mirrors\.ustc\.edu\.cn/pypi",
        r"pypi\.douban\.com",
        r"mirrors\.cloud\.tencent\.com/pypi",
        r"mirrors\.huaweicloud\.com/repository/pypi",
        r"mirrors\.bfsu\.edu\.cn/pypi",
    ],
    "npm": [
        r"registry\.npmmirror\.com",
        r"mirrors\.cloud\.tencent\.com/npm",
        r"mirrors\.huaweicloud\.com/repository/npm",
    ],
    "docker": [
        r"daocloud\.io",
        r"docker\.mirrors\.ustc\.edu\.cn",
        r"hub-mirror\.c\.163\.com",
        r"mirror\.aliyuncs\.com",
        r"mirror\.ccs\.tencentyun\.com",
        r"mirror\.baidubce\.com",
    ],
    "go": [
        r"goproxy\.cn",
        r"goproxy\.io",
        r"mirrors\.aliyun\.com/goproxy",
        r"mirrors\.tencent\.com/go",
    ],
    "cargo": [
        r"rsproxy\.cn",
        r"mirrors\.tuna\.tsinghua\.edu\.cn/crates",
        r"mirrors\.ustc\.edu\.cn/crates",
    ],
    "maven": [
        r"maven\.aliyun\.com",
        r"mirrors\.huaweicloud\.com/repository/maven",
        r"mirrors\.cloud\.tencent\.com/nexus/repository/maven",
    ],
    "homebrew": [
        r"mirrors\.aliyun\.com/homebrew",
        r"mirrors\.tuna\.tsinghua\.edu\.cn/git/homebrew",
        r"mirrors\.tuna\.tsinghua\.edu\.cn/homebrew",
        r"mirrors\.ustc\.edu\.cn/(?:brew|homebrew)",
    ],
    "flutter": [
        r"flutter-io\.cn",
        r"mirrors\.cloud\.tencent\.com/flutter",
    ],
}

# 默认（境外）源 / 视为 warn
DEFAULT_REMOTE = {
    "pip": [r"pypi\.org/simple", r"files\.pythonhosted\.org"],
    "npm": [r"registry\.npmjs\.org"],
    "docker": [r"registry\.docker\.io", r"registry-1\.docker\.io"],
    "go": [r"proxy\.golang\.org", r"^direct$", r"^off$"],
    "cargo": [r"crates\.io"],
    "maven": [r"repo\.maven\.apache\.org", r"repo1\.maven\.org", r"repo\.maven\.org"],
    "homebrew": [r"github\.com/Homebrew", r"homebrew\.bintray\.com", r"ghcr\.io/homebrew"],
    "flutter": [r"pub\.dev", r"storage\.googleapis\.com/flutter_infra"],
}

# 已弃用源（必须替换）
DEPRECATED = {
    "npm": [r"registry\.npm\.taobao\.org", r"registry\.cnpmjs\.org", r"npm\.taobao\.org"],
    "pip": [r"^http://"],  # 任何 http pip 源都不安全
}

# 私服识别正则（不修改）
PRIVATE_PATTERNS = [
    r"nexus",
    r"artifactory",
    r"harbor",
    r"\.internal\b",
    r"\.corp\b",
    r"\.local\b",
    r"\bcompany\b",
    r":8081\b",
    r":8082\b",
    r":5000\b",
    r"^https?://\d+\.\d+\.\d+\.\d+",
]
# 公共加速器白名单（含 /repository/、/nexus 等路径但不是私服）
PUBLIC_MIRROR_DOMAINS = [
    r"\.aliyun\.com",
    r"\.tsinghua\.edu\.cn",
    r"\.ustc\.edu\.cn",
    r"\.bfsu\.edu\.cn",
    r"\.huaweicloud\.com",
    r"\.tencent(?:yun)?\.com",
    r"\.tencentyun\.com",
    r"\.npmmirror\.com",
    r"\.flutter-io\.cn",
    r"goproxy\.cn",
    r"goproxy\.io",
    r"rsproxy\.cn",
    r"daocloud\.io",
]


# ============================================================
# 数据类
# ============================================================

@dataclass
class CheckResult:
    tool: str
    scope: str  # "user" / "project"
    config_path: str
    status: str  # ok / warn / private / missing / no_config / not_installed / deprecated / error
    current_value: str = ""
    recommended: str = ""
    note: str = ""


# ============================================================
# 通用工具函数
# ============================================================

def is_private_registry(url: str) -> bool:
    if not url:
        return False
    # 先排除公共加速器（即使路径里有 /repository/、/nexus 等关键字也不算私服）
    if any(re.search(p, url, re.IGNORECASE) for p in PUBLIC_MIRROR_DOMAINS):
        return False
    return any(re.search(p, url, re.IGNORECASE) for p in PRIVATE_PATTERNS)


def classify_url(tool: str, url: str) -> str:
    url = (url or "").strip()
    if not url:
        return "no_config"
    if is_private_registry(url):
        return "private"
    for pat in DEPRECATED.get(tool, []):
        if re.search(pat, url, re.IGNORECASE):
            return "deprecated"
    for pat in KNOWN_GOOD.get(tool, []):
        if re.search(pat, url, re.IGNORECASE):
            return "ok"
    for pat in DEFAULT_REMOTE.get(tool, []):
        if re.search(pat, url, re.IGNORECASE):
            return "warn"
    # 未识别 - 可能是新公共源或未知私服，保守标记 warn
    return "warn"


def is_installed(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def home() -> Path:
    return Path.home()


def is_macos() -> bool:
    return sys.platform == "darwin"


def is_linux() -> bool:
    return sys.platform.startswith("linux")


def read_text_safe(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def parse_npmrc(content: str) -> dict[str, str]:
    """.npmrc 是 key=value 格式，不带 section header。"""
    out = {}
    for line in content.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(";"):
            continue
        if "=" in line:
            k, _, v = line.partition("=")
            out[k.strip().lower()] = v.strip().strip('"').strip("'")
    return out


# ============================================================
# 各工具检查函数
# ============================================================

def check_pip(provider: str, _project: Path) -> list[CheckResult]:
    if not (is_installed("pip") or is_installed("pip3")):
        return [CheckResult("pip", "user", "-", "not_installed")]

    candidates = []
    if is_macos():
        candidates.append(home() / "Library/Application Support/pip/pip.conf")
    candidates.extend([
        home() / ".config/pip/pip.conf",
        home() / ".pip/pip.conf",
    ])

    recommended = MIRRORS[provider]["pip"]
    config_path = next((p for p in candidates if p.exists()), None)
    if not config_path:
        return [CheckResult("pip", "user", str(candidates[0]), "missing",
                            "", recommended, note="pip.conf 不存在，pip 默认走 pypi.org")]

    content = read_text_safe(config_path)
    m = re.search(r"^\s*index[-_]url\s*=\s*(.+)$", content, re.MULTILINE | re.IGNORECASE)
    current = m.group(1).strip() if m else ""
    status = classify_url("pip", current)
    return [CheckResult("pip", "user", str(config_path), status, current, recommended)]


def check_uv(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("uv"):
        return [CheckResult("uv", "user", "-", "not_installed")]

    results: list[CheckResult] = []
    recommended = MIRRORS[provider]["uv"]

    # 用户级 uv.toml
    user_uv = home() / ".config/uv/uv.toml"
    if is_macos():
        # uv 在 macOS 也用 ~/.config/uv/ 作为默认配置目录
        pass

    if user_uv.exists():
        try:
            with user_uv.open("rb") as f:
                data = tomllib.load(f)
            indexes = data.get("index", []) or []
            urls = [i.get("url", "") for i in indexes if isinstance(i, dict)]
            current = urls[0] if urls else ""
            status = classify_url("pip", current)
            results.append(CheckResult("uv", "user", str(user_uv), status, current, recommended))
        except (tomllib.TOMLDecodeError, OSError) as e:
            results.append(CheckResult("uv", "user", str(user_uv), "error", "", recommended,
                                       note=f"解析失败: {e}"))
    else:
        results.append(CheckResult("uv", "user", str(user_uv), "missing",
                                   "", recommended, note="uv.toml 不存在"))

    # 项目级 pyproject.toml 中的 [[tool.uv.index]]
    pyproject = project / "pyproject.toml"
    if pyproject.exists():
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            indexes = data.get("tool", {}).get("uv", {}).get("index", []) or []
            if indexes:
                urls = [i.get("url", "") for i in indexes if isinstance(i, dict)]
                current = urls[0] if urls else ""
                status = classify_url("pip", current)
                results.append(CheckResult("uv", "project", str(pyproject), status, current, recommended))
            else:
                results.append(CheckResult("uv", "project", str(pyproject), "no_config",
                                           "", recommended,
                                           note="pyproject.toml 未声明 [[tool.uv.index]]"))
        except tomllib.TOMLDecodeError as e:
            results.append(CheckResult("uv", "project", str(pyproject), "error", "", recommended,
                                       note=f"解析失败: {e}"))

    return results


def check_poetry(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("poetry"):
        return [CheckResult("poetry", "user", "-", "not_installed")]

    results: list[CheckResult] = []
    recommended = MIRRORS[provider]["poetry"]

    # 项目级 pyproject.toml 中的 [[tool.poetry.source]]
    pyproject = project / "pyproject.toml"
    if pyproject.exists():
        try:
            with pyproject.open("rb") as f:
                data = tomllib.load(f)
            sources = data.get("tool", {}).get("poetry", {}).get("source", []) or []
            if sources:
                urls = [s.get("url", "") for s in sources if isinstance(s, dict)]
                current = urls[0] if urls else ""
                status = classify_url("pip", current)
                results.append(CheckResult("poetry", "project", str(pyproject), status, current, recommended))
            else:
                results.append(CheckResult("poetry", "project", str(pyproject), "no_config",
                                           "", recommended,
                                           note="未声明 [[tool.poetry.source]]"))
        except tomllib.TOMLDecodeError as e:
            results.append(CheckResult("poetry", "project", str(pyproject), "error",
                                       "", recommended, note=f"解析失败: {e}"))

    return results


def _check_npmrc(tool: str, provider: str, project: Path) -> list[CheckResult]:
    results: list[CheckResult] = []
    recommended = MIRRORS[provider]["npm"]

    user_npmrc = home() / ".npmrc"
    if user_npmrc.exists():
        cfg = parse_npmrc(read_text_safe(user_npmrc))
        current = cfg.get("registry", "")
        status = classify_url("npm", current)
        results.append(CheckResult(tool, "user", str(user_npmrc), status, current, recommended))
    else:
        results.append(CheckResult(tool, "user", str(user_npmrc), "missing",
                                   "", recommended,
                                   note=f"~/.npmrc 不存在，{tool} 默认走 npmjs.org"))

    proj_npmrc = project / ".npmrc"
    if proj_npmrc.exists():
        cfg = parse_npmrc(read_text_safe(proj_npmrc))
        current = cfg.get("registry", "")
        status = classify_url("npm", current) if current else "no_config"
        note = "项目级 .npmrc 未设置 registry" if not current else ""
        results.append(CheckResult(tool, "project", str(proj_npmrc), status, current, recommended, note=note))

    return results


def check_npm(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("npm"):
        return [CheckResult("npm", "user", "-", "not_installed")]
    return _check_npmrc("npm", provider, project)


def check_pnpm(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("pnpm"):
        return [CheckResult("pnpm", "user", "-", "not_installed")]
    # pnpm 共用 .npmrc，只有 user 级与 npm 重复，避免重复输出
    # 但项目级 .npmrc 是同一个文件，pnpm 也读它 - 不用再加一次
    return [CheckResult("pnpm", "user", str(home() / ".npmrc"),
                        "ok" if (home() / ".npmrc").exists() else "missing",
                        "", MIRRORS[provider]["npm"],
                        note="pnpm 与 npm 共用 ~/.npmrc，详见上方 npm 检查结果")]


def check_yarn(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("yarn"):
        return [CheckResult("yarn", "user", "-", "not_installed")]

    results: list[CheckResult] = []
    recommended = MIRRORS[provider]["npm"]

    # yarn 1: ~/.yarnrc 用 registry "..." 格式
    yarnrc_v1 = home() / ".yarnrc"
    yarnrc_v2 = home() / ".yarnrc.yml"

    if yarnrc_v2.exists():
        content = read_text_safe(yarnrc_v2)
        m = re.search(r"^\s*npmRegistryServer:\s*[\"']?([^\"'\s]+)", content, re.MULTILINE)
        current = m.group(1) if m else ""
        status = classify_url("npm", current)
        results.append(CheckResult("yarn", "user", str(yarnrc_v2), status, current, recommended))
    elif yarnrc_v1.exists():
        content = read_text_safe(yarnrc_v1)
        m = re.search(r"^\s*registry\s+[\"']?([^\"'\s]+)", content, re.MULTILINE)
        current = m.group(1) if m else ""
        status = classify_url("npm", current)
        results.append(CheckResult("yarn", "user", str(yarnrc_v1), status, current, recommended))
    else:
        # 走 .npmrc
        npmrc = home() / ".npmrc"
        if npmrc.exists():
            cfg = parse_npmrc(read_text_safe(npmrc))
            current = cfg.get("registry", "")
            status = classify_url("npm", current)
            results.append(CheckResult("yarn", "user", str(npmrc), status, current, recommended,
                                       note="yarn 回退到 ~/.npmrc"))
        else:
            results.append(CheckResult("yarn", "user", str(yarnrc_v1), "missing",
                                       "", recommended, note="yarn 无任何配置"))

    return results


def check_docker(provider: str, _project: Path) -> list[CheckResult]:
    if not is_installed("docker"):
        return [CheckResult("docker", "user", "-", "not_installed")]

    recommended = ", ".join(MIRRORS[provider]["docker"])

    candidates = []
    if is_macos():
        candidates.append(home() / ".docker/daemon.json")
    elif is_linux():
        candidates.extend([
            Path("/etc/docker/daemon.json"),
            home() / ".docker/daemon.json",
        ])
    else:
        candidates.append(home() / ".docker/daemon.json")

    config_path = next((p for p in candidates if p.exists()), None)
    if not config_path:
        return [CheckResult("docker", "user", str(candidates[0]), "missing",
                            "", recommended,
                            note="daemon.json 不存在，需创建或在 Docker Desktop GUI 设置 registry-mirrors")]

    try:
        data = json.loads(read_text_safe(config_path) or "{}")
    except json.JSONDecodeError as e:
        return [CheckResult("docker", "user", str(config_path), "error", "", recommended,
                            note=f"daemon.json 解析失败: {e}")]

    mirrors = data.get("registry-mirrors", []) or []
    if not mirrors:
        return [CheckResult("docker", "user", str(config_path), "no_config", "", recommended,
                            note="daemon.json 缺少 registry-mirrors 字段")]

    # 任一镜像匹配国内加速器即 ok
    statuses = [classify_url("docker", url) for url in mirrors]
    if any(s == "ok" for s in statuses):
        status = "ok"
    elif "private" in statuses:
        status = "private"
    elif "warn" in statuses or "deprecated" in statuses:
        status = "warn"
    else:
        status = "warn"
    return [CheckResult("docker", "user", str(config_path), status,
                        ", ".join(mirrors), recommended)]


def check_go(provider: str, _project: Path) -> list[CheckResult]:
    if not is_installed("go"):
        return [CheckResult("go", "user", "-", "not_installed")]

    recommended = MIRRORS[provider]["go"]

    # 通过 go env 查实际生效的 GOPROXY
    import subprocess
    try:
        result = subprocess.run(
            ["go", "env", "GOPROXY"],
            capture_output=True, text=True, timeout=10, check=True,
        )
        current = result.stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return [CheckResult("go", "user", "go env", "error", "", recommended,
                            note=f"go env 调用失败: {e}")]

    # go env 文件路径
    if is_macos():
        env_file = home() / "Library/Application Support/go/env"
    else:
        env_file = home() / ".config/go/env"

    status = classify_url("go", current)
    return [CheckResult("go", "user", str(env_file), status, current, recommended)]


def check_cargo(provider: str, project: Path) -> list[CheckResult]:
    if not is_installed("cargo"):
        return [CheckResult("cargo", "user", "-", "not_installed")]

    results: list[CheckResult] = []
    recommended = MIRRORS[provider]["cargo_url"]

    # 用户级
    user_cfg = home() / ".cargo/config.toml"
    user_cfg_old = home() / ".cargo/config"  # 旧名
    actual = user_cfg if user_cfg.exists() else user_cfg_old if user_cfg_old.exists() else None

    if actual:
        try:
            with actual.open("rb") as f:
                data = tomllib.load(f)
            crates_io = data.get("source", {}).get("crates-io", {})
            replace_with = crates_io.get("replace-with", "")
            url = ""
            if replace_with:
                url = data.get("source", {}).get(replace_with, {}).get("registry", "")
            current = url or ("default" if not replace_with else f"replace-with={replace_with} 但未定义")
            status = classify_url("cargo", url) if url else "no_config"
            results.append(CheckResult("cargo", "user", str(actual), status, current, recommended))
        except tomllib.TOMLDecodeError as e:
            results.append(CheckResult("cargo", "user", str(actual), "error", "", recommended,
                                       note=f"解析失败: {e}"))
    else:
        results.append(CheckResult("cargo", "user", str(user_cfg), "missing",
                                   "", recommended, note="~/.cargo/config.toml 不存在"))

    # 项目级
    proj_cfg = project / ".cargo/config.toml"
    if proj_cfg.exists():
        try:
            with proj_cfg.open("rb") as f:
                data = tomllib.load(f)
            crates_io = data.get("source", {}).get("crates-io", {})
            replace_with = crates_io.get("replace-with", "")
            url = ""
            if replace_with:
                url = data.get("source", {}).get(replace_with, {}).get("registry", "")
            current = url or "default"
            status = classify_url("cargo", url) if url else "no_config"
            results.append(CheckResult("cargo", "project", str(proj_cfg), status, current, recommended))
        except tomllib.TOMLDecodeError as e:
            results.append(CheckResult("cargo", "project", str(proj_cfg), "error", "", recommended,
                                       note=f"解析失败: {e}"))

    return results


def check_maven(provider: str, _project: Path) -> list[CheckResult]:
    if not (is_installed("mvn") or (home() / ".m2").exists()):
        return [CheckResult("maven", "user", "-", "not_installed")]

    recommended = MIRRORS[provider]["maven"]
    settings = home() / ".m2/settings.xml"

    if not settings.exists():
        return [CheckResult("maven", "user", str(settings), "missing",
                            "", recommended, note="~/.m2/settings.xml 不存在")]

    content = read_text_safe(settings)
    # 简单正则提取 <mirror><url>...</url>
    urls = re.findall(r"<mirror>.*?<url>\s*([^<\s]+)\s*</url>", content, re.DOTALL | re.IGNORECASE)
    if not urls:
        return [CheckResult("maven", "user", str(settings), "no_config", "", recommended,
                            note="settings.xml 未配置 <mirror>")]

    current = urls[0]
    status = classify_url("maven", current)
    return [CheckResult("maven", "user", str(settings), status, current, recommended)]


def check_gradle(provider: str, _project: Path) -> list[CheckResult]:
    has_gradle = is_installed("gradle") or (home() / ".gradle").exists()
    if not has_gradle:
        return [CheckResult("gradle", "user", "-", "not_installed")]

    recommended = MIRRORS[provider]["maven"]

    candidates = [
        home() / ".gradle/init.gradle.kts",
        home() / ".gradle/init.gradle",
        home() / ".gradle/init.d/init.gradle.kts",
        home() / ".gradle/init.d/init.gradle",
    ]
    init_file = next((p for p in candidates if p.exists()), None)
    if not init_file:
        return [CheckResult("gradle", "user", str(candidates[0]), "missing",
                            "", recommended, note="未找到 init.gradle(.kts)")]

    content = read_text_safe(init_file)
    # 找 maven { url ... } 中第一个 url
    m = re.search(r"maven\s*\{\s*url\s*[=]?\s*[\"'(]?([^\"')\s]+)", content)
    current = m.group(1) if m else ""
    status = classify_url("maven", current) if current else "no_config"
    return [CheckResult("gradle", "user", str(init_file), status, current, recommended)]


def check_homebrew(provider: str, _project: Path) -> list[CheckResult]:
    if not is_installed("brew"):
        return [CheckResult("homebrew", "user", "-", "not_installed")]

    import subprocess

    recommended = MIRRORS[provider]["homebrew_brew"]

    # 查 brew.git 远程
    try:
        repo = subprocess.run(["brew", "--repo"], capture_output=True, text=True,
                              timeout=10, check=True).stdout.strip()
        remote = subprocess.run(["git", "-C", repo, "remote", "get-url", "origin"],
                                capture_output=True, text=True, timeout=10, check=True).stdout.strip()
    except (subprocess.SubprocessError, FileNotFoundError) as e:
        return [CheckResult("homebrew", "user", "brew --repo", "error", "", recommended,
                            note=f"读取 brew git remote 失败: {e}")]

    status = classify_url("homebrew", remote)
    return [CheckResult("homebrew", "user", repo, status, remote, recommended,
                        note="还需检查 HOMEBREW_BOTTLE_DOMAIN 环境变量")]


def check_flutter(provider: str, _project: Path) -> list[CheckResult]:
    if not is_installed("flutter"):
        return [CheckResult("flutter", "user", "-", "not_installed")]

    recommended = MIRRORS[provider]["flutter_pub"]
    pub_url = os.environ.get("PUB_HOSTED_URL", "")
    storage_url = os.environ.get("FLUTTER_STORAGE_BASE_URL", "")

    # 同时检查 shell rc
    shell_rcs = [home() / ".zshrc", home() / ".bashrc", home() / ".profile"]
    rc_with_config = None
    for rc in shell_rcs:
        if rc.exists() and re.search(r"PUB_HOSTED_URL", read_text_safe(rc)):
            rc_with_config = rc
            break

    if pub_url:
        status = classify_url("flutter", pub_url)
        return [CheckResult("flutter", "user", str(rc_with_config or "env"), status,
                            pub_url, recommended,
                            note=f"FLUTTER_STORAGE_BASE_URL={storage_url or '未设置'}")]

    if rc_with_config:
        return [CheckResult("flutter", "user", str(rc_with_config), "warn",
                            "未在当前 shell 生效", recommended,
                            note="rc 文件里有配置但当前 shell 未 source")]

    return [CheckResult("flutter", "user", str(home() / ".zshrc"), "missing",
                        "", recommended, note="未配置 PUB_HOSTED_URL")]


# ============================================================
# 主流程
# ============================================================

ALL_CHECKS = [
    ("pip", check_pip),
    ("uv", check_uv),
    ("poetry", check_poetry),
    ("npm", check_npm),
    ("pnpm", check_pnpm),
    ("yarn", check_yarn),
    ("docker", check_docker),
    ("go", check_go),
    ("cargo", check_cargo),
    ("maven", check_maven),
    ("gradle", check_gradle),
    ("homebrew", check_homebrew),
    ("flutter", check_flutter),
]


STATUS_ICON = {
    "ok": "✅ ok",
    "warn": "⚠️  warn",
    "private": "🏢 private",
    "missing": "❌ missing",
    "no_config": "➖ no_config",
    "not_installed": "—  not_installed",
    "deprecated": "🛑 deprecated",
    "error": "💥 error",
}


def load_preference() -> str:
    p = Path.home() / ".claude/skills/dwy-mirror-source/preference.json"
    if p.exists():
        try:
            return json.loads(p.read_text()).get("preferred_provider", "aliyun")
        except (json.JSONDecodeError, OSError):
            pass
    return "aliyun"


def render_text(results: list[CheckResult]) -> tuple[str, dict]:
    by_status = {"ok": 0, "warn": 0, "private": 0, "missing": 0,
                 "no_config": 0, "not_installed": 0, "deprecated": 0, "error": 0}
    lines = ["=" * 60, "镜像源检查报告", "=" * 60, ""]
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1
        scope_label = f"({r.scope})"
        line = f"  {r.tool:10s}{scope_label:11s}{STATUS_ICON.get(r.status, r.status):16s}"
        if r.status == "not_installed":
            lines.append(line + "  跳过")
            continue
        if r.current_value:
            line += f"当前: {r.current_value[:50]}"
        elif r.note:
            line += r.note[:60]
        lines.append(line)
        if r.note and r.current_value and r.status not in ("ok", "not_installed"):
            lines.append(f"             备注: {r.note}")
    lines.append("")
    lines.append("-" * 60)
    need_fix = by_status["warn"] + by_status["missing"] + by_status["deprecated"] + by_status["no_config"]
    skipped = by_status["private"]
    lines.append(f"汇总: 共 {len(results)} 项 / 需修复 {need_fix} 项 / 私服跳过 {skipped} 项 / 未安装 {by_status['not_installed']} 项")
    if need_fix:
        lines.append("")
        lines.append("下一步：让 Claude 帮你修复，或运行")
        lines.append("  python3 apply_mirrors.py --dry-run")
    return "\n".join(lines), by_status


def main():
    parser = argparse.ArgumentParser(description="检查镜像源配置")
    parser.add_argument("--scope", choices=["user", "project", "both"], default="both")
    parser.add_argument("--project-path", default=".", type=Path)
    parser.add_argument("--provider", choices=["aliyun", "tsinghua", "ustc"], default=None)
    parser.add_argument("--only", action="append", default=[],
                        help="只检查指定工具，可多次或逗号分隔")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()

    provider = args.provider or load_preference()
    project_path = args.project_path.resolve()

    # 解析 --only
    only: list[str] = []
    for item in args.only:
        only.extend([s.strip() for s in item.split(",") if s.strip()])

    results: list[CheckResult] = []
    for tool_name, fn in ALL_CHECKS:
        if only and tool_name not in only:
            continue
        try:
            tool_results = fn(provider, project_path)
        except Exception as e:
            tool_results = [CheckResult(tool_name, "user", "-", "error",
                                        "", "", note=f"check 异常: {e}")]
        # 按 scope 过滤
        if args.scope != "both":
            tool_results = [r for r in tool_results if r.scope == args.scope or r.status == "not_installed"]
        results.extend(tool_results)

    if args.as_json:
        print(json.dumps({"provider": provider,
                          "results": [asdict(r) for r in results]},
                         ensure_ascii=False, indent=2))
    else:
        text, by_status = render_text(results)
        print(text)

    # 退出码：有 warn / missing / deprecated → 1；error → 2；否则 0
    has_error = any(r.status == "error" for r in results)
    has_fix = any(r.status in ("warn", "missing", "deprecated", "no_config") for r in results)
    if has_error:
        sys.exit(2)
    if has_fix:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
