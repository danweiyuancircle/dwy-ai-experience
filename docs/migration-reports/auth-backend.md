# Auth backend migration — Task 2

Implemented `dwy-app-auth==0.1.0` (`dwy_app_auth`) in `modules/auth/backend`, based on EAPI 0.11.1. Google-only user sessions and administrator Cookie authentication have separate entrypoints. The new package imports neither app-cloud nor cloud-kernel. Runtime third-party versions are inherited unchanged from cloud-auth: SQLAlchemy 2.0.49, Pydantic 2.13.4 and google-auth[requests] 2.62.0. EAPI replaces the original cloud-kernel dependency; no additional runtime third-party library was introduced. The package carries `Private :: Do Not Upload` metadata.

## Preserved contracts

- Google signature/issuer/audience/time validation, stable subject identity, opaque access tokens, rotating refresh families and replay revocation, quotas and absolute expiry are preserved.
- Device listing/revocation, account cleanup transaction/rollback, deleted-account guards and cross-app/user/session boundaries are preserved. Applications still own metadata, engines, transactions, migration history, IAP catalogs and business cleanup.
- EAPI `dwyeapi.identity` now owns the only `Principal` and `IdentityVerifier` classes plus the existing deny-default implementation. cloud-kernel reexports those exact objects. A Pydantic envelope accepts an old-path Principal as the same instance.
- EAPI `create_identity_dependency` binds the app ID, verifier and Authorization limit explicitly. User HTTP installation accepts an optional trusted verifier and explicit input budget. All three app-cloud application factories pass their existing runtime verifier/configuration, preserving internal adapter behavior.
- `dwy_app_auth.admin` receives `AdminAuthConfig` explicitly. It retains PBKDF2 authentication, bounded rate/session maps, hashed in-memory sessions, exact configured Origin checking, Strict/HttpOnly/Secure/path Cookie flags and immediate logout revocation. User access/refresh tokens cannot authenticate administrators; admin cookies cannot authenticate users.
- The host retains its middleware protecting every admin business route. The package independently protects standalone auth routes and sanitizes validation errors. The extracted binding supplies `require_admin` and `same_origin`; host business queries and configuration persistence remain in app-cloud.
- cloud-auth is a compatibility shim; legacy submodule imports point to the actual shared modules, preserving existing monkeypatch/import behavior. The old host `AdminAuth(HostSettings)` entry is a small explicit configuration adapter.

Source SHA256 inventory: `auth-backend-sources.json`. The migration-file inventory `auth-backend-migrations.json` covers 16 application/admin migration resources; all 16 hashes remained unchanged at final verification. No database, real environment file or cache was migrated.

## Verification performed

All commands below were executed, not forecast. Python was 3.11.17. Commands with `app-cloud` as working directory refer to the existing external consumer workspace.

| Check | Executed command / method | Result |
|---|---|---|
| Original auth/admin/kernel baseline | `uv run --frozen pytest -q tests/auth tests/admin tests/kernel` in app-cloud | 146 passed, 2 skipped |
| Missing new identity/admin APIs | pytest on new `backend/tests/test_identity.py` and module `tests/test_admin.py` before implementation | 9 expected failures: new modules absent |
| Explicit host-verifier contract before implementation | module `test_auth.py -k explicit_verifier` | 1 expected failure: unsupported new keyword |
| New package plus EAPI identity | pytest `backend/tests/test_identity.py modules/auth/backend/tests` with new source paths | 51 passed, 2 skipped |
| Consumer complete regression after installing actual new wheels | app-cloud `.venv/bin/python -m pytest -q` | 326 passed, 5 skipped, 1 existing Starlette/httpx deprecation warning |
| New package/EAPI changed-file lint | Ruff on `modules/auth/backend`, EAPI identity source/test | Passed |
| Consumer complete lint | app-cloud `.venv/bin/ruff check .` | Passed |
| Fresh builds | `uv build --wheel backend`, `uv build modules/auth/backend`, app-cloud `uv build --all-packages`, each to the validation wheel directory | Passed |
| Standalone authentication wheel | Fresh venv; install the actual EAPI/auth wheels with locked third-party constraints, aiosqlite and httpx; run `modules/auth/backend/tests/packaging_smoke.py` outside source with empty PYTHONPATH | Passed; app-cloud, cloud-kernel, cloud-auth and all three application modules absent |
| Three standalone application wheels | One fresh venv per adbox/quadrant/rightflow; install locked external dependencies, then explicitly reinstall the exact newly built host/kernel/shim/shared-auth/EAPI/IAP/current-app wheels; run app-cloud `tests/packaging_smoke.py <app>` outside source | All three passed |
| Packaging inspection | Inspect all 19 generated wheel/sdist archives | No real `.env`, database, bytecode, VCS, environment or cache entries; new auth wheel contains no host/kernel/shim/test packages |

Each application smoke ran its application and admin migration upgrade/check, checked fixed required table names independently of metadata, verified configuration writes/inheritance/conflicts/audit and persistence after host restart, exercised lifecycle/default-deny behavior and confirmed **both** other application packages and databases were absent. The quadrant environment also omits cloud-sync. This avoids stale path-package wheels or all-app installs masking a broken isolated artifact.

Baseline EAPI-wide regression was separately performed by the parent executor (248 passing before adding the two identity cases). This task ran the two new EAPI cases within the 51-case combined passing run; final aggregate CI remains owned by the parent executor.

## App-cloud file changes

Only these backend compatibility/dependency files were changed; existing administrator query/storage/configuration work and all migrations remain in place:

- `pyproject.toml`, `uv.lock`: shared auth/EAPI dependencies and local validation sources.
- `packages/cloud-auth/pyproject.toml`, `packages/cloud-auth/src/cloud_auth/__init__.py`: shim and legacy module aliases; remove duplicate `google.py`, `http.py`, `models.py`, `service.py`, `storage.py` implementations.
- `packages/cloud-kernel/pyproject.toml`, `packages/cloud-kernel/src/cloud_kernel/identity.py`: EAPI 0.11.1 and canonical type reexports.
- `packages/{adbox,quadrant,rightflow}-server/src/{adbox,quadrant,rightflow}_server/app.py`: explicit existing verifier/Authorization-budget injection only.
- `src/app_cloud/admin/auth.py`, `src/app_cloud/admin/http.py`: compatibility adapter and authentication binding; business handlers retained.
- `tests/auth/test_compatibility.py`, `tests/auth/TEST_CASES.md`, `tests/packaging_smoke.py`: canonical identities and installed versions/isolated artifact assertions.

No frontend, business query/storage, root CI workflow or private publishing script was changed by this task.

## Remaining integration / environment boundaries

- app-cloud local uv sources currently point to the migration checkout for implementation validation. **They are not final consumer configuration.** The parent executor will replace them with the private release/tag source and regenerate the consumer lock after private 0.4.0 publication. Do not ship the temporary worktree paths.
- `ci/uv.lock` was resolved from the official PyPI index while retaining the existing seven-day cutoff. The first default-mirror resolution failed because the mirror lacks upload metadata; official resolution succeeded, but initial package download reached the local 180-second command timeout. Parent executor owns continuation of `uv sync --project ci --frozen --default-index https://pypi.org/simple` and final aggregate CI. No cutoff was weakened.
- No PostgreSQL test DSN was provided in this task: two standalone-auth and five app-cloud PostgreSQL-dependent tests were skipped. SQLite SQL/HTTP, concurrency/replay, deletion and installation checks passed. Real Google network/OAuth login and production PostgreSQL were not claimed as tested.
- Administrator sessions remain process-local and reset on restart, matching the source implementation; use a single host worker. Secure cookies and trusted public origin must be supplied explicitly by the deployment.
- No stage, commit, push or publication was performed by this task. Private distribution, final consumer source replacement and CI/release acceptance remain with the parent executor.
