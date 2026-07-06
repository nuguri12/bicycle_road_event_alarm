# Entity Definitions

## 1. run_logs

GitHub Actions 실행 1회를 나타냅니다.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| id | uuid | yes | 실행 ID |
| status | text | yes | `running`, `success`, `partial_success`, `failed` |
| started_at | timestamptz | yes | 실행 시작 시각 |
| finished_at | timestamptz | no | 실행 종료 시각 |
| raw_event_count | integer | yes | 수집한 원문 이벤트 수 |
| normalized_event_count | integer | yes | 정규화된 이벤트 수 |
| published_message_count | integer | yes | 발행 성공 메시지 수 |
| error_summary | text | no | 실행 전체 오류 요약 |
| created_at | timestamptz | yes | 레코드 생성 시각 |

## 2. raw_events

출처에서 수집한 원문 이벤트 후보입니다.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| id | uuid | yes | 원문 이벤트 ID |
| run_id | uuid | yes | 수집한 실행 ID |
| source_name | text | yes | 출처 이름 |
| source_url | text | yes | 원문 URL |
| raw_title | text | no | 원문 제목 |
| raw_body | text | no | 원문 본문 또는 요약 |
| raw_date_text | text | no | 원문 날짜 표현 |
| raw_location_text | text | no | 원문 장소 표현 |
| content_hash | text | yes | 원문 중복 확인용 해시 |
| fetched_at | timestamptz | yes | 수집 시각 |
| created_at | timestamptz | yes | 레코드 생성 시각 |

## 3. normalized_events

발행 판단과 메시지 생성에 사용하는 표준 이벤트입니다.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| id | uuid | yes | 정규화 이벤트 ID |
| raw_event_id | uuid | yes | 원문 이벤트 ID |
| title | text | yes | 표준화된 이벤트 제목 |
| start_datetime | timestamptz | yes | 이벤트 시작 시각 |
| end_datetime | timestamptz | no | 이벤트 종료 시각 |
| location_name | text | yes | 대표 장소명 |
| region | text | yes | 서울 또는 경기도 내 지역 |
| event_type | text | yes | 행사, 통제, 축제 등 이벤트 유형 |
| cyclist_impact_level | text | yes | 자전거 이용자 영향도 |
| cyclist_impact_reason | text | no | 영향도 판단 이유 |
| publish_candidate | boolean | yes | 발행 후보 여부 |
| deterministic_duplicate_key | text | yes | 결정적 중복 판단 키 |
| validation_status | text | yes | `valid`, `invalid`, `needs_review` |
| created_at | timestamptz | yes | 레코드 생성 시각 |
| updated_at | timestamptz | yes | 레코드 수정 시각 |

## 4. publish_attempts

Telegram 발행 시도 1회를 나타냅니다.

| Column | Type | Required | Description |
| --- | --- | --- | --- |
| id | uuid | yes | 발행 시도 ID |
| run_id | uuid | yes | 발행을 시도한 실행 ID |
| normalized_event_id | uuid | no | 관련 정규화 이벤트 ID |
| telegram_channel_id | text | yes | 발행 대상 채널 ID 또는 사용자명 |
| message_hash | text | yes | 메시지 중복 확인용 해시 |
| status | text | yes | `success`, `failed`, `skipped` |
| failure_reason | text | no | 실패 또는 건너뜀 사유 |
| attempted_at | timestamptz | yes | 발행 시도 시각 |
| created_at | timestamptz | yes | 레코드 생성 시각 |

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` cyclist_impact_level 값 목록
- `[사용자 입력 필요]` event_type 값 목록
- `[사용자 입력 필요]` validation_status에 `needs_review`를 유지할지 여부
- `[사용자 입력 필요]` 빈 주말 메시지를 publish_attempts에 저장할지 여부
