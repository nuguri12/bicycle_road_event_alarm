# State

Last updated: 2026-07-03

## Current Objective

Operate and verify the Weekend Cycling Event Alert Service as a scheduled GitHub Actions batch that collects bicycle-impacting public events, normalizes them, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

Monitor the daily 07:30 KST production schedule after a successful push-based Telegram smoke.

## Current Runtime State

- Repository: `nuguri12/bicycle_road_event_alarm`
- Branch strategy: direct development on `main`
- Latest verified smoke run: GitHub Actions run `28660665074` on commit `2a0c825`
- Workflow: `.github/workflows/manual-batch.yml`
- Production schedule: `cron: "30 22 * * *"`
- Meaning: every day 07:30 KST
- Temporary push smoke trigger has been removed after successful verification.
- Scheduled runs force real publish mode:
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
- Manual workflow runs default to safe dry-run mode:
  - `dry_run=true`
  - `enable_telegram_publish=false`
  - `force_fallback=false`
  - `apply_migrations=false`

## Implemented Runtime Behavior

- Runtime sources are Hangang events, Hangang notices, and Ara Waterway notices.
- SPATIC code remains for regression/reference but is not called by runtime ingestion.
- Ingest emits `RUN_ID=<uuid>`.
- Normalize and message generation are scoped to that run id.
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
- Ara Waterway often times out from GitHub Actions runners.
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid duplicate hash collisions, but daily scheduling increases the chance of repeated no-event messages.

## Next Actions

1. Monitor the next normal `schedule` event run.
2. Confirm Telegram receives the scheduled production message.
3. Check run logs for:
   - `MESSAGE_STATUS=generated`
   - `MESSAGE_CONTEXT=<...>`
   - `TELEGRAM_STATUS=success` or a clear failure reason
4. If no `schedule` event run appears at the production time, treat GitHub schedule triggering as the remaining operational issue.
