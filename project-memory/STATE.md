# State

Last updated: 2026-07-03

## Current Objective

Operate and verify the Weekend Cycling Event Alert Service as a scheduled GitHub Actions batch that collects bicycle-impacting public events, normalizes them, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

Wait for the temporary production smoke scheduled for 2026-07-03 17:30 KST, then restore the normal weekly production cron.

## Current Runtime State

- Repository: `nuguri12/bicycle_road_event_alarm`
- Branch strategy: direct development on `main`
- Latest pushed commit at the time of this memory update: `0d9d800 chore: schedule temporary production smoke`
- Workflow: `.github/workflows/manual-batch.yml`
- Temporary schedule: `cron: "30 8 3 7 *"`
- Meaning: 2026-07-03 08:30 UTC, which is 2026-07-03 17:30 KST
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
- Duplicate successful publish prevention is active.

## Known Current Observations

- Ara Waterway often times out from GitHub Actions runners.
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid same-day duplicate hash collisions, but that also weakens dedupe for repeated no-event scheduled runs.

## Next Actions

1. After 2026-07-03 17:30 KST, check GitHub Actions for a `schedule` event run.
2. Confirm Telegram received the production smoke message.
3. Check run logs for:
   - `MESSAGE_STATUS=generated`
   - `MESSAGE_CONTEXT=<...>`
   - `TELEGRAM_STATUS=success` or a clear failure reason
4. Restore production cron to `0 22 * * 4` after the smoke result is known.
5. Update this project memory after restoring the cron.
