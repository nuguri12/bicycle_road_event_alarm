# Supabase DB Setup Design

## Objective

Supabase PostgreSQL에 연결할 수 있는 SQLAlchemy/Alembic 환경을 구성하고, MVP 문서에서 정의한 초기 이벤트 저장 스키마를 코드와 마이그레이션으로 고정한다.

## Required Inputs

- `.env`의 `SUPABASE_DATABASE_URL`
- 기존 프로젝트 설정 로더
- Sprint 2의 엔티티 정의와 관계 문서

## Expected Outputs

- DB engine/session 생성 모듈
- SQLAlchemy declarative models
- Alembic 설정과 초기 마이그레이션
- 외부 DB 없이 실행되는 unit tests
- 명시적으로 실행 가능한 Supabase `SELECT 1` 연결 확인 명령

## Assumptions

- `.env`에는 실제 Supabase PostgreSQL 직접 연결 문자열이 있다.
- 실제 비밀값은 `.env.example`, 문서, 테스트 출력, Git 커밋에 남기지 않는다.
- 기본 테스트는 live DB에 접속하지 않는다.
- 운영 텔레그램 발송 설정은 이번 작업 범위가 아니다.

## Components

- `src/bicycle_road_event_alarm/db/engine.py`: 환경 설정에서 DB URL을 읽고 SQLAlchemy engine/session을 만든다.
- `src/bicycle_road_event_alarm/db/models.py`: `run_logs`, `raw_events`, `normalized_events`, `publish_attempts` 모델과 제약조건을 선언한다.
- `src/bicycle_road_event_alarm/db/health.py`: `SELECT 1` 연결 확인을 제공한다.
- `alembic.ini`, `migrations/env.py`, `migrations/versions/0001_initial_schema.py`: Alembic migration 환경을 제공한다.

## Data Flow

`.env` 값을 `load_settings()`가 읽고, DB 모듈은 `SUPABASE_DATABASE_URL`만 사용한다. Unit test는 SQLite compile 경로와 SQLAlchemy metadata를 검증하고, 실제 Supabase 연결은 별도 명령에서만 수행한다.

## Error Handling

DB URL이 비어 있으면 engine 생성 전에 명시적인 `ValueError`를 발생시킨다. 실제 DB 연결 확인은 성공 시 `True`, 실패 시 예외를 그대로 노출해 원인을 확인할 수 있게 한다.

## Testing

- Unit: metadata 테이블/컬럼/제약조건 검증
- Unit: DB URL 누락 시 engine 생성 실패
- Unit: health check가 `SELECT 1`을 실행하는지 검증
- Live: `.env`의 Supabase DB URL로 `SELECT 1`
