# 账户与会话测试

在 `backend/packages/auth` 目录执行 `python -m pytest tests -q`，覆盖独立用户认证与管理员认证测试。

| 文件 | 覆盖行为 |
| --- | --- |
| `test_apple_auth.py` | raw nonce 的密文与摘要、过期/跨应用/并发单次挑战、重复与并发首次登录稳定主体、显式绑定、签发失败回滚与补偿撤销、真实 SecretStr 配置、删号事务与撤销 lease/退避、通知去重及在途授权屏障、只撤 Apple 会话 |
| `test_auth.py` | Google subject 关联账户、邮箱不作为关联键、应用隔离、设备不作为账户身份、仅持久化凭据摘要、轮换与并发单胜者、退出范围、凭据绝对到期、账户禁用、HTTP 验证与保密、Google 配置闭锁；PostgreSQL 并发测试仅在配置测试数据库 URL 时执行 |
| `test_google.py` | 官方 Google JWT 验签边界、issuer/audience/有效期/签名/用户字段校验及上游错误闭锁，具体以文件内测试为准 |
| `test_apple.py` | 本地 RSA/EC 密钥真实验签与 client_secret 签名；单应用 audience、issuer、固定 RS256、iat/exp、nonce 与授权码兑换身份一致性；JWKS 缓存/轮换/single-flight/未知 kid 请求预算；未验证邮箱、缺 refresh token、撤销及跨应用拒绝；兑换后验证失败或取消时补偿撤销，补偿失败以 SecretStr 安全交付持久化重试；通知签名/时效/jti/events 格式校验；网络异常保密、配置密钥校验与默认传输超时/响应大小/重定向拒绝。挑战消费与通知去重由服务层测试覆盖 |
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

## Email/password authentication (`test_email_auth.py`)

- Real SQLite registration/login preserves stable UUIDs, normalizes only case/whitespace, stores bcrypt/HMAC only and never merges Google users.
- Concurrent challenge consumption and sends have one winner; app/purpose isolation, expiry, resend invalidation, five-attempt limits and committed login/send budgets reject replay/abuse.
- Password reset revokes old access/refresh sessions; account deletion removes credentials and challenges.
- HTTP code/register/login/reset envelopes, automatic login, no-store tokens, sensitive validation, 15-character minimum, UTF-8 72-byte ceiling and password whitespace preservation.
- EAPI transport adapter does not use Redis; failed delivery leaves no active challenge.
- Rolling sessions survive multiple months, prune expired evidence, retain replay revocation and bound recent evidence without a lifetime refresh cap; default fixed-policy regression remains in `test_auth.py`.
- Cancellation does not release running bcrypt concurrency; populated legacy Google migration preserves old UUIDs/sessions and allows email-only users.

- Delivery latency returns remaining code/cooldown seconds (including zero cooldown); delivery at code expiry fails and removes the challenge.
- An in-flight old-password login paused after bcrypt is rejected after password reset commits, without issuing another session.
- HTTP rate keys use the ASGI peer address and ignore arbitrary X-Forwarded-For/Forwarded headers.
- Both old authentication HTTP routes and the generic runtime pass Chinese/English language per request; Chinese variants and nonzero weighted Chinese select Chinese, all other or missing headers select English.
- `test_email_language.py`: missing, unknown, mixed-case, traditional/simplified Chinese, weighted, excluded, and malformed language ranges normalize to exactly `zh` or `en`.

- `packaging_smoke.py`: new wheel-only environment verifies distribution `dwy-auth==0.1.0`, import namespace `dwy_auth` and absence of the legacy namespace; fixed six-table database inspection, EAPI transport availability, English default/Chinese header propagation and template language, explicit rolling policy/secret/mail fixture assembly, email registration/login/reset revocation, Google/admin isolation and deletion; no real email is sent.

## Runtime 邮箱变更与登录入口 (`test_runtime.py`)

- Google 首次添加邮箱密码保持 subject/issuer/sub，后续 Google 登录保留主邮箱。
- 当前账号限用途重新认证；过期、跨主体与重放证明不发码。
- 改邮箱后旧邮箱失效、新邮箱密码可用；保持 subject/device，同事务撤销旧会话并签发新会话。
- 挑战的 app/subject/email/purpose/期限/凭据版本隔离；公开发码拒绝 email_update。
- 邮箱被其他账号占用、会话后端失败整体回滚，不合并账号或核销可重试挑战。
- 真实 SQLite 并发消费只有一个成功；任一凭据变更永久核销其他挑战，绑定再解绑恢复原内容也不复活发信中的旧快照。
- 入口列表仅包含当前账号已启用且可用的入口，不输出凭据摘要；已有最后登录方式保护保持。
- `backend/tests/test_auth_runtime.py` 通过真实 HTTP/JWT 验证两接口、当前 Bearer、受限字段、主邮箱资料与旧 access/refresh 撤销。

Review 修补回归：password_reset 发码绑定 subject/凭据代次，改邮箱核销旧邮箱的 legacy NULL subject 重置挑战；重置在主体锁后重查邮箱归属及挑战版本。`test_reset_rechecks_email_owner_after_subject_lock` 使用 SQLite 适配器边界模拟；`test_postgres_reset_waiting_for_email_update_lock_cannot_revoke_rotated_session` 使用专用 PostgreSQL URL 验证真实锁交错，未配置时明确跳过。

## 准入与 Apple 管理整合

- `backend/packages/auth/tests/test_admission.py`：注册、首次外部登录、会话签发失败时原子回滚；低层入口不能绕过准入；外部证明独立预算；拒绝刷新不消费旧 token。
- `backend/packages/auth/tests/test_apple_auth.py`：Apple 准入先于上游授权，拒绝后回滚主体与会话并保留撤销任务；Apple 管理挑战绑定当前主体与用途，proof 和挑战只消费一次，非法材料不访问上游。
- `backend/tests/test_auth_apple.py`：管理挑战要求当前会话，邮箱管理将 Apple 重新认证路由到专用授权服务；请求总预算覆盖准入证明。

## JWT 滑动会话 (`test_session_backend.py`)

- 默认固定期限保持不变；`rolling_refresh=True` 第25天刷新续期到第55天，后续成功刷新继续顺延30天。
- 到期边界与已撤销会话不能续期；准入拒绝回滚期限、凭据与摘要写入，旧 refresh 仍可重试。
- 连续活跃跨多个月清理到期摘要，不累计终身配额；保留同 family 有效证据，不清理其他 family 的记录。
- 旧 refresh 消费后保留30天，即使超过最初会话到期日，重放仍撤销后继；窗口到期清理后旧摘要不再撤销后继。
- 固定与滑动两种模式均验证单次消费、真实 SQLite 并发仅一次胜出、重放撤销、4096有效摘要边界；可选 PostgreSQL 并发测试需要 `APP_CLOUD_TEST_POSTGRES_URL`。
