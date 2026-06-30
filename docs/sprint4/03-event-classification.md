# Event Classification

## 1. 분류 목표

이벤트 분류는 정규화된 이벤트가 자전거 이용자에게 어떤 종류의 영향을 줄 수 있는지 판단합니다.

출력 필드:

- event_type
- cyclist_impact_level
- cyclist_impact_reason
- publish_candidate

## 2. event_type 값

MVP 기본값:

- `road_closure`: 도로 통제
- `running_event`: 마라톤, 달리기 대회
- `walking_event`: 걷기 행사
- `festival`: 축제
- `public_event`: 공공 행사
- `cycling_event`: 자전거 행사
- `river_park_event`: 한강 또는 하천 공원 행사
- `unknown`: 분류 불가

## 3. cyclist_impact_level 값

MVP 기본값:

- `none`: 자전거 이동 영향 없음
- `low`: 혼잡 가능성 있음
- `medium`: 우회 또는 주의 필요
- `high`: 통제 또는 심각한 혼잡 가능성 높음
- `unknown`: 판단 불가

## 4. 결정 규칙

### 4.1 high

다음 표현이 있으면 high 후보입니다.

- 도로 통제
- 전면 통제
- 교통 통제
- 출입 제한
- 우회
- 마라톤 코스
- 자전거도로 통제

### 4.2 medium

다음 표현이 있으면 medium 후보입니다.

- 대규모 행사
- 축제
- 인파 집중
- 공원 행사
- 일부 구간 혼잡

### 4.3 low

다음 표현이 있으면 low 후보입니다.

- 소규모 행사
- 체험 행사
- 안내 부스
- 장소가 자전거도로와 인접하지만 통제 표현이 없음

### 4.4 unknown

날짜 또는 장소는 있으나 영향 표현이 부족하면 unknown으로 둡니다.

## 5. publish_candidate 규칙

발행 후보는 다음 경우 true입니다.

- cyclist_impact_level이 `low`, `medium`, `high` 중 하나입니다.
- validation_status가 `valid`입니다.
- 알림 기간 안의 이벤트입니다.

unknown은 기본적으로 발행하지 않습니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` event_type 값 목록 승인 여부
- `[사용자 입력 필요]` cyclist_impact_level 값 목록 승인 여부
- `[사용자 입력 필요]` unknown 이벤트를 발행 후보에서 제외하는 정책 승인 여부
