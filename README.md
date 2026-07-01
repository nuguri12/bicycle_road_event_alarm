# Weekend Cycling Event Alert Service

주말 자전거도로 이용자가 교통 통제, 대회, 축제, 공원 행사 같은 이동 방해 요소를 미리 확인할 수 있도록 공개 정보를 수집하고 알림으로 전달하는 배치 서비스입니다.

## 1. 서비스 개요

이 프로젝트는 공공 웹사이트의 교통 통제 및 행사 정보를 수집해 자전거 이용자 관점으로 정리하는 알림 서비스를 목표로 합니다.

현재 구현된 흐름은 다음과 같습니다.

1. 서울경찰청 교통정보센터(SPATIC) 페이지에서 원문 이벤트 후보를 수집합니다.
2. 원문 이벤트를 Supabase PostgreSQL의 `raw_events`에 저장합니다.
3. 저장된 원문 이벤트를 날짜, 장소, 이벤트 유형, 자전거 이동 영향도 기준으로 정규화합니다.
4. 정규화 결과를 `normalized_events`에 중복 없이 저장합니다.
5. 발송 후보 이벤트를 한국어 알림 메시지로 생성합니다.
6. Telegram 발송 단계를 안전 플래그와 dry-run 모드로 실행합니다.

아직 구현 예정인 흐름은 다음과 같습니다.

1. `publish_attempts`에 발송 이력을 저장하고 중복 발송을 방지합니다.
2. 실제 Telegram 채널 발송을 운영 플래그로 검증합니다.
3. GitHub Actions로 주말 전 정기 실행합니다.

### 페인 포인트

- 자전거도로 이용자는 주말 행사, 마라톤, 축제, 교통 통제 정보를 여러 사이트에서 따로 확인해야 합니다.
- 공공 공지의 제목만으로는 자전거 이동에 실제 영향이 있는지 판단하기 어렵습니다.
- 통제 구간, 시간, 장소 표현이 비정형 텍스트로 제공되어 놓치기 쉽습니다.
- 같은 이벤트가 여러 출처에 반복되거나 비슷한 제목으로 올라올 수 있습니다.
- 주말 라이딩 직전에 정보를 확인하면 우회 계획을 세우기 늦습니다.

## 2. 기대되는 효과

- 주말 라이딩 전 교통 통제와 행사 정보를 한 번에 확인할 수 있습니다.
- 날짜, 장소, 영향도 기준으로 이벤트를 정리해 불필요한 정보 탐색 시간을 줄입니다.
- 중복 이벤트 저장과 중복 발송을 줄여 알림 품질을 높입니다.
- Telegram 채널 발송을 통해 별도 앱 없이 빠르게 알림을 받을 수 있습니다.
- 배치 실행과 로그 저장으로 수집, 정규화, 발송 이력을 추적할 수 있습니다.

## 3. 기술스택

### 사용 언어

- Python 3.12+

### 주요 라이브러리

- Requests: 공공 웹 페이지 HTTP 요청
- BeautifulSoup4: HTML 파싱
- SQLAlchemy 2.x: DB 모델과 session 관리
- Alembic: DB migration 관리
- Psycopg 3: PostgreSQL 연결
- Python Dotenv: 로컬 `.env` 로딩
- OpenAI Python SDK: 알림 메시지 생성
- Pytest: 테스트
- Ruff: lint
- Black: formatting
- Mypy: type checking

### DB

- Supabase PostgreSQL
- 연결 방식: Supabase Transaction Pooler
- DB 작성 방식:
  - SQLAlchemy ORM 모델로 schema 정의
  - Alembic migration으로 실제 DB 반영
  - `.env`의 `SUPABASE_DATABASE_URL`로 로컬/운영 연결

현재 초기 migration은 다음 테이블을 생성합니다.

- `run_logs`: 배치 실행 이력
- `raw_events`: 수집한 원문 이벤트
- `normalized_events`: 정규화된 이벤트
- `publish_attempts`: Telegram 발송 시도 이력

### 현재 실행 가능한 명령

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

Supabase migration 적용:

```bash
python -m alembic upgrade head
```

SPATIC 원문 이벤트 수집:

```bash
python -m bicycle_road_event_alarm.cli.ingest_raw_events
```

원문 이벤트 정규화:

```bash
python -m bicycle_road_event_alarm.cli.normalize_events
```

메시지 생성 및 Telegram 발송 단계 실행:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages
```

OpenAI 없이 fallback 전체 흐름 검증:

```bash
python -m bicycle_road_event_alarm.cli.generate_messages --force-fallback
```

DB/CLI 검증용 publishable 더미 이벤트 생성:

```bash
python -m bicycle_road_event_alarm.cli.seed_publishable_fixture
```

GitHub Actions 수동 배치:

- Actions 탭에서 `Manual Batch` workflow를 수동 실행합니다.
- 기본값은 `dry_run=true`, `enable_telegram_publish=false`라 실제 Telegram 발송을 하지 않습니다.
- 실제 발송 검증 시에만 `dry_run=false`, `enable_telegram_publish=true`로 바꿉니다.

## 4. 기타

### 현재 구현 상태

- DDD 문서화 Sprint 0-9 완료
- Python 프로젝트 골격 완료
- Supabase DB 연결 및 초기 migration 완료
- SPATIC fixture 기반 raw event 파서 완료
- SPATIC live 수집 CLI 완료
- `raw_events` 저장 로직 완료
- 규칙 기반 `normalized_events` 저장 로직 완료
- OpenAI wrapper와 규칙 기반 fallback 메시지 생성 완료
- Telegram publisher wrapper와 dry-run CLI 연결 완료
- 랜덤 publishable fixture seed CLI 완료
- `generate_messages --force-fallback` fallback 검증 옵션 완료
- Private Telegram 채널 실제 발송 및 중복 발송 방지 검증 완료
- OpenAI 메시지 생성 CLI 검증 완료
- `publish_attempts` 성공 기록 및 중복 발송 방지 완료
- GitHub Actions 수동 배치 workflow 완료

자세한 이어받기 문서는 `docs/handoff-current-status.md`를 참고하세요.

### 보안 및 환경 변수

- 실제 API key, DB URL, Telegram token은 Git에 커밋하지 않습니다.
- `.env`는 `.gitignore`에 포함되어 있습니다.
- `.env.example`은 빈 템플릿으로 유지합니다.
- Telegram 실제 발송은 기본적으로 꺼져 있습니다.

기본 안전 설정:

```env
ENABLE_TELEGRAM_PUBLISH=false
DRY_RUN=true
```

GitHub Secrets에 필요한 값:

- `SUPABASE_DATABASE_URL`
- `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHANNEL_ID`

### 남은 주요 작업

- GitHub Actions manual dispatch 검증
- GitHub Secrets 설정
- GitHub Actions 정기 스케줄 활성화
- Sprint 8: 통합 테스트와 live test marker
- Sprint 9: 운영 문서, 모니터링, 릴리즈 체크리스트 보강
