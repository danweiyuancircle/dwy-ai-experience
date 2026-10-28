# App Store review notifications implementation plan

**Goal:** Poll Apple customer reviews hourly by default, persist bounded history, and deliver new/changed reviews to Discord.

**Architecture:** Extend `backend/packages/webhooks` with an isolated review collector, database-backed schedule and state, and the existing durable Discord delivery queue. The consuming project injects settings, sessions and migration-owned tables. FastAPI lifespan owns asyncio tasks; no Redis or scheduler service is required.

**Tech Stack:** Python, existing httpx/PyJWT/SQLAlchemy, FastAPI lifespan and asyncio.

**Spec:** User-approved chat scope: shared package implementation; configurable hourly interval; configurable database retention (default 30 days, supports 60/90); notification only, no Discord replies.

## Constraints

- Preserve unrelated App Cloud working tree changes. The follow-up authorizes publishing `dwy-webhooks 0.2.0` after source validation; deployment and real Apple/Discord requests remain outside scope.
- Configuration and secrets are injected; no host environment reads in the library.
- Apple pagination must finish before baseline/state changes. Persist schedule leases across restarts/workers.
- Initial synchronization establishes a baseline and sends one summary. Later synchronization alerts on new/changed reviews.
- Retention removes review content and delivery payloads; minimal per-app schedule/baseline state remains.
- Expired reviews are not reimported or repeatedly notified. Only text reviews and their star ratings are covered.
- Use existing dependencies and add no scheduler framework.

## Tasks

- [x] TDD: Apple review models/configuration, bounded authenticated client and pagination security.
- [x] TDD: injected SQLAlchemy tables/store, atomic state+outbox, leases, retention and restart behavior.
- [x] TDD: collector orchestration and cancellable periodic runtime; reuse existing queue/sender.
- [x] TDD: App Cloud settings, lifecycle, independent admin migration and disabled default.
- [x] Document configuration/retention semantics and verify package tests plus affected host integration.
- [x] Independent code review and isolated wheel import check.

## Verification

### 0.2.0 source validation and release preparation

- Current shared source: 182 tests passed, with import paths checked against this checkout.
- App Cloud: 521 tests passed and 13 environment-dependent tests skipped with editable `0.2.0`; 34 parent and migration-child import records used the same source and interpreter. Admin migration `003` created the three review tables without schema drift.
- Explicit `reviews` dependencies cover HTTP, ES256 JWT and cryptography. A valid Redis 8 dependency combination reproduced the missing JWT import without this extra; the extra fixed it without installing the Apple Server SDK or Resend.
- The actual `0.2.0` wheel passed isolated minimal-extra import, offline signing, collection and registration checks. CI additionally imports the review client/runtime from the installed wheel in both full and minimal-extra environments.
- Concurrency storage tests use SQLite. Production PostgreSQL competition and real Apple/Discord acceptance are separate from this source validation.

### Initial implementation verification

- Shared package: 182 tests passed against the built wheel; import came from the wheel and product packages were absent.
- App Cloud: 167 affected integration/admin/auth/webhook tests passed with the same built wheel; the adapter agent also ran a broader 181-test selection successfully.
- Ruff and both repositories' diff whitespace checks passed.
- Review caught and fixed optional Apple pagination metadata, old-history notifications after retention expansion, and expired delivery before cleanup.
- Live Apple/Discord, production PostgreSQL, package publication and deployment were not performed. The package manifest remains at its existing version; production must publish/lock a version containing this capability before building the consumer.
