# Supabase DB Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a SQLAlchemy/Alembic DB environment and verify Supabase PostgreSQL connectivity.

**Architecture:** Runtime code lives under `src/bicycle_road_event_alarm/db`. Models own schema metadata, Alembic imports that metadata for migrations, and live DB checks are kept out of default unit tests.

**Tech Stack:** Python 3.12+, SQLAlchemy 2.x, Alembic, psycopg, python-dotenv, Pytest.

---

### Task 1: Add Failing DB Tests

**Files:**
- Create: `tests/unit/db/test_models.py`
- Create: `tests/unit/db/test_engine.py`
- Create: `tests/unit/db/test_health.py`

- [x] Write tests for expected tables, required columns, unique constraints, DB URL validation, and `SELECT 1` health checks.
- [x] Run `python -m pytest tests/unit/db -q` and confirm the tests fail because `bicycle_road_event_alarm.db` does not exist yet.

### Task 2: Implement DB Runtime Modules

**Files:**
- Create: `src/bicycle_road_event_alarm/db/__init__.py`
- Create: `src/bicycle_road_event_alarm/db/engine.py`
- Create: `src/bicycle_road_event_alarm/db/health.py`
- Create: `src/bicycle_road_event_alarm/db/models.py`

- [x] Add focused modules with Korean feature-section comments.
- [x] Run `python -m pytest tests/unit/db -q` and confirm DB unit tests pass.

### Task 3: Add Alembic Environment

**Files:**
- Create: `alembic.ini`
- Create: `migrations/env.py`
- Create: `migrations/script.py.mako`
- Create: `migrations/versions/0001_initial_schema.py`

- [x] Configure Alembic to read `SUPABASE_DATABASE_URL` through existing settings.
- [x] Add initial schema migration matching SQLAlchemy models.
- [ ] Run `python -m alembic upgrade head` only after live DB connection succeeds.

### Task 4: Verify and Commit

- [x] Run unit tests, lint, type checks, format checks, and compile checks.
- [ ] Run a live Supabase `SELECT 1` check without printing secrets.
- [ ] Commit and push the completed DB setup to `main`.

## Current Blocker

Live Supabase verification is blocked because the local `.env` `SUPABASE_DATABASE_URL` still contains bracket characters in the password segment. Replace the bracketed placeholder with the real database password, or URL-encode literal bracket characters if they are part of the password.
