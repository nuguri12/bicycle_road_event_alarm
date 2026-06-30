# Sprint 5 AI Generation Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 5 AI Generation 승인에 필요한 AI 메시지 생성 설계 문서를 작성한다.

**Architecture:** 구현 코드는 만들지 않고, 검증된 Normalized Event 목록을 15초 안에 읽을 수 있는 Telegram 메시지로 변환하는 정책만 확정한다. AI는 요약과 영향도 설명에만 제한하고, 실패 시 결정적 fallback 메시지로 전환한다.

**Tech Stack:** Markdown, OpenAI API design, deterministic fallback generation, token budgeting, mock-based test planning

---

### Task 1: Sprint 4 Approval Record

**Files:**
- Create: `docs/sprint4/APPROVAL.md`

- [ ] **Step 1: Record approval**

Create `docs/sprint4/APPROVAL.md` with the approval date, approved Sprint 4 scope, next step, and implementation restriction.

- [ ] **Step 2: Verify file exists**

Run: `Get-ChildItem docs\sprint4\APPROVAL.md`

Expected: `APPROVAL.md` is listed.

### Task 2: Sprint 5 AI Generation Documents

**Files:**
- Create: `docs/sprint5/README.md`
- Create: `docs/sprint5/01-prompt-design.md`
- Create: `docs/sprint5/02-ai-usage-policy.md`
- Create: `docs/sprint5/03-fallback-strategy.md`
- Create: `docs/sprint5/04-message-generation-rules.md`
- Create: `docs/sprint5/05-token-optimization-strategy.md`

- [ ] **Step 1: Write AI generation documents**

Create each document with prompt design, AI usage boundaries, fallback behavior, message rules, token optimization, and user input markers.

- [ ] **Step 2: Verify required documents**

Run: `Get-ChildItem docs\sprint5`

Expected: 6 Markdown files are listed.

- [ ] **Step 3: Verify user input markers**

Run: `rg "\[사용자 입력 필요\]" docs\sprint5`

Expected: Sprint 5 user input markers are listed.

- [ ] **Step 4: Verify implementation restriction**

Run: `rg "Sprint 5 문서 승인 전|Sprint 5 문서가 승인되기 전" docs`

Expected: implementation restriction is documented.
