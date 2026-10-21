# dwy-app-auth

Private Python distribution `dwy-app-auth==0.1.0`, import `dwy_app_auth`. Requires `dwyeapi==0.11.1`. The Google user entry and administrator Cookie entry are separate. No dependency on app-cloud or cloud-kernel; no environment variables or global database are read by this package. Do not upload this package to a public index.

User authentication uses the existing Google subject identity, app-scoped SQL tables, 15-minute opaque access tokens, rotating refresh families, device revocation and transactional account deletion. The application owns its engine/session factory, metadata and Alembic history. No migrations are created or run automatically. Google configuration accepts one explicit Web OAuth audience; a missing configuration closes login.

```python
from fastapi import FastAPI
from dwyeapi.exceptions import register_exception_handlers
from dwy_app_auth import AuthService, GoogleConfig, OfficialGoogleVerifier, build_auth_tables, install_auth_routes

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
from dwy_app_auth.admin import AdminAuthConfig, install_admin_auth

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
