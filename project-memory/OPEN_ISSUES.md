# Open Issues

Last updated: 2026-07-03

## Must Resolve Soon

### Restore production cron after temporary smoke

- Current temporary cron: `30 8 3 7 *`
- Intended production cron: `0 22 * * 4`
- Production meaning: every Friday 07:00 KST
- Restore after the 2026-07-03 17:30 KST smoke result is known.

### Verify scheduled production Telegram publish

- Manual runs have been mostly dry-run or skipped by duplicate publish protection.
- Need one scheduled `event=schedule` run with:
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
- It can also allow repeated no-event messages if scheduled too frequently.
- Production cron is weekly, so risk is acceptable for now.

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
