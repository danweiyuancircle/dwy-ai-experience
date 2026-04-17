---
description: Docker/Docker Compose 开发与生产环境规范
paths:
  - "**/Dockerfile*"
  - "**/docker-compose*.yml"
  - "**/docker-compose*.yaml"
  - "**/.dockerignore"
  - "**/dev.sh"
---

# Docker 规范

每个项目**必须**提供两个 compose 文件,不可合并。

---

## 一、docker-compose.dev.yml(开发环境)

**核心原则:** 快速启动、热更新、方便调试。

```yaml
# docker-compose.dev.yml — 只跑基础设施,应用在宿主机跑
services:
  postgres:
    image: postgres:16
    ports:
      - "${PG_PORT:-15432}:5432"     # 映射到宿主机,方便用 DBeaver 连
    environment:
      POSTGRES_DB: ${DB_NAME:-app}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-postgres}
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "${REDIS_PORT:-16379}:6379"

  minio:
    image: minio/minio
    ports:
      - "${MINIO_PORT:-19000}:9000"
      - "${MINIO_CONSOLE_PORT:-19001}:9001"
    environment:
      MINIO_ROOT_USER: ${MINIO_USER:-minioadmin}
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD:-minioadmin}
    command: server /data --console-address ":9001"
    volumes:
      - miniodata:/data

  # 可选:DolphinDB(量化金融项目)
  # dolphindb:
  #   image: dolphindb/dolphindb:v3.00.5
  #   ports:
  #     - "18848:8848"

volumes:
  pgdata:
  miniodata:
```

**关键要点:**
- 基础设施容器化,应用代码在宿主机运行(`uvicorn --reload` / `vite dev`)
- 端口映射到宿主机非标准端口(避免与其他项目冲突),端口用环境变量可配
- volume 持久化数据

---

## 二、docker-compose.prod.yml(生产环境)

**核心原则:** 安全、稳定、最小权限。

```yaml
# docker-compose.prod.yml — 所有服务容器化
services:
  postgres:
    image: postgres:16
    # 不暴露端口(仅内网通信)
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
    image: redis:7
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s

  minio:
    image: minio/minio
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

**关键要点:**
- 基础设施不暴露端口(仅通过 Docker 网络内部通信)
- 后端容器只读根文件系统 + tmpfs
- 所有服务 `restart: unless-stopped`
- 健康检查确保启动顺序
- 环境变量从 `.env` 注入(不硬编码在 yml 中)

---

## 三、Dockerfile 规范

**后端 Dockerfile.dev:**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install uv && uv pip install -e ".[dev]" --system
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

**后端 Dockerfile.prod:**
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

**前端 Dockerfile(生产):**
```dockerfile
FROM node:20-slim AS builder
RUN npm i -g pnpm
WORKDIR /app
COPY package.json pnpm-lock.yaml .
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**强制规则:**
- 生产镜像必须用多阶段构建(builder + runtime)
- 生产镜像必须用 non-root user 运行
- 必须有 `.dockerignore`(排除 node_modules/、.env、__pycache__/、.git/)
- 禁止在镜像中包含 dev 依赖

---

## 四、一键启动脚本

每个项目提供 `dev.sh`:

```bash
#!/bin/bash
# 启动基础设施
docker compose -f docker-compose.dev.yml up -d

# 等待 PostgreSQL 就绪
until docker compose -f docker-compose.dev.yml exec postgres pg_isready -U postgres; do
  sleep 1
done

# 后端(热更新)
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Worker(后台任务)
cd backend && arq app.worker.WorkerSettings &

# 前端(热更新)
cd frontend && pnpm dev &

wait
```
