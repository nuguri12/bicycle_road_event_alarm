# Sprint 6 Telegram Integration Documents

## 목적

Sprint 6는 생성된 자전거 주의 메시지를 Telegram Channel에 안전하게 발행하기 위한 연동 설계를 확정하는 단계입니다.

## 산출물

1. [Telegram Integration Design](./01-telegram-integration-design.md)
2. [Bot Flow](./02-bot-flow.md)
3. [Channel Structure](./03-channel-structure.md)
4. [Retry Policy](./04-retry-policy.md)
5. [Failure Handling](./05-failure-handling.md)
6. [Logging Strategy](./06-logging-strategy.md)

## 승인 조건

Sprint 6 문서가 승인되기 전에는 Telegram Bot API 연동 코드, Bot Token 설정, Channel 발행 코드, 발행 테스트 mock 생성을 시작하지 않습니다.

## 설계 범위

- Telegram Channel 단방향 발행만 다룹니다.
- 사용자별 DM, 구독 관리, 관리자 명령어는 MVP 범위에서 제외합니다.
- 비밀값은 문서와 코드에 저장하지 않고 GitHub Actions Secrets 또는 로컬 `.env`에서만 주입합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 7 또는 구현 시작 전에 통합 체크리스트에서 다시 정리합니다.
