# Technology Selection Report

## 1. 언어: Python 3.12+

선정 이유:

- 크롤링, 데이터 처리, AI API 연동, 자동화 스크립트에 적합합니다.
- Requests, BeautifulSoup, SQLAlchemy, Pydantic, Pytest 생태계가 안정적입니다.

대안:

- Node.js는 비동기 I/O에 강하지만, 이 프로젝트의 데이터 처리와 스크립트 중심 워크플로에는 Python이 더 단순합니다.

## 2. API 서버: FastAPI

선정 이유:

- API가 필요해질 경우 Pydantic 기반 타입 검증과 문서화가 쉽습니다.
- MVP에서는 외부 API 서버가 필수는 아니므로 Sprint 1에서 실제 필요 여부를 판단합니다.

결정:

- MVP 자동 실행만으로 충분하면 FastAPI 구현은 보류합니다.

## 3. 데이터베이스: Supabase PostgreSQL

선정 이유:

- PostgreSQL 기반으로 구조화 이벤트 저장에 적합합니다.
- 소규모 프로젝트에서 운영 부담이 낮습니다.
- 백업과 관리 기능을 활용할 수 있습니다.

주의:

- 비밀값은 GitHub Actions Secrets 또는 로컬 환경 변수로 관리해야 합니다.

## 4. ORM 및 Migration: SQLAlchemy, Alembic

선정 이유:

- Python에서 PostgreSQL 모델링과 마이그레이션 관리가 안정적입니다.
- 스키마 변경 이력을 명시적으로 관리할 수 있습니다.

## 5. Validation: Pydantic

선정 이유:

- 크롤링 결과, 정규화 이벤트, 설정값 검증에 적합합니다.
- 타입 힌트와 런타임 검증을 함께 제공합니다.

## 6. Crawler: Requests, BeautifulSoup, Playwright

선정 이유:

- 정적 페이지는 Requests와 BeautifulSoup으로 단순하게 처리합니다.
- JavaScript 렌더링이 필수인 출처에만 Playwright를 제한적으로 사용합니다.

비용 및 복잡도:

- Playwright는 실행 시간이 길고 GitHub Actions 설정이 복잡하므로 기본 도구로 사용하지 않습니다.

## 7. AI: OpenAI API

선정 이유:

- 자전거 이용자 관점의 요약, 영향도 추정, 애매한 중복 판단에 적합합니다.

사용 제한:

- 날짜 필터링, URL 중복 제거, 필드 검증처럼 결정 가능한 작업에는 사용하지 않습니다.

## 8. Messaging: Telegram Bot API

선정 이유:

- 소규모 그룹 공지에 적합하고 Channel 발행이 단순합니다.
- 모바일 알림 도달성이 좋습니다.

## 9. Scheduler 및 CI/CD: GitHub Actions

선정 이유:

- 별도 서버 없이 정기 실행할 수 있습니다.
- Secrets 관리와 수동 실행 workflow를 함께 제공할 수 있습니다.

주의:

- 정확한 시간 실행이 보장되지 않으므로 여유 있는 발행 시간이 필요합니다.

## 10. 품질 도구

- 테스트: Pytest
- Lint: Ruff
- Formatting: Black
- Typing: Mypy
- Container: Docker

## 11. 사용자 입력 필요 항목

- `[사용자 입력 필요]` Supabase 사용 확정 여부
- `[사용자 입력 필요]` OpenAI 모델 선호 또는 비용 기준
- `[사용자 입력 필요]` Telegram 외 추가 알림 채널 필요 여부
- `[사용자 입력 필요]` Docker 기반 로컬 실행 필요 여부
