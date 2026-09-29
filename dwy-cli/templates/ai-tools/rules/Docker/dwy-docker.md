---
description: Docker 通用规则（镜像固定版本、容器内存上限、日志大小限制、配置变更重启姿势）
---

# Docker 通用规则

适用于 `Dockerfile`、`docker-compose*.yml`、`compose.yml`、Kubernetes manifest、CI 配置中的所有 `FROM` / `image:` 字段，以及容器资源与日志配置。

## 一、Docker 镜像固定版本

- **必须**使用固定版本 tag
- **禁止** `latest`
- **禁止**省略 tag。省略 tag 等同于 `latest`
- **禁止**浮动 tag：`stable`、`mainline`、`current`、`release`、`lts`、`rolling`、`main`、`master`、`head`、`edge`、`nightly`
- **禁止**只写环境或发行版 tag：`alpine`、`slim`、`bookworm`、`bullseye`、`buster`、`jammy`、`focal`、`noble`、`trixie`
- 数据库、缓存、网关、消息队列等关键基础设施，优先固定到 `tag@sha256:...`

### 正反例

```dockerfile
# 反例
FROM nginx:latest
FROM python
image: redis:7
image: postgres:bookworm

# 正例
FROM nginx:1.26.2
FROM python:3.12.10-slim
image: redis:7.4.2
image: postgres:16.4
image: postgres:16.4@sha256:xxxxx
```

正例里的版本号只示范具体 tag 的写法。该装哪一个，以当次查到的 tag 列表为准，不从本规则抄数字。

## 二、Docker 容器配置要求

### 1. 内存设置

- 每一个容器**必须**设置最大可用内存
- 与 Redis 配合使用时，容器最大可用内存**必须大于** Redis 的 `maxmemory`
- **禁止**容器无限制使用宿主机内存

### 2. 日志设置

- Docker 日志**必须**设置最大使用量
- **必须**限制单个日志文件大小与轮转文件数量
- **禁止**不设上限长期写入，避免占满磁盘

具体数字以当次测到的内存占用和日志增速为准。没有实测的新环境才用经验起点，服务跑起来后重测。下面示例只示范字段怎么写。

### compose 示例

```yaml
services:
  app:
    image: myapp:1.2.3
    mem_limit: 512m
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  redis:
    image: redis:7.4.2
    command: ["redis-server", "--maxmemory", "256mb", "--maxmemory-policy", "allkeys-lru"]
    mem_limit: 384m
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

## 三、配置变更重启姿势（env_file / environment / .env）

### 根因

`docker compose restart` 只重启**已存在的容器进程**，**不会重读** `env_file` / `environment` / `.env`。env 变量只在**容器创建时**注入容器配置；restart 沿用旧容器的旧环境，新 env 永远进不去。

### 现象（真实踩坑）

预览机改了 `.env` 的 `DOLPHINDB_FACTOR__PORT=18560`，用 `docker compose restart` 加载 → preview 容器一直拿不到新值，因子 provider 静默回退到主库 8848，功能"看起来通了"实际走错库。当时报"已验证"是错的——只验了隧道连通，没验 app 实际配置（`printenv`）。

release 环境没踩坑：deploy-bg 是 build 后 `up -d`，镜像变更触发容器重建，重建时重读了 env_file。

### 强制规则

**改了 env_file / environment / `.env` 后，必须重建容器，不能只 restart：**

```bash
# 正确：重建容器，重读 env
docker compose up -d --force-recreate backend

# 或更精准：只重建受影响服务，不动依赖
docker compose up -d --force-recreate --no-deps backend

# 错误：restart 不重读 env，新配置永远不生效
docker compose restart backend
```

### 判断容器是否重建的速查

| 操作 | 容器是否重建 | env 是否重读 |
|------|------------|------------|
| `docker compose restart` | 否（仅重启进程） | **否** |
| `docker compose up -d`（镜像无变化） | 否 | 否 |
| `docker compose up -d`（镜像有变化） | 是 | 是 |
| `docker compose up -d --force-recreate` | 是 | 是 |
| `docker compose up -d --env-file .env.prod`（换了 env 文件） | 是 | 是 |

### 验证清单（改 env 后必跑）

```bash
# 1. 确认容器内实际生效的 env（不是宿主机的 .env）
docker compose exec backend printenv | grep DOLPHINDB_FACTOR__

# 2. 不要只验连通性，要验 app 实际读到的配置
#    连通=隧道通，不代表 app 配置对
```

### 一句话

> 配置改了别 restart，`up -d --force-recreate`。验证别只看连通，`printenv` 看容器内真值。

## 四、镜像源

文档和脚本里的镜像站 URL 是当前候选，不是指定赢家。

- 先探测即将真正使用的路径（包索引、发行版 `Release`、镜像 manifest）。超时、证书错误、状态不对、没有目标包或 tag 的源丢掉
- 在剩下的源里用本次延迟最低的。连通不等于可用
- 私服、用户指定的源不参与公网竞速
- 候选全部不成立时另找可用源，再测一次。测速结果不写回本规则
