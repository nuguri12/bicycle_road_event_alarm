# Open Issues

Last updated: 2026-07-07

## Must Resolve Soon

None.

## Operational Risks

### Ara Waterway parser precision

- Ara Waterway now uses official K-water 경인아라뱃길 notice URL.
- Live parsing still over-collects surrounding page text and does not reliably extract detail URLs or location/section text.
- Current behavior:
  - DB/CLI records `partial_source_unavailable`.
  - User-facing message remains quiet no-event.
- Next step: narrow notice row selection and extract route/section text such as bridge-to-bridge segments.

### No-event dedupe weakened by send time

- Empty fallback messages now include KST send date and time.
- This helps smoke tests avoid stale duplicate hashes.
- It can also allow repeated no-event messages.
- Cloudflare production cron is daily, so monitor whether the channel receives too many no-event confirmations.

### Split run logs make batch correlation harder

- `ingest_raw_events` creates one `run_logs` row and `generate_messages` creates another.
- The workflow passes the ingest run id to normalization/message selection, but the message publish attempt is recorded against the message run id.
- This is functional, but operational review requires correlating two run ids.
- Next step only if this becomes painful: add a lightweight batch correlation id or store the ingest run id in the message run summary.

## Technical Debt

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
