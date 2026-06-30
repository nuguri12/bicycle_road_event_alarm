# Data Retention Policy

## 1. 보관 정책 목표

데이터 보관은 운영 추적과 중복 방지에 필요한 기간만 유지합니다. 장기 분석이 MVP 범위 밖이므로 불필요한 장기 보관을 피합니다.

## 2. 데이터별 기본 보관 기간

| Data | Default Retention | Reason |
| --- | --- | --- |
| run_logs | 90 days | 최근 장애 분석과 실행 추적 |
| raw_events | 180 days | 원문 추적과 크롤러 회귀 분석 |
| normalized_events | 365 days | 중복 방지와 계절성 이벤트 참고 |
| publish_attempts | 365 days | 중복 발행 방지와 운영 감사 |

## 3. 삭제 정책

- 보관 기간이 지난 데이터는 별도 작업으로 삭제합니다.
- 삭제 작업은 Sprint 7 Scheduler 또는 Sprint 9 Operation 단계에서 확정합니다.
- 삭제 전 백업 필요 여부를 확인합니다.
- MVP 초기에는 자동 삭제보다 수동 검토를 우선합니다.

## 4. 개인정보 정책

MVP는 사용자 계정과 개인화 경로를 저장하지 않습니다.

주의할 수 있는 정보:

- Telegram Channel ID
- 공개 행사 URL
- 공개 행사 텍스트

비밀값과 개인 토큰은 데이터베이스에 저장하지 않습니다.

## 5. 데이터 최소화

- 원문 전체 HTML 저장은 기본 정책으로 채택하지 않습니다.
- 필요한 원문 제목, 본문 요약, 날짜 문자열, 장소 문자열만 저장합니다.
- 크롤러 디버깅에 전체 HTML이 필요하면 fixture 또는 임시 로그로 제한합니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` raw_events 보관 기간 승인 여부
- `[사용자 입력 필요]` normalized_events와 publish_attempts 365일 보관 승인 여부
- `[사용자 입력 필요]` Telegram Channel ID 저장 정책 승인 여부
