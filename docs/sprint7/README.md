# Sprint 7 Scheduler Documents

## 목적

Sprint 7은 GitHub Actions를 사용해 주말 자전거 이벤트 알림 파이프라인을 정기 실행하기 위한 스케줄러 설계를 확정하는 단계입니다.

## 산출물

1. [GitHub Actions Workflow](./01-github-actions-workflow.md)
2. [Deployment Flow](./02-deployment-flow.md)
3. [Environment Variables](./03-environment-variables.md)
4. [Secret Management](./04-secret-management.md)
5. [Scheduler Recovery](./05-scheduler-recovery.md)

## 승인 조건

Sprint 7 문서가 승인되기 전에는 `.github/workflows` 파일, scheduler 실행 코드, Secret 설정 자동화, 배포 스크립트 구현을 시작하지 않습니다.

## 설계 범위

- GitHub Actions 기반 정기 실행과 수동 실행을 다룹니다.
- 상시 서버 운영은 MVP 범위에서 제외합니다.
- 실패 복구는 다음 실행 재처리와 수동 재실행 중심으로 설계합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 8 또는 구현 시작 전에 통합 체크리스트에서 다시 정리합니다.
