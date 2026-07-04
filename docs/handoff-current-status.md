# Codex Handoff Current Status

Last updated: 2026-07-05

## Purpose

This document is the handoff note for another local Codex session. It summarizes the current repository state, implemented behavior, operational status, verification baseline, and next recommended tasks.

## Repository State

- Repository: `https://github.com/nuguri12/bicycle_road_event_alarm.git`
- Active branch: `main`
- Branch strategy: the user approved direct development on `main`
- Latest pushed commit before the cron failure fix: `ae6fa78 docs: add remaining risk opinion`
- Current local working tree contains unpushed source-validation, same-day filtering, IDE interpreter, documentation, and test updates.

## Project Goal

Daily Cycling Event Alert Service.

The service collects public traffic-control and event information that may affect bicycle-road users, stores raw events, normalizes them, generates Korean alert messages, and publishes them to a Telegram channel.

The runtime MVP sources are Hangang park events, Hangang park notices via Seoulboard JSON API (`bbsNo=5211`), and Ara Waterway notices via the official K-water 경인아라뱃길 notice URL. SPATIC code remains in the repository for regression/reference purposes, but the runtime ingest path no longer calls SPATIC.

## Current Operational Status

### GitHub Actions

- Workflow file: `.github/workflows/manual-batch.yml`
- Workflow name: `Manual Batch`
Cloudflare Cron:

```toml
crons = ["30 22 * * *"]
```

Meaning:

- Cloudflare cron uses UTC.
- `30 22 * * *` runs every day at 07:30 KST.

Scheduled runs force real publish mode:

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

Manual runs keep safe defaults:

```env
dry_run=true
enable_telegram_publish=false
force_fallback=false
apply_migrations=false
```

Latest natural production observation:

- The 2026-07-05 07:31 KST Telegram no-event message was received from the Cloudflare-triggered scheduled path.
- Local live-source verification after source parser updates found 19 raw candidates and 0 same-day publish candidates.

### Schedule Failure Diagnosis

The initial 2026-07-01 14:30 KST scheduled run did not appear in GitHub Actions, so a temporary `*/5 * * * *` smoke schedule was used.

Checked evidence:

- GitHub workflow state was `active`.
- Repository default branch was `main`.
- Remote `main` contained the expected workflow file.
- Remote workflow contained the expected cron expression.
- Later GitHub API checks confirmed schedule runs were being created.

Final root cause of the red scheduled runs:

- Scheduled runs failed at the `Apply database migrations` step.
- Alembic ran migration `0001_initial_schema -> 0002_publish_attempt_success_index`.
- The database migration itself reached Alembic bookkeeping.
- Updating `alembic_version.version_num` failed because the revision ID was 34 characters.
- Alembic's default `version_num` column is `varchar(32)`.

Observed error:

```text
psycopg.errors.StringDataRightTruncation: value too long for type character varying(32)
[SQL: UPDATE alembic_version SET version_num='0002_publish_attempt_success_index' ...]
```

Fix applied locally:

- Added a migration test that enforces revision IDs are at most 32 characters.
- Renamed the second migration revision to `0002_publish_success_idx`.
- Verified `python -m alembic heads` reports `0002_publish_success_idx (head)`.
- Verified `python -m alembic upgrade head` succeeds against Supabase.
- Production cron is now Cloudflare Cron `30 22 * * *`.
- Added workflow `concurrency` so manual and scheduled batches on the same branch run sequentially.
- Separated Alembic migrations from scheduled runtime batches.
- Migrations now run only for manual `workflow_dispatch` when `apply_migrations=true`.

## Runtime Flow

Current GitHub Actions batch flow:

1. Optionally apply database migrations for manual `workflow_dispatch` only when `apply_migrations=true`.
2. Run `python -m bicycle_road_event_alarm.cli.ingest_raw_events`.
3. Capture `RUN_ID=<uuid>` from the ingest output.
4. Store it as `BATCH_RUN_ID` in `$GITHUB_ENV`.
5. Run `python -m bicycle_road_event_alarm.cli.normalize_events --run-id "$BATCH_RUN_ID"`.
6. Run `python -m bicycle_road_event_alarm.cli.generate_messages --run-id "$BATCH_RUN_ID"`.
7. If manual `force_fallback=true`, add `--force-fallback`.

Important behavior:

- `ingest_raw_events` always emits `RUN_ID=<uuid>`.
- `normalize_events --run-id` processes only raw events from the current ingest run.
- `generate_messages --run-id` selects publishable events only from the current ingest run.
- Empty publishable event sets generate a dated KST no-event message.
- Publish candidates are limited to events active on the KST date when they were fetched.
- Non-empty publish outcomes are recorded in `publish_attempts` for `success`, `failed`, and `skipped`.
- Empty message skips are not recorded because they do not represent a publishable message.

## Environment And Secrets

The user has created:

- Supabase project
- Telegram bot/API configuration
- OpenAI API key

Local `.env` exists and is ignored by Git.

Required GitHub Repository Secrets:

- `SUPABASE_DATABASE_URL`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

Known Telegram channel status:

- Private Telegram channel was verified.
- Channel ID used during verification: `-1004448224539`
- Bot was able to send real messages after the channel ID and permissions were fixed.

Do not print or commit secret values.

## Implemented Features

### Project Bootstrap

- `pyproject.toml`
- `.gitignore`
- `.env.example`
- package skeleton under `src/bicycle_road_event_alarm`
- settings loader in `config/settings.py`
- unit test baseline

### Supabase DB Setup

- SQLAlchemy engine/session helpers
- DB health check
- ORM models:
  - `run_logs`
  - `raw_events`
  - `normalized_events`
  - `publish_attempts`
- Alembic environment
- Initial migration
- Partial unique success index for publish deduplication

### Raw Event Ingestion

- Hangang park event fixture parser
- Hangang park notice parser backed by Seoulboard JSON API (`https://seoulboard.seoul.go.kr/front/bbs.json?bbsNo=5211`)
- Ara Waterway notice parser using K-water 경인아라뱃길 notice URL (`https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do`)
- multi-source live ingestion
- SPATIC parser retained but excluded from runtime ingestion
- request timeout/retry wrapper
- raw candidate hashing
- duplicate-aware `raw_events` save
- run log start/finish helpers
- CLI: `python -m bicycle_road_event_alarm.cli.ingest_raw_events`
- graceful source timeout handling:
  - prints `INGEST_STATUS=skipped`
  - prints `INGEST_REASON=source_unavailable`
  - exits successfully so the rest of the batch can still report no-event status

### Normalization

- title cleanup
- date/time parsing
- full date-range parsing for same-day active checks
- location detection
- event type classification
- cyclist impact classification
- deterministic duplicate key
- publish candidate flag
- KST same-day publish candidate filtering
- duplicate-aware normalized save
- CLI: `python -m bicycle_road_event_alarm.cli.normalize_events`
- run-scoped CLI option: `--run-id`

### Message Generation

- message input DTOs
- publishable event repository
- OpenAI wrapper
- deterministic fallback generator
- OpenAI-first message generation service
- fallback on OpenAI errors or invalid output
- no-event fallback message with generated KST date/time and "today" wording
- CLI: `python -m bicycle_road_event_alarm.cli.generate_messages`
- run-scoped CLI option: `--run-id`
- fallback option: `--force-fallback`

### Telegram Publishing

- `TelegramPublishConfig`
- `TelegramPublishResult`
- `RequestsTelegramClient`
- guarded publish behavior:
  - disabled publishing
  - dry-run
  - missing config
  - empty message
  - client failure
- duplicate successful publish prevention
- `publish_attempts` records:
  - `success`
  - `failed`
  - non-empty `skipped`

### Fixtures And Local Verification Helpers

- CLI: `python -m bicycle_road_event_alarm.cli.seed_publishable_fixture`
- Creates one random local publishable fixture event for DB/CLI end-to-end verification.
- Fixture rows were removed after real Telegram verification.

## Current Commands

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Run all local checks:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src tests
python -m black --check .
python -m compileall src
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Run ingestion:

```bash
python -m bicycle_road_event_alarm.cli.ingest_raw_events
```

Run normalization for a specific ingest run:

```bash
python -m bicycle_road_event_alarm.cli.normalize_events --run-id "<RUN_ID>"
```

Generate and publish for a specific ingest run:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>"
```

Force fallback:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>" --force-fallback
```

Seed a test publishable fixture:

```bash
python -m bicycle_road_event_alarm.cli.seed_publishable_fixture
```

## Latest Verification Baseline

Latest full local verification before this handoff:

```text
python -m pytest -q
85 passed

python -m ruff check .
All checks passed!

python -m mypy src tests
Success: no issues found in 70 source files

python -m black --check .
73 files would be left unchanged

python -m compileall src
success
```

Remote verification after push:

- GitHub `main` uses `workflow_dispatch`; Cloudflare Cron owns production scheduling.
- GitHub `main` contained workflow `concurrency`.
- GitHub `main` gated `python -m alembic upgrade head` behind manual `apply_migrations=true`.
- GitHub `main` contained `BATCH_RUN_ID` capture.
- GitHub `main` contained `normalize_events --run-id "$BATCH_RUN_ID"`.
- GitHub `main` contained `generate_messages --run-id "$BATCH_RUN_ID"`.

## Operator Checks

After the current local changes are pushed, check GitHub Actions:

1. Open the repository Actions tab.
2. Select `Manual Batch`.
3. Wait for the next daily 07:30 KST Cloudflare-triggered run, or run `workflow_dispatch` manually to verify the same batch path.
4. Use `apply_migrations=true` only when an Alembic migration should be applied.
5. Open the run logs.
6. Confirm:
   - `RUN_ID=<uuid>`
   - `MESSAGE_STATUS=generated`
   - `MESSAGE_SOURCE=openai` or `MESSAGE_SOURCE=fallback`
   - `MESSAGE_EVENT_COUNT=<number>` where only same-day KST active events should count
   - `TELEGRAM_STATUS=success`, `failed`, or `skipped`

Check Supabase:

```sql
select id, status, started_at, finished_at, raw_event_count, normalized_event_count, published_message_count, error_summary
from run_logs
order by started_at desc
limit 10;
```

```sql
select run_id, status, failure_reason, attempted_at, telegram_channel_id
from publish_attempts
order by attempted_at desc
limit 10;
```

## Known Risks

- GitHub Actions native schedule was unreliable in this project.
- Cloudflare Workers Cron now owns the production trigger and produced a received 2026-07-05 07:31 KST Telegram no-event message.
- Ara Waterway source now points to the official K-water notice page, but the parser still over-collects surrounding page text and needs row/detail-link refinement.
- Source outage and true no-event are separated in DB/CLI context, while partial outages intentionally remain quiet in user-facing messages.
- HTML/API parsers are fixture-driven and may require fixture updates when source pages change.
- Normalization rules are deterministic MVP heuristics.
- Some older sprint docs may still contain mojibake text from earlier encoding issues.

## Recommended Next Tasks

1. Push the current source-validation, same-day filtering, docs, and test updates.
2. Run or wait for one post-push production batch and confirm `MESSAGE_EVENT_COUNT` reflects only KST same-day active events.
3. Refine the Ara Waterway parser row scope, source URLs, and location/section extraction.
4. Consider recording a clearer run-level publish summary in `run_logs`.
5. Continue monitoring no-event message frequency after the daily 07:30 KST schedule.
