# Sprint 5 AI Generation Documents

## 목적

Sprint 5는 검증된 이벤트 목록을 자전거 이용자가 15초 안에 읽을 수 있는 Telegram 메시지로 생성하기 위한 AI 사용 정책과 메시지 생성 규칙을 확정하는 단계입니다.

## 산출물

1. [Prompt Design](./01-prompt-design.md)
2. [AI Usage Policy](./02-ai-usage-policy.md)
3. [Fallback Strategy](./03-fallback-strategy.md)
4. [Message Generation Rules](./04-message-generation-rules.md)
5. [Token Optimization Strategy](./05-token-optimization-strategy.md)

## 승인 조건

Sprint 5 문서가 승인되기 전에는 OpenAI SDK 연동, 프롬프트 코드, 메시지 생성 코드, AI 테스트 mock, Telegram 메시지 생성 구현을 시작하지 않습니다.

## 설계 범위

- AI는 검증된 이벤트를 짧고 명확한 사용자 메시지로 바꾸는 데만 사용합니다.
- 날짜, 장소, URL, 영향도 같은 구조화 필드는 코드가 제공한 값을 우선합니다.
- AI 실패 또는 불안정 응답이 있어도 결정적 fallback 메시지를 생성할 수 있어야 합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 6 또는 구현 시작 전에 확정되어야 합니다.
