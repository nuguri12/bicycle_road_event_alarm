# Sprint 3 Crawler Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 3 Crawler 승인에 필요한 크롤러 설계 문서를 작성한다.

**Architecture:** 구현 코드는 만들지 않고, 출처별 수집 책임과 실패 처리 기준만 확정한다. Sprint 2의 `raw_events` 저장 모델에 맞춰 크롤러 출력 필드와 중복 판단 입력값을 정의한다.

**Tech Stack:** Markdown, Requests, BeautifulSoup, Playwright only when required, Pytest fixtures

---

### Task 1: Sprint 2 Approval Record

**Files:**
- Create: `docs/sprint2/APPROVAL.md`

- [ ] **Step 1: Record approval**

Create `docs/sprint2/APPROVAL.md` with the approval date, approved Sprint 2 scope, next step, and implementation restriction.

- [ ] **Step 2: Verify file exists**

Run: `Get-ChildItem docs\sprint2\APPROVAL.md`

Expected: `APPROVAL.md` is listed.

### Task 2: Sprint 3 Crawler Documents

**Files:**
- Create: `docs/sprint3/README.md`
- Create: `docs/sprint3/01-crawler-design.md`
- Create: `docs/sprint3/02-target-sources.md`
- Create: `docs/sprint3/03-crawler-strategy.md`
- Create: `docs/sprint3/04-retry-policy.md`
- Create: `docs/sprint3/05-duplicate-detection-strategy.md`
- Create: `docs/sprint3/06-crawler-test-plan.md`

- [ ] **Step 1: Write crawler documents**

Create each document with MVP crawler boundaries, source candidates, retry policy, duplicate strategy, test plan, and user input markers.

- [ ] **Step 2: Verify required documents**

Run: `Get-ChildItem docs\sprint3`

Expected: 7 Markdown files are listed.

- [ ] **Step 3: Verify user input markers**

Run: `rg "\[사용자 입력 필요\]" docs\sprint3`

Expected: Sprint 3 user input markers are listed.

- [ ] **Step 4: Verify implementation restriction**

Run: `rg "Sprint 3 문서 승인 전|Sprint 3 문서가 승인되기 전" docs`

Expected: implementation restriction is documented.
