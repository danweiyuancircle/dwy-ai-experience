# Email verification language implementation plan

> **For agentic workers:** Use TDD and verification-before-completion. Execute the approved request in this session; do not publish packages or deploy services.

**Goal:** Explicit Chinese in `Accept-Language` selects Chinese verification mail; all other or missing languages select English.

**Architecture:** The Apple client sends `zh` or `en` from its current preferred language. Both authentication HTTP integrations normalize the bounded header and pass `language` as a per-call keyword through the authentication runtime, sender adapter, and email provider. HTML, plain text, and subject select the same language without mutable instance language state.

**Tech Stack:** Existing Swift/Foundation, Python/FastAPI, pytest, and Resend SDK.

**Spec:** User-approved conversation on 2026-10-25: add the request header, retain Chinese, implement English, and use English unless the header specifies Chinese.

## Global constraints

- Scope: shared library only; preserve unrelated app-cloud work. No package publication or deployment.
- Default language is `en`; `zh` and `zh-*` language ranges select Chinese, ignoring ranges excluded with `q=0`.
- Bound `Accept-Language` to 512 characters at HTTP boundaries; malformed/non-Chinese values use English.
- Existing Chinese subject remains configurable; provide a separate English subject. Do not automatically translate brand identities.
- Language must not participate in verification-code storage, rate-limit keys, or challenge identity.
- Keep tests outside source and synchronize test inventories. No new external dependencies.

## Review focus

- Missing, malformed, mixed-case, weighted, and excluded Chinese headers.
- Concurrent requests in different languages on one provider instance.
- Custom Chinese brand taglines must not leak into English templates.
- AuthRuntime overrides and both legacy/new HTTP installers must pass language.
- Existing custom sender/provider implementations need the documented keyword parameter.

### Task 1: Apple request header

Files: `ios/Sources/Shared/AuthCore/AppCloudAuthClient.swift`, matching AuthCore tests and test inventory.

- [x] Add header tests with injectable preferred-language source; observe RED.
- [x] Add a compatible initializer default and resolve language per request.
- [x] Verify Chinese variants, other languages, empty value, and changed language between requests.

### Task 2: Provider templates and delivery

Files: `backend/src/dwyeapi/providers/email/`, provider tests, configuration documentation.

Interfaces: `send_code(target, *, language="en")`, `send_verification_code(target, code, *, language="en")`, `_send(target, code, *, language="en")`.

- [x] Add failing tests for English default, Chinese selection, subject/body consistency, escaping, and concurrency.
- [x] Preserve Chinese template; add English template text and language-aware subject/configuration.
- [x] Pass language through both delivery APIs without storing it on shared instances.
- [x] Run provider regression tests and update inventory/docs.

### Task 3: Authentication header-to-delivery integration

Files: `backend/packages/app-auth/src/dwy_app_auth/{email_auth,runtime,http}.py`, `backend/src/dwyeapi/auth.py`, matching authentication tests and inventories.

Interfaces: `resolve_email_language(accept_language: str | None) -> Literal["zh", "en"]`; `send_email_code(..., *, remote_key="local", language="en")`; `EmailCodeSender.send(..., *, language="en")`.

- [x] Add failing HTTP tests for both installers and a real-provider capture test through authentication.
- [x] Parse the header at both HTTP boundaries; propagate the normalized language through runtime and sender.
- [x] Update repository test senders to accept the new keyword, retaining existing challenge assertions.
- [x] Run affected authentication/provider tests and lint; update inventory and usage documentation.

### Task 4: Final verification

- [x] Run backend provider, authentication package, and EAPI auth-runtime regression suites.
- [x] Run affected Swift tests and check the final diff for API consistency.
- [x] Build current wheels and smoke-test actual built artifacts in a fresh environment if tooling/dependencies permit.
- [x] Record measured results and explicitly separate local verification from real email delivery/deployment.

## Verification results

- Backend: `PYTHONPATH=src:packages/app-auth/src .venv/bin/python -m pytest tests packages/app-auth/tests -q --tb=short` from `backend`: 445 passed, 3 PostgreSQL-dependent tests skipped, 2 existing Starlette deprecation warnings.
- Provider RED: 8 failing new cases before implementation; GREEN: 38 provider tests passed.
- HTTP RED: 7 expected failures (missing language propagation and header bound); GREEN: 32 language cases passed.
- Swift RED: missing request header failed. GREEN: 43 AuthCore tests passed using a temporary SwiftPM package linking the real repository CoreKit/L10nKit/AuthCore sources and all AuthCoreTests. Root SwiftPM testing could not start because GRDB SQLiteLib submodule cloning timed out; root package acceptance is not claimed.
- Built both actual wheels into `backend/build/email-language-verification/wheels`, installed into a new environment, and passed `python -I packages/app-auth/tests/packaging_smoke.py` with site-packages import-path assertions, fixed six-table inspection, English/Chinese header propagation and template-language checks.
- Changed Python files passed Ruff lint and format checks. Independent review found no critical/important issues; updated the outdated Playground custom-provider example it identified.
- Validation did not send real Resend mail, publish packages, or deploy services. Source submission and release status are handled separately.

## Release assessment (2026-10-25)

- Release both Python packages together for registry consumers: public PyPI currently has `dwyeapi==0.11.0`, while `dwy-app-auth` has no public project yet. Current source manifests are `0.11.1` and `0.1.0`; these source versions are not evidence of publication.
- SwiftPM consumers need a new semantic version tag after this change; the latest current tag is `0.5.0`. No frontend npm package release is required for the documentation-only Playground change.
- App-cloud currently pins local preview wheels for both Python packages. Publishing alone will not update that deployment: refresh its package artifacts/dependencies and rebuild affected Compose containers.
- Publish via the existing package-specific GitHub Actions/OIDC workflows after verifying paired dependency versions and first-release authorization. Do not trigger publication as part of this source commit.
