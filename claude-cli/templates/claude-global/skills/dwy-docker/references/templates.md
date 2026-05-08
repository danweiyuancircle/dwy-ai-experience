# Docker 工程结构模板

新建 docker 工程或用户问"compose / Dockerfile / dev.sh 怎么写"时读这份文件。

## docker-compose.dev.yml（开发环境）

**核心原则**：快速启动、热更新、方便调试。基础设施容器化，应用代码在宿主机跑（这样 `uvicorn --reload` / `vite dev` 的文件监听才能生效，不用每次改代码都 rebuild 镜像）。

```yaml
# docker-compose.dev.yml — 只跑基础设施，应用在宿主机跑
services:
  postgres:
    image: postgres:17.1                  # 固定具体版本，按 query_dockerhub.py 推荐
    ports:
      - "${PG_PORT:-15432}:5432"          # 映射到宿主机非标准端口，避免与其他项目冲突
    environment:
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7.2.6
    ports:
      - "${REDIS_PORT:-16379}:6379"

  minio:
    image: minio/minio:RELEASE.2024-11-07T00-52-20Z
    ports:
      - "${MINIO_PORT:-19000}:9000"
      - "${MINIO_CONSOLE_PORT:-19001}:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

volumes:
  pgdata:
  miniodata:
```

**关键要点**：
- 端口映射到宿主机非标准端口（`15432` / `16379` / `19000`），用环境变量可配，方便多项目并行开发
- volume 持久化数据，避免 `docker compose down` 丢数据
- 应用本身在宿主机跑（`uvicorn --reload` / `vite dev`）— 这样改代码立刻生效

---

## docker-compose.prod.yml（生产环境）

**核心原则**：安全、稳定、最小权限。

与 dev 关键差异：
- 基础设施**不暴露端口**（仅通过 docker 网络通信，对外只开 backend / frontend）
- 所有服务带 `restart: unless-stopped`
- 数据库 / 缓存有 `healthcheck`，应用 `depends_on` 用 `condition: service_healthy` 等待
- 后端容器 `read_only: true` + tmpfs，缩小攻击面

```yaml
services:
  postgres:
    image: postgres:17.1
    # 不暴露端口（仅内网通信）
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7.2.6
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  minio:
    image: minio/minio:RELEASE.2024-11-07T00-52-20Z
    # 不暴露端口
    environment:
      MINIO_ROOT_USER: ${MINIO_USER}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    command: server /data
    volumes:
      - miniodata:/data
    restart: unless-stopped

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    ports:
      - "${API_PORT:-8000}:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    read_only: true                    # 只读根文件系统
    tmpfs:
      - /tmp                           # 临时文件写 tmpfs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
      interval: 30s

  worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    command: arq app.worker.WorkerSettings
    environment:
      DATABASE_URL: postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/${DB_NAME}
      REDIS_URL: redis://redis:6379/0
      SECRET_KEY: ${SECRET_KEY}
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "${WEB_PORT:-3000}:80"
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  pgdata:
  miniodata:
```

**关键要点**：
- 基础设施不暴露端口 → 攻击面缩到只有 `${API_PORT}` 和 `${WEB_PORT}`
- `restart: unless-stopped` → 单容器崩溃不影响整体，但人工 stop 后不会自启
- healthcheck → 让 `depends_on: service_healthy` 真正等到数据库可连，而不是容器一启就放行
- 环境变量从 `.env` 注入，不硬编码 → 凭证不进 git

---

## Dockerfile

### 后端 `Dockerfile.dev`（单阶段，包含 dev 依赖）

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e ".[dev]" --system
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### 后端 `Dockerfile.prod`（多阶段 + non-root）

```dockerfile
# 多阶段构建
FROM python:3.11-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e "." --system

FROM python:3.11-slim
RUN useradd -r -s /bin/false appuser
WORKDIR /app
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .
USER appuser
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**为什么这样写**：
- 多阶段：builder 装包（含编译工具），runtime 只复制 site-packages，镜像缩小一半以上
- `useradd -r -s /bin/false appuser` + `USER appuser`：容器逃逸时拿不到 root，缩小攻击面
- 不 COPY 整个项目，只 COPY `src/` / `alembic/` / `alembic.ini`：避免误带 `.git/` / `tests/` / `.env` 进生产镜像

### 前端 `Dockerfile`（多阶段 + nginx 静态托管）

```dockerfile
FROM node:20.18.0-slim AS builder
RUN npm i -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml .
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:1.26.2-alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

### 配套 `.dockerignore`（必须有）

```
node_modules/
.git/
.env
.env.*
__pycache__/
*.pyc
dist/
.pytest_cache/
.vscode/
.idea/
```

不写这个，构建上下文会把整个 `node_modules/` / `.git/` 上传给 Docker daemon，速度慢且可能泄露 `.env`。

---

## 一键启动脚本（`dev.sh` + `prod.sh`）

每个项目根放两份脚本：`dev.sh` 用于本地开发，`prod.sh` 用于生产环境管理。两个脚本都采用**子命令模式 + 显式传参**设计。

**两个脚本的统一约束**：

- **必须显式传子命令**（`start` / `stop` / `restart` / ...），不传参数时**只打印帮助文档不执行任何动作**
- 帮助文档必须列出所有子命令、参数含义、典型示例
- 子命令未匹配（拼错或不支持）时同样打印帮助并以非零退出码退出

**为什么强制传参 + 不传打印 help**：

`bash dev.sh` / `bash prod.sh` 不带参数直接拉起服务是**危险的默认行为**。运维人员在生产 SSH 里手抖少敲一个词就可能误启动服务、覆盖容器、拉新镜像。强制传子命令让每一次操作都是**有意识的**，并且帮助文档让新接手项目的人不用看 README 就知道怎么用。

**为什么要有这两个脚本**：

- `dev.sh` — 新人 clone 项目后一行 `bash dev.sh start` 跑起来全栈，不用查文档；同时支持 `infra` 模式让你在 IDE 里断点调试应用
- `prod.sh` — 运维人员（或部署 CI）用统一入口管理生产，避免每次手敲长串 `docker compose --env-file ... -f ... ...`，也避免漏 `--env-file` 等参数导致的事故

### `dev.sh`（开发环境管理）

```bash
#!/bin/bash
# 开发环境管理脚本
# 用法: bash dev.sh {start|stop|restart|infra|status|logs} [service]

set -e

COMPOSE_FILE="docker-compose.dev.yml"

# 前置检查
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "错误：当前目录找不到 $COMPOSE_FILE"
  exit 1
fi

# 统一调用 docker compose 的封装
dc() {
  docker compose -f "$COMPOSE_FILE" "$@"
}

# Ctrl+C 时清理所有后台进程和容器
cleanup() {
  echo ""
  echo "→ 停止后台应用进程..."
  jobs -p | xargs -r kill 2>/dev/null || true
  echo "→ 停止基础设施容器..."
  dc down
  echo "✓ 已清理"
}

ACTION="${1:-}"
SERVICE="${2:-}"

case "$ACTION" in
  start)
    echo "→ 启动基础设施..."
    dc up -d

    echo "→ 等待 PostgreSQL 就绪..."
    until dc exec postgres pg_isready -U postgres > /dev/null 2>&1; do
      sleep 1
    done

    trap cleanup INT TERM EXIT

    echo "→ 启动后端 (热更新)..."
    (cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload) &

    echo "→ 启动 Worker..."
    (cd backend && arq app.worker.WorkerSettings) &

    echo "→ 启动前端 (热更新)..."
    (cd frontend && pnpm dev) &

    echo ""
    echo "✓ 全栈已启动。Ctrl+C 退出会自动清理所有进程和容器"
    wait
    ;;

  stop)
    echo "→ 停止基础设施..."
    dc down
    echo "✓ 已停止（volume 数据保留）"
    ;;

  restart)
    echo "→ 重启基础设施容器..."
    dc restart
    echo "✓ 基础设施已重启。应用层（uvicorn / vite / arq）请重新跑 'bash dev.sh start'"
    ;;

  infra)
    echo "→ 仅启动基础设施容器（不启动应用）..."
    dc up -d
    echo "✓ 基础设施已启动。应用请你自己在 IDE 里跑（方便断点调试）"
    echo ""
    dc ps
    ;;

  status)
    dc ps
    ;;

  logs)
    if [ -n "$SERVICE" ]; then
      dc logs -f --tail=200 "$SERVICE"
    else
      dc logs -f --tail=200
    fi
    ;;

  *)
    cat <<EOF
用法: bash dev.sh {start|stop|restart|infra|status|logs} [service]

  start              一键拉起全栈：基础设施容器 + 后端 + Worker + 前端
                     前台运行，Ctrl+C 退出会自动清理所有进程和容器
  stop               停止并清理基础设施容器（volume 保留，下次 start 数据还在）
  restart            重启基础设施容器（应用层不动，需自行重新启动）
  infra              只启动基础设施容器，应用让你在 IDE 里跑（推荐：断点调试场景）
  status             查看基础设施容器状态
  logs [service]     实时查看基础设施日志（最近 200 行起），可指定 service

示例:
  bash dev.sh start           # 一键全栈，适合纯命令行开发
  bash dev.sh infra           # 容器跑数据库，IDE 里跑应用（推荐用于断点调试）
  bash dev.sh logs postgres   # 看 postgres 日志
EOF
    exit 1
    ;;
esac
```

### `prod.sh`（生产环境管理）

```bash
#!/bin/bash
# 生产环境部署管理脚本
# 用法: bash prod.sh {start|stop|restart|status|logs|update} [service]

set -e

COMPOSE_FILE="docker-compose.prod.yml"
ENV_FILE=".env.prod"

# 前置检查
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "错误：当前目录找不到 $COMPOSE_FILE"
  exit 1
fi

if [ ! -f "$ENV_FILE" ]; then
  echo "错误：缺少 $ENV_FILE，请先从 .env.prod.example 复制并填写生产环境变量"
  exit 1
fi

# 统一调用 docker compose 的封装（避免重复参数）
dc() {
  docker compose --env-file "$ENV_FILE" -f "$COMPOSE_FILE" "$@"
}

ACTION="${1:-}"
SERVICE="${2:-}"

case "$ACTION" in
  start)
    echo "→ 启动生产环境（后台运行）..."
    dc up -d
    echo "✓ 已启动。用 'bash prod.sh status' 查看状态"
    ;;

  stop)
    echo "→ 停止生产环境..."
    dc down
    echo "✓ 已停止（volume 数据保留）"
    ;;

  restart)
    if [ -n "$SERVICE" ]; then
      echo "→ 重启服务 $SERVICE ..."
      dc restart "$SERVICE"
    else
      echo "→ 重启所有服务..."
      dc restart
    fi
    echo "✓ 已重启"
    ;;

  status)
    dc ps
    ;;

  logs)
    if [ -n "$SERVICE" ]; then
      dc logs -f --tail=200 "$SERVICE"
    else
      dc logs -f --tail=200
    fi
    ;;

  update)
    echo "→ 拉取最新镜像并重建容器..."
    dc pull
    dc up -d --remove-orphans
    echo "✓ 已更新到最新镜像"
    ;;

  *)
    cat <<EOF
用法: bash prod.sh {start|stop|restart|status|logs|update} [service]

  start              启动所有服务（后台运行）
  stop               停止所有服务并清理容器（volume 保留）
  restart [service]  重启所有服务，或指定单个服务（不重建容器）
  status             查看服务状态
  logs [service]     实时查看日志（最近 200 行起），可指定 service
  update             拉取最新镜像并重建容器（应用 compose 配置变更）

示例:
  bash prod.sh start
  bash prod.sh restart backend
  bash prod.sh logs nginx
  bash prod.sh update
EOF
    exit 1
    ;;
esac
```

**两个脚本共同的设计**：

- **子命令模式**：所有操作必须显式传子命令（`start` / `stop` / `restart` / ...），不传或传错都只打印 help，不执行任何动作。生产环境最忌"默认行为"
- **`dc()` 封装**：所有 docker compose 命令都自动带 `--env-file ... -f ...` 参数，杜绝漏参事故
- **`restart` 走 `docker compose restart` 而不是 `down + up`**：重启容器但不删除（保留运行时状态），更快也更安全；只有 `update`（prod）/ 重新跑 `start`（dev）才会重建
- **`stop` 走 `down` 而非 `stop`**：彻底清理网络和容器，下次 `start` 是全新的；volume 默认保留，不丢数据

**`dev.sh` 特有设计**：

- **`trap cleanup INT TERM EXIT`**：`start` 子命令前台运行（`wait` 阻塞），用户按 Ctrl+C 时会自动 kill 所有后台子进程（uvicorn / arq / vite）并 `docker compose down` 清理容器。避免出现"应用进程已退出但容器还在跑"的孤儿状态
- **`infra` 子命令**：只启基础设施，应用让用户在 IDE 里跑。这是断点调试场景的最佳工作流，比"全栈启动后再 attach 调试器"轻量得多

**`prod.sh` 特有设计**：

- **前置检查 `.env.prod`**：生产环境变量缺失时第一时间退出，不会因为读到默认值跑起一个错误配置的服务
- **`update` 单独命令**：日常运维（重启 / 看日志）不会误触发镜像拉取，只有显式 `update` 才会拉新镜像并重建容器
