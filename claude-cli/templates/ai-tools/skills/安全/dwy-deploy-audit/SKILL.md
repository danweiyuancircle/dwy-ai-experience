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

**脚本目录：** `./scripts/`（以下简称 `{scripts}`）

**详细检查规则索引：**

| 文件 | 何时读 | 覆盖 |
|------|--------|------|
| `references/checks-network.md` | 即将运行 4.1 / 4.2 / 4.4 / 4.7 类检查或解读其输出时 | SSH / Nginx / HTTPS / 依赖服务连通性 |
| `references/checks-data.md` | 即将运行 4.3 / 4.5 / 4.11 类检查或解读其输出时 | 数据库暴露 / 环境变量 / 凭证强度 |
| `references/checks-runtime.md` | 即将运行 4.6 / 4.8 / 4.9 / 4.10 类检查或解读其输出时 | Docker / 自愈 / 日志防爆 / 资源推荐 |
| `references/security-doc-search.md` | 本地 checks 不够判定、需要查官方安全文档、需要按版本追 CVE、或需要把新规则沉淀回 skill 时 | 权威文档检索策略 / 官方来源清单 / 沉淀规则 |

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
4. 权威文档检索  → 必要时查官方文档 / CVE / OWASP,补足判定依据
5. 分类检查      → SSH / Nginx / DB / HTTPS / Env / Docker / Services / Resilience / Logs / Capacity / Secrets(主 Bash 调用 run_all.sh,12 路并行)
6. 生成报告      → 按等级聚合,Markdown 格式
7. 修复建议      → 每条问题给出修复方向(不执行)
```

**共 7 步，按顺序执行。**

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

## Step 4: 权威文档检索（必要时执行）

当出现以下任一情况，**先读** `references/security-doc-search.md`，再用 WebSearch / 官方站点检索：

1. `references/checks-*.md` 里只有抽象规则，没有给出当前版本依据
2. audit 输出出现了明确版本号，需要判断是否存在已知高危 CVE
3. 配置项语义、默认值、版本门槛不确定
4. 用户明确要求“按官方安全文档”解释
5. 本次发现适合沉淀回长期规则

### 强制来源顺序

1. 官方产品文档 / 官方 security 页面
2. 官方 release notes / advisories
3. CISA KEV / NVD / CVE
4. OWASP Cheat Sheet

**禁止**把论坛、博客、AI 聚合页当唯一依据。

### 强制检索输出

每次外部检索至少产出 3 个字段：

| 字段 | 说明 |
|------|------|
| `source` | 权威来源 URL |
| `claim` | 从文档得到的明确结论 |
| `impact` | 这条结论如何影响本次分级 / 判定 / 修复建议 |

### 需要沉淀时怎么做

- 可复用的配置语义 / 检查基线 → 回写对应 `references/checks-*.md`
- 可复用的检索方法 / 来源入口 → 回写 `references/security-doc-search.md`
- 单次版本漏洞情报 → 只写进本次报告,不固化成长期规则

---

## Step 5: 分类检查（并行执行）

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

**各类检查内容如下（详细规则见 references/）：**

### 4.1 SSH 安全 — `{scripts}/check_ssh.sh`

检查 SSH 配置是否禁用密码登录、root 直登、是否暴露默认 22 端口，是否启用 fail2ban 等登录防爆机制。

→ 详细检查项、期望值、严重级见 `references/checks-network.md` §「4.1 SSH 安全」

### 4.2 Nginx 配置 — `{scripts}/check_nginx.sh`

检查 Nginx 的 HTTPS 强跳、TLS 协议/密码套件、安全 header、限流（limit_req / limit_conn）、慢速攻击防护与敏感路径暴露。

→ 详细检查项、期望值、严重级见 `references/checks-network.md` §「4.2 Nginx 配置」

### 4.3 数据库暴露 — `{scripts}/check_db.sh`

检查 PostgreSQL / Redis 的监听地址、公网可达性、认证强度、SSL、保护模式与版本 CVE。

→ 详细检查项、期望值、严重级见 `references/checks-data.md` §「4.3 数据库暴露」

### 4.4 HTTPS 证书 — `{scripts}/check_https.sh`

检查证书有效期、域名匹配、证书链完整性、自签证书与 OCSP Stapling。

→ 详细检查项、期望值、严重级见 `references/checks-network.md` §「4.4 HTTPS 证书」

### 4.5 环境变量 / 文件权限 — `{scripts}/check_env.sh`

检查 `.env` 文件权限与位置、nginx 静态目录是否泄漏敏感文件、`/etc/shadow` 权限、应用进程运行用户与 sudo 配置。

→ 详细检查项、期望值、严重级见 `references/checks-data.md` §「4.5 环境变量 / 文件权限」

### 4.6 Docker 安全 — `{scripts}/check_docker.sh`

检查 docker.sock 挂载、容器 root 运行、内部端口公网暴露、镜像 tag 固定度、`--privileged`、daemon 远程 API、RestartPolicy、daemon 日志驱动、registry-mirrors 与境外 registry 使用。

→ 详细检查项、期望值、严重级（含跨 skill 联动指引）见 `references/checks-runtime.md` §「4.6 Docker 安全」

### 4.7 依赖服务连通性 — `{scripts}/check_services.sh`

检查内部服务端口可达性、健康检查端点、跨服务连通、防火墙与外部访问入口。

→ 详细检查项、期望值、严重级见 `references/checks-network.md` §「4.7 依赖服务连通性」

### 4.8 自愈与资源耗尽防护 — `{scripts}/check_resilience.sh`

检查关键服务是否 systemd enable（重启自启）、swap、根分区使用率、logrotate、ulimit、内存压力与容器内存上限。

→ 详细检查项、期望值、严重级（B 节系统服务开机自启 + D 节资源耗尽防护）见 `references/checks-runtime.md` §「4.8 自愈与资源耗尽防护」

### 4.9 日志大小与防爆检查 — `{scripts}/check_logs.sh`

按"日志源"细化到单文件粒度，检查 Docker json-log、Nginx 日志、journal、应用日志，并基于容器存活时长粗估"撑天数"。

→ 详细检查项、期望值、严重级与撑天数粗估说明见 `references/checks-runtime.md` §「4.9 日志大小与防爆检查」

### 4.10 硬件识别与资源推荐 — `{scripts}/check_capacity.sh`

输出宿主硬件规格 + 当前容器 mem_limit + Postgres/Redis 启动参数 + compose 资源声明；主 Claude 对照分级表生成"推荐 vs 当前"对比报告。

→ 容器资源推荐分级表、配比原则、对比报告格式、严重等级标记与日志大小推荐分级表见 `references/checks-runtime.md` §「4.10 硬件识别与资源推荐」

### 4.11 凭证强度审计 — `{scripts}/check_secrets.sh`

读取 7 类凭证源（.env / docker env / Redis requirepass / Postgres POSTGRES_PASSWORD / frps/frpc auth.token / DolphinDB / SSH 私钥），输出强度派生指标 `len / classes / strength / reason`，**强制脱敏不输出明文**。

→ 完整检查范围、强度评级算法、SSH 私钥单独评级、脱敏样例、禁止事项与修复指引见 `references/checks-data.md` §「4.11 凭证强度审计」

---

## Step 6: 生成报告

报告必须为 Markdown 格式,**核心是"完整检查清单 + 状态可视化"** — 让用户一眼看到"检查了哪些 / 通过哪些 / 失败哪些 / 跳过哪些 / 未覆盖哪些"。

### 状态图标统一

| 图标 | 含义 | audit raw 输出触发条件 |
|------|------|---------------------|
| ✅ | 通过 | `[OK]` / `[OK+]` |
| ❌ | 失败 | `[!!!] CRITICAL` / `[!!] HIGH` / `[!] MEDIUM` / `[!] LOW` |
| ⊘ | 跳过 | `[i] xxx 未安装/未运行/不可读/跳过` |
| ❓ | 未覆盖 | 本 skill `references/checks-*.md` 4.x 表格里有但 audit 输出没出现该项 |

### 主 Claude 生成报告的强制流程

1. **拿"清单基准"**:`references/checks-network.md` / `references/checks-data.md` / `references/checks-runtime.md` 各小节里的"**检查项**"列即为完整清单基准(共 ~120 项)
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

> 按 references 中 4.1-4.11 分组,每节一张表,节标题带通过率。
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
**包含"推荐 vs 当前"对比表(见 references/checks-runtime.md §4.10),保留原对比格式**

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

> 这些项 references/checks-*.md 列了但 audit 输出没出现 — 说明脚本未实际检查或未输出该项判定。
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

## Step 7: 修复建议(只输出,不执行)

**严格禁止：**

- 自动执行任何修改命令
- 通过 SSH 直接修改服务器配置
- 重启任何服务
- 主动建议"我来帮你修复"

**允许：**

- 在报告中给出修复命令片段(供用户复制)
- 解释修复后的影响和验证方法
- 推荐修复优先级
- 给出本次实际引用过的权威文档 URL

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
