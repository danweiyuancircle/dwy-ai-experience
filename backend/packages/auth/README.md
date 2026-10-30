# dwy-auth

New integrations use `AuthRuntime` with application-owned users and a replaceable `SessionBackend`. See [runtime integration](../../../docs/auth-runtime-integration.md). The authentication core is independent of EAPI and FastAPI; the legacy service, HTTP and administrator interfaces below require EAPI when used.

Python distribution `dwy-auth==0.2.0`, import `dwy_auth`. Install the independent core from public PyPI with `pip install "dwy-auth==0.2.0"`. For EAPI integration and compatibility interfaces, install `pip install "dwyeapi[email]==0.12.1" "dwy-auth==0.2.0"`; the older `dwyeapi[auth]==0.12.1` aggregate extra pins authentication to 0.1.1. Source is available in the public repository; registry releases use `.github/workflows/publish-auth.yml` with GitHub Actions OIDC. The Google user entry and administrator Cookie entry are separate. No dependency on app-cloud or cloud-kernel; no environment variables or global database are read by this package.

Upgrading runtime hosts from 0.1.1 requires a host-owned Alembic revision: add the `auth_runtime_credential_versions` table from `build_runtime_tables`, plus nullable `subject` and `credential_version` columns on `auth_runtime_email_challenges`. Snapshot these definitions in the revision; do not import a future builder inside historical migrations. Existing accounts and sessions remain intact; application admission remains opt-in.

When upgrading a preview integration, update both the dependency name and Python imports. The new wheel exports only `dwy_auth`; no legacy namespace alias is shipped. The source package is `backend/packages/auth` and release tags use `dwy-auth@VERSION`.

User authentication uses the existing Google subject identity, app-scoped SQL tables, 15-minute opaque access tokens, rotating refresh families, device revocation and transactional account deletion. The application owns its engine/session factory, metadata and Alembic history. No migrations are created or run automatically. Google configuration accepts one explicit Web OAuth audience; a missing configuration closes login.

```python
from fastapi import FastAPI
from dwyeapi.exceptions import register_exception_handlers
from dwy_auth import AuthService, GoogleConfig, OfficialGoogleVerifier, build_auth_tables, install_auth_routes

# metadata and sessions are owned by this application.
service = AuthService("myapp", sessions, build_auth_tables(metadata), OfficialGoogleVerifier(
    GoogleConfig(client_id=google_client_id)
))
app = FastAPI()
register_exception_handlers(app)
install_auth_routes(app, service, authorization_limit=8192)
```

`dwyeapi.identity.Principal` and `IdentityVerifier` are the canonical identity contract. `create_identity_dependency(app_id, verifier, authorization_limit=...)` binds business routes to an explicitly chosen application/verifier. `install_auth_routes` uses its AuthService by default and accepts an explicitly injected trusted `identity_verifier` for existing host adapters. The host must apply request-body limits before parsing (the Google token schema separately limits token length to 16384 characters). Validation errors installed by this package omit submitted credentials.

```python
from dwy_auth.admin import AdminAuthConfig, install_admin_auth

admin = install_admin_auth(app, AdminAuthConfig(
    username=admin_username,
    password=admin_password,
    secure_cookie=True,
    origin="https://admin.example.com",
))
# Protect host-owned business routes with Depends(admin.require_admin).
# Also add Depends(admin.same_origin) to host-owned mutation routes.
```

Admin paths remain `/api/admin/auth/login`, `/me`, `/logout`. Cookies remain HttpOnly, SameSite=Strict, scoped to `/api/admin`; production callers explicitly enable Secure and enforce their deployment password policy. A configured origin is matched exactly. Without one, an Origin header must match the request scheme/host; forwarded headers are not trusted. Requests without Origin preserve the existing API contract. Standalone admin installation bounds auth request bodies at 4096 bytes and forbids caching. A host that already protects every admin path can pass `install_security=False` and retain that middleware.

Admin state is in memory: restarting revokes every session, with one host worker required for this existing implementation. Sessions, rate limits and credentials are independent of user access/refresh tokens. The binding grants no user Principal and contains no business queries or configuration storage.

Run `pytest tests` from this directory with the dev extra installed. `tests/packaging_smoke.py` additionally runs against installed wheels in a clean environment and asserts the host, kernel and business packages are absent. PostgreSQL concurrency cases need an explicitly provided `APP_CLOUD_TEST_POSTGRES_URL`.

## Email/password authentication

Email/password is opt-in. Email accounts have stable random UUIDs and an independent unique `(app_id,email)` credential; email normalization only trims and lowercases. A Google account with the same email is never merged. New/reset passwords require at least 15 Unicode code points and at most 72 UTF-8 bytes; login accepts nonempty existing passwords up to 72 bytes. Passwords are never trimmed or truncated. EAPI bcrypt executes in a bounded worker pool (4 concurrent, at most 32 queued/running per service); cancellation keeps running work charged to this budget.

```python
from dwy_auth import EmailAuthConfig, EapiEmailCodeSender, SessionPolicy
from dwyeapi.providers.email import make_email_provider

# email_settings and challenge_secret come from the host's validated settings.
# Every worker must share the same secret (at least 32 bytes). Never commit it.
provider = make_email_provider(email_settings)
service = AuthService(
    "myapp", sessions, build_auth_tables(metadata), google_verifier,
    email_sender=EapiEmailCodeSender(provider),
    email_config=EmailAuthConfig(challenge_secret=challenge_secret),
    session_policy=SessionPolicy(refresh_ttl=180 * 86400, rolling_refresh=True),
)
install_auth_routes(app, service)
```

Use the matching EAPI version containing `EmailProviderBase.send_verification_code`. This public transport-only method reuses existing Resend templates/domain policy and does not access Redis. Match the provider template TTL with `EmailAuthConfig.code_ttl`. The host owns the email sender/provider lifecycle. Without email configuration all email routes fail closed with `EMAIL_NOT_CONFIGURED`.

Both authentication HTTP installers accept an optional `Accept-Language` header (maximum 512 characters) for email codes. Any valid `zh`/`zh-*` range with nonzero quality selects Chinese; missing, malformed, excluded (`zh;q=0`), or other languages select English. The subject, HTML, and plain-text body use the same language. The current Apple client explicitly sends `zh` for a Chinese first preferred language and `en` otherwise. Language is passed per call and never changes code identity or resend limits.

Custom senders must accept `send(email, code, purpose, *, language="en")`; custom EAPI providers must accept `_send(target, code, *, language="en")`. Programmatic calls may pass `send_email_code(..., language="zh")`; only `zh` and `en` are supported. Configure `resend.subject` for Chinese and `resend.subject_en` for English. English brand taglines/slogans use `brand_tagline_en`/`brand_slogan_en` (empty by default), without falling back to Chinese promotional copy. Brand names remain as configured.

| POST path | JSON input | SUCCESS data |
|---|---|---|
| `/api/v1/auth/email/code` | `email,purpose` (`register` or `password_reset`) | `challenge_id,expires_in,resend_after,code_length` |
| `/api/v1/auth/register` | `email,password,code,challenge_id,device_id` | Existing `TokenResponse`; automatically logged in |
| `/api/v1/auth/login` | `email,password,device_id` | Existing `TokenResponse` |
| `/api/v1/auth/password/reset` | `email,password,code,challenge_id` | `{"status":"completed"}`; all existing user sessions revoked |

Codes are six digits, expire after 300 seconds and have a 60-second resend cooldown by default. Response `expires_in` and `resend_after` report actual remaining database deadlines after delivery; a delivery that outlasts the challenge fails and removes that challenge. Only a successful delivery activates a challenge; a new delivered challenge invalidates older challenges for the same app/email/purpose. The database stores an HMAC bound to app/email/purpose/challenge, never the code. Conditional updates make consumption single-use; failed-attempt counters commit independently so business rollback cannot replenish attempts. Each challenge allows at most five attempts. Atomic SQL budgets apply per app, peer IP, purpose/email and action; send limits are 50/IP/hour, 1000/app/hour, 10/email/purpose/hour; verification is 100/IP/15min and 20/email/purpose/15min; login is 100/IP/15min and 10/email/15min. Expired counters/challenges are pruned on use. Configure trusted proxy middleware at the host if deployed behind a proxy; request forwarding headers are not read directly. Continue enforcing host request-body and ingress limits.

Errors never echo submitted secrets. Public codes are `EMAIL_INVALID`, `PASSWORD_INVALID`, `EMAIL_PURPOSE_INVALID`, `EMAIL_CODE_INVALID` (wrong/expired/used/exhausted), `EMAIL_ALREADY_REGISTERED`, `CREDENTIALS_INVALID`, `EMAIL_RATE_LIMITED`, `EMAIL_NOT_CONFIGURED`, `EMAIL_DELIVERY_FAILED`. Schema validation uses the existing `VALIDATION_ERROR` envelope. Failed delivery remains charged to resend budgets to prevent abusive retries. Delivery to existing and unknown accounts follows the same public send contract.

The default `SessionPolicy()` retains the existing fixed 30-day refresh deadline and 15-minute access lifetime. Explicit rolling policy extends refresh validity to 180 days on successful refresh. Old refresh digests remain replay evidence for at most `replay_retention` (default 30 days) and expire independently, so normal 15-minute refreshes do not accumulate a lifetime 4096 cap. The 4096 limit still bounds *unexpired* evidence (normal 30-day use is 2880); an abusive burst gets 429 without invalidating the current token. Refresh replay, device revocation and account deletion remain enforced. Account deletion removes email credentials/challenges transactionally; it preserves the anonymized UUID for independent purchase ledgers.

### Host Alembic migration

Fresh applications include all six auth tables via `build_auth_tables(metadata)` in their own migration. Existing Google-only databases must migrate before enabling the new package; `metadata.create_all` does not alter the old non-nullable subject column. Add a revision to the **host** Alembic history:

```python
from alembic import op
from dwy_auth.migrations import upgrade_email_auth

# revision/down_revision belong to the host migration history.
def upgrade():
    upgrade_email_auth(op)
```

The helper makes `auth_users.google_subject` nullable and creates `auth_password_credentials`, `auth_email_challenges`, `auth_rate_limits`; existing UUIDs, sessions and Google subjects remain untouched. PostgreSQL alters the column in place. SQLite uses Alembic batch mode; hosts with foreign keys enabled must follow Alembic's SQLite foreign-key PRAGMA procedure outside the transaction. Downgrade is intentionally host-owned: email-only users have null Google subjects, so restoring NOT NULL requires an explicit data-retention decision. Do not run this helper at application startup. `tests/test_email_auth.py` migrates a populated legacy Google schema and verifies both existing sessions and new email registration afterward.

## Apple 原生登录（dwy-auth 0.1.1 / dwyeapi 0.12.1）

已通过 GitHub Actions OIDC 发布到公开 PyPI；独立配置与迁移步骤见 [Apple 后端接入](../../../docs/apple-auth-integration.md)。

使用 `dwy_auth.apple.AppleSignInConfig`、`AppleGateway`、`dwy_auth.apple_auth.AppleAuthService` 和 `dwy_auth.apple_storage.build_apple_tables(metadata)`。多步骤 Apple 授权使用独立挑战/登录接口；不能把 Apple ID token 塞进通用 external credential 接口绕过 nonce 和授权码验证。

宿主提供自己的 AuthRuntime、业务主体、会话撤销回调及 Alembic 迁移，并在现有 `install_runtime_auth` 后安装 `dwyeapi.auth_apple.install_apple_auth`。把 service 注册为 runtime 的 apple provider，驱动 `process_revocations()`，在业务删号事务内调用 `prepare_delete(db, subject)`；其返回值为撤销任务 ID，可用于区分本地删除完成与上游撤销 pending。签名 Key 与 Fernet token_encryption_key 只保留服务端，不能复用内购配置或按邮箱合并账号。

原生 Swift 接入使用共享 AuthCore 与 AuthAppleIOS，说明见仓库根 `ios/Docs/APPLE_AUTH.md`。每个应用独立配置 client_id、密钥、数据库与业务 UUID，代码共享不代表跨产品 SSO。

## 已登录账号的邮箱与登录方式管理

`AuthRuntime.send_email_update_code(principal, email, *, reauthentication, remote_key="local", language="en")`
消费 `purpose="email_update"` 的 `VerifiedIdentity`，将验证码绑定当前 app、subject、规范化目标邮箱和凭据代次。
`AuthRuntime.update_email(principal, email, code, challenge_id, *, new_password=None, remote_key="local")`
在宿主事务中消费挑战、更新邮箱凭据与已验证主邮箱、撤销所有旧会话并签发同一 subject 的新会话。
首次添加密码必须提供符合共享密码政策的新密码；已有密码可保留。Google issuer/sub 不变，邮箱不用于自动合并。
公开 `send_email_code` 不接受 `email_update`，因此注册/重置验证码不能绕过重新认证。

启用变更的宿主适配器实现 `EmailSubjectAdapter.update_email(db, subject, email)`，与挑战/凭据/会话共同提交，不能自行提交或更换 subject。
未实现此接口的宿主在发码前返回 `EMAIL_UPDATE_NOT_CONFIGURED`，既有注册/登录不受影响。
主邮箱经用户验证后，宿主不得用 Google profile 邮箱覆盖它。

EAPI `install_runtime_auth` 额外提供：

- POST `/api/v1/auth/email/update/code`：`email` 与 `reauthentication`，需要当前 Bearer。
- POST `/api/v1/auth/email/update`：`email/code/challenge_id/new_password?`，需要当前 Bearer，返回既有 token/user 信封。
- GET `/api/v1/auth/identities`：当前主体可用入口的 `LoginIdentity` 数组，仅含 `kind/value/provider/issuer`；密码、版本摘要与 token 不进入响应。

重新认证 `method` 仍为 `email/username/external`；Google 使用 `method=external, identifier=google, credential=<ID token>`。
已有外部绑定/解绑接口继续执行主体证明、唯一归属与最后一种可用登录方式保护。

宿主 Alembic revision 在启用前升级 `build_runtime_tables` 使用的实际前缀：

- 已有 `email_challenges` 增加可空 `subject VARCHAR(255)`、`credential_version VARCHAR(64)`。
- 新建 `credential_versions`，`app_id VARCHAR(32)` 与 `subject VARCHAR(255)` 为联合主键，`generation VARCHAR(36) NOT NULL`。

旧挑战两列保持 NULL，不补认旧验证码。代次由首次凭据变更创建；改邮箱、改密、重置、绑定和解绑都会同事务轮换代次并核销未完成挑战。
凭据内容恢复成旧值也不会恢复旧挑战，发信中的旧快照同样失效。共享包不在启动时执行迁移。


## 可选应用准入

- `AuthRuntime(..., admission=...)` 接受 `AuthAdmission`：`prepare(proof)` 在数据库事务外验证本次请求证明，`admit(db, subject, prepared)` 在主体、凭据、会话共用事务内验证或写入业务归属。准入不得自行提交事务。仅配置准入时，在 `prepare` 外网工作前复用独立 `admission-ip` 预算（每个可信来源 900 秒最多 100 次）；refresh 使用与登录相同的来源解析。默认不配置，不强制业务资格。
- 对外登录调用 `runtime.login(method, ..., admission_proof=...)`；注册调用 `runtime.register_email_session(...)`。配置准入后，独立 `register_email`、登录用途 `authenticate`、`issue` 拒绝绕过；内部 `_db` 参数只供受信运行时事务组合，不能暴露给请求。
- `refresh(..., admission_proof=...)` 必须提供本次证明。会话后端需实现可选 `before_lock(db, principal)` 纯主体锁检查（CAS 前，保持 account→session 锁序）和 `before_rotate(db, principal)` 准入写入回调，并在原有刷新事务内、CAS 与配额检查成功后且生成新 token 前调用，准入失败必须回滚尚未生效的轮换。未配置准入仍兼容原会话实现；自定义后端启用准入前必须实现这个合同。
- EAPI 认证请求总预算为 163840 字节；`admission_proof` 最多 131072 个 UTF-8 字节，日志和模型表示不包含原文。邮箱发码、忘记密码不签发会话，不要求准入证明；变更邮箱会签发新会话，因此同样要求证明。

Apple 专用 `AppleAuthService.login(..., admission_proof=...)` 使用同一准入配置：先验证证明，再消费 Apple 挑战与授权码；准入归属、账号、授权与会话共同提交，拒绝时回滚并持久化上游撤销任务。

### Apple-only 账号的管理重新认证

先用当前 Bearer 向 `/api/v1/auth/apple/challenges` 提交 `purpose=reauth_email_update`、`reauth_bind` 或 `reauth_unlink`；服务端将挑战绑定当前 subject 与具体操作。原生授权使用服务端原始 nonce。
管理请求的 `reauthentication` 使用 `method=external, identifier=apple`，其 `credential` 为包含 `challenge_id`、`identity_token`、`authorization_code` 的 JSON 字符串（最多 32768 个 UTF-8 字节）。EAPI 通过 `AppleAuthService.reauthenticate` 兑换一次性 code 并生成当前主体、限用途、单次消费的 proof；跨主体、跨操作或重放均拒绝。通用 Apple 登录仍拒绝单凭据路径，不能恢复旧 `AppleIdentityProvider` 或客户端自建 nonce 方案。

## JWT 会话滑动有效期

`JWTSessionBackend(..., rolling_refresh=True)` 在每次刷新成功时，把会话期限延到当时起 `refresh_ttl` 秒（默认 30 天）；第 25 天刷新后到期日为第 55 天。默认 `False` 保持签发起固定期限，不影响已有调用方。普通业务请求不会续期；已经过期或撤销的会话不能恢复。客户端继续使用现有刷新接口和返回的轮换凭据，无需修改协议或数据库结构。

滑动模式下，每个已消费 refresh 摘要从消费时起再保留 `refresh_ttl` 秒用于重放撤销，刷新成功时只清理同应用、同 family 的到期摘要。4096 条上限约束有效证据窗口，不再累计终身刷新次数；短时间超额仍返回 `REFRESH_QUOTA_EXCEEDED` 并撤销当前 family，需重新登录。CAS 轮换、期限更新与准入写入共同提交，失败回滚不会消费旧凭据或延长期限。
