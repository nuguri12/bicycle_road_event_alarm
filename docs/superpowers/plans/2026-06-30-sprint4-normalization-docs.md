# Sprint 4 Normalization Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 4 Normalization 승인에 필요한 정규화 설계 문서를 작성한다.

**Architecture:** 구현 코드는 만들지 않고, Sprint 3의 Raw Event Candidate를 Sprint 2의 normalized_events 모델로 변환하는 규칙만 확정한다. 날짜, 위치, 분류, 중복, 검증 규칙을 분리해 후속 구현이 테스트 가능하도록 문서화한다.

**Tech Stack:** Markdown, Pydantic validation design, deterministic Python normalization rules, Pytest fixture planning

---

### Task 1: Sprint 3 Approval Record

**Files:**
- Create: `docs/sprint3/APPROVAL.md`

- [ ] **Step 1: Record approval**

Create `docs/sprint3/APPROVAL.md` with the approval date, approved Sprint 3 scope, next step, and implementation restriction.

- [ ] **Step 2: Verify file exists**

Run: `Get-ChildItem docs\sprint3\APPROVAL.md`

Expected: `APPROVAL.md` is listed.

### Task 2: Sprint 4 Normalization Documents

**Files:**
- Create: `docs/sprint4/README.md`
- Create: `docs/sprint4/01-normalization-rules.md`
- Create: `docs/sprint4/02-location-extraction.md`
- Create: `docs/sprint4/03-event-classification.md`
- Create: `docs/sprint4/04-duplicate-rules.md`
- Create: `docs/sprint4/05-validation-rules.md`

- [ ] **Step 1: Write normalization documents**

Create each document with deterministic normalization rules, location extraction, event classification, duplicate rules, validation rules, and user input markers.

- [ ] **Step 2: Verify required documents**

Run: `Get-ChildItem docs\sprint4`

Expected: 6 Markdown files are listed.

- [ ] **Step 3: Verify user input markers**

Run: `rg "\[사용자 입력 필요\]" docs\sprint4`

Expected: Sprint 4 user input markers are listed.

- [ ] **Step 4: Verify implementation restriction**

Run: `rg "Sprint 4 문서 승인 전|Sprint 4 문서가 승인되기 전" docs`

Expected: implementation restriction is documented.
