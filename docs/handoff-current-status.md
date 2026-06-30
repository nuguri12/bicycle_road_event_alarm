# Codex Handoff Current Status

Last updated: 2026-06-30

## Purpose

This document is a handoff note for another local Codex session. It summarizes what has been approved, implemented, verified, pushed to GitHub, and what remains.

## Repository State

- Repository: `https://github.com/nuguri12/bicycle_road_event_alarm.git`
- Active branch: `main`
- Branch strategy: user approved direct development on `main`
- Latest pushed commit at handoff: `98d7dca feat: add normalized event storage`
- Current local working tree at last check: clean

## Project Goal

Weekend Cycling Event Alert Service.

The service collects public event/traffic-control information that may affect bicycle-road users, stores raw events, normalizes them, later generates alert messages, and eventually publishes to Telegram on a schedule.

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
- OpenAI planned for message generation, with fallback later
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

Apply DB migrations:

```bash
python -m alembic upgrade head
```

## Current Verification Baseline

Latest verified baseline before this handoff doc:

- `python -m pytest -q` passed with `32 passed`
- `python -m ruff check .` passed
- `python -m mypy src tests` passed
- `python -m black --check .` passed
- `python -m compileall src` passed

## Important Implementation Notes

- Default Telegram publish is off.
- `.env` is ignored and contains local secrets.
- `.env.example` must remain secret-free.
- Live crawler tests should not be part of default unit tests.
- Current SPATIC parser is intentionally simple and fixture-driven.
- If SPATIC HTML changes, update fixture first, then parser.
- Current normalization is deterministic/rule-based only.
- OpenAI is not yet used in runtime logic.
- Telegram is not yet used in runtime logic.
- GitHub Actions scheduler is not yet implemented.

## Remaining Work

### Next Recommended Task: Sprint 5 Message Generation

Implement message generation from `normalized_events`.

Recommended scope:

- Select publishable normalized events:
  - `publish_candidate=true`
  - not already successfully published
- Build deterministic message input DTO
- Generate Korean alert message
- Add OpenAI-backed generator with deterministic fallback
- Keep OpenAI failures non-fatal
- Add tests with mocked OpenAI client

Suggested files:

- `src/bicycle_road_event_alarm/messaging/message_builder.py`
- `src/bicycle_road_event_alarm/messaging/openai_generator.py`
- `src/bicycle_road_event_alarm/messaging/repository.py`
- `tests/unit/messaging/*`

### Then: Sprint 6 Telegram Integration

Implement Telegram publishing after message generation.

Recommended scope:

- Telegram client wrapper
- Dry-run mode support
- `ENABLE_TELEGRAM_PUBLISH` guard
- Store `publish_attempts`
- Avoid duplicate successful publish by `message_hash`

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
- Some older Korean docs display mojibake in PowerShell output, but repo files should be handled carefully and not rewritten unless needed.
- `created_at_column()` in existing DB models still uses `datetime.utcnow`; current tests pass, but a future cleanup can replace this with timezone-aware UTC if desired.
- Normalization rules are MVP heuristics, not AI-assisted yet.

## What The User Needs To Do

Nothing required before the next implementation step.

Later, before real Telegram publishing:

- Confirm Telegram channel ID
- Confirm bot is channel admin
- Decide when to switch:
  - `DRY_RUN=false`
  - `ENABLE_TELEGRAM_PUBLISH=true`

Until then, keep publish disabled.
