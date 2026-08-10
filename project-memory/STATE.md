# State

Last updated: 2026-08-11

## Current Objective

Operate and verify the Daily Cycling Event Alert Service as a Cloudflare-triggered GitHub Actions batch that collects bicycle-impacting public events, normalizes same-day active events, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

MVP daily triggering remains stable. The 2026-07-28 user-received Telegram no-event message was cross-checked against live source crawling and Supabase records, and matched `PUBLISH_COUNT=0` with the latest Ara Waterway notice `1217` row marked `[개방완료]` and `publish_candidate=False`. Continue light monitoring before expanding sources, adding Telegram subscription flows, or evaluating Hermes Agent message generation.

Current investigation: Daily Telegram messages have been missing from 2026-08-04 through 2026-08-11. Live source smoke on 2026-08-11 found no source failures and 2 publish candidates from Hangang events. Supabase has no `run_logs` or `publish_attempts` after the 2026-08-03 07:31 KST success. Cloudflare GraphQL scheduled invocations show the 2026-08-04 through 2026-08-11 07:30 KST crons fired but ended with `status=scriptThrewException`, so the failure is inside the Worker scheduled dispatch path before the app batch reached Supabase ingest.

## Current Runtime State

- Repository: `nuguri12/bicycle_road_event_alarm`
- Branch strategy: direct development on `main`
- Latest verified Cloudflare Worker smoke run: GitHub Actions run `28689723865` on commit `6b519ba`
- Latest locally fixed false no-event issue: Ara Waterway notice `1217` was active and publishable, but the user-facing message could still say no-event. Fix commits: `461154a` (`fix: refresh duplicate active source observations`) and `a3685b3` (`fix: include publish candidates in messages`).
- Latest resolved production incident: 2026-07-10 07:30 KST run failed at the GitHub Actions `Check formatting` step before ingestion; Black formatting was applied and manual recovery run `29057983250` completed with `TELEGRAM_STATUS=success`.
- Workflow: `.github/workflows/manual-batch.yml`
- External scheduler: `cloudflare/scheduler`
- Cloudflare Worker: `bicycle-road-event-alarm-scheduler`
- Cloudflare Worker URL: `https://bicycle-road-event-alarm-scheduler.matthew-dev.workers.dev`
- Latest Cloudflare deployment version: `6b69f230-842b-4fa7-80cc-ca3c6119f158`
- Production schedule: Cloudflare Cron `30 22 * * *`
- Meaning: every day 07:30 KST
- Cloudflare cron trigger deployment is confirmed by Wrangler.
- Cloudflare Worker secret `GITHUB_TOKEN` is set as of 2026-07-04 09:20 KST (`npx wrangler secret list` returned `GITHUB_TOKEN`).
- Cloudflare Worker secret `SMOKE_TRIGGER_TOKEN` is set for authenticated manual production smoke runs.
- GitHub Actions native `schedule` is removed to avoid duplicate sends.
- Temporary push smoke trigger has been removed after successful verification.
- Authenticated Worker smoke endpoint `POST /__internal/run-scheduled` dispatches the same GitHub workflow payload for immediate validation.
- Cloudflare dispatches `workflow_dispatch` with real publish inputs:
  - `ENABLE_TELEGRAM_PUBLISH=true`
  - `DRY_RUN=false`
- Natural Cloudflare-triggered Telegram no-event message was received at 2026-07-05 07:31 KST.
- Natural Cloudflare-triggered Telegram no-event message was received at 2026-07-07 07:31 KST after the Supabase pooler prepared-statement fix.
- Natural Cloudflare-triggered runs on 2026-07-07 through 2026-07-09 completed and published successfully, so the MVP production path was considered stable as of 2026-07-09.
- Natural Cloudflare-triggered runs on 2026-07-11, 2026-07-12, and 2026-07-13 all completed and published no-event Telegram messages successfully on commit `ec71518`.
- Natural Cloudflare-triggered run on 2026-07-14 completed and published a no-event Telegram message successfully on commit `ec71518`.
- Natural Cloudflare-triggered run on 2026-07-15 completed and published a no-event Telegram message successfully on commit `cecc804`.
- Natural Cloudflare-triggered run on 2026-07-16 completed and published a no-event Telegram message successfully on commit `e943e3e`.
- Natural Cloudflare-triggered run on 2026-07-20 completed and published an Ara Waterway event alert successfully on commit `75f346e`.
- User-received Telegram message on 2026-07-22 contained one Ara Waterway notice `1217` alert after commit `0d6f1fc`.
- User-received Telegram message on 2026-07-23 contained one Ara Waterway notice `1217` alert after commit `5c0abff`.
- User-received Telegram message on 2026-07-24 contained one Ara Waterway notice `1217` alert after commit `fc31ed2`.
- User-received Telegram message on 2026-07-26 said there were no cycling caution events; live source crawling at 07:32 KST found no publishable candidates.
- User-received Telegram message on 2026-07-28 said there were no cycling caution events; live source crawling found no publishable candidates.
- User-received Telegram no-event messages on 2026-07-27 through 2026-07-31 are backed by Supabase `publish_attempts.status=success`.
- The 2026-08-01 07:30 KST Telegram message was missing. Supabase has no runtime rows after the 2026-07-31 07:32 KST publish. Live source smoke for 2026-08-01 07:32 KST found 23 source candidates, no source failures, and 5 publish candidates, all from Hangang events.
- 2026-08-01 mitigation: Cloudflare Worker was re-deployed with scheduled-dispatch logs and Wrangler re-applied `schedule: 30 22 * * *`; active version is `6b69f230-842b-4fa7-80cc-ca3c6119f158`.
- The 2026-08-02 07:30 KST natural run succeeded and published an event alert. Supabase recorded ingest run `320899c5-b7dd-47ee-9194-c9a1171b0612`, message run `73d53a1f-1e5c-4ae2-84e1-bdb53989465b`, `message_context=event_alert`, and `publish_attempts.status=success`. Live source smoke found 22 candidates, no source failures, and 4 publish candidates matching the Telegram message URLs.
- The 2026-08-03 07:31 KST natural run succeeded. Latest Supabase rows before the 2026-08-04 incident are ingest run `67327e8f-86ff-43fb-8dbe-906a505db186` and message run `c2d360b5-9a6c-4822-9ec2-c359f7cc3aeb` with `message_context=event_alert`.
- The 2026-08-04 07:30 KST Telegram message was missing:
  - Live source smoke found 20 source candidates, no source failures, and 2 publish candidates: Hangang event `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Supabase had no `run_logs` or `publish_attempts` after 2026-08-03 07:31 KST.
  - Worker public URL returned `200`, so the deployment was reachable.
  - Cloudflare API token was verified successfully.
  - Cloudflare secrets `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN` exist.
  - Cloudflare schedules API returned `30 22 * * *`.
  - Cloudflare GraphQL `workersInvocationsScheduled` showed one 2026-08-04 invocation: `status=scriptThrewException`, `cron=30 22 * * *`, `datetime=2026-08-03T22:30:33Z`.
  - Worker script settings returned `observability=null`, so past console error details were not available through Workers Logs.
- The 2026-08-05 07:30 KST Telegram message was also missing:
  - Live source smoke found 20 source candidates, no source failures, and 2 publish candidates: Hangang event `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Supabase had no `run_logs` or `publish_attempts` after 2026-08-03 07:31 KST.
  - Cloudflare API token verified successfully, Worker public URL returned `200`, schedules API returned `30 22 * * *`, and secrets list still showed `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`.
  - Cloudflare GraphQL `workersInvocationsScheduled` showed one 2026-08-05 invocation: `status=scriptThrewException`, `cron=30 22 * * *`, `datetime=2026-08-04T22:30:31Z`.
  - Worker script settings still returned `observability=None` and `logpush=False`, so the exact exception body is not available from persisted logs.
- The 2026-08-06 through 2026-08-11 07:30 KST Telegram messages were also missing:
  - Cloudflare GraphQL `workersInvocationsScheduled` returned `status=scriptThrewException` for every daily cron from `2026-08-05T22:30:30Z` through `2026-08-10T22:30:18Z`.
  - Supabase had no `run_logs` or `publish_attempts` after the 2026-08-03 07:31 KST success.
  - Live source smoke for `CHECK_KST=2026-08-11 07:32` found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=18`, and `PUBLISH_COUNT=2`, again Hangang event `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Cloudflare settings still show cron `30 22 * * *`, secrets `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`, `observability.enabled=False`, and `logpush=False`.
- Local remediation started on 2026-08-05:
  - Added `[observability] enabled = true` and `head_sampling_rate = 1` to `cloudflare/scheduler/wrangler.toml`.
  - Added a regression test requiring the Cloudflare scheduler config to persist Worker logs.
  - Cloudflare API read checks succeeded, but direct settings update via `PATCH /workers/scripts/bicycle-road-event-alarm-scheduler/settings` returned `403 Authentication error`, so the current `CLOUDFLARE_API_TOKEN` cannot modify Worker settings.
- Manual workflow runs default to safe dry-run mode:
  - `dry_run=true`
  - `enable_telegram_publish=false`
  - `force_fallback=false`
  - `apply_migrations=false`

## Implemented Runtime Behavior

- Runtime sources are Hangang events, Hangang notices via Seoulboard JSON API, and Ara Waterway notices via the official K-water 경인아라뱃길 notice URL.
- SPATIC code remains for regression/reference but is not called by runtime ingestion.
- Ingest emits `RUN_ID=<uuid>`.
- Normalize and message generation are scoped to that run id.
- Publish candidates are limited to events active on the KST date when they were fetched.
- Source outage and true no-event are separated in CLI/DB message context.
- Partial source outage is recorded in DB and CLI, but user-facing no-event text stays quiet.
- Empty fallback messages include KST send date and time.
- Telegram publish attempts are recorded for success, failed, and non-empty skipped outcomes.
- Production-mode Telegram publish failures return a non-zero CLI exit code so GitHub Actions fails visibly.
- Duplicate successful publish prevention is active.
- Message-stage run summaries now include the ingest run id when message generation is scoped with `--run-id`, which makes ingest/message/publish correlation easier during operations review.
- Duplicate raw source observations refresh the existing `raw_events` row to the current ingest `run_id`, latest raw fields, and latest `fetched_at`.
- Duplicate normalized events update the existing `normalized_events` row with the latest normalized fields.
- Normalized saves now prefer updating the existing row for the same `raw_event_id` and remove stale same-raw normalized duplicates before falling back to deterministic duplicate key matching.
- Message candidate selection treats `publish_candidate=True` as the final alert eligibility contract; high-impact `needs_review` candidates are no longer discarded by a stale `validation_status == "valid"` message query filter.
- Ara Waterway bridge/section names extracted into `raw_location_text` are preserved as normalized locations with `region=경기`, even when they do not contain the generic 서울/경기 keyword list.

## Known Current Observations

- The 2026-07-03 19:00 KST one-off schedule did not create a GitHub Actions run.
- The 2026-07-03 21:20 KST one-off schedule did not create a GitHub Actions run.
- The push-based production smoke succeeded at 2026-07-03 21:31 KST with `TELEGRAM_STATUS=success` and `TELEGRAM_MESSAGE_ID=11`.
- The Cloudflare Worker authenticated smoke endpoint returned `202 scheduled dispatch accepted` at 2026-07-04 09:46 KST and created GitHub Actions run `28689723865`.
- Run `28689723865` completed successfully at 2026-07-04 09:47 KST.
- The 2026-07-05 07:31 KST natural Cloudflare-triggered Telegram message was received and said there were no today cycling caution events.
- The 2026-07-06 07:30 KST Cloudflare-triggered run did execute, saved 16 raw events, then failed before Telegram in `normalize_events`.
- Root cause: Supabase transaction pooler reused a server connection where psycopg prepared statement `_pg3_0` already existed.
- Local verification against failed run `7b01d78c-3816-472b-856b-4eafcbe28ab1` succeeded after disabling psycopg prepared statements:
  - `NORMALIZED_EVENTS_SAVED=16`
  - dry-run message generation produced `MESSAGE_CONTEXT=no_event`
- The 2026-07-07 07:31 KST daily run succeeded:
  - Ingest run `fc1f62f4-16b4-4cd2-a9bc-cc3b7bedf4ef` saved 4 raw Ara Waterway notice rows.
  - Message run `df074c65-fe5b-4228-9367-3816b561321a` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - No `DuplicatePreparedStatement` recurrence was observed.
  - The 4 raw rows matched existing non-publishable normalized notices and produced a no-event Telegram message.
- The 2026-07-08 07:31 KST daily run succeeded:
  - Ingest run `ceabbd6e-eb4b-4bf8-9902-cd491becf8e2` completed with no newly saved raw events.
  - Message run `1767d14b-b05e-4311-adc4-d98bae795cec` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - Live source cross-check found 17 candidates across Hangang events, Hangang notices, and Ara Waterway notices, with 0 publish candidates and no source failures.
- The 2026-07-09 07:31 KST daily run succeeded:
  - Ingest run `81a17fa6-7022-41c3-b5fc-d5419b578c45` completed with no newly saved raw events and `error_summary=None`.
  - Message run `e2811ac4-1f8c-4834-9a50-586dbafbbcf7` recorded `published_message_count=1`.
  - `publish_attempts.status=success`, `failure_reason=None`.
  - This is the third consecutive successful natural daily run after the 2026-07-06 prepared-statement incident.
- The 2026-07-10 07:30 KST daily run was dispatched by Cloudflare but failed before ingestion at GitHub Actions `Check formatting`:
  - Failed run: `29054715710`
  - Commit: `a8b3a33`
  - Root cause: `python -m black --check .` would reformat `src/bicycle_road_event_alarm/cli/generate_messages.py` and `src/bicycle_road_event_alarm/normalization/normalizer.py`.
  - Fix commit: `361b2ca` (`style: apply black formatting`)
  - Recovery run: `29057983250`
  - Recovery result: `RAW_EVENTS_SAVED=1`, `NORMALIZED_EVENTS_SAVED=1`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=19`.
- Post-recovery source comparison found the no-event message was a false negative:
  - Ara Waterway notice `1224` says bicycle-road, Aramaru observatory, and Ara waterfall access is closed from 2026-07-09 13:00 until weather conditions improve.
  - Root cause: Ara detail body `<차단구간>`/`<차단기간>` was not preserved, and open-ended weather closures were treated as same-day only.
  - At the time of the fix, local live-source normalization produced `PUBLISH_COUNT=1` for notice `1224`.
- Current live-source/local normalization check found 16 raw candidates, no source failures, and 0 KST same-day publish candidates. This is expected because Ara Waterway notice `1224` is now marked `[개방완료]` at the source.
- The 2026-07-11 through 2026-07-13 07:30 KST daily runs were verified from GitHub Actions logs:
  - 2026-07-11 run `29127918535`: `RUN_ID=156d80d8-d81a-4ade-90e3-85558bb19808`, `RAW_EVENTS_SAVED=12`, `NORMALIZED_EVENTS_SAVED=11`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=20`.
  - 2026-07-12 run `29170623309`: `RUN_ID=e4c824ad-0322-4ac8-b791-88bee652e360`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=21`.
  - 2026-07-13 run `29211677015`: `RUN_ID=59d9f6aa-e203-4520-b05b-50cc8faf2f1f`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=22`.
- The 2026-07-14 07:30 KST daily run `29290118663` was verified from GitHub Actions logs:
  - `RUN_ID=7d90531b-b148-43fe-b8af-22dde039f769`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=23`.
  - Live source cross-check found 16 candidates, no source failures, and 0 KST same-day publish candidates. Ara Waterway notice `1224` remains `[개방완료]`.
- The 2026-07-15 07:30 KST daily run `29373204016` was verified from GitHub Actions logs:
  - `RUN_ID=7003c5c0-ac79-4166-8871-ccdb27261e7b`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=24`.
  - Live source cross-check found 16 candidates, no source failures, and 0 KST same-day publish candidates. Ara Waterway notice `1224` remains `[개방완료]`.
- The 2026-07-16 07:30 KST daily run `29455620182` was verified from GitHub Actions logs:
  - `RUN_ID=d847c9ea-4c5e-4a93-a40f-cfd189d8d55b`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_CONTEXT=no_event`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=25`.
  - Live source cross-check found 16 candidates, no source failures, and 0 KST same-day publish candidates. Ara Waterway notice `1224` remains `[개방완료]`.
- Ara Waterway now uses an official K-water notice URL. Parser precision has been improved for title links without nested `strong` tags and detail pages that put `통제 구간` on a label line followed by the section text; live-source precision should still be monitored.
- 2026-07-18/2026-07-19 manual and live-source checks found a false no-event path for Ara Waterway notice `1217`:
  - Live source returned 17 candidates, no source failures, and Ara Waterway notice `1217` normalized to `publish_candidate=True`.
  - Manual workflow run on commit `461154a` emitted `RUN_ID=770e519e-95b4-4df2-b67f-3bdd3aac99da`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_EVENT_COUNT=0`, and `MESSAGE_CONTEXT=no_event`.
  - Root causes were fixed in commits `461154a` and `a3685b3`.
  - Local verification after `a3685b3` passed with `96 passed`, and live-source dry-run smoke produced `MESSAGE_EVENT_COUNT=1` with Ara Waterway notice `1217` in the generated message.
- The 2026-07-20 07:30 KST daily run `29706279968` verified the Ara Waterway notice `1217` fix in production:
  - Commit: `75f346e`
  - `RUN_ID=2f43dc66-a93b-485a-bf2b-a327dc3b878e`, `RAW_EVENTS_SAVED=0`, `NORMALIZED_EVENTS_SAVED=0`, `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, `MESSAGE_SOURCE=openai`, `TELEGRAM_STATUS=success`, `TELEGRAM_MESSAGE_ID=29`.
  - Telegram text matched the publishable source item for notice `1217`: active 2026-07-17 Ara Waterway bicycle-road, Aramaru observatory, and Ara waterfall closure until weather conditions improve.
  - Live source cross-check found 18 candidates, no source failures, and exactly 1 publish candidate: Ara Waterway notice `1217`.
- Ara Waterway notice `1217` location precision follow-up was fixed locally on 2026-07-20:
  - `raw_location_text` sections such as `시천교~계양대교 남, 북측 자전거도로; 굴포천 연결수로 좌안(서측) 자전거도로; 아라마루 전망대 및 아라폭포` now normalize as `location_name` with `region=경기` and `validation_status=valid`.
  - Live-source smoke after the fix found 18 candidates, no source failures, exactly 1 publish candidate, and preserved the detailed Ara blocked sections as `location_name`.
- The 2026-07-21 user-reported Telegram message contained duplicate Ara Waterway notice `1217` entries with the same URL but different locations (`경기(...)` and `구간 확인 필요`):
  - Root cause: `normalized_events` dedupe used a key containing location/region, so the old `구간 확인 필요` row and the new detailed-location row could coexist for the same refreshed `raw_event_id`.
  - Local fix: `save_normalized_events` now updates same-raw normalized rows first, deletes stale same-raw duplicates, and updates the deterministic duplicate key during refresh.
  - Verification: `python -m pytest -q` reported `99 passed`; `python -m ruff check .` and `python -m black --check .` passed.
- The 2026-07-22 user-received Telegram message verified the same-raw normalized dedupe fix at the user-facing level:
  - Message contained one Ara Waterway notice `1217` entry, not the previous detailed-location plus stale `구간 확인 필요` duplicate pair.
  - Live source cross-check found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=18`, and `PUBLISH_COUNT=1`.
  - The single publish candidate was notice `1217` with `raw_location_text=시천교~계양대교 남, 북측 자전거도로; 굴포천 연결수로 좌안(서측) 자전거도로; 아라마루 전망대 및 아라폭포`, `region=경기`, `validation_status=valid`, `event_type=road_closure`, and `cyclist_impact_level=high`.
  - Supabase verification found ingest run `3e51c8b8-ad0b-4682-86cf-c7780262c367`, message run `a947db97-20bf-40a2-ab66-74760c8fe2ed`, `published_message_count=1`, and latest `publish_attempts.status=success`.
  - DB rows for source URL `1217` now show `ARA_1217_NORMALIZED_ROW_COUNT=1`, one raw id, one publishable normalized row, and `NORMALIZED_DUPLICATE_RAW_EVENT_GROUPS=0`.
  - GitHub CLI and public GitHub API could not verify private Actions logs without authentication, but Supabase runtime records verify the production batch outcome.
- The 2026-07-23 user-received Telegram message again matched live source and DB state:
  - User message: `[통행차단/영향 큼] 2026-07-17 경기, 시천교~계양대교 남·북측 자전거도로/굴포천 연결수로 좌안(서측)/아라마루 전망대·아라폭포`, reason `교통통제(기상 여건 완화 시까지)`, source URL `1217`.
  - Live source cross-check found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=18`, and `PUBLISH_COUNT=1`.
  - The single publish candidate was notice `1217` with the same date, detailed blocked sections, `region=경기`, `validation_status=valid`, `event_type=road_closure`, and `cyclist_impact_level=high`.
  - Supabase verification found ingest run `2d9d5c6c-8e27-43b1-96cb-e98c8a693813`, message run `877a97f4-462c-4d14-81e8-8118269908a8`, `published_message_count=1`, latest `publish_attempts.status=success`, `ARA_1217_NORMALIZED_ROW_COUNT=1`, and `NORMALIZED_DUPLICATE_RAW_EVENT_GROUPS=0`.
- The 2026-07-24 user-received Telegram message again matched live source and DB state:
  - User message: `[위험도 높음] 2026-07-17 | 경기 | 시천교~계양대교 남·북측 자전거도로, 굴포천 연결수로 좌안(서측), 아라마루 전망대·아라폭포 통행 차단(기상 여건 완화 시까지)`, reason `교통통제/통행 차단`, source URL `1217`.
  - Live source cross-check found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=19`, and `PUBLISH_COUNT=1`.
  - The single publish candidate was notice `1217` with the same date, detailed blocked sections, `region=경기`, `validation_status=valid`, `event_type=road_closure`, and `cyclist_impact_level=high`.
  - Supabase verification found ingest run `cf247199-7405-4338-858b-74dd7cfd0ab4`, message run `01b777e1-bcc5-439f-af38-6eb0a3fad14d`, `published_message_count=1`, latest `publish_attempts.status=success`, `ARA_1217_NORMALIZED_ROW_COUNT=1`, and `NORMALIZED_DUPLICATE_RAW_EVENT_GROUPS=0`.
- The 2026-07-26 user-received Telegram no-event message matched live source state:
  - Message text: `2026-07-26 07:32 기준 오늘 자전거 주의 이벤트가 없습니다.`
  - Live source cross-check for 2026-07-26 07:32 KST found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=18`, and `PUBLISH_COUNT=0`.
  - Source counts were Hangang events 2, Hangang notices 3, and Ara Waterway notices 13.
  - Ara Waterway notices `1217` and `1224` were both present but completed and normalized to `publish_candidate=False`, so excluding them from the Telegram message was correct.
- The 2026-07-28 user-received Telegram no-event message matched live source and DB state:
  - Message text: `2026-07-28 07:32 기준 오늘 자전거 주의 이벤트가 없습니다.`
  - Live source cross-check found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=20`, and `PUBLISH_COUNT=0`.
  - Ara Waterway notice `1217` was still present in the source, but the title included `[개방완료]`; it normalized to `publish_candidate=False`, so excluding it from the Telegram message was correct.
  - Supabase verification found ingest run `ac0d604e-8ce5-401f-aa9b-d1c80f563eb6`, message run `9c0966bf-5ed0-475d-bdc3-23ae7aa0dba7`, `message_context=no_event`, `published_message_count=1`, and latest `publish_attempts.status=success`.
  - DB rows for source URL `1217` show two historical normalized rows because the completed title changed the raw content hash; the latest `[개방완료]` row is linked to the current ingest run and has `publish_candidate=False`, while the older active row is not in the current run scope. `NORMALIZED_DUPLICATE_RAW_EVENT_GROUPS=0`.
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid duplicate hash collisions, but daily scheduling increases the chance of repeated no-event messages.

## Next Actions

1. Continue light monitoring of daily 07:30 KST production runs.
2. Resolve the 2026-08-04 Cloudflare Worker scheduled-dispatch failure before changing crawler/parser logic:
   - Enable Worker observability/log persistence.
   - Re-register Cloudflare Worker secret `GITHUB_TOKEN` with a valid GitHub PAT.
   - Run the authenticated smoke endpoint only with operator approval because it can publish a real Telegram alert.
   - Confirm GitHub `workflow_dispatch`, Supabase ingest, message generation, and Telegram publish all complete.
3. Stabilize parsing before adding product features:
   - Review Hangang notice detail coverage only if source coverage becomes the priority.
   - Keep live-source smoke checks lightweight.
   - Keep the current `requests` + BeautifulSoup crawler stack unless a source repeatedly breaks on static HTML parsing.
   - Revisit Scrapling as a source-level parser adapter only after a concrete parser fragility or anti-bot/dynamic-rendering problem is observed.
4. Add only one new regional source after parser stability improves.
5. Add Telegram personal chat delivery before web or SNS:
   - Start with `/start`, `/stop`, stored `chat_id`, and `enabled` status.
   - Defer complex preferences; first personalization should be a simple region choice.
6. Build a minimal web/admin surface only after Telegram personal delivery works.
7. Defer SNS publishing, Hermes Agent evaluation, VPS scheduler changes, and richer preference controls until real usage proves the need.
8. Review whether message-stage run summaries are sufficient for operations correlation before adding a dedicated batch id.
9. Revisit no-event message dedupe only if daily no-event confirmations become noisy.
