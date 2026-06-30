# Live SPATIC Ingestion Design

## Objective

SPATIC 목록/상세 페이지를 HTTP로 가져와 `RawEventCandidate`로 변환하고, Supabase `raw_events`에 중복 없이 저장하는 실행 흐름을 구현한다.

## Required Inputs

- `.env`의 `SUPABASE_DATABASE_URL`
- SPATIC 목록 URL
- DB session

## Expected Outputs

- 재시도 가능한 HTTP client
- SPATIC 목록/상세 수집 orchestration
- `run_logs` 생성/완료 기록
- CLI entrypoint
- 외부 네트워크 없는 unit tests

## Assumptions

- 기본 테스트는 live SPATIC와 Supabase에 접속하지 않는다.
- HTTP 429/5xx/timeout은 재시도하고, 4xx는 재시도하지 않는다.
- 실제 저장 실행은 명령으로 명시적으로 실행한다.
- 정규화와 Telegram 발송은 이번 범위가 아니다.

## Components

- `crawler/http.py`: `requests` 기반 HTTP client와 retry 정책
- `crawler/spatic_ingestion.py`: SPATIC 목록/상세 HTML을 후보 리스트로 변환
- `crawler/repository.py`: `run_logs` 생성과 저장 결과 반영
- `cli/ingest_raw_events.py`: `.env`를 읽고 DB 저장 실행

## Testing

- HTTP client가 retry 대상 status code를 재시도한다.
- HTTP client가 404를 재시도하지 않는다.
- SPATIC ingestion이 목록과 상세 페이지를 순서대로 가져온다.
- Repository가 run log 상태와 count를 기록한다.
