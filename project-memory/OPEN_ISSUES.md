# Open Issues

Last updated: 2026-07-21

## Operational Risks

### Verify same-raw normalized dedupe in production

- A 2026-07-21 user-reported Telegram message contained two entries for Ara Waterway notice `1217` with the same URL: one detailed-location row and one stale `구간 확인 필요` row.
- Local code now updates/deletes normalized rows by `raw_event_id` before duplicate-key fallback.
- Next step: after pushing the fix, verify the next production run has at most one message item per `raw_event_id`/source URL.
- Optional cleanup if needed before the next run: mark or delete the stale `구간 확인 필요` normalized row for notice `1217` in Supabase.

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
- Current crawler stack is intentionally `requests` + BeautifulSoup because the active sources are static enough for the MVP.
- Future option: evaluate Scrapling only as a source-level parser adapter when a real source repeatedly breaks BeautifulSoup selectors, over-collects page chrome, or requires anti-bot/dynamic-rendering support.
- Do not replace the whole crawler engine preemptively; keep the raw candidate output contract stable and compare Scrapling output against existing fixtures/live smoke before adoption.

### Normalization is deterministic MVP logic

- Current rules are heuristic.
- OpenAI is used for message generation, not as the source of truth for event validity.
