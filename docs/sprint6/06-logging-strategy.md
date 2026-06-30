# Logging Strategy

## 1. 로깅 목표

Telegram 연동 로그는 메시지가 언제, 어디에, 어떤 결과로 발행되었는지 추적하기 위한 것입니다.

## 2. 구조화 로그 필드

공통 필드:

- run_id
- step
- message_hash
- telegram_channel_id_masked
- attempt_number
- status
- error_type
- http_status
- elapsed_ms

비밀값 금지:

- Bot Token 전체 값
- Channel ID 전체 값이 민감하다고 판단되는 경우
- Supabase 연결 문자열
- OpenAI API Key

## 3. publish_attempts 기록

발행 시도마다 다음 값을 저장합니다.

- run_id
- normalized_event_id
- telegram_channel_id
- message_hash
- status
- failure_reason
- attempted_at

빈 이벤트 목록으로 발행을 건너뛰는 경우:

- 기본 정책은 publish_attempts에 기록하지 않고 run_logs에 skipped reason을 기록합니다.
- 운영상 필요하면 publish_attempts에 `skipped`로 기록할 수 있습니다.

## 4. 마스킹 정책

로그에서 Channel ID를 표시해야 한다면 일부만 노출합니다.

예:

- `-1001234567890` -> `-100******7890`
- `@cycling_alert` -> `@cyc****lert`

## 5. 운영 확인 로그

발행 성공 시:

- status: success
- message_hash
- elapsed_ms
- Telegram message id가 제공되면 기록 후보로 둡니다.

발행 실패 시:

- status: failed
- failure_reason
- error_type
- http_status

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` telegram_channel_id를 DB에는 평문 저장하고 로그에는 마스킹하는 정책 승인 여부
- `[사용자 입력 필요]` Telegram message id 저장 필요 여부
- `[사용자 입력 필요]` 빈 이벤트 목록 skipped 기록 위치 승인 여부
