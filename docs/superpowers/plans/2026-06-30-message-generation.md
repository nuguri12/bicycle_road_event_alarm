# Message Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Generate Korean cycling alert messages from publishable normalized events with OpenAI-first and fallback-safe behavior.

**Architecture:** DTO conversion is isolated in `message_input.py`, deterministic fallback lives in `fallback_generator.py`, OpenAI integration is a thin wrapper, and `service.py` chooses OpenAI or fallback.

**Tech Stack:** Python 3.12+, SQLAlchemy, OpenAI Python SDK, Pytest.

---

### Task 1: Fallback TDD

- [x] Add message input and fallback tests.
- [x] Run targeted tests and confirm RED failures.
- [x] Implement DTO and fallback generator.
- [x] Run targeted tests and confirm GREEN.

### Task 2: OpenAI Wrapper and Service

- [x] Add OpenAI wrapper tests with fake client.
- [x] Add service fallback-on-failure tests.
- [x] Implement wrapper and service.
- [x] Run messaging tests.

### Task 3: Repository and CLI

- [x] Add repository tests for publishable event selection.
- [x] Add CLI entrypoint.
- [x] Run all local checks.

### Task 4: Verify and Commit

- [x] Run tests, Ruff, Mypy, Black, compileall.
- [x] Run CLI against current Supabase data.
- [ ] Commit and push to `main`.
