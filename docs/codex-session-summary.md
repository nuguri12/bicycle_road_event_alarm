# Codex Session Summary

## 목적

이 문서는 IDE 안에서 진행한 Codex 대화와 결정 사항을 다른 로컬 환경이나 GitHub에서 빠르게 확인할 수 있도록 요약한 기록입니다.

## 프로젝트

- Repository: `nuguri12/bicycle_road_event_alarm`
- 목적: 주말 자전거 라이딩 전 서울/경기 지역의 행사, 통제, 공원 이벤트 등으로 인한 주의 구간을 자동 수집하고 Telegram Channel에 짧게 알리는 서비스
- 개발 방식: Documentation Driven Development
- 구현 원칙: Sprint 0부터 Sprint 9까지 문서 승인 후 구현 시작

## 진행 요약

### 1. Sprint 문서화 완료

첨부 프롬프트의 DDD 절차에 따라 Sprint 0부터 Sprint 9까지 문서화했습니다.

- Sprint 0: Planning
- Sprint 1: Architecture
- Sprint 2: Database
- Sprint 3: Crawler
- Sprint 4: Normalization
- Sprint 5: AI Generation
- Sprint 6: Telegram Integration
- Sprint 7: Scheduler
- Sprint 8: Testing
- Sprint 9: Deployment and Operation

각 Sprint에는 `README.md`, 세부 설계 문서, `APPROVAL.md`가 포함되어 있습니다.

### 2. 모든 Sprint 승인 완료

사용자가 Sprint 0부터 Sprint 9까지 순차적으로 승인했습니다.

승인 파일 위치:

```text
docs/sprint0/APPROVAL.md
docs/sprint1/APPROVAL.md
docs/sprint2/APPROVAL.md
docs/sprint3/APPROVAL.md
docs/sprint4/APPROVAL.md
docs/sprint5/APPROVAL.md
docs/sprint6/APPROVAL.md
docs/sprint7/APPROVAL.md
docs/sprint8/APPROVAL.md
docs/sprint9/APPROVAL.md
```

### 3. 구현 전 통합 체크리스트 작성

Sprint별 Remaining Risks와 `[사용자 입력 필요]` 항목은 구현 직전에 한 번에 정리하기로 했고, 최종적으로 다음 문서에 정리했습니다.

```text
docs/pre-implementation-checklist.md
```

이 문서는 항목을 다음 범주로 나눕니다.

- 구현 진입 기준
- 필수 입력
- 기본값으로 진행 가능
- 구현 중 확정할 정책
- 운영 전 확정
- 보류 가능

## 주요 아키텍처 결정

- MVP는 상시 서버 없이 GitHub Actions 배치로 실행합니다.
- FastAPI는 MVP에서 보류합니다.
- 데이터베이스는 Supabase PostgreSQL을 사용합니다.
- ORM은 SQLAlchemy, migration은 Alembic을 사용합니다.
- 크롤러는 Requests와 BeautifulSoup을 우선 사용합니다.
- Playwright는 JavaScript 렌더링이 필수인 출처에만 제한적으로 사용합니다.
- AI는 요약, 영향도 설명, 애매한 중복 판단 보조처럼 추론이 필요한 곳에만 사용합니다.
- Telegram은 Channel 단방향 발행만 다룹니다.
- 웹 프론트엔드, 모바일 앱, 사용자 계정, 개인화 경로, 결제, 관리자 대시보드는 MVP 범위에서 제외합니다.

## 기본 정책

구현 시 별도 변경이 없으면 다음 기본값을 따릅니다.

- 기본 수집 범위: 다음 14일
- 크롤러 timeout: 10초
- 크롤러 최대 재시도: 2회
- Telegram 발행 최대 재시도: 2회
- AI 실패 시 재시도 없이 fallback 메시지 생성
- 메시지 최대 이벤트 수: 5개
- 최종 메시지 최대 길이: 600자
- `needs_review`, `invalid`, `unknown`, `none` 이벤트는 발행 제외
- 빈 이벤트 목록은 기본적으로 Telegram 발행하지 않음
- `ENABLE_TELEGRAM_PUBLISH` 기본값은 false
- live crawler, live AI, live Telegram 테스트는 기본 CI에서 제외
- 코드 기능 블록에는 한글 주석 작성

## 구현 전 필수 입력

실제 값은 repository에 커밋하지 않습니다. 로컬에서는 `.env`, GitHub Actions에서는 Secrets에만 입력해야 합니다.

```text
<USER_INPUT_REQUIRED:TELEGRAM_BOT_TOKEN>
<USER_INPUT_REQUIRED:TELEGRAM_CHANNEL_ID>
<USER_INPUT_REQUIRED:SUPABASE_DATABASE_URL>
<USER_INPUT_REQUIRED:OPENAI_API_KEY>
```

추가로 구현 전 확인할 항목:

- 첫 번째 크롤링 출처: 기본 권장 `서울경찰청 교통정보센터`
- Supabase 프로젝트 사용 확정
- Telegram Channel 사용 확정
- OpenAI API 사용 확정
- GitHub Actions 정기 실행 요일과 시간
- 수동 실행 권한을 가진 GitHub 사용자

## Supabase 관련 결정

사용자가 Supabase에 가입하고 새 프로젝트를 생성했습니다.

권장 사항:

- Supabase Security의 `Enable automatic RLS`는 활성화 권장
- 실제 DB connection string은 채팅이나 문서에 붙여 넣지 않음
- `SUPABASE_DATABASE_URL`은 로컬 `.env` 또는 GitHub Secrets에만 입력
- Publishable key는 초기 SQLAlchemy/Alembic 중심 MVP에서는 필수가 아닐 수 있음

## Repository 업로드 상태

DDD 문서화 산출물은 GitHub에 push되었습니다.

이전 커밋:

```text
3e141b8 docs: add DDD planning artifacts
```

포함 내용:

- Sprint 0부터 Sprint 9까지 문서화 산출물
- 각 Sprint 승인 기록
- 구현 전 통합 체크리스트
- superpowers 계획 문서

## 다음 권장 작업

1. 이 요약 문서를 repository에 커밋하고 push합니다.
2. 실제 구현 계획을 작성합니다.
3. 구현은 `docs/pre-implementation-checklist.md`의 권장 순서대로 시작합니다.

권장 구현 시작 순서:

1. 프로젝트 기본 구조와 품질 도구 설정
2. 설정 로딩과 Secret 검증
3. 데이터 모델과 migration
4. 크롤러 1개 출처 구현
5. 정규화와 분류
6. 중복 방지
7. fallback 메시지 생성
8. OpenAI 요약 연동
9. Telegram mock 발행
10. GitHub Actions dry-run
11. 테스트 Channel 발행
12. 운영 전 릴리즈 체크

## 참고 문서

- [Pre-Implementation Checklist](./pre-implementation-checklist.md)
- [Sprint 0 README](./sprint0/README.md)
- [Sprint 1 README](./sprint1/README.md)
- [Sprint 2 README](./sprint2/README.md)
- [Sprint 3 README](./sprint3/README.md)
- [Sprint 4 README](./sprint4/README.md)
- [Sprint 5 README](./sprint5/README.md)
- [Sprint 6 README](./sprint6/README.md)
- [Sprint 7 README](./sprint7/README.md)
- [Sprint 8 README](./sprint8/README.md)
- [Sprint 9 README](./sprint9/README.md)
