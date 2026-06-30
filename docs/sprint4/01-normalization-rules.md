# Normalization Rules

## 1. 정규화 목표

정규화는 크롤러가 반환한 Raw Event Candidate를 데이터베이스에 저장 가능한 Normalized Event로 변환합니다.

입력:

- source_name
- source_url
- fetched_at
- raw_title
- raw_body
- raw_date_text
- raw_location_text

출력:

- title
- start_datetime
- end_datetime
- location_name
- region
- event_type
- cyclist_impact_level
- cyclist_impact_reason
- publish_candidate
- deterministic_duplicate_key
- validation_status

## 2. 제목 정규화

규칙:

- 앞뒤 공백을 제거합니다.
- 연속 공백은 하나로 줄입니다.
- 출처명이 반복 포함된 경우 제거합니다.
- 제목이 비어 있으면 `raw_body` 첫 문장을 후보로 사용합니다.
- 제목 후보가 없으면 `validation_status`를 `invalid`로 둡니다.

하지 않는 일:

- 제목을 마케팅 문구처럼 재작성하지 않습니다.
- AI로 제목을 새로 만들지 않습니다.

## 3. 날짜와 시간 정규화

우선순위:

1. raw_date_text
2. raw_body 안의 날짜 표현
3. raw_title 안의 날짜 표현

기본 규칙:

- 연도 누락 시 fetched_at의 연도를 사용합니다.
- 종료 시간이 없으면 end_datetime은 null로 둡니다.
- 날짜가 과거이고 연도 누락 가능성이 높으면 `needs_review`로 둡니다.
- 날짜를 찾을 수 없으면 `invalid`로 둡니다.

주의:

- 한국 시간대 기준으로 해석합니다.
- 모호한 기간 표현은 임의로 확정하지 않습니다.

## 4. 장소와 지역 정규화

우선순위:

1. raw_location_text
2. raw_body 안의 장소 표현
3. raw_title 안의 장소 표현

규칙:

- 대표 장소명은 가장 구체적인 지명을 우선합니다.
- 서울과 경기도 밖의 장소는 기본적으로 발행 후보에서 제외합니다.
- 장소가 없으면 `needs_review` 또는 `invalid`로 둡니다.

## 5. 발행 후보 판단

`publish_candidate`는 다음 조건을 모두 만족할 때 true입니다.

- validation_status가 `valid`입니다.
- 날짜가 알림 대상 기간에 포함됩니다.
- 서울 또는 경기도 관련 이벤트입니다.
- event_type이 자전거 이동에 영향을 줄 수 있습니다.
- cyclist_impact_level이 `low` 이상입니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 연도 누락 날짜를 fetched_at 연도로 해석하는 규칙 승인 여부
- `[사용자 입력 필요]` 날짜 모호성 발생 시 `needs_review`로 둘지 `invalid`로 둘지 여부
- `[사용자 입력 필요]` publish_candidate 최소 영향도 기준
