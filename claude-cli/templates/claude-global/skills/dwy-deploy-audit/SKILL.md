---
name: dwy-deploy-audit
description: "部署后线上环境基础安全巡检：远程 SSH 到目标服务器，逐项核对 SSH/Nginx/数据库/HTTPS/Docker/环境变量等基础环境配置，输出分级安全报告，只报告不修复。触发条件：用户说'部署巡检'、'上线检查'、'基础环境检查'、'部署审计'、'线上安全检查'、'生产环境审计' 时。"
---

# 部署后基础环境巡检 (deploy-audit)

对**已部署上线**的服务器执行只读式安全合规审计，逐项核对基础环境配置，输出分级报告。

**与 dwy-pentest 的区别：**

| 维度 | dwy-pentest | dwy-deploy-audit (本 skill) |
|------|-------------|------------------------------|
| 视角 | 攻击者(黑盒) | 运维者(白盒) |
| 行为 | 主动扫描、漏洞利用尝试 | 只读配置文件、状态检查 |
| 范围 | 全栈漏洞 + Web 测试 + 暴力破解 | 基础环境配置合规 |
| 副作用 | 可能触发 IDS、产生大量请求 | 仅 SSH 登录读取配置，零侵入 |
| 输出 | 漏洞清单 + 复现步骤 | 配置不合规清单 + 修复建议 |

**脚本目录：** `~/.claude/skills/dwy-deploy-audit/scripts/`（以下简称 `{scripts}`）

---

## 强制原则

1. **只读不写** — 所有检查只读取配置和状态，**禁止**执行任何修改命令（`sed -i`、`systemctl restart`、`iptables -A` 等）
2. **远程 SSH 执行** — 不在本地猜测，所有结论必须基于目标服务器的真实配置
3. **明确目标** — 用户必须显式提供 SSH 连接信息（host、user、端口、key），未提供则停止并询问
4. **不修复** — 发现问题只输出报告 + 修复建议，**禁止**自动修复或建议用户立即执行修复命令
5. **分级输出** — 所有问题必须按 critical / high / medium / low / info 五级分类
6. **生产环境敏感** — 任何检查命令需明确标注是否涉及生产数据，避免 `pg_dump`、`tcpdump` 等高负载操作

---

## 流程总览

```
1. 收集目标信息  → 确认 SSH 连接、目标服务范围
2. 连通性测试    → SSH 登录、sudo 权限确认
3. 基础环境识别  → 系统版本、已部署服务清单
4. 分类检查      → SSH / Nginx / DB / HTTPS / Env / Docker / Services / Resilience / Logs / Capacity / Secrets(主 Bash 调用 run_all.sh,12 路并行)
5. 生成报告      → 按等级聚合,Markdown 格式
6. 修复建议      → 每条问题给出修复方向(不执行)
```

**共 6 步，按顺序执行。**

---

## Step 1: 收集目标信息

向用户确认以下参数，**任一缺失则停止并询问**：

| 参数 | 必填 | 说明 |
|------|------|------|
| `host` | 是 | 服务器 IP 或域名 |
| `user` | 是 | SSH 登录用户(优先非 root) |
| `port` | 否 | SSH 端口,默认 22 |
| `key` | 是 | SSH 私钥路径 或 用户已配置 ssh config |
| `sudo` | 否 | 是否有 sudo 权限(影响检查覆盖率) |
| `services` | 否 | 已知的部署服务清单(nginx / postgres / redis / docker 等),不填则自动探测 |

**示例对话：**
```
用户: 帮我审计一下我的服务器
助手: 请提供以下信息:
  1. 服务器地址(IP 或域名):
  2. SSH 用户名:
  3. SSH 端口(默认 22):
  4. SSH 私钥路径(如 ~/.ssh/id_ed25519):
  5. 该用户是否有 sudo 权限(影响 nginx/sshd 等系统配置的可读性):
```

---

## Step 2: 连通性测试

执行最小连通性测试，确认 SSH 可用：

```bash
ssh -o ConnectTimeout=5 -o BatchMode=yes -p ${PORT} -i ${KEY} ${USER}@${HOST} "uname -a && id"
```

- 失败 → 报告"无法 SSH 连接"，列出常见原因(key 错误 / 端口防火墙 / 用户不存在)，停止
- 成功 → 记录 `uname` 输出和当前用户 id，进入 Step 3

---

## Step 3: 基础环境识别

**自动探测目标服务器上已部署的关键服务**，决定后续检查覆盖范围：

```bash
ssh ${TARGET} "
  echo '=== OS ==='
  cat /etc/os-release | grep -E '^(NAME|VERSION)='
  echo '=== Listening Ports ==='
  ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null
  echo '=== Running Services ==='
  systemctl list-units --type=service --state=running --no-pager 2>/dev/null | head -30
  echo '=== Docker ==='
  docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Ports}}' 2>/dev/null || echo 'docker not installed'
"
```

根据探测结果跳过不存在的服务检查（例如未部署 Redis 则跳过 check_db.sh 的 Redis 部分）。

---

## Step 4: 分类检查（并行执行）

**主 Claude 直接用 Bash 调用 `run_all.sh`,12 路并行跑完全部检查类目**,把原始输出落到 `/tmp/dwy_audit_<host>.txt`,再由主 Claude `Read` 文件后做分析。

### 为什么不用 subagent 派遣

实测踩坑后的结论(请勿绕过本节直接派 subagent):

1. **subagent 读不到主用户的 `~/.ssh/config`** — 隔离环境下 alias 方式(如 `ssh tencent`)解析失败,报 `Could not resolve hostname :`(host 字段为空)。
2. **`cat script.sh | ssh host "bash -s"` 调用方式是错的** — 本目录每个 `check_*.sh` **本身就是 wrapper,脚本内部已 ssh**,接收 `<target> [ssh_opts...]` 作为参数。被外层 ssh 再包一层会嵌套两次 ssh,失败。
3. **subagent 多包一层反而引入协议偏差** — 主 Claude 直接 Bash 既快又能精确控制错误处理。

### 调用方式（强制）

**主流程：一键并行 + 落盘**

```bash
# 用户提供了 ssh alias(推荐,SSH config 已配好)
bash {scripts}/run_all.sh <ssh_alias>           > /tmp/dwy_audit_<tag>.txt 2>&1

# 用户提供显式参数
bash {scripts}/run_all.sh <user>@<host> -p <port> -i <key>  > /tmp/dwy_audit_<tag>.txt 2>&1
```

`run_all.sh` 内部已实现 12 路并行（每个 section 独立后台进程，约 15–30s 完成全部 12 类）。完成后所有 section 按固定顺序串接到 stdout。主 Claude 用 `Read` 工具读取该 txt 后做分析。

**输出文件命名规则**：`/tmp/dwy_audit_<host_or_alias>.txt`，便于用户回看 + 多次审计互不覆盖。

### 脚本调用约定（理解原理用）

每个 `check_xxx.sh` 是 wrapper，签名固定为：

```bash
bash {scripts}/check_xxx.sh <target> [ssh_opts...]
# 例:
bash {scripts}/check_ssh.sh root@host -p 22 -i ~/.ssh/key
bash {scripts}/check_ssh.sh tencent              # alias 形式(主 Bash 可用)
```

脚本内部用 `ssh "${SSH_OPTS[@]}" "${TARGET}" bash -s <<'REMOTE' ... REMOTE` 把检查体 heredoc 给远端执行。**不要再外层管道 / stdin 重定向**。

```bash
# ❌ 错误调用(嵌套 ssh,失败):
cat {scripts}/check_ssh.sh | ssh root@host "bash -s"
ssh root@host "bash -s" < {scripts}/check_ssh.sh

# ✅ 正确调用:
bash {scripts}/check_ssh.sh root@host -p 22 -i ~/.ssh/key
```

### 何时退化为串行

目标服务器 `sshd MaxStartups` 限制并发，或网络抖动导致并发失败：

```bash
bash {scripts}/run_all.sh <target> [ssh_opts...] --serial > /tmp/dwy_audit_<tag>.txt 2>&1
```

### 单类目重跑

某一类目失败需重跑时，直接调对应 `check_xxx.sh` 即可：

```bash
bash {scripts}/check_db.sh <target> [ssh_opts...]
```

**各类检查内容如下：**

### 4.1 SSH 安全 — `{scripts}/check_ssh.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `PermitRootLogin` | `no` 或 `prohibit-password` | **critical** |
| `PasswordAuthentication` | `no` (强制 key) | **high** |
| `PermitEmptyPasswords` | `no` | **critical** |
| `Port` | 非默认 22 (建议) | medium |
| `Protocol` | 只允许 2 | high |
| `MaxAuthTries` | ≤ 4 | medium |
| `LoginGraceTime` | ≤ 60s | low |
| `AllowUsers` / `AllowGroups` | 已配置白名单 | medium |
| `/var/log/auth.log` 或 `journalctl _COMM=sshd` | 有日志 | high |
| fail2ban / sshguard | 已安装并运行 | medium |

### 4.2 Nginx 配置 — `{scripts}/check_nginx.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| HTTP → HTTPS 强制跳转 | 80 端口 return 301 至 https | **critical** |
| `ssl_protocols` | 仅 `TLSv1.2 TLSv1.3` | high |
| `ssl_ciphers` | 排除弱加密(RC4/3DES/MD5) | high |
| `server_tokens` | `off` | medium |
| `access_log` | 已开启 | **high**(用户特别要求) |
| `error_log` | 已开启,级别 ≥ warn | high |
| `client_max_body_size` | 显式配置,业务非上传 ≤ 10m(对齐 dwy-payload-limits) | medium |
| `limit_req_zone` 已定义 | 至少 1 个 zone（防 CC 攻击 / 暴力请求） | high |
| `limit_req` 应用到敏感路由 | 登录 / 注册 / 验证码 / 高频 API 必须有 | **critical** |
| `limit_conn_zone` + `limit_conn` | 限制同 IP 高并发连接 | medium |
| `limit_req_status` | 建议 `429`（默认 503 易被误判为后端故障） | low |
| `client_body_timeout` / `client_header_timeout` | ≤ 10s（防 slowloris 慢速攻击） | medium |
| `add_header Strict-Transport-Security` | `max-age=31536000` | high |
| `add_header X-Frame-Options` | `DENY` 或 `SAMEORIGIN` | medium |
| `add_header X-Content-Type-Options` | `nosniff` | medium |
| `add_header Content-Security-Policy` | 已配置 | low |
| `autoindex` | `off` | high |
| 暴露的 location | 排查 `/.git`、`/.env`、`/admin` 是否泄漏 | **critical** |
| Nginx 版本 | 非已知 CVE 版本 | medium |

### 4.3 数据库暴露 — `{scripts}/check_db.sh`

**PostgreSQL：**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `listen_addresses` | `localhost` 或内网 IP,**禁止** `*` | **critical** |
| 5432 公网可达性 | 公网不可达 | **critical** |
| `pg_hba.conf` 认证方式 | `scram-sha-256` 或 `md5`,**禁止** `trust` | **critical** |
| `password_encryption` | `scram-sha-256` | high |
| 默认账号 `postgres` 密码 | 已设置且非弱密码 | **critical** |
| `ssl` | `on` (远程连接场景) | high |
| `log_connections` / `log_disconnections` | `on` | medium |

**Redis：**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `bind` | `127.0.0.1` 或内网 IP,**禁止** `0.0.0.0` 暴露 | **critical** |
| 6379 公网可达性 | 公网不可达 | **critical** |
| `requirepass` | 已设置且 ≥ 32 字符随机串 | **critical** |
| `protected-mode` | `yes` | high |
| `maxmemory` | 已设置（推荐物理内存 50%–70%）,**禁止** `0`（无上限） | high |
| `maxmemory-policy` | 业务侧已感知（`allkeys-lru` / `volatile-lru` 常见，`noeviction` 需特别确认） | info |
| `rename-command` | 危险命令(FLUSHALL/CONFIG)已重命名 | medium |
| Redis 版本 | 非已知 CVE 版本 | medium |

### 4.4 HTTPS 证书 — `{scripts}/check_https.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 证书有效期 | 剩余 > 30 天 | high (< 7 天 critical) |
| 证书域名匹配 | CN/SAN 包含访问域名 | **critical** |
| 证书链完整 | 中间证书已配置 | high |
| 自签证书 | 仅内网允许,公网为 critical | varies |
| OCSP Stapling | 已启用 | low |

### 4.5 环境变量 / 文件权限 — `{scripts}/check_env.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `.env` 文件权限 | `600` 或更严 | **critical** |
| `.env` 文件位置 | 不在 nginx `root` 目录下 | **critical** |
| `nginx -T` 可达静态目录 | 不包含 `.env`、`.git`、密钥 | **critical** |
| `/etc/shadow` 权限 | `640` 或 `600` | high |
| 应用进程运行用户 | 非 root | high |
| sudo 免密配置 | 仅必要命令 | medium |

### 4.6 Docker 安全 — `{scripts}/check_docker.sh`

> **跨 skill 联动**:本节发现的镜像版本/镜像源问题,只**报告**不修复。具体修复路径:
> - 镜像 tag 不固定 / `:latest` / 浮动 tag → 引导用户跑 `/dwy-docker-image`(走 query_dockerhub.py 选 N-1 minor)
> - daemon 未配 registry-mirrors / 容器用境外 registry → 引导用户跑 `/dwy-mirror-source`(写阿里云/中科大/daocloud)

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `/var/run/docker.sock` 挂载到容器 | 仅可信容器 | **critical** |
| 容器以 root 运行 | 应使用非 root user | high |
| 端口绑定 | DB/Redis 等内部服务**不应** `0.0.0.0:5432` 暴露 | **critical** |
| 镜像 tag = `:latest` 或省略 tag | 固定到具体 patch | **critical** |
| 镜像 tag = 浮动 tag(`:stable` `:mainline` `:alpine` `:bookworm` `:slim` `:edge` `:nightly` 等) | 固定到具体 patch | high |
| 镜像 tag = 仅 major(`:7` `:16`) | 至少到 minor,推荐到 patch | high |
| 镜像 tag = `major.minor`(`:7.4`)| 固定到 patch(`:7.4.9`) | medium |
| 镜像 tag = `@sha256:...` digest | — | OK 加分 |
| `--privileged` 容器 | 无 | **critical** |
| Docker 版本 | 非已知 CVE 版本 | medium |
| Docker daemon 远程 API | 未暴露 2375/2376 公网 | **critical** |
| 容器 `RestartPolicy` | `always` 或 `unless-stopped`（**服务器重启后自动起来**） | **critical** |
| 容器 `RestartPolicy=no` 但正在 running | 不允许（重启会丢） | **critical** |
| 容器 `RestartPolicy=on-failure` | 不推荐（手动 stop / OOM 后不会重启） | high |
| daemon 日志驱动 `log-opts.max-size` | 已配置（≤ 100m，防容器日志写满磁盘） | high |
| **daemon `registry-mirrors`**(时区在 PRC 时) | 至少 1 个国内源(daocloud / aliyun / ustc / tsinghua) | high(PRC 无配置)/ info(境外) |
| **运行容器使用境外 registry**(`gcr.io` `ghcr.io` `k8s.gcr.io` `quay.io` `mcr.microsoft.com` `nvcr.io` `docker.elastic.co`)且时区在 PRC | 改用 `<registry>.m.daocloud.io` 前缀(`registry-mirrors` **不**对它们生效) | high |

### 4.7 依赖服务连通性 — `{scripts}/check_services.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 内部服务端口 | 仅内网/loopback 可达 | high |
| 健康检查端点 | 返回 200 | medium |
| 跨服务网络 | 应用 → DB/Redis 连通正常 | info |
| 防火墙规则 | iptables / ufw / firewalld 已启用 | high |
| 外部访问入口 | 仅 80/443 + SSH 端口 | high |

### 4.8 自愈与资源耗尽防护 — `{scripts}/check_resilience.sh`

服务器意外重启后能否自动恢复，以及在异常负载下能否守住底线。

**B. 系统服务开机自启**（默认清单 + 自动探测）

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `sshd` is-enabled | enabled（不起就再也连不上） | **critical** |
| `nginx` is-enabled | enabled | **critical** |
| `docker` is-enabled | enabled（影响所有容器） | **critical** |
| `postgresql` is-enabled | enabled | **critical** |
| `redis` / `redis-server` is-enabled | enabled | high |
| `frps` / `frpc` is-enabled（如部署） | enabled | high |
| `fail2ban` is-enabled（如安装） | enabled | medium |
| 应用主进程 systemd unit | enabled | **critical** |
| running 但 disabled 的服务 | 不应存在（重启即丢失） | high |
| 自动探测：`systemctl list-unit-files --state=enabled` | 输出供人工核对应用进程是否在内 | info |

**D. 资源耗尽防护**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `swap` 已配置 | ≥ 1GB（OOM 缓冲） | medium |
| 根分区使用率 | < 80% | medium（≥ 90% critical） |
| `/etc/logrotate.conf` 存在 | 是 | high |
| 关键服务有 `/etc/logrotate.d/<name>` | nginx / postgresql / redis 等都应有 | high |
| nginx / postgres / redis 进程 `ulimit -n` | ≥ 4096，建议 65535 | medium |
| `/proc/pressure/memory`（PSI） | 输出供观察当前内存压力 | info |
| 容器 `HostConfig.Memory` | 关键容器应有内存上限 | medium |

### 4.9 日志大小与防爆检查 — `{scripts}/check_logs.sh`

防止日志写满磁盘把整机拖垮。check_resilience.sh 的 D 节给的是宏观信号（`/var/log` 总大小、logrotate 是否存在），本节按"日志源"细化到单文件粒度，并基于容器存活时长粗估"撑天数"。

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| Docker 单容器 `*-json.log` 大小 | < 500 MB（daemon 配 log-opts max-size 时自动控） | high(>500 MB) / critical(>1 GB 且 daemon 无 log-opts) |
| 容器自身 `LogConfig.Config` 覆盖 | 至少有 `max-size`，否则继承 daemon | high（容器 + daemon 都没配） |
| Docker daemon `log-opts.max-size` | 已配置 ≤ 100m | high（同 check_docker.sh，本节关联展开） |
| Nginx access.log / error.log 单文件 | < 500 MB | high |
| `/etc/logrotate.d/nginx` | 存在 | high |
| `journalctl --disk-usage` | < 2 GB | medium / high(≥ 2 GB 且 SystemMaxUse 未配) |
| `/etc/systemd/journald.conf` `SystemMaxUse` | 已显式配置 | low |
| 应用日志目录（`/var/log/<svc>` / `/opt/*/logs` / `/home/*/logs` / `/srv/*/logs`） | 列出 Top 10 供人工核对 | info |
| 日志按当前 docker 容器存活时长粗估的撑天数 | > 90 天 | high(<90) / critical(<30) |

**输出规约：** 脚本会汇总 `Docker json-log + Nginx + journal + 应用日志` 总占用，对照根盘可用空间，给出"按 docker 当前增速预计可撑 N 天"的粗估。粗估只算 docker json-log 增量，不含数据库/应用日志业务增量，因此**结论偏乐观**，作为下限警示使用。

### 4.10 硬件识别与资源推荐 — `{scripts}/check_capacity.sh`

> 脚本只输出 raw（硬件规格 + 当前容器 mem_limit + Postgres/Redis 启动参数 + compose 资源声明）；主 Claude 用下表生成 "推荐 vs 当前" 对比报告。详细推荐规则与配比公式参考 `dwy-docker-image` skill 第二部分。

**容器资源推荐分级表（按宿主总内存）**

| 宿主总内存 | Backend mem_limit | Postgres mem_limit / shm_size / shared_buffers / effective_cache_size | Redis mem_limit / maxmemory |
|-----------|-------------------|--------------------------------------------------------------------|----------------------------|
| 2 GB | 384m | 512m / 128m / 128MB / 384MB | 256m / 180mb |
| 4 GB | 1g | 1g / 256m / 256MB / 768MB | 384m / 256mb |
| 8 GB | 2g | 2g / 512m / 512MB / 1536MB | 768m / 512mb |
| 16 GB | 4g | 4g / 1g / 1GB / 3GB | 1g / 700mb |

**配比原则**

- 容器 `mem_limit` 合计 ≤ 宿主总内存的 **65%**（预留 OS / 全局 nginx / 监控 agent / frpc 等）
- Postgres `shared_buffers` = 容器 `mem_limit` 的 **25%**
- Postgres `effective_cache_size` = 容器 `mem_limit` 的 **75%**
- Redis `maxmemory` = 容器 `mem_limit` 的 **70%**（剩 30% 给 RDB/AOF fork 时 COW 留 buffer）
- Redis `mem_limit` = `maxmemory ÷ 0.7` 向上取整

**对比报告格式（主 Claude 在报告里生成）**

```
| 服务 | 配置项 | 推荐(基于 X GB 宿主) | 当前 | 状态 |
|------|--------|--------------------|------|------|
| backend | mem_limit | 1g | 无 | ❌ 缺失 |
| db | mem_limit | 1g | 1g | ✅ |
| db | shared_buffers | 256MB | 128MB(默认) | ⚠️ 偏低 |
| db | shm_size | 256m | 64m(默认) | ⚠️ 偏低 |
| redis | maxmemory | 256mb | 256mb | ✅ |
| redis | mem_limit | 384m | 384m | ✅ |
| redis | appendonly | yes | no | ⚠️ 重启丢数据 |
```

**严重等级标记规则**

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 关键服务（redis / postgres / mysql / mongo / clickhouse / elasticsearch）容器无 `mem_limit` | 已设置 | high |
| Redis `--maxmemory` 未设置或 `0` | 已设置 | **critical** |
| Postgres `shared_buffers` > 宿主总内存 50% | ≤ 宿主总内存 50% | high |
| Postgres `shm_size` < 128m | ≥ 256m | medium |
| Redis 未启用 AOF（`--appendonly yes`） | yes | medium |
| 容器 `mem_limit` 合计 > 宿主总内存 75% | ≤ 65% | high |
| `mem_limit` 偏离推荐表 ±50% 以上（主 Claude 判定） | 在分级表区间内 | medium |

---

#### 日志大小推荐分级表（防容器日志无限增长撑爆磁盘）

依据是 `<根盘容量>` × `<容器规模>`,**单容器最大日志占用 = `max-size` × `max-file`**;所有容器日志合计应 ≤ 根盘可用空间的 **5%**(留磁盘给数据/swap/OS)。

**daemon 兜底配置(`/etc/docker/daemon.json` `log-opts`)**

| 宿主规格 | 根盘 | 容器数(估) | `max-size` | `max-file` | 单容器 quota | 备注 |
|---------|------|-----------|------------|-----------|-------------|------|
| 入门 | < 50 GB | 任意 | `10m` | `3` | ~30 MB | 2-4 GB VM 入门款,日志少留磁盘 |
| 标准 | 50-150 GB | ≤ 5 | `50m` | `5` | ~250 MB | 4-8 GB VM 通用 |
| 标准 | 50-150 GB | > 5 | `20m` | `5` | ~100 MB | 容器多则降单容器 quota |
| 大型 | > 150 GB | 任意 | `100m` | `5` | ~500 MB | 16+ GB 服务器,空间充裕 |

**容器级覆盖(compose `logging.options`,优先于 daemon)**

| 容器类型 | `max-size` | `max-file` | 理由 |
|---------|-----------|-----------|------|
| 数据库 (postgres / mysql / mongo) | `20m` | `10` | 慢查询日志价值高,保留更多滚动 |
| Web 反代 (nginx access log 走 stdout) | `50m` | `5` | 写入量大,单文件可放宽 |
| 应用后端 (FastAPI / Node 等) | `10m` | `5` | 通用 |
| Redis / 缓存类 | `10m` | `3` | 写入少,保留少 |

**daemon.json 模板**

```json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "50m",
    "max-file": "5",
    "compress": "true"
  }
}
```

**严重等级标记(脚本侧 + 主 Claude 对照表)**

| 判定 | 严重级 |
|------|--------|
| daemon 无 `log-opts.max-size` 且容器也无 `LogConfig.Config` | **critical** |
| daemon `max-size` > 推荐档 50% 以上(如根盘 < 50 GB 用 100m) | high |
| 容器无 `LogConfig.Config` 但 daemon 有兜底 | OK(走 daemon) |
| 容器 `LogConfig.Config` 设了但 max-size 偏离推荐档 ±50% | medium |
| 估算所有容器日志合计 > 根盘可用 5% | high |

---

### 4.11 凭证强度审计 — `{scripts}/check_secrets.sh`

> **强制脱敏:** 脚本能读密码,但**绝不输出明文**。所有结论以派生指标形式输出:`len=N classes=K strength=STRONG/MEDIUM/WEAK reason=xxx`。Claude 在生成报告时也**禁止**任何还原或猜测明文。

**检查范围(7 类凭证源):**

| # | 凭证源 | 提取方式 | 字段示例 |
|---|--------|---------|---------|
| 1 | `.env` 文件 | `find /home /opt /srv /root -name ".env*"` | `*PASSWORD* / *SECRET* / *TOKEN* / *KEY* / *AK / *SK` |
| 2 | docker 容器内联 env | `docker inspect --format '{{range .Config.Env}}'` | 同上 |
| 3 | Redis `--requirepass` | `docker inspect <redis> .Args` | requirepass 启动参数值 |
| 4 | Postgres `POSTGRES_PASSWORD` | docker container env | POSTGRES_PASSWORD |
| 5 | frps/frpc `auth.token` | find `frps.toml` `frpc.toml` `*.ini` | `token = ...` / `auth.token = ...` |
| 6 | DolphinDB 配置 | find `dolphindb.cfg` / `cluster.cfg` / `controller.cfg` | `password / passwd / adminPassword` |
| 7 | SSH 私钥 | `ssh-keygen -l -f ~/.ssh/id_*` | type + bits + perm |

**强度评级算法(脚本侧):**

| 条件 | 等级 | 严重级 |
|------|------|--------|
| 长度 < 8 | WEAK | **critical** |
| 字典词命中(内置 30 词:`password / admin / root / test / changeme / 123 / qwerty / welcome / letmein / secret` 等) | WEAK | **critical** |
| 长度 < 16 | MEDIUM | medium |
| 字符类 < 3(大小写/数字/符号) | MEDIUM | medium |
| 长度 ≥ 16 且 字符类 ≥ 3 | STRONG | OK |
| **高敏字段附加门槛**(SECRET/JWT/TOKEN/API_KEY/AK/SK/PRIVATE_KEY 类):长度 < 32 | — | high |

**SSH 私钥单独评级:**

| 类型 / 位数 | 严重级 |
|------------|--------|
| ED25519 | OK |
| RSA ≥ 4096 | OK |
| RSA 3072 | OK(建议升 ed25519) |
| RSA 2048 | medium |
| RSA < 2048 | **critical** |
| ECDSA(NIST 曲线) | medium(建议 ed25519) |
| DSA | **critical**(已废弃) |
| 私钥 perm ≠ 600/400 | high |

**输出脱敏样例:**

```
[/opt/ai-quant/quant-cloud/backend/.env]
  POSTGRES_PASSWORD     len=20 classes=4 strength=STRONG reason=ok           [OK]
  REDIS_PASSWORD        len=20 classes=4 strength=STRONG reason=ok           [OK]
  JWT_SECRET            len=12 classes=2 strength=MEDIUM reason=len<16       [!!] HIGH: 高敏字段建议 >= 32 字符随机串
  OSS_ACCESS_KEY_SECRET len=8  classes=1 strength=WEAK   reason=dict_match   [!!!] CRITICAL: 弱凭证, 必须立即轮换

[~/.ssh/id_rsa]
  type=RSA bits=2048 perm=600                                                [!] MEDIUM: RSA-2048 可接受但建议升 ed25519 或 RSA-4096
```

**禁止事项:**

- 禁止把密码明文(或片段、字符片段、md5/sha1 等单向哈希)写入报告
- 禁止"我看到密码是 xxx**" 这类提示性表述
- 禁止把 audit raw 输出原文复制到报告(必须只摘 strength/len/classes 三段)
- 禁止建议用户"轮换为 abc123" 这种举例(用 `openssl rand -base64 24` 这种**生成命令**)

**修复指引(脚本末尾自动输出):**

- 通用密码 ≥ 16 字符 + 三类:`openssl rand -base64 24 | tr -d '=+/' | cut -c1-20`
- 高敏 token ≥ 32 字符:`openssl rand -hex 32`
- SSH key 升级:`ssh-keygen -t ed25519 -C "your@email"`

---

## Step 5: 生成报告

报告必须为 Markdown 格式,**核心是"完整检查清单 + 状态可视化"** — 让用户一眼看到"检查了哪些 / 通过哪些 / 失败哪些 / 跳过哪些 / 未覆盖哪些"。

### 状态图标统一

| 图标 | 含义 | audit raw 输出触发条件 |
|------|------|---------------------|
| ✅ | 通过 | `[OK]` / `[OK+]` |
| ❌ | 失败 | `[!!!] CRITICAL` / `[!!] HIGH` / `[!] MEDIUM` / `[!] LOW` |
| ⊘ | 跳过 | `[i] xxx 未安装/未运行/不可读/跳过` |
| ❓ | 未覆盖 | 本 SKILL.md 4.x 表格里有但 audit 输出没出现该项 |

### 主 Claude 生成报告的强制流程

1. **拿"清单基准"**:本 SKILL.md `### 4.1` ~ `### 4.10` 各小节里的"**检查项**"列即为完整清单基准(共 ~120 项)
2. **拿"实际数据"**:用 Read 工具读 `/tmp/dwy_audit_<host>.txt`(run_all.sh 输出)
3. **逐项配对**:对清单每一项,在 audit 输出里 grep 对应关键词,按图标规则归类
4. **不可省略**:即使某项是 ✅,**也要列出来**;不能只列失败
5. **未覆盖项必须显式列出**:暴露脚本侧的盲区,作为后续补强依据

### 报告固定结构

```markdown
# 部署巡检报告

**目标:** {host}
**时间:** {iso8601}
**执行人:** {user}@{client}
**覆盖类别:** SSH / Nginx / DB / HTTPS / Env / Docker / Services / Resilience / Logs / Capacity / Secrets

---

## 摘要面板

| 指标 | 值 |
|------|---|
| 总检查项 | N |
| ✅ 通过 | A |
| ❌ 失败 | B |
| ⊘ 跳过 | C |
| ❓ 未覆盖 | D |
| **通过率** | **A / (A+B) = X%** |

**失败按等级:**

| 等级 | 数量 |
|------|------|
| 🔴 Critical | N |
| 🟠 High | N |
| 🟡 Medium | N |
| 🔵 Low | N |
| ⚪ Info | N |

**整体评估:** [一句话结论:可放行 / 需立即处理 / 建议优化]

---

## 完整检查清单

> 按 SKILL.md 4.1-4.10 分组,每节一张表,节标题带通过率。
> 表头四列固定:`#` / `检查项` / `严重级` / `状态` / `实际值/备注`

### 4.1 SSH 安全 (8/10 ✅)

| # | 检查项 | 严重级 | 状态 | 实际值 / 备注 |
|---|--------|--------|------|--------------|
| 1 | PermitRootLogin | critical | ✅ | prohibit-password |
| 2 | PasswordAuthentication | high | ❌ | yes(期望 no) |
| 3 | PermitEmptyPasswords | critical | ✅ | no |
| 4 | Port | medium | ⊘ | sshd_config 不可读(无 sudo) |
| 5 | Protocol | high | ✅ | 2 |
| 6 | MaxAuthTries | medium | ✅ | 3 |
| 7 | LoginGraceTime | low | ❓ | audit 输出未提及该项 |
| 8 | AllowUsers / AllowGroups | medium | ❌ | 未配白名单 |
| 9 | sshd 日志可见 | high | ✅ | journalctl _COMM=sshd 有输出 |
| 10 | fail2ban / sshguard | medium | ⊘ | 未安装 |

### 4.2 Nginx 配置 (12/19 ✅)
[同上格式...]

### 4.3 数据库暴露 (PostgreSQL 6/7 ✅, Redis 7/8 ✅)
[同上格式,PG 与 Redis 各一张子表]

### 4.4 HTTPS 证书 (4/5 ✅)
[...]

### 4.5 环境变量 / 文件权限 (5/6 ✅)
[...]

### 4.6 Docker 安全 (10/17 ✅)
[...]

### 4.7 依赖服务连通性 (4/5 ✅)
[...]

### 4.8 自愈与资源耗尽防护 (B 节 9/10 + D 节 6/7)
[B 系统服务开机自启 + D 资源耗尽防护 各一张子表]

### 4.9 日志大小与防爆检查 (7/9 ✅)
[...]

### 4.10 硬件识别与资源推荐 (容器资源 5/7 + 日志推荐 4/5)
**包含"推荐 vs 当前"对比表(见 SKILL.md 4.10),保留原对比格式**

### 4.11 凭证强度审计 (12/15 ✅)

> **强制脱敏:** 不论 audit raw 输出包含什么,清单中**只能列** `key 名 / len / classes / strength / reason / 严重级`,不得出现密码片段、明文、md5/sha1 哈希。

| # | 凭证源 | 字段 | 严重级 | 状态 | 强度详情 |
|---|--------|------|--------|------|---------|
| 1 | .env (cloud/backend) | POSTGRES_PASSWORD | critical | ✅ | len=20 classes=4 STRONG |
| 2 | .env (cloud/backend) | REDIS_PASSWORD | critical | ✅ | len=20 classes=4 STRONG |
| 3 | .env (cloud/backend) | JWT_SECRET | high | ❌ | len=12 classes=2 MEDIUM(高敏字段建议 ≥ 32) |
| 4 | docker env (cloud-db) | POSTGRES_PASSWORD | critical | ✅ | len=20 classes=4 STRONG |
| 5 | Redis --requirepass | (cloud-redis-1) | critical | ✅ | len=20 classes=4 STRONG |
| 6 | frps.toml | auth.token | high | ⊘ | 未发现 frp 配置 |
| 7 | DolphinDB cluster.cfg | adminPassword | high | ⊘ | 未发现 DolphinDB 配置 |
| 8 | ~/.ssh/id_ed25519 | type+bits | high | ✅ | ED25519 perm=600 |
| 9 | ~/.ssh/id_rsa | type+bits | medium | ❌ | RSA-2048 perm=600(建议升 ed25519) |

---

## 失败项详情(按严重级排序)

> 仅展开 ❌ 项,按 critical → high → medium → low 排序;每条一段。

### 🔴 [CRITICAL] PostgreSQL listen_addresses 设置为 *

- **类目:** 4.3 数据库暴露
- **位置:** /etc/postgresql/15/main/postgresql.conf:59
- **当前值:** `listen_addresses = '*'`
- **期望值:** `listen_addresses = 'localhost,10.0.0.0/8'`
- **风险:** 数据库监听所有网卡,若防火墙未拦截则公网可直接访问数据库
- **修复建议:**
  1. 编辑 postgresql.conf 改为内网地址
  2. 配合 pg_hba.conf 限制源 IP
  3. 重载: `sudo systemctl reload postgresql`
- **参考:** https://www.postgresql.org/docs/current/runtime-config-connection.html

### 🟠 [HIGH] ...

[继续列出每条 ❌ 项,严格按等级降序]

---

## 跳过项 (⊘)

> 透明化暴露:列出所有 ⊘ 项 + 跳过原因,让用户决定是否追加权限/装服务后重跑。

| 类目 | 检查项 | 跳过原因 |
|------|--------|---------|
| 4.1.4 SSH | Port | sshd_config 不可读(用户无 sudo) |
| 4.1.10 SSH | fail2ban / sshguard | 未安装 |
| ... | ... | ... |

---

## 未覆盖项 (❓) — 暴露脚本盲区

> 这些项 SKILL.md 列了但 audit 输出没出现 — 说明脚本未实际检查或未输出该项判定。
> **行动:** 反馈到 dwy-deploy-audit skill 维护者,后续补强 check_*.sh。

| 类目 | 检查项 | 备注 |
|------|--------|------|
| 4.1.7 SSH | LoginGraceTime | check_ssh.sh 未输出该项 |
| ... | ... | ... |

---

## 跨 skill 衍生建议

根据本次失败项归纳的可执行后续动作:

- 镜像版本不固定 (4.6) → 跑 `/dwy-docker-image` 选 N-1 minor
- daemon 未配 registry-mirrors (4.6) → 跑 `/dwy-mirror-source` 写国内源
- 容器资源偏离推荐 (4.10) → 改 `docker-compose.prod.yml` 的 mem_limit/maxmemory
- ...

---

## 未覆盖范围(本 skill 边界外)

- 未执行渗透测试(如需要,使用 `/dwy-pentest`)
- 未审计应用层逻辑(SQL 注入 / XSS 等)
- 未审计应用日志内容(只看大小,不看内容合规)
```

---

## Step 6: 修复建议(只输出,不执行)

**严格禁止：**

- 自动执行任何修改命令
- 通过 SSH 直接修改服务器配置
- 重启任何服务
- 主动建议"我来帮你修复"

**允许：**

- 在报告中给出修复命令片段(供用户复制)
- 解释修复后的影响和验证方法
- 推荐修复优先级

---

## 严重等级定义

| 等级 | 含义 | 示例 |
|------|------|------|
| **critical** | 公网可直接利用、数据可被直接访问、root 可被远程获取 | DB 公网暴露无密码、SSH 允许 root 密码登录 |
| **high** | 需特定条件可被利用,可能导致权限提升或敏感信息泄漏 | 弱 TLS、无 fail2ban、密码登录开启 |
| **medium** | 配置不规范但短期不致命,长期累积风险 | 默认端口、无 HSTS、autoindex 开 |
| **low** | 最佳实践类,可选改进 | OCSP Stapling、CSP header |
| **info** | 信息记录,非问题 | 当前 Nginx 版本号 |

---

## 禁止事项

- **禁止**未确认 SSH 连接信息就开始检查
- **禁止**执行任何写入命令(`sed -i`、`systemctl restart`、`echo > file`、`iptables -A` 等)
- **禁止**主动 `tcpdump` / `pg_dump` / `redis-cli FLUSHALL` 等高负载或破坏性命令
- **禁止**将检查结果中的敏感信息(密钥片段、密码哈希)完整输出到报告(必须脱敏)
- **禁止**在未获得用户明确授权时审计**非用户自有**的服务器(出现陌生 host 必须二次确认所有权)
- **禁止**自动修复发现的问题
- **禁止**省略 critical / high 等级的问题不报告
