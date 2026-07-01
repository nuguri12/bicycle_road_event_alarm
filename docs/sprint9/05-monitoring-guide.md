# Monitoring Guide

## Latest Monitoring Checklist: Schedule Smoke Test

During the temporary `*/5 * * * *` schedule verification window, monitor these signals:

- GitHub Actions has at least one `Manual Batch` run with `event=schedule`.
- The run reaches `Generate and publish message`.
- The logs include:
  - `RUN_ID=<uuid>` from ingestion
  - `MESSAGE_STATUS=generated`
  - `TELEGRAM_STATUS=success`, `failed`, or `skipped`
- Supabase `publish_attempts` has a recent row for the same verification window.
- If `TELEGRAM_STATUS=skipped`, verify `failure_reason` in DB:
  - `duplicate_successful_publish` means the scheduler reached publish logic and duplicate protection worked.
  - `dry_run` or `telegram_publish_disabled` should not happen for `schedule` events unless workflow env mapping changed.

If no `schedule` run appears after 15-30 minutes:

1. Confirm workflow state is active.
2. Confirm `.github/workflows/manual-batch.yml` exists on default branch `main`.
3. Confirm the cron is present on remote `main`.
4. Re-push a commit that changes the cron line, then observe the next 5-minute window.
5. If it still does not run, treat this as GitHub schedule unreliability and use manual dispatch while investigating.

## 1. 모니터링 목표

모니터링은 정기 실행 성공 여부, 이벤트 처리량, Telegram 발행 결과, 외부 API 실패를 빠르게 확인하기 위한 것입니다.

## 2. 확인 지표

필수 지표:

- workflow 실행 성공 여부
- run_logs status
- raw_event_count
- normalized_event_count
- published_message_count
- failed publish_attempt count
- crawler source failure count
- OpenAI fallback count
- Telegram failure count

## 3. 확인 위치

기본 확인 위치:

- GitHub Actions logs
- Supabase run_logs
- Supabase publish_attempts
- Telegram Channel

MVP에서는 별도 모니터링 SaaS를 도입하지 않습니다.

## 4. 경고 기준

운영자가 확인해야 하는 상황:

- 정기 실행 실패
- 2회 연속 raw_event_count 0
- Telegram 발행 실패
- OpenAI fallback 급증
- 같은 message_hash 중복 발행 시도

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 운영자가 확인할 기본 모니터링 위치
- `[사용자 입력 필요]` 실패 알림을 받을 방식
- `[사용자 입력 필요]` 2회 연속 이벤트 0건을 문제로 볼지 여부
