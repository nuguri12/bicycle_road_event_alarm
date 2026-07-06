# Indexes

## 1. 인덱스 목표

인덱스는 MVP에서 실제로 필요한 조회와 중복 방지에만 사용합니다. 과도한 인덱스는 쓰기 비용과 마이그레이션 복잡도를 높이므로 피합니다.

## 2. raw_events 인덱스

### 2.1 content_hash unique index

목적:

- 같은 원문 이벤트를 반복 저장하지 않습니다.

대상:

- `raw_events.content_hash`

정책:

- source_url, raw_title, raw_date_text, raw_location_text를 기반으로 content_hash를 생성합니다.
- 해시 생성 규칙은 Sprint 3 Crawler와 Sprint 4 Normalization에서 확정합니다.

### 2.2 source_url index

목적:

- 특정 원문 URL 재수집 여부를 빠르게 확인합니다.

대상:

- `raw_events.source_url`

## 3. normalized_events 인덱스

### 3.1 deterministic_duplicate_key unique index

목적:

- 동일한 이벤트가 여러 출처에서 수집되어도 하나의 발행 후보로 관리합니다.

대상:

- `normalized_events.deterministic_duplicate_key`

### 3.2 weekend lookup index

목적:

- 주말 또는 알림 기간에 해당하는 이벤트를 조회합니다.

대상:

- `normalized_events.start_datetime`
- `normalized_events.end_datetime`
- `normalized_events.publish_candidate`

### 3.3 region lookup index

목적:

- 지역별 이벤트 조회와 메시지 정렬을 지원합니다.

대상:

- `normalized_events.region`

## 4. publish_attempts 인덱스

### 4.1 message_hash index

목적:

- 같은 메시지 중복 발행을 방지합니다.

대상:

- `publish_attempts.message_hash`

### 4.2 publish success lookup index

목적:

- 특정 이벤트가 이미 성공적으로 발행되었는지 확인합니다.

대상:

- `publish_attempts.normalized_event_id`
- `publish_attempts.status`

## 5. run_logs 인덱스

### 5.1 started_at index

목적:

- 최근 실행 기록과 운영 장애를 빠르게 확인합니다.

대상:

- `run_logs.started_at`

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` content_hash 생성 기준 승인 여부
- `[사용자 입력 필요]` deterministic_duplicate_key 생성 기준 승인 여부
- `[사용자 입력 필요]` 지역별 조회가 운영상 필요한지 여부
