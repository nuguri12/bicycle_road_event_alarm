# Sprint 2 Database Documents Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sprint 2 Database 승인에 필요한 데이터베이스 설계 문서를 작성한다.

**Architecture:** 구현 코드는 만들지 않고 Supabase PostgreSQL에 들어갈 논리 스키마와 운영 정책만 확정한다. Sprint 1 데이터 흐름의 Raw Event Candidate, Normalized Event, Classified Event, Publish Result를 추적 가능한 테이블로 분리한다.

**Tech Stack:** Markdown, Mermaid ERD, Supabase PostgreSQL, SQLAlchemy, Alembic

---

### Task 1: Sprint 1 Approval Record

**Files:**
- Create: `docs/sprint1/APPROVAL.md`

- [ ] **Step 1: Record approval**

Create `docs/sprint1/APPROVAL.md` with the approval date, approved Sprint 1 scope, next step, and implementation restriction.

- [ ] **Step 2: Verify file exists**

Run: `Get-ChildItem docs\sprint1\APPROVAL.md`

Expected: `APPROVAL.md` is listed.

### Task 2: Sprint 2 Database Documents

**Files:**
- Create: `docs/sprint2/README.md`
- Create: `docs/sprint2/01-database-erd.md`
- Create: `docs/sprint2/02-entity-definitions.md`
- Create: `docs/sprint2/03-relationships.md`
- Create: `docs/sprint2/04-indexes.md`
- Create: `docs/sprint2/05-migration-strategy.md`
- Create: `docs/sprint2/06-backup-strategy.md`
- Create: `docs/sprint2/07-data-retention-policy.md`

- [ ] **Step 1: Write database documents**

Create each document with MVP table definitions, relationships, indexes, migration policy, backup policy, data retention policy, and user input markers.

- [ ] **Step 2: Verify required documents**

Run: `Get-ChildItem docs\sprint2`

Expected: 8 Markdown files are listed.

- [ ] **Step 3: Verify user input markers**

Run: `rg "\[사용자 입력 필요\]" docs\sprint2`

Expected: Sprint 2 user input markers are listed.

- [ ] **Step 4: Verify implementation restriction**

Run: `rg "Sprint 2 문서 승인 전|Sprint 2 문서가 승인되기 전" docs`

Expected: implementation restriction is documented.
