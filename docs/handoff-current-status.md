# Codex Handoff Current Status

Last updated: 2026-07-20

## Purpose

This document is the handoff note for another local Codex session. It summarizes the current repository state, implemented behavior, operational status, verification baseline, and next recommended tasks.

## Repository State

- Repository: `https://github.com/nuguri12/bicycle_road_event_alarm.git`
- Active branch: `main`
- Branch strategy: the user approved direct development on `main`
- Latest runtime fixes in project memory: psycopg prepared statements are disabled for Supabase Transaction Pooler compatibility; Ara Waterway parsing/location precision, message-stage run correlation, the 2026-07-10 formatting-gate recovery, and the 2026-07-19 Ara Waterway false no-event fixes are documented.
- Check `git status --short` before editing.

## Project Goal

Daily Cycling Event Alert Service.

The service collects public traffic-control and event information that may affect bicycle-road users, stores raw events, normalizes them, generates Korean alert messages, and publishes them to a Telegram channel.

The runtime MVP sources are Hangang park events, Hangang park notices via Seoulboard JSON API (`bbsNo=5211`), and Ara Waterway notices via the official K-water 경인아라뱃길 notice URL. SPATIC code remains in the repository for regression/reference purposes, but the runtime ingest path no longer calls SPATIC.

As of 2026-07-20, the Cloudflare-triggered daily production path is operational. The 2026-07-20 natural run verified the latest Ara Waterway false no-event fixes in production, and local normalization now preserves explicit Ara Waterway blocked sections as message-ready locations.

## Current Operational Status

### GitHub Actions

- Workflow file: `.github/workflows/manual-batch.yml`
- Workflow name: `Manual Batch`
Cloudflare Cron:

```toml
crons = ["30 22 * * *"]
```

Meaning:

- Cloudflare cron uses UTC.
- `30 22 * * *` runs every day at 07:30 KST.

Scheduled runs force real publish mode:

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

Manual runs keep safe defaults:

```env
dry_run=true
enable_telegram_publish=false
force_fallback=false
apply_migrations=false
```

Latest natural production observation:

- The 2026-07-05 07:31 KST Telegram no-event message was received from the Cloudflare-triggered scheduled path.
- The 2026-07-06 07:30 KST Cloudflare-triggered run did execute, but failed before Telegram publishing.
  - Ingest succeeded.
  - `RUN_ID=7b01d78c-3816-472b-856b-4eafcbe28ab1`
  - `RAW_EVENTS_SAVED=16`
  - Normalization failed with `psycopg.errors.DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`.
  - Root cause: psycopg prepared statement reuse conflicts with the Supabase transaction pooler.
  - Fix: SQLAlchemy engine now passes `connect_args={"prepare_threshold": None}` to disable psycopg prepared statements.
  - Local verification against the failed run succeeded with `NORMALIZED_EVENTS_SAVED=16`.
  - Safe dry-run message generation then produced `MESSAGE_STATUS=generated`, `MESSAGE_CONTEXT=no_event`, and `TELEGRAM_STATUS=skipped`.
- The 2026-07-07, 2026-07-08, and 2026-07-09 natural Cloudflare-triggered runs completed and published successfully.
- The 2026-07-10 07:30 KST daily run was dispatched by Cloudflare but failed before ingestion at GitHub Actions `Check formatting`.
  - Failed run: `29054715710`
  - Commit: `a8b3a33`
  - Root cause: `python -m black --check .` would reformat `src/bicycle_road_event_alarm/cli/generate_messages.py` and `src/bicycle_road_event_alarm/normalization/normalizer.py`.
  - Fix commit: `361b2ca` (`style: apply black formatting`)
  - Recovery run: `29057983250`
  - Recovery result: `RAW_EVENTS_SAVED=1`, `NORMALIZED_EVENTS_SAVED=1`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=19`.
- Post-recovery source comparison found the 2026-07-10 no-event message was a false negative:
  - Ara Waterway notice `1224` announced bicycle-road, Aramaru observatory, and Ara waterfall access closure from 2026-07-09 13:00 until weather conditions improve.
  - Root cause: Ara detail body `<차단구간>`/`<차단기간>` was not preserved, and open-ended weather closures were treated as same-day only.
  - At the time of the fix, local live-source normalization produced `PUBLISH_COUNT=1` for notice `1224`.
  - Current source state no longer publishes it because notice `1224` is now marked `[개방완료]`.
- The 2026-07-11 through 2026-07-14 natural Cloudflare-triggered daily runs completed and published no-event Telegram messages successfully.
- The 2026-07-18/2026-07-19 source/message review found a false no-event path for active Ara Waterway notice `1217`:
  - Live source returned 17 candidates, no failures, and notice `1217` normalized to `publish_candidate=True`.
  - Manual workflow run on commit `461154a` emitted `RUN_ID=770e519e-95b4-4df2-b67f-3bdd3aac99da`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_EVENT_COUNT=0`, and `MESSAGE_CONTEXT=no_event`.
  - Commit `461154a` refreshes duplicate raw observations into the current run and updates duplicate normalized rows.
  - Commit `a3685b3` removes the stale message-query `validation_status == "valid"` filter so `publish_candidate=True` is the final message eligibility contract.
  - Local live-source smoke after `a3685b3` produced `MESSAGE_EVENT_COUNT=1` and included Ara Waterway notice `1217` in the generated message.
- The 2026-07-20 07:30 KST natural run verified the Ara Waterway notice `1217` fix in production:
  - Run: `29706279968`
  - Commit: `75f346e`
  - `RUN_ID=2f43dc66-a93b-485a-bf2b-a327dc3b878e`
  - `RAW_EVENTS_SAVED=0`
  - `NORMALIZED_EVENTS_SAVED=0`
  - `MESSAGE_SOURCE=openai`
  - `MESSAGE_EVENT_COUNT=1`
  - `MESSAGE_CONTEXT=event_alert`
  - `TELEGRAM_STATUS=success`
  - `TELEGRAM_MESSAGE_ID=29`
  - The generated Telegram text matched Ara Waterway notice `1217`.
- A follow-up location precision fix now preserves Ara Waterway blocked sections as normalized message locations:
  - `시천교~계양대교 남, 북측 자전거도로`
  - `굴포천 연결수로 좌안(서측) 자전거도로`
  - `아라마루 전망대 및 아라폭포`
- Local Ara Waterway parser smoke after precision updates found 13 K-water notice candidates, included the 2026-06-19 latest board post, excluded footer links, generated detail URLs, and enriched locations from detail-page control sections.

### Schedule Failure Diagnosis

The initial 2026-07-01 14:30 KST scheduled run did not appear in GitHub Actions, so a temporary `*/5 * * * *` smoke schedule was used.

Checked evidence:

- GitHub workflow state was `active`.
- Repository default branch was `main`.
- Remote `main` contained the expected workflow file.
- Remote workflow contained the expected cron expression.
- Later GitHub API checks confirmed schedule runs were being created.

Final root cause of the red scheduled runs:

- Scheduled runs failed at the `Apply database migrations` step.
- Alembic ran migration `0001_initial_schema -> 0002_publish_attempt_success_index`.
- The database migration itself reached Alembic bookkeeping.
- Updating `alembic_version.version_num` failed because the revision ID was 34 characters.
- Alembic's default `version_num` column is `varchar(32)`.

Observed error:

```text
psycopg.errors.StringDataRightTruncation: value too long for type character varying(32)
[SQL: UPDATE alembic_version SET version_num='0002_publish_attempt_success_index' ...]
```

Fix applied locally:

- Added a migration test that enforces revision IDs are at most 32 characters.
- Renamed the second migration revision to `0002_publish_success_idx`.
- Verified `python -m alembic heads` reports `0002_publish_success_idx (head)`.
- Verified `python -m alembic upgrade head` succeeds against Supabase.
- Production cron is now Cloudflare Cron `30 22 * * *`.
- Added workflow `concurrency` so manual and scheduled batches on the same branch run sequentially.
- Separated Alembic migrations from scheduled runtime batches.
- Migrations now run only for manual `workflow_dispatch` when `apply_migrations=true`.

## Runtime Flow

Current GitHub Actions batch flow:

1. Optionally apply database migrations for manual `workflow_dispatch` only when `apply_migrations=true`.
2. Run `python -m bicycle_road_event_alarm.cli.ingest_raw_events`.
3. Capture `RUN_ID=<uuid>` from the ingest output.
4. Store it as `BATCH_RUN_ID` in `$GITHUB_ENV`.
5. Run `python -m bicycle_road_event_alarm.cli.normalize_events --run-id "$BATCH_RUN_ID"`.
6. Run `python -m bicycle_road_event_alarm.cli.generate_messages --run-id "$BATCH_RUN_ID"`.
7. If manual `force_fallback=true`, add `--force-fallback`.

Important behavior:

- `ingest_raw_events` always emits `RUN_ID=<uuid>`.
- `normalize_events --run-id` processes only raw events from the current ingest run.
- `generate_messages --run-id` selects publishable events only from the current ingest run.
- Duplicate raw observations refresh their existing row into the current ingest run, and duplicate normalized events update their existing row.
- Message generation treats `publish_candidate=True` as the final alert eligibility contract; high-impact `needs_review` candidates are no longer excluded by a message-stage `validation_status == "valid"` filter.
- Ara Waterway bridge/section names extracted into `raw_location_text` are preserved as normalized locations with `region=경기`, even when they do not contain the generic 서울/경기 keyword list.
- Empty publishable event sets generate a dated KST no-event message.
- Publish candidates are limited to events active on the KST date when they were fetched.
- Non-empty publish outcomes are recorded in `publish_attempts` for `success`, `failed`, and `skipped`.
- Empty message skips are not recorded because they do not represent a publishable message.
- Message-stage run summaries include the ingest run id when `generate_messages --run-id` is used, making ingest, message, and publish records easier to correlate.

## Environment And Secrets

The user has created:

- Supabase project
- Telegram bot/API configuration
- OpenAI API key

Local `.env` exists and is ignored by Git.

Required GitHub Repository Secrets:

- `SUPABASE_DATABASE_URL`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

Known Telegram channel status:

- Private Telegram channel was verified.
- Channel ID used during verification: `-1004448224539`
- Bot was able to send real messages after the channel ID and permissions were fixed.

Do not print or commit secret values.

## Implemented Features

### Project Bootstrap

- `pyproject.toml`
- `.gitignore`
- `.env.example`
- package skeleton under `src/bicycle_road_event_alarm`
- settings loader in `config/settings.py`
- unit test baseline

### Supabase DB Setup

- SQLAlchemy engine/session helpers
- SQLAlchemy psycopg engine disables prepared statements for Supabase transaction pooler compatibility.
- DB health check
- ORM models:
  - `run_logs`
  - `raw_events`
  - `normalized_events`
  - `publish_attempts`
- Alembic environment
- Initial migration
- Partial unique success index for publish deduplication

### Raw Event Ingestion

- Hangang park event fixture parser
- Hangang park notice parser backed by Seoulboard JSON API (`https://seoulboard.seoul.go.kr/front/bbs.json?bbsNo=5211`)
- Ara Waterway notice parser using K-water 경인아라뱃길 notice URL (`https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do`)
- Ara Waterway notice row selector narrowed to board-list rows with `.ntt_sj`.
- Ara Waterway detail URLs are built from `bbsMstrView('<id>')` onclick handlers.
- Ara Waterway title extraction supports board title links with or without nested `strong` tags.
- Ara Waterway location extraction now uses explicit place fields, title parenthetical bridge/section text, detail-page `통제 구간: ...` body lines, and detail pages where `통제 구간` is a label followed by the section line.
- Multi-source ingestion enriches Ara Waterway candidates by fetching each parsed detail URL; detail fetch failures leave the list candidate intact.
- multi-source live ingestion
- SPATIC parser retained but excluded from runtime ingestion
- request timeout/retry wrapper
- raw candidate hashing
- duplicate-aware `raw_events` save
- run log start/finish helpers
- CLI: `python -m bicycle_road_event_alarm.cli.ingest_raw_events`
- graceful source timeout handling:
  - prints `INGEST_STATUS=skipped`
  - prints `INGEST_REASON=source_unavailable`
  - exits successfully so the rest of the batch can still report no-event status

### Normalization

- title cleanup
- date/time parsing
- full date-range parsing for same-day active checks
- location detection
- Ara Waterway-specific bridge/section location preservation
- event type classification
- cyclist impact classification
- deterministic duplicate key
- publish candidate flag
- KST same-day publish candidate filtering
- duplicate-aware normalized save
- CLI: `python -m bicycle_road_event_alarm.cli.normalize_events`
- run-scoped CLI option: `--run-id`

### Message Generation

- message input DTOs
- publishable event repository
- OpenAI wrapper
- deterministic fallback generator
- OpenAI-first message generation service
- fallback on OpenAI errors or invalid output
- no-event fallback message with generated KST date/time and "today" wording
- CLI: `python -m bicycle_road_event_alarm.cli.generate_messages`
- run-scoped CLI option: `--run-id`
- fallback option: `--force-fallback`

### Telegram Publishing

- `TelegramPublishConfig`
- `TelegramPublishResult`
- `RequestsTelegramClient`
- guarded publish behavior:
  - disabled publishing
  - dry-run
  - missing config
  - empty message
  - client failure
- duplicate successful publish prevention
- `publish_attempts` records:
  - `success`
  - `failed`
  - non-empty `skipped`

### Fixtures And Local Verification Helpers

- CLI: `python -m bicycle_road_event_alarm.cli.seed_publishable_fixture`
- Creates one random local publishable fixture event for DB/CLI end-to-end verification.
- Fixture rows were removed after real Telegram verification.

## Current Commands

Install dependencies:

```bash
python -m pip install -e .[dev]
```

Run all local checks:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src tests
python -m black --check .
python -m compileall src
```

Apply migrations:

```bash
python -m alembic upgrade head
```

Run ingestion:

```bash
python -m bicycle_road_event_alarm.cli.ingest_raw_events
```

Run normalization for a specific ingest run:

```bash
python -m bicycle_road_event_alarm.cli.normalize_events --run-id "<RUN_ID>"
```

Generate and publish for a specific ingest run:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>"
```

Force fallback:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>" --force-fallback
```

Seed a test publishable fixture:

```bash
python -m bicycle_road_event_alarm.cli.seed_publishable_fixture
```

## Latest Verification Baseline

Latest full local verification after the 2026-07-20 Ara Waterway location precision fix:

```text
python -m pytest tests/unit/normalization/test_rules.py tests/unit/normalization/test_normalizer.py -q
15 passed

python -m pytest -q
98 passed

python -m ruff check .
All checks passed!

python -m mypy src tests
Success: no issues found in 70 source files

python -m black --check .
73 files would be left unchanged

python -m compileall src
success
```

Latest live-source smoke after the 2026-07-20 Ara Waterway location precision fix:

```text
SOURCE_FAILURES={}
SOURCE_CANDIDATE_COUNT=18
PUBLISH_COUNT=1
PUBLISH title=자전거도로, 아라마루 전망대 및 아라폭포 통행 차단 알림 (7.17(금) 21:30 ~ 기상 여건 완화 시)
PUBLISH raw_location_text=시천교~계양대교 남, 북측 자전거도로; 굴포천 연결수로 좌안(서측) 자전거도로; 아라마루 전망대 및 아라폭포
PUBLISH location_name=시천교~계양대교 남, 북측 자전거도로; 굴포천 연결수로 좌안(서측) 자전거도로; 아라마루 전망대 및 아라폭포
PUBLISH region=경기
PUBLISH validation=valid
PUBLISH url=https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/1217/view.do
```

Latest full local verification after the prepared-statement fix:

```text
python -m pytest -q
91 passed

python -m ruff check .
All checks passed!

python -m mypy src tests
Success: no issues found in 70 source files

python -m black --check .
73 files would be left unchanged

python -m compileall -q src tests
success

npm test
4 passed
```

Latest targeted verification after the 2026-07-09 Ara parser and run-correlation changes:

```text
python -m pytest tests/unit/crawler/test_ara_waterway.py -q
7 passed

python -m pytest tests/unit/messaging/test_generate_messages_cli.py -q
5 passed

python -m pytest -q
91 passed in 2.79s
```

Ara Waterway local smoke against saved K-water snapshots:

```text
candidate_count 13
failures {}
first_location_enriched True
calls 14
```

Remote verification after push:

- GitHub `main` uses `workflow_dispatch`; Cloudflare Cron owns production scheduling.
- GitHub `main` contained workflow `concurrency`.
- GitHub `main` gated `python -m alembic upgrade head` behind manual `apply_migrations=true`.
- GitHub `main` contained `BATCH_RUN_ID` capture.
- GitHub `main` contained `normalize_events --run-id "$BATCH_RUN_ID"`.
- GitHub `main` contained `generate_messages --run-id "$BATCH_RUN_ID"`.

## Operator Checks

After the current local changes are pushed, check GitHub Actions:

1. Open the repository Actions tab.
2. Select `Manual Batch`.
3. Wait for the next daily 07:30 KST Cloudflare-triggered run, or run `workflow_dispatch` manually to verify the same batch path.
4. Use `apply_migrations=true` only when an Alembic migration should be applied.
5. Open the run logs.
6. Confirm:
   - `RUN_ID=<uuid>`
   - `MESSAGE_STATUS=generated`
   - `MESSAGE_SOURCE=openai` or `MESSAGE_SOURCE=fallback`
   - `MESSAGE_EVENT_COUNT=<number>` where only same-day KST active events should count
   - `TELEGRAM_STATUS=success`, `failed`, or `skipped`
   - If Ara Waterway notice `1217` is still active after the location precision fix is pushed, expect `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, `TELEGRAM_STATUS=success`, and a message location that includes the detailed blocked sections rather than `구간 확인 필요`.

Check Supabase:

```sql
select id, status, started_at, finished_at, raw_event_count, normalized_event_count, published_message_count, error_summary
from run_logs
order by started_at desc
limit 10;
```

```sql
select run_id, status, failure_reason, attempted_at, telegram_channel_id
from publish_attempts
order by attempted_at desc
limit 10;
```

## Known Risks

- GitHub Actions native schedule was unreliable in this project.
- Cloudflare Workers Cron now owns the production trigger and has produced verified successful natural daily runs after the 2026-07-06 prepared-statement incident.
- The first natural production run after commit `a3685b3` was verified on 2026-07-20 with `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, and `TELEGRAM_STATUS=success`.
- The Ara Waterway location precision fix is locally verified, but still needs the next production run after push to confirm that Telegram output includes detailed blocked sections instead of `구간 확인 필요`.
- Ara Waterway parser precision has been improved for the current K-water board DOM, including title links without nested `strong` tags and detail pages where `통제 구간` is followed by a separate section line, but it still depends on `.ntt_sj`, `.ntt_cn`, and `bbsMstrView('<id>')` remaining stable.
- Ara Waterway detail enrichment adds one detail HTTP request per parsed candidate; failures are tolerated but would reduce location precision.
- Source outage and true no-event are separated in DB/CLI context, while partial outages intentionally remain quiet in user-facing messages.
- Message-stage run summaries now include the ingest run id when `generate_messages --run-id` is used; add a dedicated batch correlation id only if manual operations review remains painful.
- HTML/API parsers are fixture-driven and may require fixture updates when source pages change.
- The current crawler stack remains `requests` + BeautifulSoup. Scrapling is recorded as a future source-level evaluation option, not an approved full-engine migration.
- Normalization rules are deterministic MVP heuristics.
- Some older sprint docs may still contain mojibake text from earlier encoding issues.

## Recommended Next Tasks

1. Push the Ara Waterway location precision fix, then verify the next 07:30 KST Cloudflare-triggered production run if notice `1217` remains active.
2. Continue light monitoring of daily 07:30 KST Cloudflare-triggered production runs.
3. Monitor Ara Waterway live-source precision and add fixtures only if K-water markup changes again.
4. Add only one new regional source after current parser/source precision stays stable.
5. Evaluate Scrapling only if a concrete source-level parser problem appears; start with one parser adapter and fixture/live-smoke comparison, not a full crawler rewrite.
6. Review whether message-stage run summaries are sufficient for operations correlation before adding a dedicated batch id.
7. Revisit no-event message dedupe only if daily no-event confirmations become noisy.
8. Treat Hangang notice detail fetching as lower priority unless real source coverage gaps recur.
