# 账户与会话测试

使用 `/Users/chances/freetime/ios/app-cloud/.venv/bin/pytest tests/auth -q` 执行。

| 文件 | 覆盖行为 |
| --- | --- |
| `test_auth.py` | Google subject 关联账户、邮箱不作为关联键、应用隔离、设备不作为账户身份、仅持久化凭据摘要、轮换与并发单胜者、退出范围、凭据绝对到期、账户禁用、HTTP 验证与保密、Google 配置闭锁；PostgreSQL 并发测试仅在配置测试数据库 URL 时执行 |
| `test_google.py` | 官方 Google JWT 验签边界、issuer/audience/有效期/签名/用户字段校验及上游错误闭锁，具体以文件内测试为准 |
| `test_lifecycle.py` | 旧 refresh 摘要重放撤销后继凭据且不影响独立 family；设备按本人聚合、有界游标分页、整设备撤销与应用隔离；账户删除去标识、全凭据撤销、再次登录新 user_id；同事务业务清理成功与失败回滚；其他应用账户保留；伪造/过期会话拒绝；HTTP 鉴权、未知查询字段拒绝、分页上限、设备不存在统一 404、删除返回 completed |
| `test_growth.py` | 每账户未到期会话配额包含已撤销会话；每 family 的旧刷新摘要配额；429 不轮换凭据或删除有效重放证据；配额按账户/应用隔离；登录与刷新在绝对到期边界清理本人摘要和会话；到期清理在返回错误前提交；SQLite 开启真实外键验证先摘要后会话的删除顺序；配置 PostgreSQL URL 后验证并发登录不会超额 |

刷新 family 由单个 `auth_sessions` 行代表。轮换前摘要写入 `auth_refresh_history`，有效期沿用原始 refresh 绝对到期时间；重放错误在撤销事务提交后才返回。账户删除保留用户主键及 IAP 历史归属，不允许后续 Google 登录继承旧用户主键。

每账户最多保留 **100 条未到期会话**，包含已撤销会话，防止反复登录/退出持续刷写；超限返回 `SESSION_QUOTA_EXCEEDED`（HTTP 429）。每个 family 最多保留 **4096 条旧刷新摘要**，覆盖 30 天内每 15 分钟刷新一次的 2880 次常规用量；超限返回 `REFRESH_QUOTA_EXCEEDED`（HTTP 429），需要重新登录建立新 family。配额检查与写入都在账户行锁保护下完成。

登录与刷新只清理当前账户、当前应用的到期记录，先删 `expires_at <= now` 的历史摘要，再删 `refresh_expires_at <= now` 且已无剩余重放证据的会话；未到期摘要不会因为达到配额而被删除。安全清理先提交，再报告配额或过期凭据错误。此机制是请求触发的本账户清理，不包含后台全库垃圾回收。

## Independent package boundary

The four Google/user/session test files were migrated from app-cloud with their assertions preserved. HTTP fixtures now use FastAPI plus EAPI directly; they import neither cloud-kernel nor app-cloud.

- `test_auth.py::test_explicit_verifier_and_authorization_budget_preserve_host_boundary`: host-provided trusted verifier and bounded Authorization configuration remain explicit and effective.
- `test_admin.py::test_admin_cookie_contract_and_user_token_isolation`: user Bearer cannot become admin; exact Origin, Secure/HttpOnly/Strict/path flags, hashed sessions and immediate logout revocation.
- `test_admin.py::test_admin_rejects_oversized_or_secret_inputs_and_limits_attempts`: bounded auth body, sanitized validation, no-store, five-attempt window and Retry-After.
- `test_admin.py::test_admin_config_requires_a_valid_explicit_origin`: malformed origins and URLs containing paths/credentials are rejected.
- `packaging_smoke.py`: installed wheel versions and EAPI Principal, user Google/device/deletion flow, admin/user isolation; app-cloud, cloud-kernel, cloud-auth and every business module must be absent.
