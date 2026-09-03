# Open Issues

Last updated: 2026-09-04

## Operational Risks

### 2026-09-02 through 2026-09-04 Telegram delivery gap

- Symptom: The user reported no Telegram messages after the delayed 2026-09-01 message.
- Verified evidence:
  - 2026-09-02 production batch reached Supabase at 09:25 KST and generated an `event_alert`, but `publish_attempts.status=skipped`, `failure_reason=duplicate_successful_publish`, `message_hash_prefix=d88a8df7a8b4`.
  - 2026-09-03 production batch reached Supabase at 09:31 KST and generated an `event_alert`, but `publish_attempts.status=skipped`, `failure_reason=duplicate_successful_publish`, `message_hash_prefix=d88a8df7a8b4`.
  - 2026-09-01 publish attempt succeeded with the same `message_hash_prefix=d88a8df7a8b4`, so 9/2 and 9/3 were suppressed by the historical duplicate guard.
  - As of 2026-09-04 08:16 KST, Supabase had no `run_logs` or `publish_attempts` rows for the 9/4 daily run.
  - Live-source replay for 2026-09-04 08:16 KST found no source failures, 22 source candidates, and 1 publish candidate: Hangang event `evntSn=446`, active through 2026-09-04.
  - Cloudflare Worker schedules API still returned `{"schedules": []}`, so the independent 07:45 KST backup trigger remains inactive.
  - Local `gh` remains unauthenticated, and the unauthenticated GitHub Actions API returned `404 Not Found`, so direct Actions run inspection is still blocked locally.
- Current assessment: 9/2 and 9/3 were not scheduler misses; they ran and were suppressed by the too-broad duplicate publish policy. 9/4 is currently a scheduler delay/missed-trigger symptom; if a delayed run appears later, it is expected to hit the same duplicate guard unless the daily duplicate policy is fixed first.
- Proposed fix:
  - Scope duplicate suppression to the same KST delivery date, or include the KST delivery date in the hash/dedupe key for scheduled daily messages.
  - Keep same-day duplicate prevention for overlapping GitHub primary and future Cloudflare backup runs.
  - Restore/apply the Cloudflare backup cron only after the dedupe policy is fixed, otherwise a backup trigger can still be suppressed by the same historical hash.

### 2026-09-01 daily Telegram message missing as of local check

- Symptom: The user reported no Telegram message was received for the 2026-09-01 morning run.
- Verified evidence:
  - Supabase has no `run_logs` rows and no `publish_attempts` rows since `2026-08-31 22:00:00+00` (2026-09-01 07:00 KST).
  - Latest Supabase rows remain the 2026-08-31 production batch at 09:46-09:47 KST, where publishing was skipped by `duplicate_successful_publish`.
  - Local `gh` is not authenticated, and the unauthenticated GitHub Actions API returned `404 Not Found`, so direct GitHub Actions run inspection is blocked from this environment.
  - Cloudflare Worker schedules API returned `{"schedules": []}`, confirming the backup cron is still not active in production.
- Current assessment: The application pipeline has not reached Supabase for the 2026-09-01 run. From local evidence this is a trigger/scheduler-layer issue or a delayed GitHub schedule, not a source crawling, normalization, or Telegram send failure.
- Follow-up evidence:
  - Supabase later recorded the 2026-09-01 production batch at 10:21-10:22 KST: ingest run `a0b8508a-e53d-43b9-9a15-8c4e8bc06e09`, message run `780222c0-3b6a-4293-80f6-22b5c38f925a`, and `publish_attempts.status=success`.
  - Live-source replay for 2026-09-01 found no source failures, 23 source candidates, and 1 publish candidate: Hangang event `evntSn=446` (`‘서울팅 2.0’ ｢설렘 in 서울, 한강버스편｣ 참가자 모집`) active from 2026-08-18 through 2026-09-04.
  - The user-received Telegram message matches the fallback output for that single publish candidate. Hangang event `evntSn=441` ended on 2026-08-31 and was correctly excluded on 2026-09-01.
- Remaining next check:
  - Confirm the GitHub Actions UI or authenticated GitHub API for a 2026-09-01 `Scheduled` run.
  - If the run header shows `Scheduled`, classify this as another delayed GitHub native schedule and prioritize the Cloudflare backup cron credential/config fix.

### 2026-08-30/2026-08-31 daily messages skipped by duplicate hash

- Symptom: The user reported the last Telegram message was received on 2026-08-29; no Telegram messages were received on 2026-08-30 or 2026-08-31.
- Verified evidence:
  - Supabase shows both 2026-08-30 and 2026-08-31 production batches ran successfully through message generation.
  - 2026-08-30 publish attempt was recorded as `status=skipped`, `failure_reason=duplicate_successful_publish`, `message_hash_prefix=a49388142ae4`.
  - 2026-08-31 publish attempt was recorded as `status=skipped`, `failure_reason=duplicate_successful_publish`, `message_hash_prefix=a49388142ae4`.
  - 2026-08-29 publish attempt succeeded with the same `message_hash_prefix=a49388142ae4`.
  - Live-source replay for 2026-08-31 07:50 KST found 2 publish candidates matching the 2026-08-29 user-received message: Hangang event `evntSn=441` and `evntSn=446`.
- Current assessment: Source selection is consistent, and the application ran on 8/30 and 8/31. Messages did not arrive because `publish_message_once` suppresses any message body that has already succeeded historically, even when the KST delivery date is different. This duplicate guard is too broad for a daily alert product.
- Proposed fix:
  - Scope duplicate suppression to the same KST delivery date, or include the KST delivery date in the hash/dedupe key for scheduled daily messages.
  - Keep same-day duplicate prevention so GitHub primary plus Cloudflare backup cannot double-send on the same date.
  - Add regression coverage for same body sent on a new KST date and same body skipped on the same KST date.

### 2026-08-28 missing daily Telegram message as of 08:10 KST

- Symptom: The user reported no Telegram message had arrived by 2026-08-28 08:10 KST.
- Verified evidence:
  - Supabase had zero `run_logs` and zero `publish_attempts` since 2026-08-28 07:00 KST.
  - Latest Supabase rows are still the late 2026-08-27 12:27 KST production batch.
  - Cloudflare schedules API returned `[]`, so the planned 07:45 KST backup cron is not active in production.
  - Live source check for `CHECK_KST=2026-08-28 08:10` found no source failures, 21 source candidates, and 2 publish candidates: Hangang event `evntSn=446` and `evntSn=441`.
  - Unauthenticated GitHub API returned 404 for workflow runs, and local `gh` is not authenticated, so Actions event/log verification remains blocked from this local environment.
- Current assessment: The application pipeline has not run today. This is not a source, normalization, or Telegram send failure. The primary GitHub native `schedule` either has not created the run yet or is again severely delayed, and the Cloudflare backup did not fire because its production cron remains unapplied.
- Follow-up evidence:
  - Supabase later recorded the production batch at 15:14 KST: ingest run `7ccdda61-e24a-4567-ac93-1aee9572dd6d`, message run `665dba8b-4983-47d2-bd04-ad0d95582960`, and `publish_attempts.status=success`.
  - Once DB-visible app steps started, runtime was short: `15:14:07` through `15:14:39` KST.
  - Shared GitHub Actions job log starts at `2026-08-28T06:13:27Z` (15:13:27 KST), checked out commit `e1b9ded`, and ran with `ENABLE_TELEGRAM_PUBLISH=true`, `DRY_RUN=false`, and `FORCE_FALLBACK=true`.
  - The job log shows about 72 seconds from runner start to `TELEGRAM_STATUS=success`, including about 21 seconds for ingest, 7 seconds for normalization, and 5 seconds for message/publish.
  - Current assessment after late delivery: the delay happened before the application pipeline started, at the GitHub Actions schedule delivery/queueing layer. Cloudflare was not a factor because live schedules still returned `[]`.
- Remaining next check:
  - Confirm in the GitHub Actions UI whether a 2026-08-28 run appears later and whether its event is `Scheduled`.
  - The shared job log does not include `github.event_name`; confirm the run header in GitHub UI. If the UI shows a 07:30 scheduled event with a much later job start time, classify this as GitHub Actions queue delay. If it shows the run was created near 15:14, classify it as schedule event delivery delay.
  - Apply Cloudflare Worker code and cron config with a Worker-edit-capable Cloudflare credential, then verify schedules include `45 22 * * *`.
  - Consider replacing GitHub native schedule as primary if delayed schedules continue after the backup credential issue is resolved.

### 2026-08-27 missing daily Telegram message

- Symptom: The user reported no Telegram message arrived for the 2026-08-27 morning run.
- Verified evidence:
  - Supabase had no `run_logs` or `publish_attempts` after the 2026-08-26 07:56 KST successful message run.
  - User-provided GitHub Actions screenshot at 2026-08-27 11:26 KST showed no 2026-08-27 workflow run; latest scheduled run was `Manual Batch #84` on 2026-08-26 07:55 KST.
  - Live source check for `CHECK_KST=2026-08-27 07:50` found no source failures, 21 source candidates, and 2 publish candidates: Hangang event `evntSn=446` and `evntSn=441`.
  - Current local `main` and `origin/main` are both commit `20180e5`.
  - Local workflow-equivalent checks passed: `python -m pytest -q`, `python -m ruff check .`, `python -m black --check .`, `python -m mypy src tests`, `python -m compileall src`, and `python -m pytest tests/unit/test_github_actions_workflow.py -q`.
  - Local `gh` is not authenticated, and unauthenticated GitHub API returned 404 for Actions workflow runs, so GitHub Actions log inspection is blocked.
- Current assessment: This is not a source no-event and not a Telegram publish failure. The GitHub Actions native `schedule` did not create the 2026-08-27 run.
- Local remediation:
  - Treat GitHub native `schedule` as best-effort and add Cloudflare Worker cron as a backup at `45 22 * * *` (07:45 KST).
  - Force deterministic fallback message generation for GitHub scheduled runs and Cloudflare Worker dispatches to stabilize `message_hash` duplicate prevention if both triggers run.
  - Keep manual workflow dispatch defaults safe; manual real publish still requires explicit inputs.
- Deployment status:
  - Cloudflare schedules API read succeeded and showed no active cron triggers.
  - Worker script upload and schedule update with the current `.env` `CLOUDFLARE_API_TOKEN` both failed with Cloudflare API `403 Authentication error`.
  - The local repository change is ready, but the Cloudflare production backup trigger is not applied until a token/session with Worker script and Worker cron edit permission is used.
- Follow-up evidence:
  - After commit `b2d8a11` was pushed, Supabase recorded a late 2026-08-27 production batch at 12:27 KST: ingest run `0430b976-e4fe-483e-aa1a-fb50477f15da`, message run `147427ec-0716-45b5-a11c-24fa933f1f18`, and `publish_attempts.status=success`.
  - The user received the deterministic fallback event-alert message for Hangang event `evntSn=441` and `evntSn=446`.
  - No manual dispatch or smoke endpoint was intentionally triggered from this workspace. The workflow has no `push` trigger, and Cloudflare schedules still returned `[]`.
  - Current likely cause: GitHub Actions created a delayed native `schedule` run after the user screenshot, using the latest `main` workflow at execution time. Local `gh` is unauthenticated, so the Actions event type still needs confirmation from the GitHub UI or an authenticated API call.
- Remaining next check:
  - Apply Cloudflare Worker code and cron config with a Worker-edit-capable Cloudflare credential, then verify schedules include `45 22 * * *`.
  - Confirm the 12:27 KST GitHub Actions run event type in the Actions UI. If it says `Scheduled`, this incident should be reclassified from dropped schedule to severely delayed schedule.

### 2026-08-04 through 2026-08-11 missing daily Telegram messages

- Symptom: No daily Telegram message was received from 2026-08-04 through 2026-08-11.
- Verified evidence:
  - Supabase `run_logs` and `publish_attempts` have no rows after the 2026-08-03 07:31 KST successful publish.
  - Cloudflare schedules API still shows `30 22 * * *`.
  - Cloudflare Worker `secret list` still shows `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`.
  - Cloudflare GraphQL `workersInvocationsScheduled` shows the daily cron fired from 2026-08-04 through 2026-08-11 but ended with `status=scriptThrewException` each time.
  - Live source smoke for `CHECK_KST=2026-08-11 07:32` returned `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=18`, and `PUBLISH_COUNT=2`.
  - The 2 publish candidates are Hangang event items: `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Worker settings currently show `observability.enabled=False` and `logpush=False`, so persisted exception details remain unavailable.
- Current assessment: This is the same root-cause class as the 2026-08-04/2026-08-05 incidents. The scheduler fires, but the Worker scheduled dispatch throws before GitHub Actions and Supabase ingest. The likely failure point is still `triggerWorkflowDispatch`, especially the hidden Cloudflare-stored `GITHUB_TOKEN` value or GitHub API authorization.
- Proposed fix:
  - Done on 2026-08-22: deployed the local `wrangler.toml` observability change so Worker logs persist, and re-applied cron `30 22 * * *` to Worker version `ec6acfbe-217c-4767-91f8-9b2312cc4e86`.
  - Still required: re-register Cloudflare Worker `GITHUB_TOKEN` with a valid raw GitHub PAT string that can dispatch `manual-batch.yml` on `main`. After the 2026-08-22 re-registration attempt, the Worker reached GitHub but GitHub returned HTTP 400 even for workflow lookup.
  - Run the authenticated smoke endpoint only with operator approval because it can publish a real Telegram alert.
  - Confirm GitHub Actions run creation, Supabase `run_logs`, and Telegram publish attempt.
- 2026-08-22 code hardening:
  - Worker now trims env values, strips common `Bearer`/`token` prefixes and whitespace from `GITHUB_TOKEN`, and no longer sends an explicit `X-GitHub-Api-Version` header.
  - Added smoke-protected diagnostic endpoints for GitHub workflow lookup and safe dry-run dispatch.
  - A temporary smoke token was used for diagnostics and then rotated to a new random value.
- 2026-08-22 token recheck:
  - The user reported the newly created GitHub PAT still showed `Never used` in GitHub.
  - A fresh smoke-protected Worker workflow-status diagnostic call reached the Worker but returned GitHub HTTP 400.
  - Assessment: The GitHub PAT shown by the user has not been used by Cloudflare; the current Cloudflare `GITHUB_TOKEN` value is still not a valid raw PAT value for GitHub REST API requests.
  - After the user re-registered `GITHUB_TOKEN` again, the Worker secret-change version became `6dc39b02-8617-4c78-9c92-c33acc38b35e`; a fresh smoke-protected workflow-status diagnostic still returned GitHub HTTP 400. A follow-up smoke token rotation produced active Worker version `14ece178-19fd-447f-8a2b-4306ceb65d52`.
  - After another user re-entry of `GITHUB_TOKEN`, active Worker version became `933e413c-bdce-41ee-877a-e859752d3e35`, but workflow-status diagnostic still returned GitHub HTTP 400.
  - Worker code was further hardened to extract a `github_pat_...` or `gh*_...` token pattern from the secret value before building the Authorization header; after deploy and smoke-token rotation, active Worker version became `39abc495-e077-48f4-92ad-e8964251ae26`, but workflow-status diagnostic still returned GitHub HTTP 400.
  - After the user re-entered `GITHUB_TOKEN` again, a fresh smoke-protected workflow-status diagnostic still returned GitHub HTTP 400. The smoke token was rotated again, producing active Worker version `d71a14b0-748d-4bae-b55c-e131e1e92b97`.
  - Ponytail/minimal recovery assessment: stop adding Worker code until the PAT is proven. Validate the token locally against GitHub Actions workflow lookup; if fine-grained PAT permissions remain unclear, temporarily use a classic PAT with `repo` scope; only then re-register Cloudflare `GITHUB_TOKEN` and run the existing safe dry-run smoke endpoint. Treat GitHub native schedule restoration as the fallback only if Cloudflare token dispatch keeps failing with a known-good PAT.
  - 2026-08-23: The daily Telegram message was again missing. A fresh smoke-protected Worker diagnostic reached the Worker, but GitHub workflow lookup returned HTTP 400 and safe dry-run dispatch returned HTTP 500. The smoke token rotation produced active Worker version `8bc32b0d-6245-4f4d-b54a-a29e71b2606c`. Mitigation changed production scheduling back to GitHub Actions native `schedule` and disabled the Cloudflare cron trigger. Cloudflare cron-disable deploy succeeded as Worker version `9b671e08-dcce-4cdb-9d6e-ec0c29393f68`.
- 2026-08-24 recovery check:
  - GitHub Actions native `schedule` produced Supabase ingest run `a395699f-30a8-4dee-8862-a79cc47cbe02` at 2026-08-24 07:48 KST and message run `6662d4dd-47b9-439a-b114-68ca8201e621` at 2026-08-24 07:50 KST.
  - `publish_attempts.status=success` was recorded at 2026-08-24 07:50 KST, so the production publish path is partially recovered through GitHub native schedule.
  - The user received a no-event Telegram message: `2026-08-24 07:50 기준 오늘 자전거 주의 이벤트가 없습니다.`
  - The same run recorded `message_context=partial_source_unavailable` because Hangang events and Hangang notices timed out from the GitHub runner.
  - DB check: the ingest run refreshed 13 Ara Waterway raw rows; all 13 linked normalized rows had `publish_candidate=False`, so the no-event message matched the degraded production source subset.
  - Full live-source check: current crawling for `CHECK_KST=2026-08-24 07:50` found `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=20`, and `PUBLISH_COUNT=2`, both from Hangang events. At whole-source level, the no-event message was false.
  - Keep this issue open until the next natural GitHub scheduled run confirms both publish delivery and healthy source crawling.

### 2026-08-24 false no-event under partial source outage

- Symptom: Telegram delivered `2026-08-24 07:50 기준 오늘 자전거 주의 이벤트가 없습니다.`
- Verified evidence:
  - Supabase message run `6662d4dd-47b9-439a-b114-68ca8201e621` published successfully with `message_context=partial_source_unavailable`.
  - Ingest run `a395699f-30a8-4dee-8862-a79cc47cbe02` timed out on `hangang_events` and `hangang_notices`; only Ara Waterway candidates were available to the production message stage.
  - Ara Waterway had 13 normalized rows for the run and all had `publish_candidate=False`, mostly because current closure notices were already `[개방완료]`.
  - A full live-source check for the same KST 기준 found 20 candidates, no source failures, and 2 publish candidates from Hangang events: `evntSn=446` and `evntSn=441`.
- Current assessment: The message was internally consistent with the partial production run but inaccurate against the complete source set. The quiet no-event fallback for `partial_source_unavailable` is now an operational risk.
- Local fix:
  - Minimal policy change implemented: when `message_context=partial_source_unavailable` and `events=[]`, fallback now sends a degraded-source warning instead of a plain no-event message.
  - Regression coverage updated in `tests/unit/messaging/test_fallback_generator.py`.
- Remaining follow-up:
  - Investigate GitHub runner connectivity to Hangang sources only if the next natural scheduled run still records Hangang timeouts.

### 2026-08-25/2026-08-26 OpenAI message format variability

- Symptom: User-received Telegram messages for the same two Hangang event sources used different line formats and labels across days:
  - `[주의/혼잡] ... 한강 밤핑(행사)` / `[주의/혼잡] ... 서울팅 2.0 ...`
  - `[중] ... 한강 밤핑(Night+Camping) 행사/축제 영향 가능` / `[중] ... 서울팅 2.0 ...`
- Verified evidence:
  - Production DB rows for 2026-08-25 and 2026-08-26 recorded successful `event_alert` message runs and Telegram publish attempts.
  - 2026-08-26 normalized rows had exactly 2 publish candidates: Hangang event `evntSn=441` with date range `2026-08-01` through `2026-08-31`, and `evntSn=446` with date range `2026-08-18` through `2026-09-04`.
  - Live source replay for 2026-08-26 matched the same 2 candidates. Current live replay for 2026-08-25 also sees a newer same-day notice that was posted after the morning run, so it should not be used to contradict the 2026-08-25 morning message.
- Current assessment: Source and normalized event selection are consistent for the two user-provided messages. The issue is message presentation determinism: OpenAI output is accepted if it is non-empty, under 600 characters, and includes every source URL, so labels and phrasing can vary day to day.
- Proposed fix:
  - Minimal option: use deterministic fallback for event alerts until message format requirements are stable.
  - Alternative: tighten the OpenAI prompt and validator to require an exact label/date/location/reason template.
  - Do not change crawler or normalization rules for this symptom unless future source comparison shows the selected candidates are wrong.

### 2026-08-05 missing daily Telegram message

- Symptom: No Telegram message was received for the 2026-08-05 07:30 KST production run.
- Verified evidence:
  - Live source smoke for `CHECK_KST=2026-08-05 07:32` returned `SOURCE_FAILURES={}`, `SOURCE_CANDIDATE_COUNT=20`, and `PUBLISH_COUNT=2`.
  - The 2 publish candidates were Hangang event items: `evntSn=441` (`한강 밤핑`) and `evntSn=440` (`2026 한강페스티벌 여름 축제`).
  - Supabase `run_logs` and `publish_attempts` still have no rows after the 2026-08-03 07:31 KST successful publish.
  - Cloudflare API token verified successfully.
  - Worker public URL returned `200`.
  - Cloudflare Worker `secret list` shows `GITHUB_TOKEN` and `SMOKE_TRIGGER_TOKEN`.
  - Cloudflare schedules API shows `30 22 * * *`.
  - Cloudflare GraphQL `workersInvocationsScheduled` shows the 2026-08-05 07:30 KST cron fired with `status=scriptThrewException`.
  - Worker script settings still returned `observability=None` and `logpush=False`, so the exact historical exception body is not available through persisted Workers Logs.
- Current assessment: This is the same failure pattern as 2026-08-04. The scheduler fired, but the Worker scheduled dispatch threw before the application batch reached Supabase ingest. The likely failure point remains `triggerWorkflowDispatch`, especially the GitHub API call or the Cloudflare-stored `GITHUB_TOKEN`.
- Proposed fix: Enable Worker observability/log persistence, re-register Cloudflare Worker `GITHUB_TOKEN` with a valid GitHub PAT that can dispatch `manual-batch.yml` on `main`, then run the authenticated smoke endpoint only with operator approval because it can publish a real Telegram alert.
- Remediation status:
  - Local `cloudflare/scheduler/wrangler.toml` now includes `[observability] enabled = true` and `head_sampling_rate = 1`.
  - Added a regression test to keep Worker log persistence configured.
  - Direct Cloudflare settings update with the current `CLOUDFLARE_API_TOKEN` failed with `403 Authentication error`; a token with Worker edit permission or a local Wrangler deploy session is still required to apply the setting.

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
