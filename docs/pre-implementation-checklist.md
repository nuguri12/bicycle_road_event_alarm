# Pre-Implementation Checklist

## 목적

이 문서는 Sprint 0부터 Sprint 9까지 승인된 문서의 `[사용자 입력 필요]` 항목과 Remaining Risks를 구현 전 관점에서 정리합니다.

모든 항목을 지금 확정할 필요는 없습니다. 아래 분류에 따라 실제 구현을 시작하기 전에 반드시 필요한 항목과 운영 전까지 확정해도 되는 항목을 구분합니다.

## 승인 상태

- [x] Sprint 0 Planning 승인
- [x] Sprint 1 Architecture 승인
- [x] Sprint 2 Database 승인
- [x] Sprint 3 Crawler 승인
- [x] Sprint 4 Normalization 승인
- [x] Sprint 5 AI Generation 승인
- [x] Sprint 6 Telegram Integration 승인
- [x] Sprint 7 Scheduler 승인
- [x] Sprint 8 Testing 승인
- [x] Sprint 9 Deployment and Operation 승인

## 구현 진입 기준

구현을 시작하려면 최소한 아래 항목이 확정되어야 합니다.

- [x] Python 패키지 이름: 기본값 `bicycle_road_event_alarm`
- [x] 첫 번째 크롤링 출처: 기본 권장 `서울경찰청 교통정보센터`
- [x] Supabase 사용 여부: 기본값 사용
- [x] Telegram Channel 사용 여부: 기본값 사용
- [x] OpenAI API 사용 여부: 기본값 사용
- [x] 실제 비밀값은 코드와 문서가 아니라 `.env` 또는 GitHub Actions Secrets에만 입력
- [x] live 외부 호출 테스트는 기본 CI에서 제외
- [x] 구현 중 코드 기능 블록에는 한글 주석 작성

## 필수 입력

구현 중 설정 검증, API 클라이언트, 배포 준비에 직접 필요한 값입니다.

### Telegram

- [x] Telegram Bot Token 발급 여부
- [x] Telegram Channel ID 또는 채널 사용자명
- [x] 테스트 Channel을 별도로 만들지 여부
- [x] Bot을 Channel 관리자로 추가할 운영자

### Supabase

- [x] Supabase 프로젝트 사용 확정
- [x] Supabase PostgreSQL 연결 문자열 준비 방식
- [x] UUID 생성 확장 사용 가능 여부
- [x] 운영 DB 마이그레이션을 수동 승인으로 진행할지 여부

### OpenAI

- [x] OpenAI API Key 사용 가능 여부
- [x] 월간 OpenAI 비용 상한
- [x] 구현 시점에 사용할 모델 선택 기준

### Scheduler

- [x] 기본 정기 실행 요일과 시간
- [x] GitHub Actions 수동 실행 권한을 가진 사용자
- [x] 운영 Secret 설정 담당자

## 기본값으로 진행 가능

사용자가 별도로 바꾸지 않으면 아래 기본값으로 구현해도 됩니다.

- [x] FastAPI는 MVP에서 보류
- [x] 상시 서버 없이 GitHub Actions 배치 사용
- [x] 기본 수집 범위는 다음 14일
- [x] 크롤러 timeout은 10초
- [x] 크롤러 최대 재시도는 2회
- [x] Telegram 발행 최대 재시도는 2회
- [x] AI 실패 시 재시도 없이 fallback 메시지 생성
- [x] 메시지 최대 이벤트 수는 5개
- [x] 최종 메시지 최대 길이는 600자
- [x] `needs_review`, `invalid`, `unknown`, `none` 이벤트는 발행 제외
- [x] 빈 이벤트 목록은 기본적으로 Telegram 발행하지 않음
- [x] `ENABLE_TELEGRAM_PUBLISH` 기본값은 false
- [x] 테스트 디렉터리는 `tests/unit`, `tests/integration`, `tests/fixtures`로 분리
- [x] live crawler, live AI, live Telegram 테스트는 수동 marker로 분리
- [x] 전체 line coverage 목표는 70%

## 구현 중 확정할 정책

코드를 작성하면서 문서 기본값을 기준으로 결정할 수 있습니다.

- [ ] `event_type` enum 값
- [ ] `cyclist_impact_level` enum 값
- [ ] `validation_status` enum 값
- [ ] `content_hash` 입력 필드
- [ ] `deterministic_duplicate_key` 입력 필드
- [ ] `message_hash` 입력 필드
- [ ] 날짜 파싱 라이브러리
- [ ] HTTP mock 라이브러리
- [ ] 시간 provider abstraction 사용 여부
- [ ] OpenAI 클라이언트 래퍼를 둘지 공식 SDK를 직접 사용할지 여부
- [ ] Telegram 호출에 Requests를 직접 쓸지 별도 클라이언트 래퍼를 둘지 여부

## 운영 전 확정

구현 시작에는 필수가 아니지만 운영 배포 전에는 필요합니다.

- [ ] 운영 Channel 이름
- [ ] 운영 Channel 전환 승인 담당자
- [ ] 첫 운영 배포 목표 날짜
- [ ] 정기 운영 확인 담당자
- [ ] 실패 알림을 받을 방식
- [ ] High 장애 대응 담당자
- [ ] 정정 공지 발행 기준
- [ ] 백업 파일 보관 위치
- [ ] 백업 수행 담당자
- [ ] 복구 승인 담당자
- [ ] Secret 회전 주기
- [ ] 의존성 업데이트 주기
- [ ] 크롤러 selector 점검 주기

## 보류 가능

MVP 구현을 막지 않으며 운영 안정화 후 결정해도 됩니다.

- [ ] Telegram 외 추가 알림 채널
- [ ] Docker 기반 로컬 실행 필수 여부
- [ ] Supabase test project 분리 여부
- [ ] downgrade 스크립트 필수 여부
- [ ] Telegram message id 저장 여부
- [ ] 수동 발행 메시지를 시스템에 기록하는 방법
- [ ] 운영 사고마다 회귀 테스트 필수 추가 정책
- [ ] MVP 이후 추가 공공 출처 확대
- [ ] 관리자 대시보드, 모바일 앱, 개인화 경로 기능

## 구현 순서 권장

문서 승인 이후 실제 구현은 아래 순서를 권장합니다.

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

## 사용자 직접 입력 표시 방식

구현 중 사용자가 직접 채워야 하는 값은 다음 형식으로 문서와 예시 파일에 표시합니다.

```text
<USER_INPUT_REQUIRED:TELEGRAM_BOT_TOKEN>
<USER_INPUT_REQUIRED:TELEGRAM_CHANNEL_ID>
<USER_INPUT_REQUIRED:SUPABASE_DATABASE_URL>
<USER_INPUT_REQUIRED:OPENAI_API_KEY>
```

실제 값은 저장소에 커밋하지 않습니다.
