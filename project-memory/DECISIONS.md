# Decisions

Last updated: 2026-07-14

## 2026-07-14: Defer SNS expansion until source quality and personal Telegram delivery are stable

- Decision: Do not expand publishing to SNS yet. Serviceization should proceed in this order: parser/source stability, one additional regional source, Telegram personal chat delivery, minimal personalization, then web management. SNS, Hermes Agent, and VPS scheduler changes stay deferred.
- Reason: Publishing to more channels before source precision and per-user delivery are stable would amplify false positives/false negatives and add platform-policy risk.
- Alternatives considered: Add SNS publishing now; build a web service first; move scheduling off Cloudflare/GitHub first.
- Impact: The next work should stay focused on parser fixtures, source precision, controlled source expansion, and Telegram subscriber support in the existing monolith.

## 2026-07-09: Allow direct high-impact bicycle-route alerts without exact location

- Decision: Treat active high-impact bicycle-route notices as publish candidates even when exact location extraction is missing.
- Reason: Public notices can say `자전거도로 통행 차단` or similar without a clean location field. Requiring `validation_status=valid` created a false-negative risk for important cycling-road closure notices.
- Alternatives considered: Keep excluding all missing-location notices; build a scoring system; wait for detail parsing improvements.
- Impact: Missing-location high-impact route alerts use `구간 확인 필요` as the message location. Generic missing-location events remain excluded.

## 2026-07-06: Disable psycopg prepared statements for Supabase pooler

- Decision: Pass `connect_args={"prepare_threshold": None}` when creating the SQLAlchemy psycopg engine.
- Reason: The 2026-07-06 07:30 KST production run failed in normalization with `psycopg.errors.DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`.
- Alternatives considered: Switch Supabase connection mode; retry failed jobs manually; use a new DB connection per query.
- Impact: Short-lived GitHub Actions batch steps avoid prepared statement name collisions through the Supabase transaction pooler.

## 2026-07-05: Limit publish candidates to same-day active events

- Decision: Treat only events active on the KST fetch date as publish candidates.
- Reason: A daily 07:30 KST Telegram alert is only useful when it reflects same-day riding impact; future, past, or broad monthly notices should not create a daily alert.
- Alternatives considered: Keep weekend-oriented alerts; filter only at message generation time.
- Impact: Normalization now keeps raw/normalized evidence but only marks same-day active events as publishable. Empty fallback copy now says "오늘 자전거 주의 이벤트가 없습니다."

## 2026-07-05: Update official runtime source endpoints

- Decision: Use Seoulboard JSON API `https://seoulboard.seoul.go.kr/front/bbs.json?bbsNo=5211` for Hangang notices and official K-water 경인아라뱃길 notice URL for Ara Waterway notices.
- Reason: Hangang notice HTML did not expose static post links, while the Seoulboard API returns the actual notice list. The previous Ara Waterway root URL was too broad.
- Alternatives considered: Disable Hangang notices; keep Ara root page; search for unrelated traffic feeds.
- Impact: Source relevance improves, but Ara Waterway parsing still needs row/detail/location refinement.

## 2026-07-03: Use project memory as the first context layer

- Decision: Add a minimal `project-memory/` directory with state, architecture, repository map, decisions, and open issues.
- Reason: The project now spans crawling, DB, OpenAI, Telegram, GitHub Actions, and operations. Without memory, future Codex sessions may re-load too much of the repository.
- Alternatives considered: Continue using only README and handoff docs.
- Impact: Future sessions should consult `project-memory/` before broad repository exploration.

## 2026-07-03: Temporary production smoke schedule

- Decision: Temporarily set GitHub Actions cron to `0 10 3 7 *` for a 2026-07-03 19:00 KST production-mode smoke.
- Reason: Manual dispatch used dry-run settings and could not verify real scheduled Telegram publishing.
- Alternatives considered: Manual workflow with real publish inputs; deleting DB dedupe records; adding a dedicated smoke message option.
- Impact: Must restore normal production cron after the smoke result is known.

## 2026-07-03: 19:00 KST smoke did not create a schedule run

- Decision: Retry the production smoke at 21:20 KST with cron `20 12 3 7 *`.
- Reason: GitHub Actions did not create a `schedule` event run for the 2026-07-03 19:00 KST one-off cron even though the workflow was active.
- Alternatives considered: Trigger workflow_dispatch through GitHub UI; run local production smoke with `.env`; use Chrome automation.
- Impact: Chrome automation was unavailable and local `.env` was absent, so the next feasible automated check is another one-off scheduled production smoke.

## 2026-07-03: 21:20 KST smoke did not create a schedule run

- Decision: Add a temporary push-based production smoke trigger limited to `project-memory/SMOKE_TRIGGER.md`.
- Reason: Both 19:00 KST and 21:20 KST one-off schedules did not create GitHub Actions runs, so the Telegram path could not be exercised through schedule.
- Alternatives considered: Wait longer for GitHub schedule; use Chrome UI automation for workflow_dispatch; local production smoke with `.env`.
- Impact: The next push should run `Manual Batch` as a `push` event with real Telegram publish mode. Remove this temporary trigger after the result is known.

## 2026-07-03: Push-based smoke verified Telegram publishing

- Decision: Remove the temporary push smoke trigger and restore production cron `0 22 * * 4`.
- Reason: Push run `28660665074` completed successfully with `TELEGRAM_STATUS=success` and `TELEGRAM_MESSAGE_ID=11`.
- Alternatives considered: Keep the push trigger for future smoke runs; add a dedicated smoke workflow.
- Impact: The temporary smoke trigger was removed, and Telegram publish failures now fail the workflow visibly.

## 2026-07-03: Change production schedule to daily 07:30 KST

- Decision: Set production cron to `30 22 * * *`.
- Reason: The operator requested daily morning execution at 07:30 KST.
- Alternatives considered: Keep weekly Friday 07:00 KST schedule.
- Impact: Scheduled runs now publish in real mode every day, so no-event message volume should be monitored.

## 2026-07-04: Replace GitHub native schedule with Cloudflare Workers Cron

- Decision: Add `cloudflare/scheduler` and remove GitHub Actions native `schedule` from `manual-batch.yml`.
- Reason: GitHub native scheduled runs did not appear reliably, while manual `workflow_dispatch` successfully sent Telegram messages.
- Alternatives considered: Continue relying on GitHub schedule; use cron-job.org; use GCP Cloud Scheduler.
- Impact: Cloudflare owns the daily 07:30 KST trigger and calls GitHub `workflow_dispatch`; GitHub no longer self-schedules to avoid duplicate sends.

## 2026-07-03: 17:30 KST smoke did not create a schedule run

- Decision: Retry the production smoke at 19:00 KST with more lead time before the scheduled minute.
- Reason: The previous attempt had a new `main` commit at 17:29:25 KST, about 35 seconds before the 17:30 KST cron minute. GitHub Actions scheduled workflows are not precise real-time timers and can be delayed or dropped.
- Alternatives considered: Use manual dispatch for real publish; use a temporary repeating cron.
- Impact: If 19:00 also does not produce an `event=schedule` run, treat GitHub schedule reliability as the issue and avoid one-off cron smoke tests.

## 2026-07-03: Keep auxiliary source outages quiet in user messages

- Decision: Keep `partial_source_unavailable` visible in DB/CLI, but render user-facing fallback as a normal no-event message.
- Reason: Ara Waterway can timeout from GitHub Actions, and repeated auxiliary outage messages degrade alert quality.
- Alternatives considered: Exclude Ara Waterway entirely; show degraded-status messages in Telegram.
- Impact: Operators can still inspect DB/CLI context, while users receive quieter no-event messages.

## 2026-07-03: Separate source outage from true no-event

- Decision: Add message context values such as `source_unavailable`, `partial_source_unavailable`, `no_event`, and `event_alert`.
- Reason: A source outage should not be operationally indistinguishable from a true no-event result.
- Alternatives considered: Treat all empty publishable event sets as no-event.
- Impact: Run logs and workflow output now support post-run diagnosis.

## 2026-07-03: Runtime sources exclude SPATIC

- Decision: Runtime ingestion uses Hangang and Ara Waterway sources; SPATIC remains as reference/regression code only.
- Reason: SPATIC was less bicycle-road specific and caused source reliability issues.
- Alternatives considered: Keep SPATIC as a runtime source; add generic traffic sources.
- Impact: Runtime relevance improves, but source coverage remains limited.

## 2026-07-01: Separate migrations from scheduled runtime batches

- Decision: Scheduled batches do not run Alembic migrations. Migrations run only in manual dispatch with `apply_migrations=true`.
- Reason: Runtime batches should not fail because of schema migration issues.
- Alternatives considered: Always run migrations before batch.
- Impact: Operators must apply migrations intentionally when schema changes.
