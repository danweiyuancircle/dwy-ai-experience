---
description: Docker 通用规则（镜像固定版本、容器内存上限、日志大小限制）
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

## 二、Docker 容器配置要求

### 1. 内存设置

- 每一个容器**必须**设置最大可用内存
- 与 Redis 配合使用时，容器最大可用内存**必须大于** Redis 的 `maxmemory`
- **禁止**容器无限制使用宿主机内存

### 2. 日志设置

- Docker 日志**必须**设置最大使用量
- **必须**限制单个日志文件大小与轮转文件数量
- **禁止**不设上限长期写入，避免占满磁盘

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
