# dwy-auth

New integrations use `AuthRuntime` with application-owned users and a replaceable `SessionBackend`. See [runtime integration](../../../docs/auth-runtime-integration.md). The authentication core is independent of EAPI and FastAPI; the legacy service, HTTP and administrator interfaces below require EAPI when used.

Python distribution `dwy-auth==0.1.1`, import `dwy_auth`. Install the independent core from public PyPI with `pip install "dwy-auth==0.1.1"`. For the EAPI integration and compatibility interfaces, install `pip install "dwyeapi[auth]==0.12.1"`; this includes `dwy-auth` and the EAPI email SDK. Source is available in the public repository; registry releases use `.github/workflows/publish-auth.yml` with GitHub Actions OIDC. The Google user entry and administrator Cookie entry are separate. No dependency on app-cloud or cloud-kernel; no environment variables or global database are read by this package.

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
