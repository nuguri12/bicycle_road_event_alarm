# 자전거 도로 이벤트 알림 서비스

매일 아침 자전거 이동에 영향을 줄 수 있는 공공 행사, 교통 통제, 공원 공지 정보를 수집하고 정규화한 뒤 Telegram 채널로 알려주는 배치 서비스입니다.

## 1. 서비스 개요

이 서비스는 여러 공공 정보원을 확인해야 하는 번거로움을 줄이기 위해 만들어졌습니다. 한강공원 행사, 한강공원 공지, 아라뱃길 공지처럼 자전거 이용자에게 영향을 줄 수 있는 정보를 수집하고, 당일 이동에 실제로 관련 있는 이벤트만 알림 후보로 분리합니다.

### 해결하려는 문제

- 자전거 도로 통제, 행사, 공원 공지가 여러 사이트에 흩어져 있습니다.
- 공지 제목만으로는 실제 자전거 이동에 영향을 주는지 판단하기 어렵습니다.
- 같은 이벤트가 반복 수집되거나 유사한 제목으로 노출될 수 있습니다.
- 라이딩 직전에 정보를 확인하면 경로 변경이나 일정 조정이 늦어질 수 있습니다.

### 현재 처리 흐름

1. 한강공원 행사, 한강공원 공지, 아라뱃길 공지에서 원문 이벤트 후보를 수집합니다.
2. 원문 이벤트를 Supabase PostgreSQL의 `raw_events`에 저장합니다.
3. 날짜, 시간, 장소, 이벤트 유형, 자전거 이동 영향도를 규칙 기반으로 정규화합니다.
4. 정규화된 이벤트를 `normalized_events`에 저장합니다.
5. KST 기준 수집 당일에 진행 중이거나 시작되는 이벤트만 발송 후보로 표시합니다.
6. OpenAI 또는 fallback 로직으로 한국어 알림 메시지를 생성합니다.
7. Telegram 비공개 채널로 메시지를 발송합니다.
8. 발송 성공, 실패, 스킵 결과를 `publish_attempts`에 기록합니다.

이벤트가 없을 때도 배치 작동 여부를 확인할 수 있도록 날짜와 시간이 포함된 no-event 메시지를 생성합니다.

같은 공지가 여러 날 반복 관찰되면 최신 수집 run으로 raw/normalized row를 갱신합니다. 메시지 후보 선정은 `publish_candidate=True`를 최종 기준으로 사용합니다. 날짜 정규화는 공지 본문이나 제목에서 명시적 기간을 찾으면 게시일보다 우선하며, `2026-11-10 ~ 2026-12-31` 및 `'26. 11. 10.(화) ~ '26. 12. 31.(목)` 형식을 처리합니다. KST 기준 수집일이 해당 기간 안에 있는지 확인한 뒤 발송 후보로 표시합니다.

아라뱃길 공지에서 상세 파싱된 교량/수로/전망대 구간명은 정규화된 location에 보존합니다. 원문에 구간 정보가 있어도 구조화된 location 추출에 실패한 경우에는 `구간 확인 필요`로 표시하며, 원문 제목과 링크는 메시지에 유지합니다.

예시:

```text
2026-07-07 07:30 기준 오늘 자전거 주의 이벤트가 없습니다.
```

## 2. 기대되는 효과

- 라이딩 당일 확인해야 할 정보를 한 곳에서 받을 수 있습니다.
- 자전거 이동에 직접 관련된 이벤트만 추려 알림 피로도를 줄입니다.
- 중복 발송 방지와 발송 이력 기록으로 운영 상태를 추적할 수 있습니다.
- 공공 정보원 장애와 실제 no-event 상황을 DB/CLI 로그에서 구분할 수 있습니다.
- Cloudflare Cron, GitHub Actions, Supabase, Telegram을 조합해 낮은 운영 비용으로 자동화할 수 있습니다.

## 3. 기술 스택

### 언어와 런타임

- Python 3.12+
- JavaScript for Cloudflare Worker

### 주요 Python 라이브러리

- Requests: 공공 사이트 HTTP 요청
- BeautifulSoup4: HTML 파싱
- SQLAlchemy 2.x: ORM과 세션 관리
- Alembic: DB 마이그레이션
- Psycopg 3: PostgreSQL 연결
- Python Dotenv: 로컬 `.env` 로딩
- OpenAI Python SDK: 알림 메시지 생성
- Pytest: 테스트
- Ruff: 린트
- Black: 포맷 검사
- Mypy: 타입 검사

### 데이터베이스

- Supabase PostgreSQL
- 연결 방식: Supabase Transaction Pooler
- DB 작성 방식:
  - SQLAlchemy ORM 모델로 schema 정의
  - Alembic migration으로 실제 DB 반영
  - `SUPABASE_DATABASE_URL` 환경 변수로 연결
  - Supabase pooler 호환을 위해 psycopg prepared statement를 비활성화

주요 테이블:

- `run_logs`: 배치 실행 이력
- `raw_events`: 수집된 원문 이벤트
- `normalized_events`: 정규화된 이벤트
- `publish_attempts`: Telegram 발송 시도 이력

### 자동화와 외부 서비스

- GitHub Actions native schedule: 매일 02:00 KST 운영 트리거
- GitHub Actions: 수집, 정규화, 메시지 생성, 발송 배치 실행
- Supabase: 실행 로그와 이벤트 저장
- OpenAI API: 사용자용 알림 문장 생성
- Telegram Bot API: 비공개 채널 발송

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
python -m compileall -q src tests
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

## 5. 운영 상태

현재 운영 스케줄:

```text
GitHub Actions schedule: 0 17 * * *
```

Production scheduling is owned by GitHub Actions native `schedule`.
Cloudflare Worker cron is disabled and kept only for diagnostics.

GitHub Actions cron은 UTC 기준입니다. 따라서 `0 17 * * *`는 한국 시간 기준 매일 02:00 실행입니다.

Cloudflare 백업 cron은 현재 비활성 상태입니다. 재활성화 시 로컬 설정의 `15 17 * * *`를 사용해 02:15 KST에 실행하도록 맞춰 두었습니다.

Cloudflare Worker는 GitHub Actions `Manual Batch` workflow를 `workflow_dispatch`로 호출합니다. 운영 호출은 실제 발송 모드입니다.

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

수동 실행은 안전 기본값을 사용합니다.

```env
dry_run=true
enable_telegram_publish=false
force_fallback=false
apply_migrations=false
```

DB 마이그레이션은 운영 배치와 분리되어 있습니다. 필요한 경우에만 수동 workflow 실행에서 `apply_migrations=true`를 선택합니다.

최근 운영 확인:

- 2026-07-20 07:30 KST 자연 실행에서 Ara Waterway 공지 `1217`이 `MESSAGE_EVENT_COUNT=1`, `MESSAGE_CONTEXT=event_alert`, `TELEGRAM_STATUS=success`로 발행되었습니다.
- 같은 source live smoke에서 후보 18건, source failure 0건, publish 후보 1건이 확인되었고, publish 후보는 공지 `1217`과 일치했습니다.
- 이후 정규화 로직은 Ara Waterway detail의 명시적 차단구간을 `location_name`으로 보존하도록 개선되었습니다.
- 2026-11-16 공지 `1234`의 본문에는 통행 차단 기간이 2026-11-10~2026-12-31로 기재되어 있었지만, 기존 파서가 게시일 2026-11-06을 이벤트 시작일로 사용해 no-event로 잘못 판단했습니다.
- 날짜 파서를 수정해 2자리 연도와 요일 표기가 포함된 기간을 인식하고, 명시적 기간을 단일 게시일보다 우선하도록 했습니다. 실제 공지 fixture 회귀 테스트와 DB 원문 재생에서 11월 16일 후보 포함 및 기간 종료 후 제외를 확인했습니다. 전체 109개 테스트와 Ruff, Mypy, Black, compileall 검사를 통과했습니다.

## 6. 환경 변수와 비밀값

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

실제 Telegram 발송이 필요한 경우에만 다음 조합을 사용합니다.

```env
ENABLE_TELEGRAM_PUBLISH=true
DRY_RUN=false
```

## 7. 기타

- 최신 운영 상태는 `project-memory/STATE.md`를 먼저 확인합니다.
- 현재 구조와 주요 파일 위치는 `project-memory/REPOSITORY_MAP.md`를 확인합니다.
- 중요한 운영 결정은 `project-memory/DECISIONS.md`에 기록합니다.
- 미해결 이슈는 `project-memory/OPEN_ISSUES.md`에 기록합니다.
- 장애, 반복 실수, 운영상 재발 방지 교훈은 `project-memory/INCIDENTS.md`에 기록합니다.
- 상세 handoff는 `docs/handoff-current-status.md`를 참고합니다.
- 오래된 sprint 문서는 `docs/archive/sprints/`에 보관합니다. 현재 운영 상태와 다를 수 있으므로 project memory를 우선합니다.
