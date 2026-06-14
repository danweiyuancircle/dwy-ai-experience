## 权威安全文档检索

当 `references/checks-*.md` 无法覆盖以下场景时，先查权威文档，再下结论：

- 目标版本是否存在已知高危 CVE
- 某个配置项语义不确定
- audit 输出与经验规则冲突
- 用户要求“按官方安全文档”解释
- 需要把新发现沉淀回本 skill

---

## 检索优先级

1. **官方产品文档 / 官方安全页**
2. **官方维护的版本公告 / 安全公告 / release notes**
3. **CISA KEV / NVD / CVE 记录**
4. **OWASP Cheat Sheet**

禁止把论坛、博客、聚合站当一手依据。

---

## 固定检索策略

### 1. 先查“配置语义”

按产品名 + 配置项名搜索，优先官方文档：

- `OpenSSH sshd_config PermitRootLogin PasswordAuthentication official`
- `nginx ssl_protocols ssl_stapling add_header official`
- `PostgreSQL listen_addresses ssl official`
- `Redis protected mode bind requirepass official`
- `Docker daemon remote access docker.sock log-driver official`

目标：确认该配置项的**官方含义、默认值、启用条件、版本约束**。

### 2. 再查“版本安全”

当 audit 输出包含版本号时，按 `产品 + 版本 + CVE` 搜：

- `nginx 1.24.0 CVE`
- `postgresql 15.6 CVE`
- `redis 7.2.4 CVE`
- `docker engine 26.1.4 CVE`

目标：确认是否存在：

- 高危未修复漏洞
- 该版本已被官方宣布 EOL
- 配置项依赖的最小版本门槛

### 3. 最后查“硬化基线”

当官方文档只解释语义、不直接给安全基线时，补查：

- `OWASP Docker Security Cheat Sheet`
- `CISA Known Exploited Vulnerabilities`
- 产品官方 security / advisories 页面

目标：把“语义”转成“审计期望值”。

---

## 推荐来源清单

### SSH / OpenSSH

- OpenSSH `sshd_config` 手册：`https://man.openbsd.org/sshd_config`

重点看：

- `PermitRootLogin`
- `PasswordAuthentication`
- `PermitEmptyPasswords`
- `AllowUsers` / `AllowGroups`

### Nginx / HTTPS

- Nginx headers 模块：`https://nginx.org/en/docs/http/ngx_http_headers_module.html`
- Nginx SSL 模块：`https://nginx.org/en/docs/http/ngx_http_ssl_module.html`

重点看：

- `add_header ... always`
- `ssl_protocols`
- `ssl_stapling`
- `ssl_stapling_verify`

### PostgreSQL

- 连接与认证：`https://www.postgresql.org/docs/current/runtime-config-connection.html`

重点看：

- `listen_addresses`
- `port`
- `ssl`

### Redis

- Redis Security：`https://redis.io/docs/latest/operate/oss_and_stack/management/security/`

重点看：

- `bind`
- `protected mode`
- 外网暴露风险

### Docker

- Docker Engine security：`https://docs.docker.com/engine/security/`
- Docker daemon remote access：`https://docs.docker.com/engine/daemon/remote-access/`
- Docker logging drivers：`https://docs.docker.com/engine/logging/configure/`
- OWASP Docker Security Cheat Sheet：`https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html`

重点看：

- daemon attack surface
- `docker.sock`
- TCP remote API
- capabilities / privileged
- `log-driver`

### CVE / 漏洞情报

- CISA KEV：`https://www.cisa.gov/known-exploited-vulnerabilities-catalog`
- NVD：`https://nvd.nist.gov/`

用途：

- 判断某版本是否已有**被在野利用**漏洞
- 给 critical / high 分级补外部依据

---

## 审计时何时必须检索

以下情况不得只靠本地规则：

1. `references/checks-*.md` 写着“非已知 CVE 版本”，但当前没附具体依据
2. audit 输出出现明确版本号，且版本看起来偏旧
3. 某项默认值与当前发行版可能有漂移
4. 需要判断某项该算 `critical` 还是 `high`
5. 用户要求“给官方文档链接”

---

## 沉淀规则

如果检索得到**稳定、可复用、非一次性**的信息，必须回写：

- 配置语义类 → 更新对应 `references/checks-network.md` / `references/checks-data.md` / `references/checks-runtime.md`
- 检索方法类 → 更新本文件
- 仅某产品某版本临时漏洞 → 不写入长期规则，只在本次报告引用

判断“适合沉淀”的标准：

- 下次审计大概率还会遇到
- 不是某个用户私有环境特例
- 可以转化为明确检查项、期望值或检索模板

---

## 输出要求

当使用了外部文档，报告里的失败项详情至少补 1 个权威链接：

- 官方文档优先
- 漏洞项可追加 CISA KEV 或 NVD
- 不引用二手博客作唯一依据

格式建议：

```markdown
- 参考:
  - https://www.postgresql.org/docs/current/runtime-config-connection.html
  - https://nvd.nist.gov/
```
