# Open Issues

Last updated: 2026-07-04

## Must Resolve Soon

### Verify Cloudflare scheduled production Telegram publish

- Production-mode Telegram publishing was verified through push-based smoke run `28660665074`.
- GitHub Actions native `schedule` was unreliable and is being replaced by Cloudflare Workers Cron.
- The Cloudflare Worker uses production cron `30 22 * * *`.
- Cloudflare deployment is live at `https://bicycle-road-event-alarm-scheduler.matthew-dev.workers.dev`.
- Wrangler confirmed trigger deployment for `schedule: 30 22 * * *`.
- `GITHUB_TOKEN` Worker secret is not set yet (`npx wrangler secret list` returned `[]`), so scheduled dispatch will fail until the secret is added.
- The 2026-07-03 19:00 KST one-off schedule did not create a GitHub Actions run.
- The 2026-07-03 21:20 KST one-off schedule did not create a GitHub Actions run.
- Need one Cloudflare-triggered `event=workflow_dispatch` run with:
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
  - clear `TELEGRAM_STATUS`
- Check both GitHub Actions logs and Telegram channel.

## Operational Risks

### Ara Waterway timeout

- Ara Waterway often times out from GitHub Actions runners.
- Current behavior:
  - DB/CLI records `partial_source_unavailable`.
  - User-facing message remains quiet no-event.
- Future option: find a more precise official Ara Waterway notice URL or replace the source.

### No-event dedupe weakened by send time

- Empty fallback messages now include KST send date and time.
- This helps smoke tests avoid stale duplicate hashes.
- It can also allow repeated no-event messages.
- Cloudflare production cron is daily, so monitor whether the channel receives too many no-event confirmations.

## Technical Debt

### Older docs may be stale

- `README.md` and `docs/handoff-current-status.md` may not reflect the temporary cron or the latest message behavior.
- Some older docs contain mojibake.
- Prefer `project-memory/` for current operational context.

### Parser fragility

- HTML parsers are fixture-driven and may need updates when source pages change.
- Crawler fixture tests are under `tests/unit/crawler/`.

### Normalization is deterministic MVP logic

- Current rules are heuristic.
- OpenAI is used for message generation, not as the source of truth for event validity.
