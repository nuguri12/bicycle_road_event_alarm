# 주말 자전거 도로 이벤트 알림 서비스

주말 라이딩 전에 자전거 이동에 영향을 줄 수 있는 교통 통제, 행사, 공원 이벤트 정보를 수집하고 정리해 Telegram으로 알려주는 배치 서비스입니다.

## 1. 서비스 개요

이 서비스는 공공 웹사이트의 교통 통제 및 행사 정보를 수집한 뒤, 자전거 이용자 관점에서 의미 있는 이벤트만 선별해 알림 메시지로 전달합니다.

현재 MVP의 기본 소스는 한강공원 행사, 한강공원 새소식, 아라뱃길 공지입니다. SPATIC 코드는 회귀 참고용으로 보존하지만 운영 수집 경로에서는 제외했습니다.

### 해결하려는 문제

- 주말 행사, 마라톤, 축제, 교통 통제 정보가 여러 사이트에 흩어져 있습니다.
- 공지 제목만으로는 자전거 이동에 실제 영향이 있는지 판단하기 어렵습니다.
- 같은 이벤트가 여러 출처에 반복되거나 비슷한 제목으로 올라올 수 있습니다.
- 라이딩 직전에 정보를 찾으면 경로 변경이나 일정 조정이 늦어집니다.

### 현재 처리 흐름

1. 한강공원 행사, 한강공원 새소식, 아라뱃길 공지에서 원문 이벤트 후보를 수집합니다.
2. 원문 이벤트를 Supabase PostgreSQL의 `raw_events`에 저장합니다.
3. 날짜, 장소, 이벤트 유형, 자전거 이동 영향도를 규칙 기반으로 정규화합니다.
4. 정규화된 이벤트를 `normalized_events`에 저장합니다.
5. 발송 후보 이벤트를 OpenAI 또는 fallback 로직으로 한국어 알림 메시지로 생성합니다.
6. Telegram 채널로 메시지를 발송합니다.
7. 발송 성공, 실패, 스킵 결과를 `publish_attempts`에 기록합니다.

이벤트가 없을 때도 운영 확인을 위해 날짜가 포함된 no-event 메시지를 생성합니다.

예:

```text
2026-07-01 기준 이번 주말 자전거 주의 이벤트가 없습니다.
```

## 2. 기대되는 효과

- 주말 라이딩 전 확인해야 할 이벤트를 한곳에서 볼 수 있습니다.
- 자전거 이동 영향이 있는 정보만 추려 확인 시간을 줄입니다.
- 중복 이벤트와 중복 발송을 줄여 알림 신뢰도를 높입니다.
- GitHub Actions, Supabase 로그, Telegram 발송 이력으로 운영 상태를 추적할 수 있습니다.
- 일부 소스 장애나 이벤트 없음 상황도 배치 실행 결과로 확인할 수 있습니다.

## 3. 기술 스택

### 언어와 런타임

- Python 3.12+

### 주요 라이브러리

- Requests: 공공 웹사이트 HTTP 요청
- BeautifulSoup4: HTML 파싱
- SQLAlchemy 2.x: ORM과 세션 관리
- Alembic: DB 마이그레이션
- Psycopg 3: PostgreSQL 연결
- Python Dotenv: 로컬 `.env` 로딩
- OpenAI Python SDK: 알림 메시지 생성
- Pytest: 테스트
- Ruff: 린트
- Black: 포맷팅
- Mypy: 타입 검사

### 데이터베이스

- Supabase PostgreSQL
- 연결 방식: Supabase Transaction Pooler
- DB 작성 방식:
  - SQLAlchemy ORM 모델로 schema 정의
  - Alembic migration으로 실제 DB 반영
  - 로컬/운영 연결 정보는 `SUPABASE_DATABASE_URL` 환경 변수 사용

주요 테이블:

- `run_logs`: 배치 실행 이력
- `raw_events`: 수집한 원문 이벤트
- `normalized_events`: 정규화된 이벤트
- `publish_attempts`: Telegram 발송 시도 이력

## 4. 실행 방법

개발 의존성 설치:

```bash
python -m pip install -e .[dev]
```

전체 로컬 검증:

```bash
python -m pytest -q
python -m ruff check .
python -m mypy src tests
python -m black --check .
python -m compileall src
```

DB 마이그레이션:

```bash
python -m alembic upgrade head
```

원문 이벤트 수집:

```bash
python -m bicycle_road_event_alarm.cli.ingest_raw_events
```

특정 실행 ID 기준 정규화:

```bash
python -m bicycle_road_event_alarm.cli.normalize_events --run-id "<RUN_ID>"
```

특정 실행 ID 기준 메시지 생성 및 발송:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>"
```

OpenAI 없이 fallback 메시지 생성:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --run-id "<RUN_ID>" --force-fallback
```

DB/CLI 검증용 더미 publishable 이벤트 생성:

```bash
python -m bicycle_road_event_alarm.cli.seed_publishable_fixture
```

## 5. GitHub Actions 운영 상태

Workflow 이름:

- `Manual Batch`

현재 운영 schedule:

```yaml
Cloudflare Cron: "30 22 * * *"
```

의미:

- Cloudflare cron은 UTC 기준입니다.
- `30 22 * * *`는 한국 시간 기준 매일 07:30입니다.

Cloudflare는 GitHub Actions `workflow_dispatch`를 실제 발송 입력값으로 호출합니다.

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

수동 실행(`workflow_dispatch`)의 기본값은 안전하게 유지합니다.

```env
dry_run=true
enable_telegram_publish=false
force_fallback=false
apply_migrations=false
```

DB 마이그레이션은 예약 실행과 분리되어 있습니다.
필요할 때만 수동 실행에서 `apply_migrations=true`를 선택해 Alembic migration을 적용합니다.

```env
apply_migrations=true
```

동일 브랜치에서 수동 실행과 예약 실행이 겹치면 GitHub Actions `concurrency` 설정으로 순차 실행됩니다.

## 6. GitHub schedule 진단 결과

2026-07-01 14:30 KST에 예정했던 schedule run이 GitHub Actions에 나타나지 않아 임시로 `*/5 * * * *` smoke schedule을 사용했습니다.
이후 GitHub schedule이 다시 불안정한 것이 확인되어 Cloudflare Workers Cron이 `workflow_dispatch`를 호출하는 방식으로 전환합니다.

확인한 내용:

- workflow 상태는 `active`였습니다.
- repository default branch는 `main`이었습니다.
- remote `main`에 workflow 파일이 존재했습니다.
- remote workflow 파일에 cron 표현식이 존재했습니다.
- 이후 `event=schedule` run 생성이 확인되었습니다.

추가로 예약 실행 실패의 직접 원인은 GitHub schedule 미생성이 아니라 Alembic revision ID 길이였습니다.
해당 migration ID는 `0002_publish_success_idx`로 단축했고, 예약 실행에서는 DB migration을 수행하지 않도록 분리했습니다.

## 7. 환경 변수와 Secrets

로컬 `.env`는 Git에 커밋하지 않습니다.

필수 GitHub Repository Secrets:

- `SUPABASE_DATABASE_URL`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

기본 안전 설정:

```env
ENABLE_TELEGRAM_PUBLISH=false
DRY_RUN=true
```

Telegram 실제 발송을 할 때만 다음 조합을 사용합니다.

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

## 8. 현재 구현 상태

완료:

- Sprint 0-9 문서화
- Python 프로젝트 구조
- Supabase DB 연결 및 Alembic migration
- 한강공원 행사 fixture 기반 파서
- 한강공원 새소식 fixture 기반 파서
- 아라뱃길 공지 fixture 기반 파서
- 다중 소스 live 수집 CLI
- `raw_events` 저장
- `normalized_events` 정규화 및 저장
- OpenAI 메시지 생성 wrapper
- fallback 메시지 생성
- Telegram publisher
- 실제 Telegram private channel 발송 검증
- 중복 발송 방지
- `publish_attempts` 기록
- Cloudflare Cron + GitHub Actions manual workflow
- no-event 메시지 생성
- skipped 발송 결과 DB 기록
- run-id 기준 배치 데이터 스코프

남은 작업:

- 다음 매일 07:30 KST Cloudflare-triggered workflow 실행 결과 확인
- 필요 시 수동 실행에서 `apply_migrations=true`로 DB migration 적용
- 아라뱃길 공식 공지 URL 정밀도 추가 검증
- 전체 소스 장애와 실제 이벤트 없음 상태를 더 명확히 분리
- 운영 모니터링 문서와 알림 기준 보강

## 9. 기타

- 실제 API key, DB URL, Telegram token은 Git에 커밋하지 않습니다.
- `.env.example`은 비밀값 없는 템플릿으로 유지합니다.
- fixture 이벤트는 검증 후 실제 알림 후보에 남지 않도록 삭제해야 합니다.
- 현재 MVP의 이벤트 판단은 규칙 기반이며, OpenAI는 최종 메시지 정규화/요약에만 사용합니다.
- 자세한 handoff는 `docs/handoff-current-status.md`를 참고하세요.
