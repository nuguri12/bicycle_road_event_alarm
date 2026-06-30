# Database Tests

## 1. 데이터베이스 테스트 목표

데이터베이스 테스트는 저장 모델, 중복 제약, 발행 이력 조회가 의도대로 동작하는지 검증합니다.

## 2. 테스트 대상

- raw_events 저장
- normalized_events 저장
- deterministic_duplicate_key unique 정책
- publish_attempts 저장
- message_hash 기반 성공 발행 조회
- run_logs 상태 기록

## 3. 테스트 방식

선택지:

- repository mock 기반 테스트
- 로컬 PostgreSQL 테스트
- Supabase test project 기반 테스트

MVP 권장:

- 단위 테스트는 repository mock을 사용합니다.
- 마이그레이션 검증은 별도 test database에서 수행합니다.

## 4. 검증 기준

- 같은 content_hash는 중복 저장되지 않습니다.
- 같은 deterministic_duplicate_key는 중복 이벤트로 처리됩니다.
- success publish_attempt가 있으면 재발행 후보에서 제외됩니다.
- failed publish_attempt는 재처리 가능합니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` test database 사용 여부
- `[사용자 입력 필요]` Supabase test project 사용 여부
- `[사용자 입력 필요]` migration 테스트 범위
