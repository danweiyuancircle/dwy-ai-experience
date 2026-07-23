---
name: dwy-deploy-first
description: >-
  通用「首次部署」检查清单 skill：按章节推进新服务/新镜像的国内可构建落地。
  当前已开放第 1 章「镜像源」——Dockerfile / 构建环境中的 apt（阿里云）与 uv/pip（阿里云 PyPI）；
  禁止写死具体业务项目名。触发：用户说「首次部署」「第一次上线」「部署第一步」「配置镜像源」
  「apt 换源」「uv 阿里云」「Docker 构建慢」「国内构建」；或用户执行 /dwy-deploy-first。
  与 dwy-mirror-source（本机用户级 13 类工具）互补：本 skill 聚焦「项目首次部署构建链路」。
---

# dwy-deploy-first — 首次部署（分章）

通用流程，**不绑定任何具体仓库或业务名**。按章节执行；用户未点名章节时，从**当前最低未完成章节**开始，完成后询问是否进入下一章。

**当前开放章节：** 仅第 1 章（镜像源）。后续章节（构建、健康检查、发布等）待补充，禁止臆造未写章节的强制步骤。

**关联 skill（按需读取，勿重复造轮）：**

| Skill | 边界 |
| --- | --- |
| `dwy-mirror-source` | 本机用户级 / 项目级 **开发机** 工具镜像源（pip/uv/npm/Docker daemon 等） |
| `dwy-docker` | Dockerfile / compose **工程规范**（禁 latest、healthcheck 等） |
| **本 skill** | **首次部署构建链路**里必须写进仓库的源配置（以 Dockerfile / CI 构建为主） |

**参考片段：** `references/chapter-01-mirrors.md`

---

## 总原则

1. **通用模板** — 示例用 `python:3.x-slim-bookworm` 等占位；路径/服务名从用户当前项目推断，不写死历史项目。
2. **默认阿里云** — 国内首次部署默认 `aliyun`；用户明确要求清华/中科大时再改。
3. **先检查后改** — 扫描现有 `Dockerfile` / `Dockerfile.*` / CI 构建脚本；已合规则静默通过，违规再改。
4. **与 dwy-docker 叠加** — 镜像 tag 仍须固定版本；本 skill 不替代版本规范。
5. **禁止** `curl https://astral.sh/uv/install.sh` 作为默认装 uv 方式（GitHub 二进制，国内慢/易失败）。

---

## 第 1 章：镜像源（首次部署强制）

### 目标

构建机 / Docker 镜像构建在国内可稳定完成：

1. **apt（Debian/Ubuntu 系）→ 阿里云**
2. **uv / pip → 阿里云 PyPI**

Alpine / RHEL 系见 `references/chapter-01-mirrors.md`；本章默认以 **Debian/Ubuntu 系官方 Python 基础镜像** 为主（最常见）。

### 1.1 检查清单

扫描用户打开或指定的 Dockerfile / 构建脚本：

| # | 检查项 | 合规 | 违规表现 |
|---|--------|------|----------|
| A1 | apt 使用国内源 | `mirrors.aliyun.com`（或团队约定的内网 apt 镜像） | 仍 `deb.debian.org` / `archive.ubuntu.com` / `security.debian.org` 且无替换 |
| A2 | 装 uv 不走 astral.sh 默认 GitHub | `pip install -i https://mirrors.aliyun.com/pypi/simple/ uv` 等 | `curl … astral.sh/uv/install.sh` |
| A3 | uv 索引 | `UV_INDEX_URL` / `UV_DEFAULT_INDEX` = 阿里云 simple | 未设且会访问 `pypi.org` |
| A4 | pip 索引 | `PIP_INDEX_URL` 或 `pip -i` = 阿里云 simple | 默认官方 PyPI 且无 `-i` |
| A5 | trusted-host | 与镜像 host 一致（`mirrors.aliyun.com`） | HTTPS 校验失败或反复警告未处理 |

**企业内网私服**（域名非公网 mirror）：保留私服，不覆盖为阿里云；记录「已使用私服，本章跳过公网镜像」。

### 1.2 默认 URL（阿里云）

```text
# Debian/Ubuntu apt
https://mirrors.aliyun.com/debian/
https://mirrors.aliyun.com/debian-security/   # 若用 security 源
https://mirrors.aliyun.com/ubuntu/

# PyPI（pip / uv）
https://mirrors.aliyun.com/pypi/simple/
trusted-host: mirrors.aliyun.com
```

### 1.3 落地动作（Dockerfile 模式）

按顺序改写（最小 diff；匹配用户现有基础镜像代号）：

#### A. apt → 阿里云

- **Debian 12 bookworm（deb822）**：改 `/etc/apt/sources.list.d/debian.sources`
- **Debian 11 / 旧 sources.list**：改 `/etc/apt/sources.list`
- **Ubuntu**：改 `sources.list` 或 `ubuntu.sources`

标准片段见 `references/chapter-01-mirrors.md` §apt。

`RUN` 中建议：`sed` 换源 → `apt-get update` → `install` → `rm -rf /var/lib/apt/lists/*`。

#### B. uv / pip → 阿里云

**推荐（安装 uv 本体）：**

```dockerfile
ENV UV_DEFAULT_INDEX=https://mirrors.aliyun.com/pypi/simple/ \
    UV_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ \
    PIP_TRUSTED_HOST=mirrors.aliyun.com

RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        "uv>=0.4"
```

**禁止默认：**

```dockerfile
# ❌ 国内易慢/失败
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
```

**安装项目依赖：**

```dockerfile
RUN uv pip install --system --no-cache .
# 或
RUN uv sync --frozen
# 环境变量已指向阿里云时无需再写 -i；若未设 ENV，则显式：
# RUN uv pip install --system --index-url https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
```

### 1.4 非 Docker 首次部署（本机/CI 脚本）

若用户不用 Docker、但在「首次部署」语境配置构建机：

| 工具 | 推荐落点 |
| --- | --- |
| pip | `PIP_INDEX_URL` 或 `pip.conf` global `index-url` |
| uv | `~/.config/uv/uv.toml` 的 `[[index]]`，或项目 `pyproject.toml` 的 `[[tool.uv.index]]` |
| apt | 构建脚本 / 镜像层内 sed；**不**强制改运维员个人笔记本（那是 `dwy-mirror-source`） |

详细用户级配置交给 `dwy-mirror-source`；本 skill 只保证**仓库内可复现的部署构建**写清源。

### 1.5 验收

执行（或指导用户执行）后，确认：

1. Dockerfile / 构建脚本中 **无** 未替换的官方 Debian/Ubuntu 默认源（私服除外）
2. **无** 默认 `astral.sh/uv/install.sh`（除非用户书面坚持并接受慢/失败风险）
3. `UV_*` / `PIP_*` 指向 `mirrors.aliyun.com`（或约定私服）
4. 能完整跑通一次构建（`docker build` 或 `uv sync` / `uv pip install`）且日志显示从阿里云域名拉取

输出简短验收表：

```text
第 1 章 镜像源
- [ ] apt 阿里云
- [ ] uv/pip 阿里云
- [ ] 禁止 astral.sh 默认装 uv
- [ ] 构建试跑通过
```

### 1.6 完成后

告知用户：第 1 章已完成。后续章节尚未写入本 skill，**不要自行扩展**未定义的「第 2 章」强制项；若用户继续「首次部署」，询问需求后再扩展 skill 章节。

---

## 反模式（本章）

| 反模式 | 正确做法 |
| --- | --- |
| 只改本机 `pip.conf`，Dockerfile 仍官方源 | 部署构建以 Dockerfile/CI 为准 |
| `astral.sh` 装 uv + 仅 pip 换源 | uv 本体也走 `pip -i 阿里云` |
| 写死某个业务仓库路径/服务名 | 用当前工作区真实路径 |
| 与 `dwy-mirror-source` 重复扫 13 类本机工具 | 部署构建场景只扫 apt/uv/pip 构建链 |

---

## 章节路线图（占位，未实现勿执行）

| 章 | 主题 | 状态 |
| --- | --- | --- |
| 1 | 镜像源（apt + uv/pip 阿里云） | **当前** |
| 2+ | （待定：构建、健康检查、发布等） | 未开放 |
