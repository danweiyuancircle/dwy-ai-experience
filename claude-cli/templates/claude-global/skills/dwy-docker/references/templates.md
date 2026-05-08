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

## 一键启动脚本 `dev.sh`

每个项目根放一份：

```bash
#!/bin/bash
# 启动基础设施
docker compose -f docker-compose.dev.yml up -d

# 等待 PostgreSQL 就绪
until docker compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres; do
  sleep 1
done

# 后端（热更新）
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Worker（后台任务）
cd backend && arq app.worker.WorkerSettings &

# 前端（热更新）
cd frontend && pnpm dev &

wait
```

**为什么要有这个**：新人 clone 项目后能一行 `bash dev.sh` 跑起来全栈，不用查文档。
