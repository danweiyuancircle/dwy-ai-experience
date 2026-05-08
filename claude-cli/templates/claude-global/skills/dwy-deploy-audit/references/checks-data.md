# Deploy Audit — 数据与凭证安全检查规则

> **何时读这份：** 当 AI 即将运行 4.3 / 4.5 / 4.11 类检查或解读其输出时读取本文件。

本文件聚焦"数据与凭证安全"维度的检查规则、严重度判定与输出格式。涵盖数据库暴露、环境变量与文件权限、凭证强度审计。

脚本目录简称 `{scripts}` = `~/.claude/skills/dwy-deploy-audit/scripts/`。

---

## 4.3 数据库暴露 — `{scripts}/check_db.sh`

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

---

## 4.5 环境变量 / 文件权限 — `{scripts}/check_env.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| `.env` 文件权限 | `600` 或更严 | **critical** |
| `.env` 文件位置 | 不在 nginx `root` 目录下 | **critical** |
| `nginx -T` 可达静态目录 | 不包含 `.env`、`.git`、密钥 | **critical** |
| `/etc/shadow` 权限 | `640` 或 `600` | high |
| 应用进程运行用户 | 非 root | high |
| sudo 免密配置 | 仅必要命令 | medium |

---

## 4.11 凭证强度审计 — `{scripts}/check_secrets.sh`

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
