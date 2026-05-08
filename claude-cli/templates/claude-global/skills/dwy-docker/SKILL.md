---
name: dwy-docker
description: "Docker 工程规范检查与镜像版本管理。触发场景：用户编辑/新建/粘贴 Dockerfile / docker-compose / k8s manifest / .github workflow / .gitlab-ci / .dockerignore / dev.sh 时；用户口头提到 docker / 容器 / compose / 镜像版本 / k8s 镜像时；用户说'扫描 latest' / '检查 docker' / '固定镜像版本' / 'docker 规范'。运作方式：问题驱动 — AI 检查合规性，合规则静默放行，违规才用 AskUserQuestion 让用户决策修复，禁止 AI 自行拍板修改。覆盖镜像版本（禁 latest / 浮动 tag、N-1 minor）、Dockerfile 工程（多阶段、non-root、.dockerignore）、compose 工程（dev/prod 分离、healthcheck、restart 策略）、一键启动 dev.sh。"
---

# Docker 工程规范

涵盖镜像版本选择 + Dockerfile / docker-compose / k8s manifest 工程结构。

**脚本目录：** `~/.claude/skills/dwy-docker/scripts/`（以下简称 `{scripts}`）

**参考文件：** `~/.claude/skills/dwy-docker/references/`
- `templates.md` — compose / Dockerfile / dev.sh 模板（用户问"怎么写"时读）
- `version-rules.md` — N-1 minor 选法 + 各类镜像表（选具体版本号时读）
- `ask-templates.md` — AskUserQuestion 模板（违规需要询问用户时读）

---

## 运作原则（最重要）

**问题驱动 + 不打扰用户**。

| 用户当前文件状态 | AI 行为 |
|---|---|
| 已合规（tag 固定 / Dockerfile 多阶段 / compose 分离） | **静默放行**，不打扰 |
| 违规（latest / 浮动 tag / 单一 compose / 缺 healthcheck 等） | 自动 `AskUserQuestion`，让用户决策 |
| AI 即将新写入（用户让我加 redis 服务） | 先 query_dockerhub.py + AskUserQuestion 选 tag，再写入 |

**为什么这样设计**：用户写 docker 一半被中断 N 次问"要选哪个版本"会很烦；已经写了 `nginx:1.26.2` 这种合规字段也不该 AI 啰嗦"建议你改成…"。只在违规时才介入。

**禁止**：
- AI 自行决定违规项的修复方案后直接 Edit
- 对已合规的字段啰嗦"建议你改成…"
- 对每个 `image:` 字段都强制询问，即使它已经是合规的具体版本号

---

## 触发场景

AI 看到下列情况之一，立即进入「检查清单」：

1. 用户编辑 / 新建 / 修改：`Dockerfile`、`Dockerfile.*`、`*.Dockerfile`、`docker-compose*.yml`、`compose.yml`、`*.dockerignore`、`dev.sh`
2. 用户在 K8s manifest（`.yaml` 含 `image:`）中改镜像
3. 用户在 `.github/workflows/*.yml` 的 `container:` / `services:` 段或 `.gitlab-ci.yml` 的 `image:` 段改镜像
4. 用户口头说"加 postgres" / "用 redis 当缓存" / "写个 Dockerfile" / "compose 怎么写"
5. 用户说"扫描 latest" / "检查 docker" / "docker 规范"

---

## 检查清单

### A. 镜像 tag（针对每个 `FROM` / `image:` 字段）

| 检测 | 严重度 | 触发 AskUserQuestion |
|---|---|---|
| `xxx:latest` 或 `xxx`（无 tag） | critical | ✓ 必须 |
| 浮动 tag：`stable` / `mainline` / `current` / `release` / `lts` / `rolling` / `main` / `master` / `head` / `edge` / `nightly` / `alpine` / `slim` / `bookworm` / `bullseye` / `buster` / `jammy` / `focal` / `noble` / `trixie` 单独使用 | high | ✓ 必须 |
| 单段版本号（如 `redis:7`，不到 minor） | high | ✓ 必须 |
| codename 不带版本号（如 `:bookworm`） | high | ✓ 必须 |
| 已固定到 `MAJOR.MINOR.PATCH` / `MAJOR.MINOR` 具体版本号 | — | ✗ 静默放行 |
| 生产关键服务（数据库、消息队列、网关）只有 tag 无 digest | low | ⚠ 仅在用户明确说"生产环境"时提示 |

→ 修复时读 `references/ask-templates.md` 模板 1（tag 违规）；选具体版本号读 `references/version-rules.md`。

### B. Dockerfile 工程结构（针对生产 Dockerfile）

文件名形如 `Dockerfile.prod` / `Dockerfile`（无 dev 后缀）时检查：

| 检测 | 严重度 | 触发 AskUserQuestion |
|---|---|---|
| 单阶段构建（无 `FROM ... AS builder` 多阶段） | high | ✓ 必须 |
| 没有 `USER` 指令，或 `USER root` | high | ✓ 必须 |
| 同目录无 `.dockerignore` | medium | ✓ 必须 |
| 镜像里包含 dev 依赖（`pip install -e ".[dev]"` / `pnpm install` 不带 `--prod`） | high | ✓ 必须 |
| 已合规 | — | ✗ 静默放行 |

→ 修复时读 `references/ask-templates.md` 模板 2（Dockerfile 结构）；模板示例读 `references/templates.md`。

### C. docker-compose 工程结构

| 检测 | 严重度 | 触发 AskUserQuestion |
|---|---|---|
| 项目只有一份 `docker-compose.yml`（没有 dev/prod 分离） | high | ✓ 必须 |
| `docker-compose.prod.yml` 中 postgres/redis/minio 等基础设施暴露端口（`ports:` 段） | critical | ✓ 必须 |
| `docker-compose.prod.yml` 中服务无 `restart:` 策略 | medium | ✓ 必须 |
| `docker-compose.prod.yml` 中数据库/缓存无 `healthcheck:` | medium | ✓ 必须 |
| compose 文件中硬编码密码（`POSTGRES_PASSWORD: postgres123` 而非 `${DB_PASSWORD}`） | critical | ✓ 必须 |
| 已合规 | — | ✗ 静默放行 |

→ 修复时读 `references/ask-templates.md` 模板 3（compose 结构）；模板示例读 `references/templates.md`。

### D. 一键启动脚本

每个全栈项目根**必须**有两个脚本：

- `dev.sh` — 开发环境一键拉起全栈（基础设施容器化 + 应用宿主机热更新）
- `prod.sh` — 生产环境管理入口，支持 `start` / `stop` / `restart` / `status` / `logs` / `update` 子命令

| 检测 | 严重度 | 触发 AskUserQuestion |
|---|---|---|
| 项目根无 `dev.sh`（且确认是 dwy 风格 monorepo / 全栈项目） | low | ⚠ 仅在用户问"怎么启动"时提示创建 |
| 项目根无 `prod.sh`（且已有 `docker-compose.prod.yml`） | medium | ⚠ 仅在用户问"怎么部署 / 怎么重启" 时提示创建 |
| `prod.sh` 不支持 `start` / `stop` / `restart` 三个核心子命令 | medium | ✓ 必须 |
| `prod.sh` 中 docker compose 命令未带 `--env-file` 加载 `.env.prod` | high | ✓ 必须 |

→ 模板见 `references/templates.md` 末尾「一键启动脚本」段。

---

## 交互流程（三种场景）

### 1. 写入前（AI 即将新增 image / Dockerfile / compose）

例：用户说"帮我加个 redis"。

1. `python3 {scripts}/query_dockerhub.py redis` 查推荐版本
2. AskUserQuestion 让用户选 tag（模板见 `references/ask-templates.md` 模板 1）
3. 用户选完后用 Edit / Write 写入，按 `references/templates.md` 填补 healthcheck / restart 等字段
4. 写入完成后**不再二次询问已写入的合规字段**

### 2. 检查现有文件（用户编辑或粘贴文件后）

1. 扫描该文件，按「检查清单 A/B/C」逐项核对
2. 收集所有违规项
3. 一次性 AskUserQuestion（最多 4 个并列询问，超过分批；批量 tag 用 `references/ask-templates.md` 模板 4）
4. 用户选完后 Edit 修改

### 3. 全项目扫描（用户主动要求）

例：用户说"扫描 latest" / "检查 docker 配置"。

1. `bash {scripts}/scan_images.sh <project-path>`
2. 收集违规清单
3. 对每个 `critical` / `high` 违规：query_dockerhub.py 拿推荐 + AskUserQuestion
4. 用户选完批量 Edit
5. `low` / `medium` 在最后汇总告诉用户但不强制改

---

## 镜像版本核心规则（速查）

1. **禁止 `latest`** — 任何位置不允许，省略 tag 等同于 `latest`。**为什么**：镜像漂移会让"昨天能跑今天炸"，CI 和 prod 跑不一样的内容
2. **必须固定 tag** — 必须是具体版本号，禁止浮动 tag（`stable` / `alpine` / `bookworm` 等）
3. **优先选 N-1 minor** — 当前最新稳定 minor 的前一个 minor 系列最新 patch。**为什么**：避开新版刚发布时未暴露的回归 bug，行业惯例
4. **生产关键服务用 digest** — 数据库、消息队列、网关钉 `@sha256:...`，让 image 100% 不可篡改

**完整选法（含 4 类镜像表 + LTS 例外 + 具体例子）**：见 `references/version-rules.md`。

---

## 工具脚本

### `query_dockerhub.py`

```bash
python3 {scripts}/query_dockerhub.py <image> [--namespace library] [--top 20]
```

输出最近的稳定 tag 列表 + 推荐 N-1 minor。私有命名空间用 `org/image`。

### `scan_images.sh`

```bash
bash {scripts}/scan_images.sh [project-path]
```

扫描项目所有 Dockerfile / docker-compose / k8s yaml / CI 配置中的镜像引用，输出违规清单。**只读，不改文件**。

### 降级流程（脚本不可用时）

`query_dockerhub.py` 失败（私有仓库 / 网络不通）：

1. 用 WebFetch 查 DockerHub `https://hub.docker.com/_/<image>/tags` 或官方 release page
2. 如果仍无法拿到版本列表，**仍然走 AskUserQuestion**，措辞改为"无法自动查询版本，请手动确认"，options 提供常见稳定版本号 + "Other (我手动输入)"

---

## 与 dwy-deploy-audit 的关系

- **本 skill (`dwy-docker`)**：源代码层面，编写阶段强制规范
- **`dwy-deploy-audit`**：生产环境层面，巡检线上服务器实际跑的镜像

两者互补：先在源码层面固定 + 工程合规，再在部署后验证实际跑的是预期版本。
