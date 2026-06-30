# Raw Event Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Parse the first SPATIC HTML fixtures into raw event candidates and save new candidates to `raw_events`.

**Architecture:** Parsing is isolated under `crawler/spatic.py`, generic raw event candidate behavior lives in `crawler/raw_event.py`, and database persistence lives in `crawler/repository.py`.

**Tech Stack:** Python 3.12+, BeautifulSoup, SQLAlchemy, Pytest.

---

### Task 1: Add Failing Tests

- [x] Add SPATIC parser fixture tests.
- [x] Add content hash determinism tests.
- [x] Add repository duplicate-skip tests.
- [x] Run `python -m pytest tests/unit/crawler -q` and confirm failures.

### Task 2: Implement Raw Event Candidate and Parser

- [x] Add `RawEventCandidate`.
- [x] Add deterministic content hash generation.
- [x] Add SPATIC list/detail parser.
- [x] Run crawler unit tests.

### Task 3: Implement Repository Mapping

- [x] Add candidate-to-model conversion.
- [x] Add duplicate-aware save function.
- [x] Run crawler and DB unit tests.

### Task 4: Verify and Commit

- [x] Run tests, lint, mypy, black, compileall.
- [ ] Commit and push to `main`.
