# State

Last updated: 2026-07-09

## Current Objective

Operate and verify the Daily Cycling Event Alert Service as a Cloudflare-triggered GitHub Actions batch that collects bicycle-impacting public events, normalizes same-day active events, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

MVP daily triggering and Telegram no-event delivery are stable after three consecutive successful natural production runs. Continue light monitoring while improving source precision and operational traceability before expanding sources, adding Telegram subscription flows, or evaluating Hermes Agent message generation.

## Current Runtime State

- Repository: `nuguri12/bicycle_road_event_alarm`
- Branch strategy: direct development on `main`
- Latest verified Cloudflare Worker smoke run: GitHub Actions run `28689723865` on commit `6b519ba`
- Latest resolved production incident: 2026-07-06 07:30 KST run failed in normalization with psycopg `DuplicatePreparedStatement`; the 2026-07-07 07:31 KST production run completed and published successfully after the fix.
- Workflow: `.github/workflows/manual-batch.yml`
- External scheduler: `cloudflare/scheduler`
- Cloudflare Worker: `bicycle-road-event-alarm-scheduler`
- Cloudflare Worker URL: `https://bicycle-road-event-alarm-scheduler.matthew-dev.workers.dev`
- Latest Cloudflare deployment version: `33484d82-8f35-4a48-b9aa-842bf7d67dc8`
- Production schedule: Cloudflare Cron `30 22 * * *`
- Meaning: every day 07:30 KST
- Cloudflare cron trigger deployment is confirmed by Wrangler.
- Cloudflare Worker secret `GITHUB_TOKEN` is set as of 2026-07-04 09:20 KST (`npx wrangler secret list` returned `GITHUB_TOKEN`).
- Cloudflare Worker secret `SMOKE_TRIGGER_TOKEN` is set for authenticated manual production smoke runs.
- GitHub Actions native `schedule` is removed to avoid duplicate sends.
- Temporary push smoke trigger has been removed after successful verification.
- Authenticated Worker smoke endpoint `POST /__internal/run-scheduled` dispatches the same GitHub workflow payload for immediate validation.
- Cloudflare dispatches `workflow_dispatch` with real publish inputs:
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
- Natural Cloudflare-triggered Telegram no-event message was received at 2026-07-05 07:31 KST.
- Natural Cloudflare-triggered Telegram no-event message was received at 2026-07-07 07:31 KST after the Supabase pooler prepared-statement fix.
- Natural Cloudflare-triggered runs on 2026-07-07, 2026-07-08, and 2026-07-09 all completed and published successfully, so the MVP production path is considered stable as of 2026-07-09.
- Manual workflow runs default to safe dry-run mode:
  - `dry_run=true`
  - `enable_telegram_publish=false`
  - `force_fallback=false`
  - `apply_migrations=false`

## Implemented Runtime Behavior

- Runtime sources are Hangang events, Hangang notices via Seoulboard JSON API, and Ara Waterway notices via the official K-water 경인아라뱃길 notice URL.
- SPATIC code remains for regression/reference but is not called by runtime ingestion.
- Ingest emits `RUN_ID=<uuid>`.
- Normalize and message generation are scoped to that run id.
- Publish candidates are limited to events active on the KST date when they were fetched.
- Source outage and true no-event are separated in CLI/DB message context.
- Partial source outage is recorded in DB and CLI, but user-facing no-event text stays quiet.
- Empty fallback messages include KST send date and time.
- Telegram publish attempts are recorded for success, failed, and non-empty skipped outcomes.
- Production-mode Telegram publish failures return a non-zero CLI exit code so GitHub Actions fails visibly.
- Duplicate successful publish prevention is active.
- Message-stage run summaries now include the ingest run id when message generation is scoped with `--run-id`, which makes ingest/message/publish correlation easier during operations review.

## Known Current Observations

- The 2026-07-03 19:00 KST one-off schedule did not create a GitHub Actions run.
- The 2026-07-03 21:20 KST one-off schedule did not create a GitHub Actions run.
- The push-based production smoke succeeded at 2026-07-03 21:31 KST with `TELEGRAM_STATUS=success` and `TELEGRAM_MESSAGE_ID=11`.
- The Cloudflare Worker authenticated smoke endpoint returned `202 scheduled dispatch accepted` at 2026-07-04 09:46 KST and created GitHub Actions run `28689723865`.
- Run `28689723865` completed successfully at 2026-07-04 09:47 KST.
- The 2026-07-05 07:31 KST natural Cloudflare-triggered Telegram message was received and said there were no today cycling caution events.
- The 2026-07-06 07:30 KST Cloudflare-triggered run did execute, saved 16 raw events, then failed before Telegram in `normalize_events`.
- Root cause: Supabase transaction pooler reused a server connection where psycopg prepared statement `_pg3_0` already existed.
- Local verification against failed run `7b01d78c-3816-472b-856b-4eafcbe28ab1` succeeded after disabling psycopg prepared statements:
  - `NORMALIZED_EVENTS_SAVED=16`
  - dry-run message generation produced `MESSAGE_CONTEXT=no_event`
- The 2026-07-07 07:31 KST daily run succeeded:
  - Ingest run `fc1f62f4-16b4-4cd2-a9bc-cc3b7bedf4ef` saved 4 raw Ara Waterway notice rows.
  - Message run `df074c65-fe5b-4228-9367-3816b561321a` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - No `DuplicatePreparedStatement` recurrence was observed.
  - The 4 raw rows matched existing non-publishable normalized notices and produced a no-event Telegram message.
- The 2026-07-08 07:31 KST daily run succeeded:
  - Ingest run `ceabbd6e-eb4b-4bf8-9902-cd491becf8e2` completed with no newly saved raw events.
  - Message run `1767d14b-b05e-4311-adc4-d98bae795cec` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - Live source cross-check found 17 candidates across Hangang events, Hangang notices, and Ara Waterway notices, with 0 publish candidates and no source failures.
- The 2026-07-09 07:31 KST daily run succeeded:
  - Ingest run `81a17fa6-7022-41c3-b5fc-d5419b578c45` completed with no newly saved raw events and `error_summary=None`.
  - Message run `e2811ac4-1f8c-4834-9a50-586dbafbbcf7` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - This is the third consecutive successful natural daily run after the 2026-07-06 prepared-statement incident.
- Current live-source/local normalization check found 19 raw candidates and 0 KST same-day publish candidates.
- Ara Waterway now uses an official K-water notice URL. Parser precision has been improved for title links without nested `strong` tags and detail pages that put `통제 구간` on a label line followed by the section text; live-source precision should still be monitored.
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid duplicate hash collisions, but daily scheduling increases the chance of repeated no-event messages.

## Next Actions

1. Continue light monitoring of daily 07:30 KST production runs.
2. Continue monitoring Ara Waterway live-source precision and add fixtures if K-water markup changes again.
3. Review whether message-stage run summaries are sufficient for operations correlation before adding a dedicated batch id.
4. Revisit no-event message dedupe only if daily no-event confirmations become noisy.
