# Sprint 8 Testing Documents

## 목적

Sprint 8은 구현 전 테스트 전략과 품질 게이트를 확정하는 단계입니다.

## 산출물

1. [Testing Strategy](./01-testing-strategy.md)
2. [Unit Tests](./02-unit-tests.md)
3. [Integration Tests](./03-integration-tests.md)
4. [Crawler Tests](./04-crawler-tests.md)
5. [Database Tests](./05-database-tests.md)
6. [AI Tests](./06-ai-tests.md)
7. [Telegram Tests](./07-telegram-tests.md)
8. [Regression Tests](./08-regression-tests.md)
9. [Failure Recovery Tests](./09-failure-recovery-tests.md)
10. [Mock Tests](./10-mock-tests.md)
11. [Coverage Goals](./11-coverage-goals.md)

## 승인 조건

Sprint 8 문서가 승인되기 전에는 pytest 테스트 파일, fixture, CI 테스트 workflow, mock 구현, coverage 설정을 시작하지 않습니다.

## 설계 범위

- Pytest 기반 테스트 전략을 정의합니다.
- 외부 API는 기본 테스트에서 mock 처리합니다.
- live crawler와 실제 Telegram 발행은 수동 marker 테스트로 분리합니다.
- 구현 전 통합 체크리스트는 Sprint 9 이후 작성합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 구현 시작 전 통합 체크리스트에서 다시 정리합니다.
