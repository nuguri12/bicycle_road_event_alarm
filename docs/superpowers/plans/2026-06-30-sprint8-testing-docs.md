# Sprint 8 Testing Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 8 Testing 승인에 필요한 테스트 전략 문서를 작성한다.

**Architecture:** 구현 코드는 만들지 않고, 각 모듈의 단위 테스트, 통합 테스트, 외부 API mock, 실패 복구, 회귀 테스트 기준만 확정한다. 테스트는 Pytest를 중심으로 하고 Ruff, Black, Mypy를 품질 게이트로 둔다.

**Tech Stack:** Markdown, Pytest, pytest markers, fixtures, mocks, Ruff, Black, Mypy, GitHub Actions test design

---

### Task 1: Sprint 7 Approval Record

**Files:**
- Create: `docs/sprint7/APPROVAL.md`

- [ ] **Step 1: Record approval**

Create `docs/sprint7/APPROVAL.md` with the approval date, approved Sprint 7 scope, next step, implementation restriction, and deferred checklist policy.

- [ ] **Step 2: Verify file exists**

Run: `Get-ChildItem docs\sprint7\APPROVAL.md`

Expected: `APPROVAL.md` is listed.

### Task 2: Sprint 8 Testing Documents

**Files:**
- Create: `docs/sprint8/README.md`
- Create: `docs/sprint8/01-testing-strategy.md`
- Create: `docs/sprint8/02-unit-tests.md`
- Create: `docs/sprint8/03-integration-tests.md`
- Create: `docs/sprint8/04-crawler-tests.md`
- Create: `docs/sprint8/05-database-tests.md`
- Create: `docs/sprint8/06-ai-tests.md`
- Create: `docs/sprint8/07-telegram-tests.md`
- Create: `docs/sprint8/08-regression-tests.md`
- Create: `docs/sprint8/09-failure-recovery-tests.md`
- Create: `docs/sprint8/10-mock-tests.md`
- Create: `docs/sprint8/11-coverage-goals.md`

- [ ] **Step 1: Write testing documents**

Create each document with test scope, validation method, mock policy, failure recovery coverage, and user input markers.

- [ ] **Step 2: Verify required documents**

Run: `Get-ChildItem docs\sprint8`

Expected: 12 Markdown files are listed.

- [ ] **Step 3: Verify user input markers**

Run: `rg "\[사용자 입력 필요\]" docs\sprint8`

Expected: Sprint 8 user input markers are listed.

- [ ] **Step 4: Verify implementation restriction**

Run: `rg "Sprint 8 문서 승인 전|Sprint 8 문서가 승인되기 전" docs`

Expected: implementation restriction is documented.
