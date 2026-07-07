# State

Last updated: 2026-07-07

## Current Objective

Operate and verify the Daily Cycling Event Alert Service as a Cloudflare-triggered GitHub Actions batch that collects bicycle-impacting public events, normalizes same-day active events, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

Observe daily 07:30 KST production runs for messaging reliability before expanding sources, adding Telegram subscription flows, or evaluating Hermes Agent message generation.

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
- Current live-source/local normalization check found 19 raw candidates and 0 KST same-day publish candidates.
- Ara Waterway now uses an official K-water notice URL, but parser precision still needs improvement.
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid duplicate hash collisions, but daily scheduling increases the chance of repeated no-event messages.

## Next Actions

1. Continue observing daily 07:30 KST production runs for 3-7 days.
2. Check that each run reaches Telegram `success` or records a clear failure reason.
3. Refine Ara Waterway parser row scope, detail URLs, and location/section extraction.
4. Consider improving run-level observability so ingest, normalization, and message publish status are easier to correlate.
