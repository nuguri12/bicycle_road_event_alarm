# Telegram Tests

## 1. Telegram 테스트 목표

Telegram 테스트는 실제 Channel 오염 없이 발행 요청, 재시도, 실패 처리를 검증합니다.

## 2. Mock 테스트 대상

- sendMessage 요청 payload
- Bot Token 누락 처리
- Channel ID 누락 처리
- HTTP 429 retry_after 처리
- HTTP 500 재시도 처리
- HTTP 400 재시도 없음
- message_hash 중복 발행 skip

## 3. 실제 발행 테스트

실제 Telegram 발행은 기본 CI에서 제외합니다.

권장 marker:

```text
pytest -m live_telegram
```

실행 조건:

- 테스트 Channel이 준비되어 있습니다.
- Bot이 테스트 Channel 관리자입니다.
- 운영 Channel Secret을 사용하지 않습니다.

## 4. 성공 기준

- 테스트 Channel에만 메시지를 보냅니다.
- 운영 Channel ID가 설정된 경우 live test를 중단합니다.
- 발행 성공 응답을 publish result로 변환합니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` live_telegram 테스트 생성 여부
- `[사용자 입력 필요]` 테스트 Channel ID 제공 가능 여부
- `[사용자 입력 필요]` 운영 Channel 보호 정책 승인 여부
