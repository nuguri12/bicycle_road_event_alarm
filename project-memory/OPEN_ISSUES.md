# Open Issues

Last updated: 2026-08-04

## Operational Risks

### 2026-08-04 missing daily Telegram message

- Symptom: No Telegram message was received for the 2026-08-04 07:30 KST production run.
- Verified evidence:
  - Live source smoke for `CHECK_KST=2026-08-04 07:32` returned `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=20`, and `PUBLISH_COUNT=2`.
  - The 2 publish candidates were Hangang event items: `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Supabase `run_logs` and `publish_attempts` have no rows after the 2026-08-03 07:31 KST successful publish.
  - Worker public URL returned `200`.
  - Cloudflare API token verified successfully.
  - Wrangler `deployments list` succeeded and latest deployment is still `6b69f230-842b-4fa7-80cc-ca3c6119f158`.
  - Wrangler `secret list` shows `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`.
  - Cloudflare schedules API shows `30 22 * * *`.
  - Cloudflare GraphQL `workersInvocationsScheduled` shows the 2026-08-04 07:30 KST cron fired with `status=scriptThrewException`.
  - Previous scheduled invocations on 2026-07-29 through 2026-08-03 were `success`.
  - Worker script settings returned `observability=null`, so the exact historical exception message is not available through persisted Workers Logs.
- Current assessment: The scheduler fired, but the Worker scheduled dispatch threw before the application batch reached Supabase ingest. The most likely failure point is `triggerWorkflowDispatch`, especially the GitHub API call or the Cloudflare-stored `GITHUB_TOKEN`.
- Proposed fix:
  - Enable Worker observability/log persistence so future exceptions are inspectable.
  - Re-register Cloudflare Worker secret `GITHUB_TOKEN` with a valid GitHub PAT that can dispatch `manual-batch.yml` on `main`.
  - Run the authenticated smoke endpoint only with operator approval because it can publish a real Telegram alert.
  - Confirm GitHub Actions run creation and Supabase/Telgram records after smoke.

### 2026-08-01 missing daily Telegram message

- Status: Follow-up succeeded.
- Summary: The 2026-08-01 daily message was missing and Supabase had no runtime rows after the 2026-07-31 success. The Worker was redeployed with scheduled-dispatch logs and cron was re-applied. The next natural run on 2026-08-02 succeeded with `message_context=event_alert`, `publish_attempts.status=success`, and live source smoke matched the user-received Telegram message URLs.
- Follow-up: Keep this as background context; the active scheduler issue is now the 2026-08-04 `scriptThrewException`.

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
