# Incidents

Last updated: 2026-07-06

## Role

This file records production incidents, operational failures, repeated mistakes, and LLM/user errors that caused user-visible impact, rework, or durable debugging lessons.

Keep unresolved follow-ups in `OPEN_ISSUES.md`. Keep resolved incident history here when future agents should remember what happened, why it happened, how it was fixed, how it was verified, and how to avoid repeating it.

## Entry Template

```text
## YYYY-MM-DD: Short title

- Symptom:
- Impact:
- Root cause:
- Fix:
- Verification:
- Prevention:
- Follow-up:
```

## 2026-07-06: Telegram message missing after Cloudflare scheduled run

- Symptom: The expected 07:30 KST Telegram message did not arrive.
- Impact: The daily user-facing alert was not delivered even though the Cloudflare cron trigger created a GitHub Actions run.
- Root cause: The batch reached ingestion and saved 16 raw events, then `normalize_events` failed with `psycopg.errors.DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`. Supabase Transaction Pooler reused a server connection where psycopg had already created the same prepared statement name.
- Fix: Disable psycopg prepared statements in the SQLAlchemy engine with `connect_args={"prepare_threshold": None}`.
- Verification: Re-ran normalization locally for failed run `7b01d78c-3816-472b-856b-4eafcbe28ab1`; it completed with `NORMALIZED_EVENTS_SAVED=16`. Safe dry-run message generation then produced `MESSAGE_CONTEXT=no_event`.
- Prevention: Keep Supabase Transaction Pooler compatibility in DB engine tests and verify production runs after DB connection behavior changes.
- Follow-up: Confirm the next 07:30 KST production run completes with `TELEGRAM_STATUS=success` or a clear failure reason.

## 2026-07-06: Initial diagnosis risk when Telegram message is missing

- Symptom: A missing Telegram message can look like a cron scheduling failure even when the scheduler actually ran.
- Impact: Debugging can drift toward Cloudflare/GitHub trigger investigation before checking pipeline step failures.
- Root cause: The visible symptom is the same for schedule failure and mid-pipeline failure: no Telegram message.
- Fix: Use a standard diagnosis order: Cloudflare trigger evidence, GitHub Actions run existence, ingest output and `RUN_ID`, normalization result, message generation output, Telegram publish result, then DB run logs and publish attempts.
- Verification: The 2026-07-06 issue was correctly reclassified from possible scheduler failure to normalization failure after reviewing the GitHub Actions log.
- Prevention: Future agents should not infer "cron did not run" from "Telegram did not arrive" without checking Actions logs and DB state.
- Follow-up: Consider adding clearer run-level status summaries to `run_logs`.
