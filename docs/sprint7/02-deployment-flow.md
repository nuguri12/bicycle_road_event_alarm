# Deployment Flow

## 1. 배포 목표

MVP 배포는 별도 서버 배포가 아니라 GitHub 저장소와 Actions 설정을 운영 가능한 상태로 만드는 것입니다.

## 2. 배포 단위

배포 대상:

- Python 패키지 코드
- GitHub Actions workflow
- GitHub Actions Secrets
- Supabase 연결 설정
- Telegram Channel 설정

배포 제외:

- 상시 서버
- 웹 프론트엔드
- 모바일 앱
- 관리자 대시보드

## 3. 기본 배포 흐름

1. main 브랜치에 승인된 코드를 병합합니다.
2. GitHub Actions Secrets를 설정합니다.
3. Supabase 마이그레이션을 적용합니다.
4. 테스트 Channel로 수동 workflow를 실행합니다.
5. 로그와 publish_attempts를 확인합니다.
6. 운영 Channel Secret으로 전환합니다.
7. 정기 schedule을 활성화합니다.

## 4. 환경 분리

권장 환경:

- local: 개발자 로컬 `.env`
- test: 테스트 Telegram Channel과 테스트 Supabase
- production: 운영 Telegram Channel과 운영 Supabase

MVP에서는 test와 production Supabase를 분리하는 것을 권장하지만, 비용상 하나의 Supabase 프로젝트를 사용할 수도 있습니다.

## 5. Rollback 기준

Rollback이 필요한 경우:

- 반복 발행 실패
- 잘못된 Channel 발행
- 대량 중복 발행 위험
- 데이터베이스 마이그레이션 문제

Rollback 방법:

- schedule 비활성화
- 운영 Secret 제거 또는 테스트 Channel로 변경
- 이전 정상 commit으로 되돌린 뒤 수동 실행

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` test와 production 환경을 분리할지 여부
- `[사용자 입력 필요]` 운영 Channel 전환 승인 담당자
- `[사용자 입력 필요]` schedule 비활성화 권한 담당자
