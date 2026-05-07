---
name: dwy-docker-image
description: "Docker 镜像版本固定规范：禁止使用 latest，必须固定到具体 tag，且优先选择「最新稳定版的上一个 minor」（N-1）。触发条件：编写或修改 Dockerfile / docker-compose.yml / Kubernetes manifests / GitHub Actions / GitLab CI 中的镜像引用时，或用户说'选 docker 镜像版本'、'docker 镜像规范'、'检查 docker 镜像'、'扫描 latest'、'固定镜像版本' 时。"
---

# Docker 镜像版本规范

固定 Docker 镜像版本是基础设施稳定性的底线。`latest` 会让 image 在不同时间、不同机器上拉到不同内容，导致「本地能跑，CI 挂；昨天能跑，今天炸」的灾难。**这条规则没有例外**。

**脚本目录：** `~/.claude/skills/dwy-docker-image/scripts/`（以下简称 `{scripts}`）

---

## 强制规则

1. **禁止 `latest`** — 任何位置（FROM / image / containers.image / services.image）都不允许使用 `latest`，也不允许省略 tag（省略 tag 等同于 `latest`）。
2. **必须固定 tag** — tag 必须是具体版本号（如 `17.1`、`1.26.2`、`3.20`），不允许使用浮动 tag（如 `17`、`stable`、`mainline`、`alpine`、`bookworm`）。浮动 tag 看起来固定，实际会随上游更新而漂移。
3. **优先选 N-1 minor** — 在 DockerHub 上找出当前最新的稳定 minor 版本，**选它前一个 minor 系列的最新 patch**。这能避开新版刚发布时未暴露的回归 bug。
4. **生产关键服务用 digest** — 数据库、消息队列、网关等丢一次数据就严重的服务，应该在 tag 后再钉 digest（`postgres:17.1@sha256:abc...`），让 image 100% 不可篡改。

---

## 「N-1 minor」具体怎么选

### semver 三段镜像（绝大多数）

格式 `MAJOR.MINOR.PATCH`，例如 `nginx:1.27.3`、`redis:7.4.1`。

选法：
1. 在 DockerHub 找当前最新稳定 minor（忽略 rc/beta/alpha/preview/nightly）
2. minor 减 1，得到目标 minor 系列
3. 取该 minor 系列的最新 patch

**例：**
| 镜像 | 当前最新稳定 | N-1 minor 选择 |
|------|-------------|---------------|
| `nginx` | `1.27.3` | `nginx:1.26.2`（1.26 系列最新 patch） |
| `redis` | `7.4.1` | `redis:7.2.6`（7.4 上一个稳定 minor 是 7.2，跳过仅维护版） |
| `node` | `22.11.0`（LTS）| `node:20.18.0`（上一个 LTS major 的最新版，LTS 镜像例外） |

### 两段版本号镜像

格式 `MAJOR.MINOR`，例如 `postgres:17.2`、`mysql:8.4`、`alpine:3.21`。这类镜像把 minor 当 patch 用。

选法：minor 减 1，取该系列最新 tag。

**例：**
| 镜像 | 当前最新稳定 | N-1 minor 选择 |
|------|-------------|---------------|
| `postgres` | `17.2` | `postgres:17.1` |
| `mysql` | `8.4` | `mysql:8.3` |
| `alpine` | `3.21` | `alpine:3.20` |

### 年份版本号镜像（Ubuntu / Debian codename）

格式 `YY.MM` 或 codename，例如 `ubuntu:24.04`、`debian:bookworm`。

选法：选**上一个 LTS / stable release**，**不要**用 codename（`bookworm`、`bullseye` 是浮动 tag），只用版本号。

**例：**
| 镜像 | 当前最新 LTS | N-1 选择 |
|------|-------------|---------|
| `ubuntu` | `24.04` | `ubuntu:22.04` |
| `debian` | `12`（bookworm）| `debian:11`（bullseye）|

### LTS 镜像例外（Node.js / OpenJDK）

LTS 镜像（如 Node.js 偶数 major 是 LTS）应该选**上一个 LTS major**的最新 patch，而不是机械地 minor - 1。原因是非 LTS 版本生命周期短，N-1 落到非 LTS 上反而不稳定。

---

## 工作流

### A. 写新配置（FROM / image 字段）

1. 用 `{scripts}/query_dockerhub.py <image>` 查 DockerHub 上的版本列表，脚本会自动给出推荐的 N-1 minor
2. 把推荐结果填入 Dockerfile / compose / k8s manifest
3. 如果脚本无法访问 DockerHub（私有仓库 / 网络不通），向用户列出可选方案：
   - 让用户手动确认版本号
   - 用 `docker pull <image>:<tag> && docker inspect ...` 在本地查
   - 用 WebFetch 查官方仓库的 release page

### B. 检查现有项目（扫描违规）

1. 运行 `{scripts}/scan_images.sh <project-path>`，扫描所有 Dockerfile / docker-compose / k8s yaml / CI 配置
2. 输出违规清单，按严重程度分级：
   - **critical**：使用 `latest` 或省略 tag
   - **high**：使用浮动 tag（`stable`、`mainline`、`alpine`、`bookworm` 等）
   - **medium**：使用了过新的版本（最新发布 < 30 天，未经过 N-1 验证）
   - **low**：仅 tag 没有 digest（生产关键服务建议补 digest）
3. 对每条违规，调用 `query_dockerhub.py` 给出推荐替换版本
4. 列出修复 diff 给用户确认，**不要**自动修改文件

### C. 升级现有镜像版本

1. 当前用的版本是 X.Y.Z，先确认 X.Y 是否还在 N-1 区间内
2. 如果 DockerHub 最新稳定已经从 (X.Y+1) 推进到 (X.Y+2)，说明可以升级到 (X.Y+1) 系列最新 patch
3. 升级前必须：
   - 查看 release notes / CHANGELOG，标记 BREAKING CHANGE
   - 在测试环境验证后再合入

---

## 查询脚本：query_dockerhub.py

```bash
python3 {scripts}/query_dockerhub.py <image> [--namespace library] [--top 20]
```

**参数：**
- `<image>` — 镜像名，如 `nginx`、`postgres`、`redis`。私有命名空间用 `org/image` 形式
- `--namespace` — DockerHub 命名空间，默认 `library`（官方镜像）
- `--top N` — 显示最近 N 个 tag，默认 20

**输出：**
- 最近的稳定 tag 列表（按时间倒序）
- 高亮当前最新稳定 minor
- **推荐使用的 N-1 minor 版本**（已剔除 rc / beta / alpha / preview / nightly / 浮动 tag）

**示例：**
```
$ python3 query_dockerhub.py nginx
最新稳定 minor: 1.27 (最新 patch: 1.27.3, 发布于 2024-11-26)
推荐 (N-1 minor): nginx:1.26.2

最近 20 个稳定 tag:
  1.27.3   2024-11-26
  1.27.2   2024-10-02
  1.26.2   2024-08-28  ← 推荐
  1.26.1   2024-05-29
  ...
```

---

## 扫描脚本：scan_images.sh

```bash
bash {scripts}/scan_images.sh [project-path]
```

扫描以下文件类型中的镜像引用：
- `Dockerfile`、`Dockerfile.*`、`*.Dockerfile`
- `docker-compose.yml`、`docker-compose.*.yml`、`compose.yml`
- `*.yaml`、`*.yml`（K8s manifests，匹配 `image:` 字段）
- `.github/workflows/*.yml`（GitHub Actions 中的 `container:` 和 `services:`）
- `.gitlab-ci.yml`（GitLab CI 中的 `image:` 和 `services:`）

输出格式：
```
[critical] frontend/Dockerfile:1
  FROM node:latest
  → 建议改为: node:20.18.0

[high] backend/docker-compose.yml:5
  image: postgres:alpine
  → 建议改为: postgres:17.1-alpine

[critical] k8s/deployment.yaml:23
  image: redis
  → 建议改为: redis:7.2.6
```

**只输出报告，不自动修改文件**。修改要等用户确认后由 Claude 用 Edit 工具逐项执行。

---

## 修复示例

### 反例 → 正例

**Dockerfile**:
```dockerfile
# ❌ 违规：latest
FROM node:latest

# ❌ 违规：省略 tag
FROM postgres

# ❌ 违规：浮动 tag
FROM nginx:alpine
FROM debian:bookworm
FROM redis:7

# ✅ 正确：固定到具体版本（N-1 minor）
FROM node:20.18.0
FROM postgres:17.1
FROM nginx:1.26.2-alpine
FROM debian:11
FROM redis:7.2.6

# ✅ 更严格：tag + digest（生产关键服务）
FROM postgres:17.1@sha256:abc123def456...
```

**docker-compose.yml**:
```yaml
# ❌ 违规
services:
  db:
    image: postgres
  cache:
    image: redis:latest
  web:
    image: nginx:stable

# ✅ 正确
services:
  db:
    image: postgres:17.1
  cache:
    image: redis:7.2.6
  web:
    image: nginx:1.26.2
```

**Kubernetes Deployment**:
```yaml
# ❌ 违规
spec:
  containers:
    - name: app
      image: myapp:latest
    - name: sidecar
      image: envoyproxy/envoy

# ✅ 正确
spec:
  containers:
    - name: app
      image: myapp:1.4.2
    - name: sidecar
      image: envoyproxy/envoy:v1.31.3
```

**GitHub Actions**:
```yaml
# ❌ 违规
jobs:
  test:
    container: node:latest
    services:
      postgres:
        image: postgres:alpine

# ✅ 正确
jobs:
  test:
    container: node:20.18.0
    services:
      postgres:
        image: postgres:17.1-alpine
```

---

## 例外情况（极少）

以下情况可以**短暂**使用浮动 tag，但必须在 commit body 或代码注释中说明原因，并设置定期 review 提醒：

1. **临时调试** — 本地排查问题时拉一下 latest 看新版行为，**禁止**进入 commit
2. **官方明确推荐使用 codename** — 极少数镜像（如某些 ML 框架）只发 codename tag，没有版本号
3. **基础镜像本身就是浮动的** — 如 `gcr.io/distroless/static:nonroot`（distroless 没有版本号），这类镜像必须钉 digest

**禁止以"为了拿安全补丁"为由用 `latest`**。安全补丁应该通过定期升级 N-1 minor 实现，而不是放任 image 漂移。

---

## 与 dwy-deploy-audit 的关系

- **本 skill (`dwy-docker-image`)**：源代码层面，编写阶段强制版本固定
- **`dwy-deploy-audit`**：生产环境层面，巡检线上服务器实际跑的镜像

两者互补：先在源码层面固定版本，再在部署后验证实际跑的是预期版本。

---

## 违规检测速查

发现以下任一情况，立即停止并提示用户修复：

| 检测项 | 严重程度 | 修复建议 |
|--------|---------|---------|
| `FROM xxx:latest` 或 `FROM xxx`（无 tag） | critical | 替换为 N-1 minor 具体版本 |
| `image: xxx:latest` 或 `image: xxx` | critical | 替换为 N-1 minor 具体版本 |
| `image: xxx:stable` / `:mainline` / `:alpine`（仅这一段） | high | 替换为带版本号的具体 tag，如 `:1.26.2-alpine` |
| `image: xxx:N`（只有一段版本号，如 `redis:7`） | high | 钉到 minor 或 patch |
| 使用 codename 不带版本号（如 `:bookworm`） | high | 改用版本号 `:12` |
| 生产 manifest 中只有 tag 无 digest | low | 关键服务建议补 `@sha256:...` |
