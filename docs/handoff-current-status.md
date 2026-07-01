# Codex Handoff Current Status

Last updated: 2026-06-30

## Purpose

This document is a handoff note for another local Codex session. It summarizes what has been approved, implemented, verified, pushed to GitHub, and what remains.

## Repository State

- Repository: `https://github.com/nuguri12/bicycle_road_event_alarm.git`
- Active branch: `main`
- Branch strategy: user approved direct development on `main`
- Latest implementation commit covered by this handoff: `2b718a9 feat: add telegram publisher`
- Current local working tree at last check: clean

## Project Goal

Weekend Cycling Event Alert Service.

The service collects public event/traffic-control information that may affect bicycle-road users, stores raw events, normalizes them, generates alert messages, and can safely dry-run Telegram publishing before real channel delivery is enabled.

## Approved Documentation

Sprint 0 through Sprint 9 documentation has been created and approved by the user.

Important docs:

- `docs/pre-implementation-checklist.md`
- `docs/codex-session-summary.md`
- `docs/sprint0` through `docs/sprint9`
- `docs/superpowers/specs/*`
- `docs/superpowers/plans/*`

The checklist decisions were resolved using the recommended defaults:

- First crawler source: Seoul Metropolitan Police traffic information center / SPATIC
- Default schedule target: Saturday 06:00 KST
- Telegram publish disabled by default
- Supabase PostgreSQL via SQLAlchemy/Alembic
- OpenAI-backed message generation is implemented with deterministic fallback
- Secrets must stay in `.env` or GitHub Secrets, never in Git-tracked docs/code

## Environment And Secrets

The user has created:

- Supabase project
- Telegram bot/API configuration
- OpenAI API key

Local `.env` exists and is ignored by Git.

Known local `.env` status:

- `SUPABASE_DATABASE_URL` uses Supabase Transaction Pooler
- Supabase `SELECT 1` succeeded
- Alembic initial migration was applied successfully
- `ENABLE_TELEGRAM_PUBLISH=false`
- `DRY_RUN=true`

Do not print or commit secret values.

## Implemented So Far

### 1. Python Project Bootstrap

Commit: `c1c313f chore: bootstrap python project`

Implemented:

- `pyproject.toml`
- `.gitignore`
- `.env.example`
- package skeleton under `src/bicycle_road_event_alarm`
- settings loader in `config/settings.py`
- initial unit tests

Validation at the time:

- Pytest passed
- Ruff passed
- Mypy passed
- Black check passed
- Compileall passed

### 2. Supabase DB Setup

Commit: `585a05e feat: add supabase database setup`

Implemented:

- SQLAlchemy DB engine/session helpers
- DB health check
- ORM models:
  - `run_logs`
  - `raw_events`
  - `normalized_events`
  - `publish_attempts`
- Alembic environment
- Initial migration: `0001_initial_schema`
- Tests for DB models, migration metadata, health check, URL handling

Live verification:

- Supabase Transaction Pooler `SELECT 1` succeeded
- `python -m alembic upgrade head` succeeded
- DB tables present
- Alembic version: `0001_initial_schema`

### 3. Raw Event Ingestion

Commit: `2dc353f feat: add raw event ingestion`

Implemented:

- `crawler/raw_event.py`
  - `RawEventCandidate`
  - deterministic `content_hash`
- `crawler/spatic.py`
  - fixture-based SPATIC list parser
  - fixture-based SPATIC detail parser
- `crawler/repository.py`
  - raw event model conversion
  - duplicate-aware `raw_events` save
- SPATIC fixture HTML
- unit tests

Notes:

- This step was fixture based.
- Live SPATIC fetching was implemented in the next step.

### 4. Live SPATIC Ingestion

Commit: `44431aa feat: add live spatic ingestion`

Implemented:

- `crawler/http.py`
  - `requests` based HTTP client
  - retry for 429 and 5xx
  - no retry for 4xx
- `crawler/spatic_ingestion.py`
  - list page fetch
  - detail page fetch
  - candidate parsing
- `crawler/repository.py`
  - `start_run_log`
  - `finish_run_log`
- CLI:
  - `python -m bicycle_road_event_alarm.cli.ingest_raw_events`

Live verification:

- Command ran successfully
- Output: `RAW_EVENTS_SAVED=0`
- Supabase latest run log:
  - `status=success`
  - `raw_event_count=0`

Interpretation:

- The live flow works.
- SPATIC had no currently parseable/storable new event rows at that time.

### 5. Normalized Event Storage

Commit: `98d7dca feat: add normalized event storage`

Implemented:

- `normalization/title.py`
  - title cleanup
  - body fallback
- `normalization/datetime.py`
  - numeric date/time range parsing such as `2026.07.04 08:00 ~ 12:00`
- `normalization/location.py`
  - Seoul/Gyeonggi keyword-based location detection
- `normalization/classifier.py`
  - event type and cyclist impact classification
- `normalization/normalizer.py`
  - `RawEvent` to `NormalizedEventData`
  - deterministic duplicate key
  - validation status
  - publish candidate flag
- `normalization/repository.py`
  - duplicate-aware `normalized_events` save
- CLI:
  - `python -m bicycle_road_event_alarm.cli.normalize_events`

Live verification:

- Command ran successfully
- Output: `NORMALIZED_EVENTS_SAVED=0`
- Supabase counts:
  - `RAW_EVENTS_COUNT=0`
  - `NORMALIZED_EVENTS_COUNT=0`

Interpretation:

- The normalized storage flow works.
- There was no live raw data to normalize at that time.

### 6. Message Generation

Commit: `5d5e241 feat: add message generation`

Implemented:

- `messaging/message_input.py`
  - message input DTOs for normalized events
  - DB model to message event conversion
- `messaging/fallback_generator.py`
  - deterministic Korean fallback alert message
  - impact-first sorting
  - empty event set skip result
- `messaging/openai_generator.py`
  - thin OpenAI Responses API wrapper
  - structured event-only prompt
  - no raw HTML or secrets in prompt input
- `messaging/service.py`
  - OpenAI-first message generation
  - fallback on OpenAI exception, empty response, long response, or missing source URL
- `messaging/repository.py`
  - publishable normalized event selection
- CLI:
  - `python -m bicycle_road_event_alarm.cli.generate_messages`

Live verification:

- Command ran successfully
- Output at that time:
  - `MESSAGE_STATUS=skipped_empty_event_set`
  - `MESSAGE_SOURCE=fallback`
  - `MESSAGE_EVENT_COUNT=0`

Interpretation:

- Message generation flow works.
- Current DB had no publishable events, so OpenAI was not called in the live run.

### 7. Telegram Publisher And Fixture Verification

Commit: `2b718a9 feat: add telegram publisher`

Implemented:

- `messaging/telegram_publisher.py`
  - `TelegramPublishConfig`
  - `TelegramPublishResult`
  - `RequestsTelegramClient`
  - safe publish guard for disabled publishing, dry-run, empty message, and missing config
- CLI integration:
  - `generate_messages` now generates a message and passes it to Telegram publisher
  - `generate_messages --force-fallback` skips OpenAI and forces deterministic fallback
  - CLI prints `TELEGRAM_STATUS`, optional `TELEGRAM_REASON`, and optional `TELEGRAM_MESSAGE_ID`
- Fixture support:
  - `python -m bicycle_road_event_alarm.cli.seed_publishable_fixture`
  - inserts one random local-fixture `run_logs`, `raw_events`, and publishable `normalized_events` set
- Unit tests:
  - disabled publish does not call Telegram
  - dry-run does not call Telegram
  - empty message skips without external call
  - missing config fails without external call
  - enabled non-dry-run uses the injected client
  - Requests client formats `sendMessage` payload
  - CLI prints Telegram publish result

Live verification:

- Command ran successfully:
  - `python -m bicycle_road_event_alarm.cli.generate_messages`
- Output with current DB:
  - `MESSAGE_STATUS=skipped_empty_event_set`
  - `MESSAGE_SOURCE=fallback`
  - `MESSAGE_EVENT_COUNT=0`
  - `TELEGRAM_STATUS=skipped`
  - `TELEGRAM_REASON=empty_message`

Interpretation:

- Telegram publisher is wired into the CLI.
- No real Telegram API call was made because the generated message was empty.
- Real Telegram publishing is still gated by `ENABLE_TELEGRAM_PUBLISH=true` and `DRY_RUN=false`.

Additional live verification after fixture support:

- `python -m bicycle_road_event_alarm.cli.seed_publishable_fixture` succeeded
- `python -m bicycle_road_event_alarm.cli.generate_messages --force-fallback` succeeded
  - `MESSAGE_STATUS=generated`
  - `MESSAGE_SOURCE=fallback`
  - `MESSAGE_EVENT_COUNT=1`
  - `TELEGRAM_STATUS=skipped`
  - `TELEGRAM_REASON=telegram_publish_disabled`
- OpenAI API path was attempted with the seeded event
  - API returned `insufficient_quota`
  - Runtime correctly fell back to deterministic fallback
- Telegram real-send path was attempted with one fallback message
  - sanitized runtime output: `TELEGRAM_STATUS=failed`, `TELEGRAM_REASON=telegram_send_failed`
  - direct sanitized diagnostic returned `Bad Request: chat not found`
  - likely causes: wrong `TELEGRAM_CHANNEL_ID`, bot not added to the channel, or bot missing channel admin/post permission
  - One earlier traceback exposed the bot token in a Telegram API URL; rotate the Telegram bot token in BotFather before any public sharing of logs.

Follow-up Telegram verification:

- New bot token was validated with `getMe`
- Private channel was discovered through `getUpdates`
  - channel title: `Bicycle_Road`
  - channel type: `channel`
  - channel id to use in `.env`: `-1004448224539`
- `getChat` with that channel id succeeded
- `python -m bicycle_road_event_alarm.cli.generate_messages --force-fallback` with:
  - `TELEGRAM_CHANNEL_ID=-1004448224539`
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
  succeeded:
  - `TELEGRAM_STATUS=success`
  - `TELEGRAM_MESSAGE_ID=6`
- Re-running the same command produced:
  - `TELEGRAM_STATUS=skipped`
  - `TELEGRAM_REASON=duplicate_successful_publish`
- A CLI bug was found and fixed: `run_logs` must be flushed before recording `publish_attempts`, otherwise successful Telegram sends can fail during DB commit with a foreign-key error.

## Current Commands

Install/update dev dependencies:

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

Run live raw ingestion:

```bash
python -m bicycle_road_event_alarm.cli.ingest_raw_events
```

Run live normalization:

```bash
python -m bicycle_road_event_alarm.cli.normalize_events
```

Generate alert message and run Telegram publish step:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages
```

Force fallback without OpenAI:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --force-fallback
```

Seed one random publishable fixture event:

```bash
python -m bicycle_road_event_alarm.cli.seed_publishable_fixture
```

Apply DB migrations:

```bash
python -m alembic upgrade head
```

## Current Verification Baseline

Latest verified baseline before this handoff doc:

- `python -m pytest -q` passed with `57 passed`
- `python -m ruff check .` passed
- `python -m mypy src tests` passed
- `python -m black --check .` passed
- `python -m compileall src` passed
- `python -m bicycle_road_event_alarm.cli.seed_publishable_fixture` ran successfully against current `.env`/Supabase data
- `python -m bicycle_road_event_alarm.cli.generate_messages --force-fallback` ran successfully against current `.env`/Supabase data
- Telegram real-send verification succeeded with the private channel id override `-1004448224539`
- Duplicate publish prevention succeeded after the first successful Telegram send

## Important Implementation Notes

- Default Telegram publish is off.
- `.env` is ignored and contains local secrets.
- `.env.example` must remain secret-free.
- Live crawler tests should not be part of default unit tests.
- Current SPATIC parser is intentionally simple and fixture-driven.
- If SPATIC HTML changes, update fixture first, then parser.
- Current normalization is deterministic/rule-based only.
- OpenAI wrapper is implemented and the live API call was attempted; the current OpenAI account returned `insufficient_quota`, so fallback behavior was verified.
- Telegram publisher is implemented and connected to CLI; real publishing succeeded after using private channel id `-1004448224539`.
- GitHub Actions scheduler is not yet implemented.

## Remaining Work

### Next Recommended Task: Persist Environment Settings And Prepare Scheduler

Persist the verified Telegram channel id in local/GitHub environments, then prepare scheduler deployment.

Recommended scope:

- Update local `.env` `TELEGRAM_CHANNEL_ID` to `-1004448224539`
- Add/update GitHub Secrets for Telegram/OpenAI/Supabase
- Decide whether to keep or delete local-fixture DB rows before production schedule
- Implement GitHub Actions workflow with manual dispatch first
- Keep scheduled production publish disabled until manual dispatch is verified

Suggested files:

- `.github/workflows/*`
- `docs/handoff-current-status.md`
- `README.md`

### Then: Sprint 7 Scheduling And GitHub Actions

Implement CI/scheduled execution.

Recommended scope:

- GitHub Actions workflow
- Saturday 06:00 KST schedule
- manual dispatch
- GitHub Secrets mapping
- default tests without live external calls

### Then: Sprint 8/9 Hardening

Recommended scope:

- integration tests with explicit live markers
- error recovery
- operation manual updates
- monitoring/logging refinement
- release checklist

## Current Known Risks

- SPATIC live page returned no new raw events during the latest run.
- Parser may need adjustment when real SPATIC table rows are available.
- OpenAI live call currently fails with `insufficient_quota`.
- Real Telegram API publish succeeded when using the discovered private channel id.
- Local `.env` was not modified by Codex; update `TELEGRAM_CHANNEL_ID=-1004448224539` before future runs without a temporary override.
- A local-fixture publishable event now exists in Supabase unless manually deleted later.
- `publish_attempts` records successful real sends only; dry-run/skipped/failed states are CLI output only for now.
- Some older Korean docs display mojibake in PowerShell output, but repo files should be handled carefully and not rewritten unless needed.
- `created_at_column()` in existing DB models still uses `datetime.utcnow`; current tests pass, but a future cleanup can replace this with timezone-aware UTC if desired.
- Normalization rules are MVP heuristics, not AI-assisted yet.

## What The User Needs To Do

Nothing required before the next implementation step.

Later, before real Telegram publishing:

- Confirm Telegram channel ID
- Confirm bot is channel admin
- Rotate the Telegram bot token because an earlier local traceback printed it in a URL
- Resolve OpenAI API billing/quota before expecting OpenAI-generated messages
- Confirm publishable fixture or live event exists for end-to-end message generation
- Set local `.env` and GitHub Secrets `TELEGRAM_CHANNEL_ID` to `-1004448224539`
- Decide when to switch:
  - `DRY_RUN=false`
  - `ENABLE_TELEGRAM_PUBLISH=true`

Until then, keep publish disabled.
