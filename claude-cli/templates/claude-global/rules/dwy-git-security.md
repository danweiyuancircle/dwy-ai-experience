---
description: Git 提交前文件与敏感内容扫描规则(全局,每次 add/commit 都应检查)
---

# Git 提交安全规则

每次 `git add` 或 `git commit` 前按本规则扫描暂存区。发现违规**立即停止并提示用户确认**。

## 一、禁止提交的文件

| 类型 | 示例 |
|---|---|
| 环境变量 | `.env`, `.env.*`, `*.env` |
| SSH 密钥 | `id_rsa`, `id_ed25519`, `*.pem`, `*.key` |
| 证书 | `*.p12`, `*.pfx`, `*.jks`, `*.keystore` |
| 数据库 | `*.sql`(含真实数据)、`*.dump`, `*.sqlite` |
| 原始数据 | `*.xlsx`, `*.csv`(含用户/学生等敏感数据) |
| 日志 | `*.log` |
| Docker 卷 | `pgdata/`, `cache/*.json` |

## 二、禁止提交的内容(敏感模式)

**总则**:代码、文档、规则文件、注释里禁止出现真实的 API Key / Token / 密码 / IP / 凭证,即使作为"示例"也不行。GitHub Secret Scanning 不区分上下文,真实格式的 key 写在文档里也会触发泄露告警。示例必须用明显的假值(`sk-xxxxxxxxxxxx`、`your-key-here`、`192.168.x.x`)。

| 类型 | 匹配模式 |
|---|---|
| API Key | `sk-[a-zA-Z0-9]{20,}` |
| AWS Key | `AKIA[0-9A-Z]{16}` |
| 密码赋值 | `password\s*[:=]\s*["'][^"']{4,}` |
| 数据库连接串 | `://\w+:[^@\s]+@` |
| 私钥内容 | `-----BEGIN (RSA \|EC )?PRIVATE KEY-----` |
| Token | `token\s*[:=]\s*["'][a-zA-Z0-9_\-]{20,}` |
| Secret | `secret\s*[:=]\s*["'][^"']{8,}` |
| 服务器 IP+端口 | `\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d+` |
| SSH 连接 | `ssh\s+.*@\d{1,3}\.\d{1,3}` |

**例外(不算违规)**:`.env.example` 里的占位符;从环境变量读取(`os.getenv("API_KEY")`);`localhost`/`127.0.0.1` 的连接串;文档里的假数据;配置文件的空字符串默认值。

## 三、违规处理

检测到违规时:

1. **立即停止** `git add` / `git commit`
2. **列出违规项**:文件 + 行号 + 匹配的敏感模式 + 脱敏摘要(如 `sk-5522****dc3`)
3. **建议**:加入 `.gitignore` / 移到 `.env` / 用环境变量
4. **等用户明确确认**后才能继续;确认提交时,commit body 附注释 `GIT-SECURITY: 用户已确认提交此内容`

## 四、已提交敏感数据

若发现已在 git 历史中:立即通知用户,**建议先轮换凭证**,然后提供清理命令(不自动执行,待确认):

- `git filter-repo --path <file> --invert-paths --force`
- 或 `bfg --delete-files <filename>`
