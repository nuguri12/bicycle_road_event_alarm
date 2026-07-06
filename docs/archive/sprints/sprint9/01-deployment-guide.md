# Deployment Guide

## 1. 배포 목표

MVP 배포는 상시 서버 배포가 아니라 GitHub Actions, Supabase, Telegram Channel, OpenAI API 설정을 연결해 정기 실행 가능한 상태를 만드는 것입니다.

## 2. 배포 전 조건

필수 조건:

- Sprint 0부터 Sprint 9까지 승인 완료
- 구현 전 통합 체크리스트 완료
- GitHub 저장소 준비
- Supabase 프로젝트 준비
- Telegram Bot과 Channel 준비
- OpenAI API Key 준비
- 테스트 Channel 또는 dry-run 경로 준비

## 3. 배포 순서

1. main 브랜치에 승인된 구현을 병합합니다.
2. GitHub Actions Secrets를 설정합니다.
3. Supabase 마이그레이션을 test 환경에 적용합니다.
4. dry-run workflow를 실행합니다.
5. 테스트 Channel 발행을 확인합니다.
6. 운영 Secrets를 설정합니다.
7. 운영 Channel 발행을 1회 수동 검증합니다.
8. schedule을 활성화합니다.
9. 첫 정기 실행 결과를 확인합니다.

## 4. 배포 중단 조건

다음 경우 배포를 중단합니다.

- 필수 Secret 누락
- 테스트 Channel 발행 실패
- 마이그레이션 실패
- 중복 발행 방지 테스트 실패
- 운영 Channel ID가 확인되지 않음

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 운영 배포 승인 담당자
- `[사용자 입력 필요]` 첫 운영 배포 목표 날짜
- `[사용자 입력 필요]` 테스트 Channel 검증을 필수로 할지 여부
