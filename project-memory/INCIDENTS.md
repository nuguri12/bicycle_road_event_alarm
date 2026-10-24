# Incidents

Last updated: 2026-10-24

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

## 2026-10-24: Scheduled batches stopped at mypy before ingestion

- Symptom: Ten consecutive GitHub `schedule` runs completed with failure; no ingest or Telegram step started. Run `40017405632` failed at `Run Mypy`.
- Impact: Daily Telegram alerts were not delivered during those runs.
- Root cause: Unbounded dependency ranges installed mypy 2.4.0 and SQLAlchemy 2.1.6 on GitHub, whose typing combination rejected two query annotations in `messaging/repository.py`. The locally installed mypy 1.20.2 and SQLAlchemy 2.0.48 passed.
- Fix: Bound mypy to `<2` and SQLAlchemy to `<2.1` in `pyproject.toml`; commit `dcc009d` also scopes duplicate hashes to the KST send date.
- Verification: GitHub manual dry-run `40086638543` passed tests, Ruff, mypy, Black, compilation, ingest, normalization, and message generation. Supabase recorded the matching successful run with Telegram intentionally skipped.
- Prevention: Keep CI dependency ranges within tested versions and verify a remote dry-run after changes to CI or dependencies.
- Follow-up: Confirm natural scheduled Telegram delivery in `OPEN_ISSUES.md`.

## 2026-09-01: GitHub scheduled run delayed, Telegram content matched source

- Symptom: The expected 2026-09-01 morning Telegram message was not received at the normal 07:30 KST window, then later arrived with one Hangang event.
- Impact: Daily alert delivery was delayed by about 2 hours 50 minutes.
- Root cause: Localized to the scheduler/Actions layer. At the initial check, Supabase had no `run_logs` or `publish_attempts` rows since 2026-09-01 07:00 KST, and Cloudflare backup schedules still returned `[]`; the app pipeline had not started. The batch later reached Supabase and finished quickly.
- Evidence: Supabase later recorded ingest run `a0b8508a-e53d-43b9-9a15-8c4e8bc06e09` at 10:21 KST, message run `780222c0-3b6a-4293-80f6-22b5c38f925a` at 10:22 KST, and `publish_attempts.status=success` with hash prefix `d88a8df7a8b4`. Live-source replay for 2026-09-01 found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=23`, and `PUBLISH_COUNT=1`: Hangang event `evntSn=446`, active from 2026-08-18 through 2026-09-04. The user-received Telegram message matched that single publish candidate; event `evntSn=441` ended on 2026-08-31 and was correctly excluded.
- Fix: None applied during verification.
- Verification: DB publish status and live-source fallback replay both matched the user-received message.
- Prevention: Complete an independent backup trigger or replace the primary scheduler if GitHub native schedule latency continues. Confirm the GitHub Actions run header when authenticated/UI access is available.
- Follow-up: Track scheduler reliability and Cloudflare backup remediation in `OPEN_ISSUES.md`.

## 2026-08-30: Daily messages skipped by historical duplicate hash

- Symptom: The user received the 2026-08-29 Telegram alert but did not receive messages on 2026-08-30 or 2026-08-31.
- Impact: Daily alert delivery was skipped even though production batches ran.
- Root cause: `publish_message_once` checks `has_successful_publish(message_hash)` across all history. The 2026-08-30 and 2026-08-31 fallback messages had the same body hash as the successful 2026-08-29 message, so both later publish attempts were skipped with `duplicate_successful_publish`.
- Evidence: Supabase recorded 2026-08-30 message run `d163ecc1-64da-4692-8209-bb5b38c5eafa` and 2026-08-31 message run `29b8c603-2261-447f-a845-005b26f526f8`; both publish attempts had `status=skipped`, `failure_reason=duplicate_successful_publish`, and `message_hash_prefix=a49388142ae4`. The 2026-08-29 successful publish attempt had the same hash prefix. Live-source replay for 2026-08-31 found the same two Hangang event candidates as the 2026-08-29 user message. The same pattern recurred on 2026-09-02 and 2026-09-03: both batches generated `event_alert` messages, both publish attempts were skipped with `duplicate_successful_publish`, and both shared the 2026-09-01 success hash prefix `d88a8df7a8b4`. It recurred on 2026-09-07 with the 2026-09-06 success hash prefix `912d6d6647c5`, and again on 2026-09-17 through 2026-09-19 with the 2026-09-16 success hash prefix `8aea6c3d9916`.
- Fix: Commit `dcc009d` includes the KST send date in the message hash while keeping the existing unique-success index for same-day duplicate prevention.
- Verification: Regression tests and remote dry-run `40086638543` passed; actual next-day Telegram delivery remains unverified.
- Prevention: Add regression tests for daily duplicate policy: same body on a new KST date should send, same body on the same KST date should skip.
- Follow-up: Verify a natural scheduled alert reaches Telegram; track in `OPEN_ISSUES.md`.

## 2026-08-28: GitHub scheduled run absent by 08:10 KST

- Symptom: The expected 2026-08-28 morning Telegram message had not arrived by 08:10 KST.
- Impact: Two active Hangang event alerts were not published by the normal morning delivery window.
- Root cause: Localized to the GitHub Actions schedule delivery/queueing layer. Supabase had no runtime rows after the 2026-08-27 12:27 KST late delivery at 08:10 KST, live source crawling was healthy, and Cloudflare backup cron was not active. The batch later appeared and finished quickly once a runner started.
- Evidence: Supabase had zero `run_logs` and zero `publish_attempts` since 2026-08-28 07:00 KST at the 08:10 check. Cloudflare schedules API returned `[]`, confirming the backup cron was still not active. Live source check for `CHECK_KST=2026-08-28 08:10` found no source failures, 21 source candidates, and 2 publish candidates: Hangang event `evntSn=446` and `evntSn=441`. Supabase later recorded ingest run `7ccdda61-e24a-4567-ac93-1aee9572dd6d`, message run `665dba8b-4983-47d2-bd04-ad0d95582960`, and `publish_attempts.status=success` at 15:14 KST. The shared GitHub Actions job log starts at `2026-08-28T06:13:27Z` (15:13:27 KST), checked out commit `e1b9ded`, and ran with `ENABLE_TELEGRAM_PUBLISH=true`, `DRY_RUN=false`, and `FORCE_FALLBACK=true`.
- Fix: None applied yet during diagnosis. The existing local/repo fix for a Cloudflare backup cron exists, but it has not been applied to Cloudflare production because the current `CLOUDFLARE_API_TOKEN` cannot edit Worker scripts or schedules.
- Verification: DB and Cloudflare API checks verified no production batch or backup trigger had run by 08:10 KST. DB and job-log checks after delivery show about 72 seconds from runner start to `TELEGRAM_STATUS=success`; DB-visible app steps ran from `15:14:07` to `15:14:39` KST, so the delay was before the app pipeline started.
- Prevention: Complete Cloudflare backup deployment with a Worker-edit-capable credential, or move the primary scheduler to a more reliable external cron once credentialing is fixed.
- Follow-up: Confirm in GitHub Actions UI whether the 2026-08-28 run event was `Scheduled`, and compare run created/queued time with job started time to distinguish delayed event delivery from Actions queue delay.

## 2026-08-27: GitHub scheduled run was not created

- Symptom: The expected 2026-08-27 morning Telegram message did not arrive.
- Impact: Two active Hangang event alerts were not published at the normal morning delivery time.
- Root cause: GitHub Actions native `schedule` did not create a 2026-08-27 workflow run. Supabase had no `run_logs` or `publish_attempts` after the 2026-08-26 successful message run, and the user-provided Actions screenshot showed no 2026-08-27 run. Source crawling was healthy locally.
- Evidence: Live source check for `CHECK_KST=2026-08-27 07:50` found no source failures, 21 source candidates, and 2 publish candidates: Hangang event `evntSn=446` and `evntSn=441`. Local workflow-equivalent checks passed on `origin/main`.
- Fix: Local config now keeps GitHub Actions schedule as primary at `30 22 * * *` and adds a Cloudflare Worker backup cron at `45 22 * * *`. Scheduled/backup paths force deterministic fallback message generation so duplicate publish prevention can rely on a stable message hash.
- Verification: Targeted workflow/config tests pass locally. Cloudflare schedule read succeeded and showed no active cron triggers before the fix attempt. Follow-up DB evidence showed a late 2026-08-27 production batch at 12:27 KST: ingest run `0430b976-e4fe-483e-aa1a-fb50477f15da`, message run `147427ec-0716-45b5-a11c-24fa933f1f18`, and `publish_attempts.status=success`; the user received the deterministic fallback event-alert message for Hangang event `evntSn=441` and `evntSn=446`.
- Prevention: Treat GitHub native schedule as best-effort for time-sensitive alerts and keep an independently hosted backup trigger.
- Follow-up: Applying the Cloudflare Worker code and cron through the current `.env` `CLOUDFLARE_API_TOKEN` failed with `403 Authentication error`; use a Cloudflare credential with Worker script and Worker cron edit permission, then verify the live schedule includes `45 22 * * *`. Confirm the 12:27 KST GitHub Actions event type in the Actions UI; if it says `Scheduled`, reclassify this from dropped schedule to severely delayed schedule.

## 2026-08-04: Cloudflare scheduled dispatch threw before GitHub Actions

- Symptom: The expected daily Telegram message did not arrive from 2026-08-04 through 2026-08-23 while Cloudflare cron remained the production trigger.
- Impact: No GitHub Actions batch reached Supabase ingest and no Telegram publish attempt was recorded.
- Root cause: Unresolved. Cloudflare GraphQL confirms the Cron Trigger fired daily, but the Worker scheduled invocation ended with `status=scriptThrewException` before GitHub Actions and Supabase ingest. The likely failure point is still `triggerWorkflowDispatch`, especially the hidden Cloudflare-stored `GITHUB_TOKEN` value or GitHub API authorization.
- Evidence: Supabase had no `run_logs` or `publish_attempts` after the 2026-08-03 07:31 KST success. Worker public URL returned `200`. Cloudflare schedules API returned `30 22 * * *`. Cloudflare secrets list showed `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`. Cloudflare GraphQL showed every scheduled invocation from 2026-08-04 through 2026-08-11 ended with `status=scriptThrewException`; previous scheduled invocations from 2026-08-02 and 2026-08-03 were `success`. Live source smoke on 2026-08-11 found no source failures and 2 publish candidates.
- Fix: Production scheduling was moved back to GitHub Actions native `schedule` and the Cloudflare cron trigger was disabled to avoid duplicate sends. Cloudflare Worker diagnostics remain available, but the Worker `GITHUB_TOKEN` dispatch path is no longer the production trigger until its token/API issue is proven fixed.
- Verification: The restored GitHub Actions native schedule created Supabase ingest run `a395699f-30a8-4dee-8862-a79cc47cbe02` at 2026-08-24 07:48 KST and message run `6662d4dd-47b9-439a-b114-68ca8201e621` at 2026-08-24 07:50 KST. `publish_attempts.status=success` was recorded, confirming the DB-backed Telegram publish path ran again. Remaining risk: that run had `message_context=partial_source_unavailable` from GitHub-runner Hangang source timeouts, while a local live-source check after the run found all sources available and 2 publish candidates.
- Prevention: Keep Workers Logs enabled for scheduler Workers. On missing Telegram messages, check Supabase rows first, then Cloudflare scheduled invocation status, then GitHub workflow dispatch evidence before changing parser or Telegram code.
- Follow-up: Track the residual GitHub-runner source timeout and Cloudflare dispatch remediation in `OPEN_ISSUES.md`.

## 2026-08-24: No-event Telegram message under partial source outage

- Symptom: The user received `2026-08-24 07:50 기준 오늘 자전거 주의 이벤트가 없습니다.`
- Impact: The channel received a no-event confirmation even though full live-source crawling for the same KST 기준 found 2 publish candidates from Hangang events.
- Root cause: The production GitHub runner timed out fetching Hangang event and notice sources during ingest, so message generation used only Ara Waterway candidates. Ara Waterway had no publishable rows, and current fallback policy renders `partial_source_unavailable` with no events as a plain no-event message.
- Evidence: Supabase recorded ingest run `a395699f-30a8-4dee-8862-a79cc47cbe02` with `partial_source_unavailable` for Hangang sources, message run `6662d4dd-47b9-439a-b114-68ca8201e621` with `published_message_count=1`, and `publish_attempts.status=success`. DB rows for that ingest contained 13 Ara Waterway candidates and 0 publish candidates. A local live-source check found 20 candidates, no source failures, and 2 Hangang publish candidates: `evntSn=446` and `evntSn=441`.
- Fix: Local fallback behavior now renders empty `partial_source_unavailable` as a degraded-source warning instead of a plain no-event confirmation.
- Verification: Targeted fallback and generate-messages CLI tests pass locally. Production verification is pending until the next natural scheduled run.
- Prevention: Do not let degraded-source empty results appear identical to true no-event confirmations. Prefer a visible partial-source warning or failed message step for `partial_source_unavailable` with zero events.
- Follow-up: Track active remediation in `OPEN_ISSUES.md`.

## 2026-07-21: Duplicate Ara Waterway source in one Telegram message

- Symptom: One Telegram message contained two entries for Ara Waterway notice `1217` with the same source URL: one detailed-location entry and one stale `구간 확인 필요` entry.
- Impact: The alert over-reported one source event as two events, reducing message trust.
- Root cause: `raw_events` correctly refreshes duplicate source observations by content hash, but `normalized_events` dedupe used `deterministic_duplicate_key`, which includes `location_name` and `region`. After Ara Waterway location precision improved, the same `raw_event_id` could have both the old `구간 확인 필요|unknown` normalized row and the new detailed-location `경기` row. Message selection joins normalized rows to the refreshed raw row, so both remained eligible in the current run.
- Fix: Local `save_normalized_events` now looks for existing rows by `raw_event_id` first, updates the preferred same-raw row, deletes stale same-raw normalized duplicates, and updates the deterministic duplicate key during refresh.
- Verification: Added a regression test for same-raw normalized stale-row cleanup. `python -m pytest -q` reported `99 passed`; `python -m ruff check .` and `python -m black --check .` passed.
- Prevention: Do not rely only on location-bearing deterministic keys when refreshing normalized data from a stable raw source. Keep one normalized row per raw source observation unless the data model explicitly supports one-to-many normalization.
- Production verification: The 2026-07-22 user-received Telegram message contained one Ara Waterway notice `1217` entry rather than the previous detailed-location plus stale `구간 확인 필요` duplicate pair. Live source cross-check found no source failures, 18 candidates, exactly one publish candidate, and the candidate matched notice `1217` with detailed blocked sections, `region=경기`, `validation_status=valid`, `event_type=road_closure`, and `cyclist_impact_level=high`. Supabase verification found ingest run `3e51c8b8-ad0b-4682-86cf-c7780262c367`, message run `a947db97-20bf-40a2-ab66-74760c8fe2ed`, `published_message_count=1`, latest `publish_attempts.status=success`, `ARA_1217_NORMALIZED_ROW_COUNT=1`, and `NORMALIZED_DUPLICATE_RAW_EVENT_GROUPS=0`.
- Follow-up: Resolved on 2026-07-22. GitHub Actions log verification still requires authenticated local GitHub access, but user-facing Telegram, live source, and Supabase runtime records all match.

## 2026-07-19: Active Ara Waterway closure omitted from Telegram message

- Symptom: The user received a no-event Telegram message even though live source checks showed active Ara Waterway notice `1217` for a bicycle-road/weather closure.
- Impact: The daily alert could miss an active high-impact cycling-road closure and tell users there were no caution events.
- Root cause: Two filters conflicted with the intended runtime contract. First, duplicate raw source observations were tied to prior runs, while normalization/message generation were scoped to the current ingest run. Second, message selection re-filtered candidates with `validation_status == "valid"`, excluding high-impact `needs_review` rows even after normalization had marked them `publish_candidate=True`.
- Fix: Commit `461154a` refreshes duplicate raw observations into the current run and updates duplicate normalized rows. Commit `a3685b3` removes the stale message-query `validation_status == "valid"` filter so `publish_candidate=True` is the final alert eligibility contract.
- Verification: Local checks after `a3685b3` passed: `python -m pytest -q` reported `96 passed`; targeted messaging repository tests passed; live-source dry-run smoke returned 17 candidates, no source failures, `MESSAGE_EVENT_COUNT=1`, and included Ara Waterway notice `1217`; Telegram publisher smoke reached `dry_run`.
- Production verification: The 2026-07-20 07:30 KST natural run `29706279968` on commit `75f346e` completed successfully with `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, `TELEGRAM_STATUS=success`, and `TELEGRAM_MESSAGE_ID=29`. The generated Telegram text matched Ara Waterway notice `1217`, and a live source cross-check found exactly one publish candidate: notice `1217`.
- Prevention: For future false no-event reports, compare live source candidates, normalized `publish_candidate`, message query eligibility, and final `MESSAGE_EVENT_COUNT` before changing parser logic. Do not add a second eligibility filter after normalization unless it is explicitly part of the `publish_candidate` contract.
- Follow-up: Resolved on 2026-07-20. Separate precision follow-up was also resolved locally on 2026-07-20: Ara Waterway bridge/section names extracted into `raw_location_text` now normalize to message-ready locations with `region=경기`.

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
