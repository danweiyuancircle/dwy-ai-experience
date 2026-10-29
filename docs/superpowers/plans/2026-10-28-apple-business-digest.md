# Apple Business Digest Implementation Plan

> For agentic workers: use superpowers:subagent-driven-development. User subsequently authorized shared release, App Cloud integration and server deployment after verification; no unrelated changes or messages.

**Goal:** Add reusable Apple daily/weekly business reports and App Cloud integration, with a default dispatch time of 08:30 Beijing time (`Asia/Shanghai`).

**Architecture:** Follow the existing reviews monitor. Shared code owns bounded ASC report ingestion, typed snapshots, aggregation, persisted scheduling and outbox, formatting and lifecycle. Projects inject resources and migrate their own tables.

**Tech Stack:** Existing Python 3.11+, Pydantic, HTTPX, PyJWT, cryptography, SQLAlchemy and Discord transport. Standard-library gzip/csv/Decimal/zoneinfo only; no new runtime package or service.

**Spec:** `docs/superpowers/specs/2026-10-28-apple-business-digest-design.md`, with the rulings below taking precedence.

## Rulings

- User approved implementation and changed delivery to Beijing 08:30. Defaults: timezone Asia/Shanghai, hour 8, minute 30; weekly Monday. Remain on existing develop checkouts.
- Purchases Standard money is explicitly USD estimates. No fabricated CNY/JPY amounts. Sales SUMMARY is deferred.
- Discovery Impression excludes page views and row-level Unique Counts cannot be added into an official unique denominator. Display event counts and leave official total conversion unavailable until a correct denominator exists.
- MRR/LTV, cohort conversion, retention and unknown ratio denominators remain explicitly unavailable. Missing reports never become numeric zeros.
- Historical reviews counts come from the existing public review store via an injected summary callback; no second review scraper. Private reviewer information never enters analytics snapshots.

## Shared Interfaces

`analytics/models.py` owns immutable Pydantic models:

- `AnalyticsApp(name: str)`.
- `AppleAnalyticsConfig(apps: dict[ASCAppID, AnalyticsApp], issuer_id, key_id, private_key: SecretStr, timezone='Asia/Shanghai', send_hour=8, send_minute=30, lag_days=3, retention_days=400, discord_webhook_url=None, discord_username=existing default)`. Validate timezone, bounds, max 100 apps and all secrets as existing reviews config. Credentials use the same validation as reviews.
- `AnalyticsValue(value: Decimal | None = None, status: Literal['available','pending','unavailable','not_applicable']='unavailable', currency: str | None=None, source: str='')`.
- `AppleBusinessSnapshot(app_id: str, report_date: date, metrics: dict[str, AnalyticsValue], breakdowns: dict[str, dict[str, Decimal]]={}, notes: tuple[str,...]=())`.
- `AnalyticsCollectionError(code: str)` exposes safe fixed codes only.

Metric keys: first_downloads, redownloads, impressions, page_views, store_conversion_rate, sales_usd, proceeds_usd, refunds_usd, refund_count, paid_subscriptions, paid_offer_subscriptions, free_trials, paid_starts, offer_conversions, renewals, voluntary_churn, involuntary_churn, billing_issues, billing_recoveries, trial_starts. Unverified event categories stay unavailable instead of guessed. Breakdowns: download_territories, proceeds_territories, download_sources. Feedback keys in snapshots: review_count, low_star_reviews (UTC review creation day, explicitly labelled).

`AppleAnalyticsClient(config, *, client=None, clock=time.time)` provides `collect(app_id, report_date)->AppleBusinessSnapshot`, `initialize(app_id)->str`, and `aclose()`. `initialize` explicitly requests ONGOING reports; collect never silently creates privileged requests. Injected client is never closed by the library.

`build_analytics_tables(metadata, prefix='app_store_analytics')->AnalyticsTables` declares state, snapshots and independent compatible deliveries. Account scope is issuer_id. Snapshot writes replace date versions rather than add revisions.

`install_analytics_monitor(app, config, sessions, tables, *, client=None, sender=None, feedback=None)->AnalyticsRuntime`. Runtime exposes monitor and queue, installed under `app.state.dwy_analytics_monitor`. Feedback is optional async `(app_id, date)->dict[str,int]`; analytics installation may not depend on reviews extras.

`apple_business_digest_content(app_name, snapshots, *, period='daily', comparison=())->list[str]` generates bounded deterministic parts; daily one snapshot, weekly seven. Weekly sums flows, compares endpoint subscription snapshots, never sums stocks or unique people. Explicit availability/date/USD labels.

## Tasks

- [ ] Task A: client/models/metrics and minimal shared ASC authentication extraction. Own only analytics models/client/metrics, common ASC module and necessary review-client compatibility edits; tests under tests/analytics/test_client.py and test_metrics.py. First demonstrate failing import/behavior, then green. Verify pagination origin, unsigned download requests, bounded gzip/TSV, all segments/instances, correction replacement, invalid columns/Decimal, future report fields, negative refunds with zero counts, source labels. Use official Apple report schemas, not imagined fields.
- [ ] Task B: formatting/storage/service/runtime and public analytics exports. Own these analytics files and tests under tests/analytics/test_monitor.py, test_storage.py, test_formatting.py, test_runtime.py. First RED then GREEN. Due date at Beijing 08:30 including restarts and Monday weekly; bounded seven-day refresh; initial run does not flood historical days. Atomic snapshot and outbox, account/app isolation, lease takeover and stale worker fences, deterministic part keys, source metrics missing/partial state, complete-period comparisons, retry/cancellation, optional feedback. Never modify Task A files; use the interfaces above.
- [ ] Task C: App Cloud config/host/CLI/migration, review summary public adapter, dependency extra declarations, docs and wheel evidence. Write failing integration tests first. Add analytics-only admin resource condition in config/CLI/host; strict production independent storage/destination; same explicit key injection as reviews. Add migration using current table definitions and independent metadata. Add explicit `analytics-init` command; never auto-send a real message during tests.
- [ ] Task D: independent code review, targeted fixes, shared regression and host integration suite, fresh wheel isolated install/import smoke. Ensure minimal extras work and no App Cloud modules installed in the shared smoke. Document real Apple/Discord and timed acceptance separately. No tests are replaced by source import-path tricks; source testing may temporarily use a documented PYTHONPATH before wheel validation.

## Review Focus

- Compressed and decompressed payload limits, foreign download URL auth leakage, redirects and signed URL logs.
- Stock/event/unique denominator and USD/refund meaning, particularly partial refunds and multi-row counts.
- Crash windows between schedule/snapshot/outbox, multi-worker fencing and exhausted retries.
- Exact 08:30 Beijing boundary, pre-boundary calls, startup after boundary, duplicate and historical dispatch.
- Disabled analytics must not initialize a DB/client, change app factories or load optional report SDK dependencies.

## Execution ledger

- 2026-10-29: User explicitly confirmed “部署上去” and “继续” after the concrete develop release question. Branch release gate is approved; continue publication and server deployment without another confirmation.

- 2026-10-28: User approved design with Beijing 08:30. Both repositories develop; preserve pre-existing untracked documents. Implementation has not been committed or published.
- 2026-10-28: User added explicit release/deployment authorization. Follow dwy-publish, dwy-git-commit, dwy-semver, dwy-sdk-spec and existing OIDC workflow. 0.x compatible features use patch: dwy-webhooks 0.4.3, App Cloud 0.1.6. Deployment branch approval rule is checked at the concrete release gate.
- 2026-10-29 Beijing: Tasks A/B implemented with RED/GREEN and independently reviewed. Shared package full suite: 302 passed. App Cloud full backend suite from a temporary cwd without deployment dotenv: 625 passed, 13 skipped. Ruff and Compose syntax passed. Review findings fixed: Product page filtering, negative purchase quantity wording and billing issue wording.
- Built actual dwy-webhooks 0.4.3 wheel, isolated analytics-only environment passed import ownership, Beijing 08:30, persistent outbox and offline actual Discord sender smoke. Official PyPI dependency fetch timed out locally; isolated installation succeeded using the existing Aliyun mirror. No source-path bypass in wheel smoke.
- Built actual App Cloud 0.1.6 and internal wheels. Independent install exposed apple-iap still pinning webhooks 0.4.2; synchronized to 0.4.3 and rebuilt. Fresh quadrant-only environment passed actual wheel imports, disabled-feature behavior and 004 migration up/down/check. Other app packages absent.
- Both origin/develop fetch and pull --rebase --autostash succeeded; origin parity was 0/0. Preserve unrelated concurrent shared server-monitor work and existing untracked App Cloud audit docs.
- Production read-only probe confirmed app-cloud 0.1.5, seven monitored App IDs and configured existing Apple Discord destination. SSH works with the active macOS agent socket. No remote files/services changed and no actual messages sent by this task.
- Release gate pending explicit confirmation requested via async question: publish dwy-webhooks@0.4.3 and app-cloud@0.1.6 from existing develop branches. Required by dwy-publish branch rule. Do not tag/push/publish/deploy until answer arrives; elapsed time is not approval. Next: narrowly stage/scan/commit shared changes, push immutable tag to existing OIDC workflow, verify real Linux wheel and registry, update App Cloud lock from registry, run existing standalone wheel checks, commit/tag/archive, back up four databases and env, preserve compose overlays/frontend, build/migrate/enable analytics from existing reviews config/recreate API, verify health and real settings. First Analytics reports may take 24–48 hours; do not fabricate metrics.
