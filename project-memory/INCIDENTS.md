# Incidents

Last updated: 2026-07-19

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

## 2026-07-19: Active Ara Waterway closure omitted from Telegram message

- Symptom: The user received a no-event Telegram message even though live source checks showed active Ara Waterway notice `1217` for a bicycle-road/weather closure.
- Impact: The daily alert could miss an active high-impact cycling-road closure and tell users there were no caution events.
- Root cause: Two filters conflicted with the intended runtime contract. First, duplicate raw source observations were tied to prior runs, while normalization/message generation were scoped to the current ingest run. Second, message selection re-filtered candidates with `validation_status == "valid"`, excluding high-impact `needs_review` rows even after normalization had marked them `publish_candidate=True`.
- Fix: Commit `461154a` refreshes duplicate raw observations into the current run and updates duplicate normalized rows. Commit `a3685b3` removes the stale message-query `validation_status == "valid"` filter so `publish_candidate=True` is the final alert eligibility contract.
- Verification: Local checks after `a3685b3` passed: `python -m pytest -q` reported `96 passed`; targeted messaging repository tests passed; live-source dry-run smoke returned 17 candidates, no source failures, `MESSAGE_EVENT_COUNT=1`, and included Ara Waterway notice `1217`; Telegram publisher smoke reached `dry_run`.
- Prevention: For future false no-event reports, compare live source candidates, normalized `publish_candidate`, message query eligibility, and final `MESSAGE_EVENT_COUNT` before changing parser logic. Do not add a second eligibility filter after normalization unless it is explicitly part of the `publish_candidate` contract.
- Follow-up: Confirm the next natural 07:30 KST production run after commit `a3685b3`. If notice `1217` remains active, expect `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, and `TELEGRAM_STATUS=success`.

## 2026-07-10: Telegram message missing because formatting gate stopped production batch

- Symptom: The expected 2026-07-10 07:30 KST Telegram message did not arrive.
- Impact: The natural Cloudflare-triggered production run was created but stopped before ingestion, normalization, and Telegram publishing.
- Root cause: GitHub Actions run `29054715710` checked out commit `a8b3a33` and failed at `Check formatting` because `python -m black --check .` would reformat `src/bicycle_road_event_alarm/cli/generate_messages.py` and `src/bicycle_road_event_alarm/normalization/normalizer.py`.
- Fix: Applied Black formatting and pushed commit `361b2ca` (`style: apply black formatting`).
- Verification: Local checks passed: `python -m pytest -q` reported 92 passed, `python -m ruff check .` passed, `python -m mypy src tests` passed, `python -m black --check .` passed, and `python -m compileall src` succeeded.
- Recovery: Manually dispatched the production `Manual Batch` workflow on `main`; run `29057983250` completed successfully. It emitted `RUN_ID=61ada9fd-2911-427a-92f9-57c80d5f1f0b`, `RAW_EVENTS_SAVED=1`, `NORMALIZED_EVENTS_SAVED=1`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, and `TELEGRAM_MESSAGE_ID=19`.
- Additional finding: Comparing the sent no-event message with live source data showed a false negative. Ara Waterway notice `1224` announced bicycle-road, Aramaru observatory, and Ara waterfall access closure from 2026-07-09 13:00 until weather conditions improve. The pipeline saved/normalized the notice but did not publish it because detail body `<차단구간>`/`<차단기간>` was not preserved and the open-ended weather closure was treated as a one-day event.
- Additional fix: Preserve Ara Waterway detail body during enrichment, extract `<차단구간>` sections, and treat non-completed `기상 여건 완화 시` bicycle-road closures as active after the start date.
- Prevention: Run `python -m black --check .` or `python -m black ...` before pushing changes that affect Python files. For missing Telegram messages, keep checking Actions run steps before assuming scheduler failure.
- Follow-up: Resolved on 2026-07-10. Consider a one-off corrective Telegram alert for Ara Waterway notice `1224` if user-facing correction is desired.

## 2026-07-06: Telegram message missing after Cloudflare scheduled run

- Symptom: The expected 07:30 KST Telegram message did not arrive.
- Impact: The daily user-facing alert was not delivered even though the Cloudflare cron trigger created a GitHub Actions run.
- Root cause: The batch reached ingestion and saved 16 raw events, then `normalize_events` failed with `psycopg.errors.DuplicatePreparedStatement: prepared statement "_pg3_0" already exists`. Supabase Transaction Pooler reused a server connection where psycopg had already created the same prepared statement name.
- Fix: Disable psycopg prepared statements in the SQLAlchemy engine with `connect_args={"prepare_threshold": None}`.
- Verification: Re-ran normalization locally for failed run `7b01d78c-3816-472b-856b-4eafcbe28ab1`; it completed with `NORMALIZED_EVENTS_SAVED=16`. Safe dry-run message generation then produced `MESSAGE_CONTEXT=no_event`.
- Prevention: Keep Supabase Transaction Pooler compatibility in DB engine tests and verify production runs after DB connection behavior changes.
- Follow-up: Resolved on 2026-07-07. The 07:31 KST production run completed message publishing successfully with no `DuplicatePreparedStatement` recurrence.

## 2026-07-06: Initial diagnosis risk when Telegram message is missing

- Symptom: A missing Telegram message can look like a cron scheduling failure even when the scheduler actually ran.
- Impact: Debugging can drift toward Cloudflare/GitHub trigger investigation before checking pipeline step failures.
- Root cause: The visible symptom is the same for schedule failure and mid-pipeline failure: no Telegram message.
- Fix: Use a standard diagnosis order: Cloudflare trigger evidence, GitHub Actions run existence, ingest output and `RUN_ID`, normalization result, message generation output, Telegram publish result, then DB run logs and publish attempts.
- Verification: The 2026-07-06 issue was correctly reclassified from possible scheduler failure to normalization failure after reviewing the GitHub Actions log.
- Prevention: Future agents should not infer "cron did not run" from "Telegram did not arrive" without checking Actions logs and DB state.
- Follow-up: Consider adding clearer run-level status summaries to `run_logs`.
