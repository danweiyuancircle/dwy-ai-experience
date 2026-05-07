---
name: dwy-mirror-source
description: "国内镜像源加速配置检查与修复：扫描 pip/uv/poetry/npm/pnpm/yarn/Docker/Go/Cargo/Maven/Gradle/Homebrew/Flutter 等 13 类工具的用户级和项目级配置，识别使用境外默认源或缺失配置的项，提供阿里云/清华/中科大镜像源切换。触发条件：用户说'检查镜像源'、'配置加速'、'换镜像源'、'mirror 检查'、'安装慢'、'下载慢' 时。"
---

# 镜像源加速配置（mirror-source）

国内开发环境下，pip/npm/Docker 等工具默认境外源会让安装/拉取拖慢数倍甚至失败。本 skill 统一检查所有支持工具的镜像源配置，识别问题并辅助切换到国内加速源。

**脚本目录：** `~/.claude/skills/dwy-mirror-source/scripts/`（以下简称 `{scripts}`）

---

## 强制原则

1. **检查与修复分离** — 默认只检查输出报告，修复必须由用户**显式确认**。禁止自动改用户配置文件。
2. **先 diff 后落盘** — 任何配置文件修改前必须输出 diff 让用户审阅。
3. **保留私服配置** — 检测到企业内网私服（如 `nexus.company.com`、`pypi.internal`、`registry.company.com` 等非公网域名）时跳过修改，避免覆盖团队配置。
4. **不自动重启 Docker daemon** — 修改 `daemon.json` 后只**提示**用户重启，禁止自动跑 `systemctl restart docker` / 重启 Docker Desktop。
5. **不动 CI/CD 配置** — 本 skill 只处理本地开发环境，不修改 `.github/workflows/` / `.gitlab-ci.yml` 等。

---

## 默认首选镜像源

**阿里云**（覆盖最全，BGP 多线，全国质量稳定）。

可通过 `~/.claude/skills/dwy-mirror-source/preference.json` 修改：

```json
{
  "preferred_provider": "aliyun"
}
```

可选值：`aliyun` / `tsinghua` / `ustc`。详细 URL 表见 `references/mirror-providers.md`。

---

## 支持的工具范围

| 类别 | 工具 | 用户级配置 | 项目级配置 |
|------|------|-----------|-----------|
| **Python** | pip | `~/.config/pip/pip.conf` 或 macOS 的 `~/Library/Application Support/pip/pip.conf` | — |
| | uv（**双源**） | `~/.config/uv/uv.toml` 同时含 `[[index]]` + `python-install-mirror` | `pyproject.toml` 的 `[[tool.uv.index]]` |
| | poetry | `~/Library/Application Support/pypoetry/auth.toml` 等 | `pyproject.toml` 的 `[[tool.poetry.source]]` |
| **Node** | npm | `~/.npmrc` | `.npmrc` |
| | pnpm | `~/.npmrc`（共用） | `.npmrc` |
| | yarn | `~/.yarnrc.yml` 或 `~/.yarnrc` | 同名项目级文件 |
| **Docker（双层）** | daemon registry-mirrors（**仅对 docker.io 生效**） | `~/.docker/daemon.json`（macOS Docker Desktop）/ `/etc/docker/daemon.json`（Linux） | — |
| | gcr/ghcr/quay/k8s 等其他 registry 加速（必须改 image 引用） | 用户在 Dockerfile / k8s yaml 中直接换前缀 | 同左 |
| **Go** | GOPROXY | `~/.config/go/env` 或 `~/Library/Application Support/go/env` | — |
| **Rust** | cargo | `~/.cargo/config.toml` | `.cargo/config.toml` |
| **JVM** | Maven | `~/.m2/settings.xml` | — |
| | Gradle | `~/.gradle/init.gradle.kts` 或 `init.gradle` | — |
| **macOS** | Homebrew | `git -C $(brew --repo) remote` + `HOMEBREW_BOTTLE_DOMAIN` | — |
| **Flutter** | PUB_HOSTED_URL | `~/.zshrc` / `~/.bashrc` 环境变量 | — |

**Linux 包管理（apt/apk/yum/dnf）** 不在自动检查范围。它们一般出现在 Dockerfile 内，是代码而非用户配置。如需在 Dockerfile 中换源，参考 `references/dockerfile-snippets.md`。

---

## 工作流

### 模式 A：检查（check）

用户说「检查镜像源」时执行。

```bash
python3 {scripts}/check_mirrors.py [--scope user|project|both] [--project-path .]
```

**默认行为**：扫描用户级 + 当前项目，输出分级报告。

**状态分级：**

| 状态 | 含义 | 处理 |
|------|------|------|
| ✅ ok | 已用国内推荐源 | 无需操作 |
| ⚠️ warn | 用了官方默认源（境外） | 提示可切换 |
| ⚠️ private | 用了企业私服 | 跳过，不动 |
| ❌ missing | 工具已安装但无配置 | 提示创建 |
| ➖ not_installed | 工具未安装 | 跳过 |

输出示例：

```
=================== 镜像源检查报告 ===================
[Python]
  pip       (user)     ⚠️ warn      默认 PyPI    → 建议: aliyun
  uv        (user)     ✅ ok        aliyun
  uv        (project)  ➖ no_config  pyproject.toml 未声明 [[tool.uv.index]]

[Node]
  npm       (user)     ✅ ok        npmmirror.com
  pnpm      (project)  ⚠️ warn      默认 registry → 建议: aliyun

[Docker]
  daemon                ❌ missing   ~/.docker/daemon.json 不存在 registry-mirrors

...

汇总: 13 项检查 / 5 项需修复 / 2 项私服跳过

下一步: 让 Claude 帮你逐项修复，或运行
  python3 apply_mirrors.py --dry-run
```

### 模式 B：修复（apply）

用户确认后执行。**不允许在用户没看 diff 之前直接落盘**。

```bash
# 第一步：dry-run 输出 diff
python3 {scripts}/apply_mirrors.py --dry-run [--tools pip,npm,docker] [--scope user]

# 第二步：用户确认后落盘
python3 {scripts}/apply_mirrors.py [--tools pip,npm,docker] [--scope user]
```

**参数：**
- `--tools` — 逗号分隔的工具列表（`pip,uv,npm,pnpm,docker,go,cargo,maven,gradle,brew,flutter`），默认全部
- `--scope` — `user` / `project` / `both`，默认 `both`
- `--provider` — `aliyun` / `tsinghua` / `ustc`，默认读 preference.json
- `--dry-run` — 只输出 diff，不写文件
- `--project-path` — 项目级配置的根目录，默认当前目录

**修复行为：**
- 文件不存在 → 创建
- 文件存在但缺字段 → 追加（保留其他配置）
- 文件存在且字段已存在但是境外源 → 替换
- 检测到私服 → 跳过该项，输出 `[skipped: private registry]`

### 模式 C：诊断单个工具（debug）

```bash
python3 {scripts}/check_mirrors.py --only npm --verbose
```

输出该工具所有相关配置位置、当前值、解析结果，用于诊断「我配过了为什么还是慢」类问题。

---

## Claude 调用流程

用户说「检查镜像源」/「配置加速」时：

1. 跑 `check_mirrors.py` 输出报告
2. 把报告里 `warn` / `missing` 项列出来给用户看
3. 询问要修复哪些（默认全部 `warn` + `missing`，私服项不动）
4. 跑 `apply_mirrors.py --dry-run --tools <user-selected>` 输出 diff
5. 等用户确认 → 跑去掉 `--dry-run` 的版本写入
6. 修改了 Docker daemon.json → 提示用户**重启 Docker**，本 skill 不自动重启
7. 修改了 shell rc 文件（Flutter / Homebrew）→ 提示用户 `source ~/.zshrc` 或重开终端

**禁止行为：**
- ❌ 不询问就修改用户全局配置
- ❌ 不输出 diff 就 apply
- ❌ 自动跑 `systemctl restart docker` / `osascript -e 'quit app "Docker"'`
- ❌ 替换企业私服 URL

---

## uv 镜像源（多层）

uv 实际有 **3 个独立的镜像源**，缺一个都会拖慢：

| 层 | 配置项 | 作用 | 国内推荐源 |
|----|--------|------|-----------|
| 1. 包索引 | `[[index]]` 或 `UV_DEFAULT_INDEX` | 装 PyPI 包 | `https://mirrors.aliyun.com/pypi/simple/` |
| 2. **Python 解释器下载** ⭐ | `python-install-mirror` 或 `UV_PYTHON_INSTALL_MIRROR` | `uv python install 3.12` 时下载解释器 | `https://registry.npmmirror.com/-/binary/python-build-standalone` |
| 3. PyPy 解释器下载 | `pypy-install-mirror` 或 `UV_PYPY_INSTALL_MIRROR` | 下载 PyPy 解释器 | 国内**无可用镜像**，保留默认 |

**关键点：** 第 2 层（Python 解释器）默认走 `github.com/astral-sh/python-build-standalone/releases`，国内不挂代理几乎无法下载。这是 `uv venv --python 3.12` 卡住的常见原因。

完整 `~/.config/uv/uv.toml` 示例：

```toml
python-install-mirror = "https://registry.npmmirror.com/-/binary/python-build-standalone"

[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
default = true
```

`apply_mirrors.py --tools uv` 会同时写入这两层。第 3 层 PyPy 不强制配置（国内无源）。

---

## Docker 镜像源（多层）

Docker 镜像加速分**两类，互不替代**：

### 类型 1：docker.io 加速 — `registry-mirrors`

唯一作用于 `docker.io`（Docker Hub）。配置在 `~/.docker/daemon.json`：

```json
{
  "registry-mirrors": [
    "https://docker.m.daocloud.io",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

`apply_mirrors.py --tools docker` 自动配置这一层。

### 类型 2：gcr / ghcr / quay / k8s 等加速 — 改 image 引用

**`registry-mirrors` 字段对它们完全无效**。必须把 image 名改前缀域名：

| 源 registry | 镜像域名 | 用途 |
|-------------|---------|------|
| `gcr.io` | `gcr.m.daocloud.io` | Google Container Registry |
| `ghcr.io` | `ghcr.m.daocloud.io` | GitHub Container Registry |
| `quay.io` | `quay.m.daocloud.io` | Red Hat Quay |
| `registry.k8s.io` | `k8s.m.daocloud.io` | Kubernetes 当前官方 registry |
| `k8s.gcr.io` | `k8s-gcr.m.daocloud.io` | Kubernetes 旧仓库 |
| `mcr.microsoft.com` | `mcr.m.daocloud.io` | Microsoft Container Registry |
| `nvcr.io` | `nvcr.m.daocloud.io` | NVIDIA Container Registry |
| `docker.elastic.co` | `elastic.m.daocloud.io` | Elastic 官方镜像 |
| `registry.ollama.ai` | `ollama.m.daocloud.io` | Ollama 模型 |

完整列表见 `references/mirror-providers.md`。

**用法：**

```bash
# 原本（国内拉不动）
docker pull gcr.io/google-containers/pause:3.9
docker pull ghcr.io/astral-sh/uv:0.5.0

# 改前缀域名走加速
docker pull gcr.m.daocloud.io/google-containers/pause:3.9
docker pull ghcr.m.daocloud.io/astral-sh/uv:0.5.0
```

```dockerfile
# Dockerfile 同理
FROM ghcr.m.daocloud.io/astral-sh/uv:0.5.0 AS uv
FROM gcr.m.daocloud.io/distroless/python3:nonroot
```

**为什么不能自动配置？** 这层加速无法在 daemon.json 实现透明代理，必须显式改 image 字符串。Claude 在用户写 Dockerfile / k8s yaml 时，如发现使用了 gcr/ghcr/quay 等域名，**应主动提示**改前缀（可与 dwy-docker-image skill 协同：固定 tag 时一并替换 registry 域名）。

> 提示：containerd（不是 Docker）支持 `[plugins."io.containerd.grpc.v1.cri".registry.mirrors]` 全局映射；Kubernetes 节点用 containerd 时可写到 `/etc/containerd/config.toml` 实现透明代理。Docker 引擎本身不支持。

---

## 与其他 skill 的关系

- **dwy-docker-image**：固定镜像版本（FROM 指令的 tag）
- **本 skill**：配置 docker pull 时走哪个 registry mirror
- **dwy-deploy-audit**：检查生产服务器的镜像源配置

三者协作：本地用 dwy-mirror-source 配好镜像加速 → 写代码用 dwy-docker-image 固定 tag → 部署后用 dwy-deploy-audit 检查线上

---

## 违规检测速查

| 检测项 | 严重程度 | 说明 |
|--------|---------|------|
| Python pip 用 `pypi.org/simple` 默认源 | warn | 改 `mirrors.aliyun.com/pypi/simple/` |
| uv 缺 `python-install-mirror` | warn | `uv python install` 卡顿，添加 npmmirror 二进制源 |
| uv 用了不稳定 GitHub 代理（如 ghfast/gh-proxy） | warn | 改用更稳定的 npmmirror.com/-/binary |
| npm/pnpm 用 `registry.npmjs.org` | warn | 改 `registry.npmmirror.com` |
| Docker 无 `registry-mirrors` | warn | 添加 `docker.m.daocloud.io` |
| Dockerfile / k8s 用 `gcr.io/...`、`ghcr.io/...`、`registry.k8s.io/...` | warn | 改前缀为 `gcr.m.daocloud.io/...` 等（改 image 字符串） |
| Go 未设 GOPROXY 或为 `direct` | warn | 改 `https://goproxy.cn,direct` |
| Maven 默认 Central | warn | 添加 aliyun mirror |
| Cargo 默认 crates.io | warn | 改 `rsproxy.cn` |
| 用 npm registry 但没用 https | high | 安全问题，强制换 https |
| 镜像源 URL 已弃用（如 `npm.taobao.org`） | high | 已 EOL，必须迁移到 npmmirror.com |
