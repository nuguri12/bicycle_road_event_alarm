# Mock Tests

## 1. Mock 테스트 목표

Mock 테스트는 외부 API 비용과 불안정성을 테스트에서 제거하기 위한 것입니다.

## 2. Mock 대상

- HTTP crawler client
- Supabase database repository
- OpenAI API client
- Telegram Bot API client
- GitHub Actions 환경 변수
- 현재 시간 provider

## 3. Mock 원칙

- 실제 API 응답 구조와 비슷하게 만듭니다.
- 비밀값은 포함하지 않습니다.
- 성공, 실패, timeout, rate limit을 모두 포함합니다.
- 과도하게 내부 구현에 결합하지 않습니다.

## 4. 금지 사항

- 실제 Bot Token을 fixture에 넣지 않습니다.
- 실제 OpenAI API Key를 fixture에 넣지 않습니다.
- 실제 운영 Channel ID로 live test를 실행하지 않습니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` HTTP mock 라이브러리 선호
- `[사용자 입력 필요]` 시간 provider abstraction 사용 승인 여부
