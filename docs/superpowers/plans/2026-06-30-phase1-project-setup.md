# Phase 1 Project Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create the first runnable Python project skeleton for the Weekend Cycling Event Alert Service.

**Architecture:** Source code lives under `src/bicycle_road_event_alarm`, tests live under `tests`, and runtime configuration is loaded from environment variables with safe defaults.

**Tech Stack:** Python 3.12+, Pytest, Ruff, Black, Mypy, SQLAlchemy/Alembic, Supabase PostgreSQL, Telegram Bot API, OpenAI API.

## Constraints

- Develop directly on `main` per user approval.
- Keep production publishing disabled by default.
- Do not store real API keys, database URLs, or Telegram tokens in the repository.
- Add Korean comments around feature sections in code.

## Implementation Tasks

- [x] Add tests for package metadata and environment settings behavior.
- [x] Run the tests and confirm they fail before implementation.
- [x] Add project metadata, dependency declarations, formatter/linter/test configuration.
- [x] Add `.gitignore` and `.env.example` with user-filled placeholders.
- [x] Add the initial package and settings loader.
- [x] Run targeted validation and record remaining risks.

## Acceptance Criteria

- `python -m pytest tests/unit -q` passes after implementation.
- The default runtime configuration does not send Telegram messages.
- Missing user-supplied secrets are discoverable without committing real values.
- User-input fields are clearly marked in `.env.example`.
