# Remaining Risk Opinion

Last updated: 2026-07-01

## Purpose

This note records my opinion on the remaining risks after reviewing the current code line. It is intended for the next working Codex or developer session so the work can continue with the right operational context.

## Current Baseline

The MVP pipeline is implemented and locally healthy:

- Ingest SPATIC raw events.
- Store raw events in Supabase PostgreSQL.
- Normalize stored events.
- Generate Korean alert messages through OpenAI or deterministic fallback.
- Publish to Telegram when explicitly enabled.
- Record publish attempts.
- Run through GitHub Actions manual and scheduled workflow.

The latest local validation I ran in this workspace passed:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src tests
python -m black --check .
python -m compileall src
```

The working tree was clean before this document was added.

## My Risk Ranking

### 1. Fallback Korean Message Encoding

Severity: High

My opinion:

This is the highest code-level risk because it directly affects user-facing Telegram output. `src/bicycle_road_event_alarm/messaging/fallback_generator.py` contains mojibake in literal Korean strings. If OpenAI is unavailable, invalid, disabled, or manually bypassed with `--force-fallback`, the service can publish unreadable Korean.

Why it matters:

- Fallback is not an exceptional debug path. It is the designed resilience path.
- No-event messages also use fallback, so this can happen on normal quiet weekends.
- Current tests lock in the corrupted strings, so the green test suite does not protect message quality.

Recommended next action:

Replace fallback output strings with valid Korean and update tests to assert readable Korean phrases. Keep the tests deterministic and include the no-event case.

Suggested validation:

```bash
python -m pytest tests/unit/messaging/test_fallback_generator.py -q
python -m pytest tests/unit/messaging/test_generate_messages_cli.py -q
python -m ruff check .
python -m mypy src tests
```

Relevant files:

- `src/bicycle_road_event_alarm/messaging/fallback_generator.py`
- `tests/unit/messaging/test_fallback_generator.py`
- `tests/unit/messaging/test_generate_messages_cli.py`
- `tests/unit/messaging/test_publish_service.py`

### 2. Batch Run ID Traceability Split

Severity: Medium to High

My opinion:

`generate_messages --run-id <RUN_ID>` correctly uses the ingest run ID to load publishable events, but it starts a new `run_logs` row and records `publish_attempts.run_id` against that new ID. This is technically consistent with the current implementation, but it weakens operational traceability.

Why it matters:

- Operators naturally expect one batch run ID to connect ingestion, normalization, message generation, and publish attempts.
- The handoff SQL asks the operator to inspect `run_logs` and `publish_attempts`, but the IDs may not line up as one logical run.
- Debugging a failed publish after a successful ingest becomes less direct.

Recommended next action:

Decide the intended model explicitly:

- Option A, preferred: treat one GitHub workflow execution as one logical run and record message publish attempts with the ingest `BATCH_RUN_ID`.
- Option B: keep separate run log rows per stage, but add an explicit parent/correlation ID so operators can join stages.

For this project size, Option A is simpler. It likely means `generate_messages` should use the provided `--run-id` for publish attempt recording when present, and only create a new run log when no run ID is provided.

Suggested validation:

```bash
python -m pytest tests/unit/messaging/test_generate_messages_cli.py -q
python -m pytest tests/unit/messaging/test_publish_service.py -q
python -m pytest -q
```

Operational check:

```sql
select id, raw_event_count, normalized_event_count, published_message_count, error_summary
from run_logs
order by started_at desc
limit 10;

select run_id, status, failure_reason, attempted_at
from publish_attempts
order by attempted_at desc
limit 10;
```

Relevant files:

- `src/bicycle_road_event_alarm/cli/generate_messages.py`
- `src/bicycle_road_event_alarm/messaging/publish_service.py`
- `src/bicycle_road_event_alarm/messaging/publish_history.py`
- `tests/unit/messaging/test_generate_messages_cli.py`

### 3. Temporary GitHub Actions Schedule

Severity: Medium

My opinion:

The workflow is intentionally set to `*/5 * * * *` as a schedule smoke test. That is useful while diagnosing whether GitHub creates scheduled runs, but it should not remain indefinitely because scheduled runs force real publish mode.

Why it matters:

- Scheduled workflow runs set `ENABLE_TELEGRAM_PUBLISH=true` and `DRY_RUN=false`.
- The current five-minute cadence can repeatedly publish no-event or fallback messages if the duplicate hash changes or message content varies by date/context.
- Even if deduplication blocks repeated identical successes, this is still not the intended production operating rhythm.

Recommended next action:

Inspect GitHub Actions for at least one `schedule` event run, then restore production cron:

```yaml
cron: "0 22 * * 4"
```

That runs every Friday 07:00 KST because GitHub Actions cron is UTC.

Suggested validation:

- Confirm an Actions run exists with event type `schedule`.
- Confirm logs include:
  - `RUN_ID=<uuid>`
  - `MESSAGE_STATUS=generated`
  - `MESSAGE_SOURCE=openai` or `MESSAGE_SOURCE=fallback`
  - `MESSAGE_EVENT_COUNT=<number>`
  - `TELEGRAM_STATUS=success`, `failed`, or `skipped`
- Confirm Supabase rows for `run_logs` and `publish_attempts`.
- Restore cron and push.

Relevant files:

- `.github/workflows/manual-batch.yml`
- `docs/handoff-current-status.md`

### 4. Source Outage vs True No-Event Messaging

Severity: Medium

My opinion:

The ingestion CLI now handles source unavailability without failing the whole batch, which is good operationally. The remaining problem is product semantics: a source outage can flow into the same user-facing no-event path as a genuine no-event weekend.

Why it matters:

- "No events found" and "source unavailable" mean different things to users.
- For an alert channel, false reassurance is worse than a clearly degraded status.
- Operators also need to distinguish normal quiet runs from crawler/source failures.

Recommended next action:

Carry source status from ingest to message generation. If the current run skipped ingestion because the source was unavailable, generate an operator-safe message such as:

```text
[YYYY-MM-DD] Source status: SPATIC was unavailable, so this run could not confirm whether bicycle-impacting events exist.
```

Whether this message should be sent to Telegram or only recorded depends on the product decision. My recommendation is to send a short degraded-status message only if the service is already configured for real scheduled publishing.

Suggested validation:

Add tests for:

- `INGEST_STATUS=skipped` with `INGEST_REASON=source_unavailable`.
- Message generation for source-unavailable run logs.
- Publish attempt recording for degraded-status messages.

Relevant files:

- `src/bicycle_road_event_alarm/cli/ingest_raw_events.py`
- `src/bicycle_road_event_alarm/cli/generate_messages.py`
- `src/bicycle_road_event_alarm/crawler/repository.py`
- `src/bicycle_road_event_alarm/messaging/fallback_generator.py`

### 5. SPATIC Source Fit and Parser Fragility

Severity: Medium

My opinion:

SPATIC is acceptable as the first MVP source, but it is not a strong long-term source for bicycle-road users. It is traffic-control oriented and the current parser is fixture-driven. The next source should improve relevance rather than just increase volume.

Why it matters:

- More broad vehicle traffic data can increase noise.
- Bicycle users need weekend route impact, park events, festivals, and riverside access changes.
- HTML source changes can silently reduce useful output unless parser tests are refreshed.

Recommended next action:

Add a second source with higher bicycle relevance before adding more broad traffic feeds. My recommended order is:

1. Hangang park events.
2. Hangang park notices.
3. Other Seoul/Gyeonggi park or festival notices with clear location and date fields.

Suggested validation:

- Add source-specific fixtures.
- Add parser unit tests before live ingestion changes.
- Add source name to stored raw events.
- Confirm normalization rules still classify cyclist impact conservatively.

Relevant areas:

- `src/bicycle_road_event_alarm/crawler/`
- `tests/fixtures/crawler/`
- `tests/unit/crawler/`
- `src/bicycle_road_event_alarm/normalization/`

### 6. Project Documentation Mojibake

Severity: Low to Medium

My opinion:

The code can run with corrupted comments and docs, but the repository is harder to operate safely. The README has mojibake in user-facing Korean text. Some source comments and tests also contain mojibake.

Why it matters:

- README is the first operational entrypoint.
- Future Codex sessions can misread intent if comments and test strings are corrupted.
- Tests that assert corrupted Korean make later cleanup harder.

Recommended next action:

After fixing fallback literals, repair the README and only the comments/tests that affect current development context. Avoid a broad rewrite of all sprint docs unless there is a concrete need.

Suggested validation:

```bash
python -m pytest -q
python -m black --check .
```

Relevant files:

- `README.md`
- `src/bicycle_road_event_alarm/messaging/fallback_generator.py`
- messaging tests that currently assert mojibake strings

## Suggested Work Order

1. Fix fallback Korean output and tests.
2. Fix or explicitly document run ID traceability for publish attempts.
3. Check GitHub Actions schedule smoke test result and restore production cron.
4. Add degraded source-unavailable messaging.
5. Add Hangang park source fixtures and parser.
6. Repair README mojibake.

## Acceptance Criteria For Next Stable State

- Fallback and no-event Telegram text is readable Korean.
- Tests assert readable Korean output, not corrupted text.
- A scheduled workflow run is observed and production cron is restored.
- Operators can connect `run_logs` and `publish_attempts` for one logical batch.
- Source outage is not presented as a confident no-event result.
- The next source choice improves bicycle relevance.
