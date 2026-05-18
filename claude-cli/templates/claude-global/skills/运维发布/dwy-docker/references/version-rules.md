# 镜像版本选择规则（N-1 minor）

选具体版本号时读这份。先用 `scripts/query_dockerhub.py` 查实时数据，再按下面规则推算 N-1。

## 为什么是 N-1 minor 而不是最新

新版镜像刚发布时，回归 bug、性能问题、新依赖不兼容这些坑还没被社区踩过。等下一个 minor 出来，前一个 minor 系列已经经历了几轮 patch 修复，**稳定性 vs 新特性的折中点**就是 N-1。这是行业惯例，不是激进保守。

举例：nginx `1.27.0` 刚发布时有个 HTTP/3 模块的 segfault，3 周后 `1.27.1` 才修复。这期间用 `1.26.x` 系列的人完全没受影响。

## 强制规则

1. **禁止 `latest`** — FROM / image / containers.image / services.image 任何位置都不允许，省略 tag 等同于 `latest`
2. **必须固定 tag** — 必须是具体版本号（如 `17.1`、`1.26.2`、`3.20`），禁止浮动 tag
3. **优先选 N-1 minor** — 当前最新稳定 minor 的前一个 minor 系列最新 patch
4. **生产关键服务用 digest** — 数据库、消息队列、网关在 tag 后再钉 `@sha256:...`，让 image 100% 不可篡改

---

## 选法分类（按版本号格式）

### 1. semver 三段镜像（绝大多数）

格式 `MAJOR.MINOR.PATCH`，例如 `nginx:1.27.3`、`redis:7.4.1`。

步骤：
1. DockerHub 找当前最新稳定 minor（**忽略 rc / beta / alpha / preview / nightly**）
2. minor 减 1，得到目标 minor 系列
3. 取该 minor 系列的最新 patch

| 镜像 | 当前最新稳定 | N-1 minor 选择 | 说明 |
|------|-------------|---------------|------|
| `nginx` | `1.27.3` | `nginx:1.26.2` | 1.26 系列最新 patch |
| `redis` | `7.4.1` | `redis:7.2.6` | 7.4 上一个稳定 minor 是 7.2，跳过仅维护版 |
| `node` | `22.11.0`（LTS）| `node:20.18.0` | LTS 镜像例外，见下文 |

### 2. 两段版本号镜像

格式 `MAJOR.MINOR`，例如 `postgres:17.2`、`mysql:8.4`、`alpine:3.21`。这类镜像把 minor 当 patch 用。

选法：minor 减 1，取该系列最新 tag。

| 镜像 | 当前最新稳定 | N-1 minor 选择 |
|------|-------------|---------------|
| `postgres` | `17.2` | `postgres:17.1` |
| `mysql` | `8.4` | `mysql:8.3` |
| `alpine` | `3.21` | `alpine:3.20` |

### 3. 年份版本号镜像（Ubuntu / Debian）

格式 `YY.MM` 或 codename，例如 `ubuntu:24.04`、`debian:bookworm`。

选法：选**上一个 LTS / stable release**，**不要**用 codename（codename 是浮动 tag，会随 release 漂移），只用版本号。

| 镜像 | 当前最新 LTS | N-1 选择 |
|------|-------------|---------|
| `ubuntu` | `24.04` | `ubuntu:22.04` |
| `debian` | `12`（bookworm）| `debian:11`（bullseye）|

### 4. LTS 镜像例外（Node.js / OpenJDK）

LTS 镜像（如 Node.js 偶数 major 是 LTS）选**上一个 LTS major** 的最新 patch，**不要**机械 minor - 1。原因是非 LTS 版本生命周期短（6 个月），N-1 落到非 LTS 上反而很快就 EOL。

例：当前 `node:22.11.0`（22 是 LTS），N-1 选 `node:20.18.0`（20 是上一个 LTS）而不是 `node:21.x`。

---

## 例外情况（极少）

以下情况可以**短暂**使用浮动 tag，必须在 commit body 或代码注释中说明原因：

1. **临时调试** — 本地排查时拉一下 `latest` 看新版行为，**禁止**进入 commit
2. **官方明确推荐使用 codename** — 极少数镜像（如某些 ML 框架）只发 codename tag
3. **基础镜像本身就是浮动的** — 如 `gcr.io/distroless/static:nonroot`（distroless 没有版本号），这类镜像必须钉 digest

**禁止以"为了拿安全补丁"为由用 `latest`**。安全补丁应该通过定期升级 N-1 minor 实现，不是放任 image 漂移。
