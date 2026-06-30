# Raw Event Ingestion Design

## Objective

첫 번째 MVP 크롤러 소스인 서울경찰청 교통정보센터 공개 HTML에서 원문 이벤트 후보를 만들고, 중복 없이 `raw_events`에 저장할 수 있는 흐름을 구현한다.

## Required Inputs

- SPATIC 목록/상세 HTML
- DB `run_logs.id`
- SQLAlchemy session

## Expected Outputs

- `RawEventCandidate` 값 객체
- SPATIC 목록/상세 fixture parser
- content hash 생성 규칙
- `raw_events` 저장 함수
- 외부 네트워크 없이 실행되는 unit tests

## Assumptions

- SPATIC 목록 페이지는 HTML 구조가 바뀔 수 있으므로 selector는 출처별 모듈에 격리한다.
- 기본 테스트는 live crawler를 실행하지 않는다.
- 날짜/장소 정규화는 Sprint 4 기능에서 처리하고, 이번 단계는 원문 문자열 저장에 집중한다.
- `content_hash`는 source name, source URL, title, body를 기반으로 생성한다.

## Components

- `src/bicycle_road_event_alarm/crawler/raw_event.py`: 후보 모델과 hash 생성
- `src/bicycle_road_event_alarm/crawler/spatic.py`: SPATIC fixture parser
- `src/bicycle_road_event_alarm/crawler/repository.py`: 후보를 `RawEvent` 모델로 변환하고 저장

## Testing

- Fixture 목록 HTML에서 상세 URL을 추출한다.
- Fixture 상세 HTML에서 원문 후보를 만든다.
- 같은 입력은 같은 content hash를 만든다.
- 같은 `content_hash`가 이미 있으면 저장하지 않는다.
