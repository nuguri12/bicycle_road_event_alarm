# State

Last updated: 2026-07-20

## Current Objective

Operate and verify the Daily Cycling Event Alert Service as a Cloudflare-triggered GitHub Actions batch that collects bicycle-impacting public events, normalizes same-day active events, generates a Korean Telegram message, and publishes to a private Telegram channel.

## Active Task

MVP daily triggering remains stable, and the 2026-07-20 natural production run confirmed the 2026-07-19 active Ara Waterway closure fix in production. Ara Waterway detail section locations now normalize to message-ready locations instead of `구간 확인 필요` when explicit bridge/section text is present. Continue light monitoring before expanding sources, adding Telegram subscription flows, or evaluating Hermes Agent message generation.

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
- Latest Cloudflare deployment version: `33484d82-8f35-4a48-b9aa-842bf7d67dc8`
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
- Partial source outage currently appears as `MESSAGE_CONTEXT=partial_source_unavailable`.
- No-event messages with send time can avoid duplicate hash collisions, but daily scheduling increases the chance of repeated no-event messages.

## Next Actions

1. Continue light monitoring of daily 07:30 KST production runs.
2. Stabilize parsing before adding product features:
   - Review Hangang notice detail coverage only if source coverage becomes the priority.
   - Keep live-source smoke checks lightweight.
3. Add only one new regional source after parser stability improves.
4. Add Telegram personal chat delivery before web or SNS:
   - Start with `/start`, `/stop`, stored `chat_id`, and `enabled` status.
   - Defer complex preferences; first personalization should be a simple region choice.
5. Build a minimal web/admin surface only after Telegram personal delivery works.
6. Defer SNS publishing, Hermes Agent evaluation, VPS scheduler changes, and richer preference controls until real usage proves the need.
7. Review whether message-stage run summaries are sufficient for operations correlation before adding a dedicated batch id.
8. Revisit no-event message dedupe only if daily no-event confirmations become noisy.
