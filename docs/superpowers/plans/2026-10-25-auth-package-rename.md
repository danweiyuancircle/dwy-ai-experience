# Rename the authentication package to dwy-auth

**Goal:** Publish the reusable Python authentication library as `dwy-auth==0.1.0`, importable as `dwy_auth`, without the former app-auth naming in active interfaces.

**Scope:** Rename `backend/packages/app-auth` to `backend/packages/auth` and its import package to `dwy_auth`. Update EAPI integration, dependency manifests/lockfile, release workflows, active documentation, package policy tests, and isolated wheel acceptance. Preserve historical archive records and prior completed plans. App-cloud's pinned old wheels and existing unrelated changes remain separate consumer migration work.

**Release contract:** `.github/workflows/publish-auth.yml` publishes on `dwy-auth@*` tags, validates metadata/tag parity, and uses GitHub OIDC. PyPI authorization is project-specific; an existing `dwyeapi` publisher does not authorize `dwy-auth`. The new Pending Publisher must use project `dwy-auth`, owner `danweiyuancircle`, repository `dwy-ai-experience`, workflow `publish-auth.yml`, and no environment unless the job is changed to declare one. No publication is triggered by this rename.

## Tasks

- [x] Run existing authentication tests before refactoring; update artifact/namespace expectations and observe failure against the old installed wheels.
- [x] Rename package/module and update all active shared-library references and OIDC workflow identity.
- [x] Validate lockfile consistency and run backend/authentication/package-policy regression tests.
- [x] Build fresh wheels and install actual artifacts into a new environment; check new distribution/import names and absence of the old ones, real HTTP mail language, and existing authentication smoke contracts.
- [x] Review remaining old-name references, final diff, and release readiness. Do not publish, push tags, or change PyPI permissions during this task.

## Verification

- Baseline and renamed authentication package: 161 passed, 3 PostgreSQL-dependent tests skipped. New namespace smoke fails as expected against the old installed wheels.
- Full backend plus renamed authentication tests: 445 passed, 3 PostgreSQL-dependent tests skipped, 2 existing Starlette deprecation warnings.
- Release policy tests: 8 passed. The new workflow filename and package path failed before the rename and passed afterward.
- `uv lock --project ci --check --offline --default-index https://pypi.org/simple`: consistent, 60 packages resolved without dependency version changes.
- Actual new wheels installed together into a fresh environment pass `python -I packages/auth/tests/packaging_smoke.py`; module paths come from that environment's site-packages, fixed database contracts hold, and Chinese/English mail behavior remains available.
- Installed distribution is `dwy-auth==0.1.0`, module is `dwy_auth`, old module/distribution are absent, and the actual EAPI wheel's auth extra depends on `dwy-auth==0.1.0`.
- Independent review mapped all 33 package files across the rename and found no functional drift or missing active references. Historical archives/completed plans retain their historical names; the smoke intentionally asserts the old namespace is absent.
- New Pending Publisher authorization still needs verification in the PyPI account. No registry publication, tag push, or permission change was performed.
- Fresh CI environment synchronization was attempted against official PyPI; a missing cached Ruff wheel required a slow download and synchronization was stopped. The lockfile check, full backend regression, and actual-wheel acceptance above completed independently; a hosted release workflow run is not claimed.
