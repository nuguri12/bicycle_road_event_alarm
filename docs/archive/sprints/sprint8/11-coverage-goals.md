# Coverage Goals

## 1. 커버리지 목표

커버리지는 숫자 자체보다 핵심 리스크가 테스트되는지를 우선합니다.

## 2. MVP 권장 목표

권장 최소 기준:

- 전체 line coverage: 70%
- normalizer/classifier: 85%
- duplicate/message hash: 90%
- fallback generator: 85%
- Telegram retry logic: 85%

## 3. 숫자보다 중요한 필수 테스트

반드시 테스트해야 하는 영역:

- 중복 발행 방지
- 날짜와 장소 검증
- invalid와 needs_review 발행 제외
- OpenAI 실패 fallback
- Telegram 실패 기록
- Secret 로그 노출 방지

## 4. 커버리지 제외 후보

제외 가능:

- 단순 dataclass 또는 Pydantic field 선언
- CLI 진입점 boilerplate
- Alembic auto-generated migration 일부
- live test 전용 코드

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 전체 line coverage 70% 승인 여부
- `[사용자 입력 필요]` 핵심 모듈별 목표치 승인 여부
- `[사용자 입력 필요]` coverage 실패 시 CI 실패 처리 여부
