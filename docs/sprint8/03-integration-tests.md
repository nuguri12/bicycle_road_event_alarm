# Integration Tests

## 1. 통합 테스트 목표

통합 테스트는 모듈 간 데이터 흐름이 Sprint 문서의 계약을 만족하는지 확인합니다.

## 2. 기본 통합 흐름

테스트할 흐름:

1. Raw Event Candidate 생성
2. Normalized Event 변환
3. Classification 적용
4. Duplicate key 생성
5. Message generation fallback 실행
6. Telegram publish mock 호출
7. publish_attempt 기록 mock 확인

## 3. 외부 의존성 처리

- 데이터베이스는 test database 또는 repository mock을 사용합니다.
- OpenAI API는 mock 응답을 사용합니다.
- Telegram API는 HTTP mock을 사용합니다.
- 실제 crawler HTTP 호출은 포함하지 않습니다.

## 4. 성공 기준

- valid 이벤트만 발행 후보가 됩니다.
- 이미 성공 발행된 message_hash는 발행하지 않습니다.
- Telegram 실패는 failed 결과로 전달됩니다.
- 전체 run 결과가 success 또는 partial_success로 계산됩니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 통합 테스트에서 실제 test DB를 사용할지 mock DB를 사용할지 여부
- `[사용자 입력 필요]` 전체 pipeline smoke test를 구현할지 여부
