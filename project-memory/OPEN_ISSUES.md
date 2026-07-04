# Open Issues

Last updated: 2026-07-05

## Must Resolve Soon

### Verify post-push same-day production semantics

- Production-mode Telegram publishing was verified through push-based smoke run `28660665074`.
- GitHub Actions native `schedule` was unreliable and was replaced by Cloudflare Workers Cron.
- The Cloudflare Worker uses production cron `30 22 * * *`.
- Cloudflare deployment is live at `https://bicycle-road-event-alarm-scheduler.matthew-dev.workers.dev`.
- Wrangler confirmed trigger deployment for `schedule: 30 22 * * *`.
- `GITHUB_TOKEN` Worker secret is set (`npx wrangler secret list` returns `GITHUB_TOKEN`).
- Authenticated Worker smoke endpoint created GitHub Actions run `28689723865`, which completed successfully.
- The 2026-07-05 07:31 KST natural Cloudflare-triggered Telegram no-event message was received.
- After pushing the current local changes, verify one production run where:
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
  - `MESSAGE_EVENT_COUNT` reflects only events active on the KST fetch date.

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
