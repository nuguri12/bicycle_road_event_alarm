# Open Issues

Last updated: 2026-07-19

## Awaiting Production Verification

### Message query excludes high-impact needs-review publish candidates

- 2026-07-19 manual workflow on commit `461154a` produced:
  - `RUN_ID=770e519e-95b4-4df2-b67f-3bdd3aac99da`
  - `RAW_EVENTS_SAVED=0`
  - `NORMALIZED_EVENTS_SAVED=0`
  - `MESSAGE_EVENT_COUNT=0`
  - `MESSAGE_CONTEXT=no_event`
- Live source cross-check immediately after the run found 17 candidates, no source failures, and Ara Waterway notice `1217` as a publish candidate.
- The notice normalized to:
  - `publish_candidate=True`
  - `validation_status=needs_review`
  - `location_name=구간 확인 필요`
  - `cyclist_impact_level=high`
- Root cause:
  - `normalize_raw_event` intentionally allows high-impact bicycle-road closures without precise location as publish candidates.
  - `load_publishable_message_events` then filters SQL results with `NormalizedEvent.validation_status == "valid"`, excluding that publish candidate before message generation.
- Impact: A source item can be classified as publishable but still be omitted from Telegram messages, producing a false no-event message.
- Local fix:
  - `load_publishable_message_events` now uses `publish_candidate=True` as the final message eligibility contract and no longer re-filters by `validation_status == "valid"`.
  - Regression coverage now checks that the message query does not add the stale validation-status filter.
  - Live-source smoke after the fix returned `MESSAGE_EVENT_COUNT=1` and included Ara Waterway notice `1217` in the generated fallback message.
- Next step: confirm the next natural production run after commit `a3685b3` sends the Ara Waterway active closure message if notice `1217` is still active at the source.

### Active event can be missed when the raw source item is a duplicate from a prior run

- 2026-07-18 live-source smoke found Ara Waterway notice `1217` as a publishable active weather closure for the 2026-07-18 07:30 KST batch window.
- The Telegram message received by the user said there were no alert events, so source state and user-facing message are inconsistent.
- Likely root cause:
  - `save_raw_event_candidates` skips rows whose `content_hash` already exists.
  - The workflow scopes normalization and message generation to the current ingest `RUN_ID`.
  - If an open-ended or multi-day notice was already stored in a previous run, the current run may save `RAW_EVENTS_SAVED=0`.
  - `generate_messages --run-id <current_run>` then queries only normalized events joined to raw rows from the current run and misses still-active duplicate source items.
- Evidence:
  - Live source returned 17 candidates and no source failures.
  - Ara Waterway notice `1217` (`https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/1217/view.do`) normalized to `publish_candidate=True` for 2026-07-18 07:30 KST.
  - 2026-07-19 live-source smoke again returned 17 candidates, no source failures, and the same Ara Waterway notice `1217` normalized to `publish_candidate=True` for the 2026-07-19 07:31 KST batch window.
- Local fix:
  - Duplicate raw observations now refresh the existing `raw_events` row with the current ingest `run_id`, latest raw fields, and latest `fetched_at`.
  - Duplicate normalized events now update the existing `normalized_events` row with the latest normalized fields.
  - Regression tests cover both update paths.
- Next step: confirm the next production run includes currently active duplicate source items in message candidate selection. The fix has been pushed in commit `461154a`.

## Operational Risks

### Ara Waterway parser precision

- Ara Waterway now uses official K-water 경인아라뱃길 notice URL.
- Parser precision was improved on 2026-07-09 for board title links without nested `strong` tags and detail pages where `통제 구간` appears as a label followed by the section line.
- Live parsing should still be monitored for future K-water markup changes.
- Current behavior:
  - DB/CLI records `partial_source_unavailable`.
  - User-facing message remains quiet no-event.
- Next step: add a new fixture and parser adjustment if live K-water output again over-collects surrounding page text or misses bridge-to-bridge segments.

### Hangang weekly event notice detail coverage

- Seoulboard JSON listed `(안내) 2026년 7월 1주차 한강공원 주요행사 현황` on 2026-07-08.
- Current crawler filters by cyclist/control relevance from JSON list fields and did not treat this as a cycling caution candidate.
- Simple HTTP access to the hash-based public detail route did not expose detail content.
- Next step only if source coverage becomes the priority: add a small detail fetch path or fixture for Hangang notice details.

### No-event dedupe weakened by send time

- Empty fallback messages now include KST send date and time.
- This helps smoke tests avoid stale duplicate hashes.
- It can also allow repeated no-event messages.
- Cloudflare production cron is daily, so monitor whether the channel receives too many no-event confirmations.

### Split run logs make batch correlation harder

- `ingest_raw_events` creates one `run_logs` row and `generate_messages` creates another.
- The workflow passes the ingest run id to normalization/message selection, but the message publish attempt is recorded against the message run id.
- Message-stage run summaries now include the ingest run id when `generate_messages --run-id` is used.
- This is functional and should make manual operations review easier.
- Next step only if this still becomes painful: add a lightweight dedicated batch correlation id.

## Technical Debt

### Serviceization sequencing

- SNS publishing, Hermes Agent evaluation, VPS scheduler changes, web UI, and rich user preferences are intentionally deferred.
- Next serviceization work should first improve parser/source stability, then add one regional source, then add Telegram personal chat delivery.
- Avoid broad publish abstractions until there is more than one real non-SNS delivery path.

### Older docs may be stale

- Older sprint docs may still describe weekend-oriented behavior or SPATIC-era source choices.
- Some older docs contain mojibake.
- Prefer `project-memory/` for current operational context.

### Parser fragility

- HTML parsers are fixture-driven and may need updates when source pages change.
- Crawler fixture tests are under `tests/unit/crawler/`.

### Normalization is deterministic MVP logic

- Current rules are heuristic.
- OpenAI is used for message generation, not as the source of truth for event validity.
