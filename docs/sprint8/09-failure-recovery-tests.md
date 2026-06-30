# Failure Recovery Tests

## 1. 실패 복구 테스트 목표

실패 복구 테스트는 부분 실패가 다음 실행을 막지 않고, 중복 발행을 만들지 않는지 검증합니다.

## 2. 테스트 시나리오

크롤러 실패:

- 한 출처가 timeout이어도 다른 출처 처리를 계속합니다.
- run status는 partial_success가 됩니다.

OpenAI 실패:

- AI timeout 시 fallback 메시지를 생성합니다.
- fallback 메시지도 검증합니다.

Telegram 실패:

- HTTP 503 후 재시도합니다.
- 최종 실패 시 failed publish_attempt를 기록합니다.
- 다음 실행에서 success 기록이 없으면 재처리 가능합니다.

중복 실행:

- 같은 message_hash success 기록이 있으면 발행하지 않습니다.

## 3. 검증 기준

- 실패 사유가 로그 또는 저장소에 남습니다.
- 비밀값이 로그에 남지 않습니다.
- 성공한 단계의 결과를 불필요하게 되돌리지 않습니다.
- 다음 실행에서 복구 가능성이 유지됩니다.

## 4. 사용자 입력 필요 항목

- `[사용자 입력 필요]` partial_success를 성공에 가까운 상태로 볼지 실패에 가까운 상태로 볼지 여부
- `[사용자 입력 필요]` Telegram 최종 실패 후 재처리 정책 승인 여부
