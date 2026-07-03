# Decisions

Last updated: 2026-07-03

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
