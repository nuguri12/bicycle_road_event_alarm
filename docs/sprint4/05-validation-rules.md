# Validation Rules

## 1. 검증 목표

검증은 부정확하거나 모호한 이벤트가 Telegram 메시지로 발행되는 것을 막기 위한 마지막 정규화 단계입니다.

## 2. validation_status 값

MVP 기본값:

- `valid`: 발행 판단에 필요한 필수 정보가 충분합니다.
- `invalid`: 필수 정보가 없어 발행하면 안 됩니다.
- `needs_review`: 정보가 일부 있지만 자동 판단이 위험합니다.

## 3. valid 조건

다음 조건을 모두 만족해야 합니다.

- title이 비어 있지 않습니다.
- start_datetime이 존재합니다.
- location_name이 존재합니다.
- region이 서울 또는 경기도입니다.
- source_url이 존재합니다.
- deterministic_duplicate_key를 만들 수 있습니다.

## 4. invalid 조건

다음 중 하나라도 해당하면 invalid입니다.

- title과 raw_body 모두 비어 있습니다.
- 날짜를 찾을 수 없습니다.
- source_url이 없습니다.
- 서울 또는 경기도와 무관한 지역입니다.
- 원문이 이벤트가 아닌 일반 안내입니다.

## 5. needs_review 조건

다음 경우 needs_review입니다.

- 날짜는 있으나 연도가 모호합니다.
- 장소가 너무 넓습니다.
- 이벤트인지 일반 공지인지 불명확합니다.
- 중복 후보가 있으나 자동 병합이 위험합니다.
- 영향도 판단에 필요한 표현이 부족합니다.

## 6. 발행 제외 규칙

다음 상태는 Telegram 발행 대상에서 제외합니다.

- validation_status가 `invalid`
- validation_status가 `needs_review`
- cyclist_impact_level이 `none`
- cyclist_impact_level이 `unknown`

## 7. 테스트 기준

정규화 구현 시 다음 fixture를 준비합니다.

- 정상 날짜, 정상 장소, high impact 이벤트
- 날짜 누락 이벤트
- 장소가 넓은 이벤트
- 서울/경기도 밖 이벤트
- 같은 날짜와 장소의 중복 후보
- 일반 공지로 보이는 이벤트

## 8. 사용자 입력 필요 항목

- `[사용자 입력 필요]` needs_review 이벤트를 발행에서 제외하는 정책 승인 여부
- `[사용자 입력 필요]` 서울/경기도 밖 이벤트를 항상 invalid로 둘지 여부
- `[사용자 입력 필요]` 정규화 테스트 fixture 최소 개수
