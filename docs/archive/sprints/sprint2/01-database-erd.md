# Database ERD

## 1. ERD 개요

MVP 데이터베이스는 원문 수집 결과, 정규화된 이벤트, 실행 기록, 발행 이력을 분리합니다.

```mermaid
erDiagram
    run_logs ||--o{ raw_events : collects
    raw_events ||--o| normalized_events : normalizes_to
    normalized_events ||--o{ publish_attempts : publishes
    run_logs ||--o{ publish_attempts : records

    run_logs {
        uuid id PK
        text status
        timestamptz started_at
        timestamptz finished_at
        integer raw_event_count
        integer normalized_event_count
        integer published_message_count
        text error_summary
        timestamptz created_at
    }

    raw_events {
        uuid id PK
        uuid run_id FK
        text source_name
        text source_url
        text raw_title
        text raw_body
        text raw_date_text
        text raw_location_text
        text content_hash
        timestamptz fetched_at
        timestamptz created_at
    }

    normalized_events {
        uuid id PK
        uuid raw_event_id FK
        text title
        timestamptz start_datetime
        timestamptz end_datetime
        text location_name
        text region
        text event_type
        text cyclist_impact_level
        text cyclist_impact_reason
        boolean publish_candidate
        text deterministic_duplicate_key
        text validation_status
        timestamptz created_at
        timestamptz updated_at
    }

    publish_attempts {
        uuid id PK
        uuid run_id FK
        uuid normalized_event_id FK
        text telegram_channel_id
        text message_hash
        text status
        text failure_reason
        timestamptz attempted_at
        timestamptz created_at
    }
```

## 2. 테이블 선택 이유

- `run_logs`: GitHub Actions 실행 단위의 성공, 실패, 처리 건수를 추적합니다.
- `raw_events`: 크롤러가 가져온 원문 후보를 보존합니다.
- `normalized_events`: 발행 판단에 필요한 표준 이벤트 데이터를 저장합니다.
- `publish_attempts`: Telegram 발행 결과와 중복 발행 방지를 추적합니다.

## 3. MVP에서 제외하는 테이블

- 사용자 계정 테이블
- 개인화 경로 테이블
- 결제 테이블
- 웹 관리자 테이블
- 상세 분석 테이블

## 4. 사용자 입력 필요 항목

- `[사용자 입력 필요]` Supabase PostgreSQL에서 UUID 생성 확장 사용 가능 여부
- `[사용자 입력 필요]` Telegram Channel ID를 평문으로 저장해도 되는지 여부
- `[사용자 입력 필요]` 실행 로그를 데이터베이스에 저장하는 방식 승인 여부
