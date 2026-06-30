# Telegram Integration Design

## 1. 연동 목표

Sprint 5에서 생성된 메시지를 지정된 Telegram Channel에 발행합니다.

목표:

- 단방향 공지 채널에 메시지를 발행합니다.
- 발행 성공과 실패를 추적합니다.
- 중복 발행을 방지합니다.
- Bot Token과 Channel ID를 안전하게 관리합니다.

## 2. 연동 범위

포함:

- Telegram Bot API `sendMessage` 사용
- Channel 대상 발행
- 발행 성공 여부 기록
- 제한된 재시도
- 실패 로그 기록

제외:

- 사용자별 DM
- 구독/구독 해지
- Bot 명령어 처리
- 관리자 대시보드
- Telegram webhook

## 3. 입력과 출력

입력:

- generated_message
- message_hash
- run_id
- normalized_event_ids
- telegram_channel_id

출력:

- publish status: `success`, `failed`, `skipped`
- attempted_at
- failure_reason
- telegram response metadata

## 4. 비밀값 관리

필수 비밀값:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

정책:

- 저장소에 커밋하지 않습니다.
- 문서에 실제 값을 적지 않습니다.
- GitHub Actions Secrets에 저장합니다.
- 로컬 실행 시 `.env`를 사용하되 `.env`는 git ignore 대상입니다.

## 5. 발행 전 검증

발행 전 확인:

- 메시지가 비어 있지 않습니다.
- 메시지가 Telegram 최대 길이를 넘지 않습니다.
- message_hash가 이미 성공 발행된 값이 아닙니다.
- channel_id가 설정되어 있습니다.
- bot_token이 설정되어 있습니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 실제 Telegram Channel ID 또는 채널 사용자명
- `[사용자 입력 필요]` Telegram Bot Token 발급 완료 여부
- `[사용자 입력 필요]` 로컬 `.env` 사용 여부
