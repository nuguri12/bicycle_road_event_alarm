# Normalized Event Storage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Convert raw events into normalized events and persist them with duplicate-key protection.

**Architecture:** Small normalization modules each own one rule family, `normalizer.py` composes them into a value object, and `repository.py` persists new normalized rows.

**Tech Stack:** Python 3.12+, SQLAlchemy, Pytest.

---

### Task 1: Add Failing Tests

- [x] Add title/date/location/classifier tests.
- [x] Add normalizer fixture tests.
- [x] Add repository duplicate-skip tests.
- [x] Run targeted tests and confirm RED failures.

### Task 2: Implement Normalization Modules

- [x] Add title normalization.
- [x] Add datetime parsing.
- [x] Add location extraction.
- [x] Add classification rules.
- [x] Add normalizer composition.

### Task 3: Implement Persistence and CLI

- [x] Add normalized event repository.
- [x] Add `normalize_events` CLI.
- [x] Run local tests.

### Task 4: Verify and Commit

- [x] Run tests, Ruff, Mypy, Black, compileall.
- [x] Run live normalize command against Supabase.
- [ ] Commit and push to `main`.
