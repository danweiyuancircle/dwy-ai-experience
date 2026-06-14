---
description: Redis 安全与使用规范（必须用 dwyeapi 客户端、密码、绑定、危险命令禁用、key TTL 与前缀、敏感数据禁存）
---

# Redis 安全与使用规范

适用于使用 Redis 作为缓存 / 会话存储 / Token 黑名单 / 速率限制存储的 Python 后端项目。

---

## 一、客户端使用（强制）

- **必须**通过 dwyeapi 缓存模块获取共享异步 Redis 客户端（具体 API 查 `dwy-eapi` skill）
- **禁止**业务代码中 `aioredis.from_url(...)` 自建连接池
- **禁止**直接使用同步 `redis-py`（除非脚本类一次性任务）

---

## 二、服务端配置（强制）

| 规则 | 说明 |
|------|------|
| 认证 | **必须**设置 `requirepass`，无密码 Redis 一律拒绝接入生产 |
| 绑定地址 | `bind 127.0.0.1` 或内网地址，**禁止** `bind 0.0.0.0`，**禁止**通过安全组 / 防火墙 / LB 直接暴露 `6379` 到公网 |
| 运行权限 | Redis 进程**禁止**以 `root` 用户运行，必须使用专用低权限用户 |
| 危险命令 | **禁用**或重命名 `FLUSHALL` / `FLUSHDB` / `CONFIG` / `KEYS` / `DEBUG` |
| 内存上限 | Redis 运行**必须**显式设置 `maxmemory` 与 `maxmemory-policy`（推荐 `allkeys-lru`），防止缓存无限膨胀或 OOM |
| 持久化 | 根据用途选择：缓存可关 AOF；会话 / 黑名单需 AOF everysec |

```conf
# redis.conf 关键项示例
requirepass <strong-password>
bind 127.0.0.1
port 6379
maxclients 10000
rename-command FLUSHALL ""
rename-command FLUSHDB ""
rename-command CONFIG ""
rename-command KEYS ""
rename-command DEBUG ""
maxmemory 256mb
maxmemory-policy allkeys-lru
```

```ini
# systemd/service 示例
User=redis
Group=redis
```

---

## 三、Key 设计规范（强制）

| 规则 | 说明 |
|------|------|
| 必须 TTL | 所有 key **必须**显式设置过期时间（`ex` / `pexpire`），**禁止**遗留无 TTL 的 key |
| 必须项目前缀 | 所有 key 必须有项目前缀，格式 `{app}:{domain}:{detail}`（如 `myapp:token:blacklist:abc123`） |
| snake_case | key 段用 snake_case，**禁止**驼峰或中文 |
| 不存敏感原文 | **禁止**存储密码、身份证、银行卡、token 原文（token 存哈希） |

### 正反例

```python
# 反例
await redis.set("abc123", "1")                       # 无前缀
await redis.set("myapp:data:xxx", value)             # 无 TTL
await redis.set("myapp:user:password", "123456")     # 存敏感原文
await redis.set("myapp:userToken", "ey...")          # 驼峰命名

# 正例
await redis.set("myapp:token:blacklist:abc123", "1", ex=3600)
await redis.set("myapp:cache:user:uuid:f7e2", json_data, ex=300)
```

---

## 四、Pub/Sub 与 Stream 使用约束

- 业务消息**禁止**用 Pub/Sub 当持久队列（Pub/Sub 无 ACK 与持久化）
- 持久任务用 dwyeapi tasks 模块（基于 ARQ）或 Redis Stream
- Stream 必须设消费者组 ACK 与死信处理

---

## 五、违规检测清单

| 检查项 | 违规模式 | 严重程度 |
|--------|---------|---------|
| 绑定 0.0.0.0 | 服务对公网暴露 | **致命 → STOP** |
| 公网开放 6379 | 安全组 / 防火墙 / LB 允许公网直连 Redis 端口 | **致命 → STOP** |
| 无密码 | 生产 Redis 未设 `requirepass` | **致命 → STOP** |
| root 运行 | Redis 进程以 `root` 身份启动 | **致命 → STOP** |
| 存敏感原文 | 密码 / 身份证 / token 明文存 Redis | **致命 → STOP** |
| 自建连接池 | 业务代码 `aioredis.from_url(...)`，未走 dwyeapi 缓存模块 | 高 |
| 危险命令未禁 | `FLUSHALL` / `KEYS` / `CONFIG` 等可在生产执行 | 高 |
| 未设 `maxmemory` | Redis 未设置缓存最大可用内存或未配置淘汰策略 | **致命 → STOP** |
| Key 无 TTL | `redis.set()` 没有 `ex` 参数（业务上明确永久存储除外） | 中 |
| Key 无前缀 | Key 无项目前缀，污染共享 Redis | 中 |
| Pub/Sub 当队列 | 业务关键消息走 Pub/Sub | 高 |
