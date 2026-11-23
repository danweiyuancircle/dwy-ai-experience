# Deploy Audit — 网络与传输安全检查规则

> **何时读这份：** 当 AI 即将运行 4.1 / 4.2 / 4.4 / 4.7 类检查或解读其输出时读取本文件。

本文件聚焦"网络与传输安全"维度的检查规则、严重度判定与输出格式。涵盖 SSH、Nginx、HTTPS 证书、依赖服务连通性。

脚本目录简称 `{scripts}` = `../scripts/`。

---

## 4.1 SSH 安全 — `{scripts}/check_ssh.sh`

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

---

## 4.2 Nginx 配置 — `{scripts}/check_nginx.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| HTTP → HTTPS 强制跳转 | 80 端口 return 301 至 https | **critical** |
| `ssl_protocols` | 仅 `TLSv1.2 TLSv1.3` | high |
| `ssl_ciphers` | 排除弱加密(RC4/3DES/MD5) | high |
| `server_tokens` | `off` | medium |
| `access_log` | 已开启 | **high**(用户特别要求) |
| `error_log` | 已开启,级别 ≥ warn | high |
| `client_max_body_size` | 显式配置,业务非上传 ≤ 10m | medium |
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

**Nginx 版本判定补充：**

- 先查官方配置语义：
  - headers 模块：`https://nginx.org/en/docs/http/ngx_http_headers_module.html`
  - SSL 模块：`https://nginx.org/en/docs/http/ngx_http_ssl_module.html`
- 再查版本安全：
  - 搜索词：`nginx <version> security advisory`、`nginx <version> CVE`
  - 优先来源：Nginx 官方公告、NVD、CISA KEV
- 分级规则：
  - 命中 **CISA KEV** 或存在明确在野利用记录 → **critical**
  - 命中高危 CVE（建议按 CVSS ≥ 7.0 参考），但未见在野利用 → high
  - 未命中高危 CVE，但版本明显老旧且缺少后续安全修复依据 → medium
- 如果只是配置项（如 `ssl_protocols`、`ssl_stapling`、`add_header ... always`）语义不清，不按“版本风险”报，改为引用官方模块文档解释配置风险。

---

## 4.4 HTTPS 证书 — `{scripts}/check_https.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 证书有效期 | 剩余 > 30 天 | high (< 7 天 critical) |
| 证书域名匹配 | CN/SAN 包含访问域名 | **critical** |
| 证书链完整 | 中间证书已配置 | high |
| 自签证书 | 仅内网允许,公网为 critical | varies |
| OCSP Stapling | 已启用 | low |

---

## 4.7 依赖服务连通性 — `{scripts}/check_services.sh`

| 检查项 | 期望值 | 严重级 |
|--------|--------|--------|
| 内部服务端口 | 仅内网/loopback 可达 | high |
| 健康检查端点 | 返回 200 | medium |
| 跨服务网络 | 应用 → DB/Redis 连通正常 | info |
| 防火墙规则 | iptables / ufw / firewalld 已启用 | high |
| 外部访问入口 | 仅 80/443 + SSH 端口 | high |
