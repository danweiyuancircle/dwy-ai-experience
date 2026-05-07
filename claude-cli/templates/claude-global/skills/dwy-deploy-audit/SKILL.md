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
4. 分类检查      → SSH / Nginx / DB / HTTPS / Env / Docker / Services
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

## Step 4: 分类检查

按以下顺序执行各类检查脚本，**每类独立成段**，单类失败不影响其他类继续：

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

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `/var/run/docker.sock` 挂载到容器 | 仅可信容器 | **critical** |
| 容器以 root 运行 | 应使用非 root user | high |
| 端口绑定 | DB/Redis 等内部服务**不应** `0.0.0.0:5432` 暴露 | **critical** |
| 镜像 tag | 非 `:latest` (生产) | medium |
| `--privileged` 容器 | 无 | **critical** |
| Docker 版本 | 非已知 CVE 版本 | medium |
| Docker daemon 远程 API | 未暴露 2375/2376 公网 | **critical** |

### 4.7 依赖服务连通性 — `{scripts}/check_services.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 内部服务端口 | 仅内网/loopback 可达 | high |
| 健康检查端点 | 返回 200 | medium |
| 跨服务网络 | 应用 → DB/Redis 连通正常 | info |
| 防火墙规则 | iptables / ufw / firewalld 已启用 | high |
| 外部访问入口 | 仅 80/443 + SSH 端口 | high |

---

## Step 5: 生成报告

报告必须为 Markdown 格式，固定结构：

```markdown
# 部署巡检报告

**目标:** {host}
**时间:** {iso8601}
**执行人:** {user}@{client}
**覆盖类别:** SSH / Nginx / DB / HTTPS / Env / Docker / Services

## 摘要

| 等级 | 数量 |
|------|------|
| Critical | N |
| High | N |
| Medium | N |
| Low | N |
| Info | N |

**整体评估:** [一句话结论:可放行 / 需立即处理 / 建议优化]

## 详细问题清单

### [CRITICAL] PostgreSQL listen_addresses 设置为 *

**位置:** /etc/postgresql/15/main/postgresql.conf:59
**当前值:** `listen_addresses = '*'`
**期望值:** `listen_addresses = 'localhost,10.0.0.0/8'`
**风险:** 数据库监听所有网卡,若防火墙未拦截则公网可直接访问数据库
**修复建议:**
  1. 编辑 postgresql.conf 改为内网地址
  2. 配合 pg_hba.conf 限制源 IP
  3. 重载: `sudo systemctl reload postgresql`
**参考:** https://www.postgresql.org/docs/current/runtime-config-connection.html

[继续列出每条问题...]

## 通过项

- [x] SSH 已禁用 root 登录
- [x] Nginx 已配置 HSTS
- ...

## 未覆盖项

- 未执行渗透测试(如需要,使用 dwy-pentest)
- 未审计应用层逻辑(SQL 注入 / XSS 等)
- 未审计应用日志内容
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
