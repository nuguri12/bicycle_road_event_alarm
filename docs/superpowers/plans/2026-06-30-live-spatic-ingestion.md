# Live SPATIC Ingestion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fetch live SPATIC HTML through a retrying HTTP client and save parsed raw event candidates into Supabase.

**Architecture:** `crawler/http.py` owns network retries, `crawler/spatic_ingestion.py` owns source orchestration, repository functions own DB persistence, and `cli/ingest_raw_events.py` wires environment, DB, and ingestion together.

**Tech Stack:** Python 3.12+, Requests, BeautifulSoup, SQLAlchemy, Pytest.

---

### Task 1: Add Failing Tests

- [x] Add HTTP retry tests.
- [x] Add SPATIC ingestion orchestration tests.
- [x] Add run log repository tests.
- [x] Run targeted tests and confirm RED failures.

### Task 2: Implement Runtime Code

- [x] Add retrying HTTP client.
- [x] Add SPATIC fetch orchestration.
- [x] Add run log repository helpers.
- [x] Add CLI entrypoint.

### Task 3: Verify

- [x] Run unit tests, Ruff, Mypy, Black, compileall.
- [x] Run live command against Supabase with network approval.

### Task 4: Commit

- [ ] Commit and push to `main`.
