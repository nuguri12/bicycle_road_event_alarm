# AI Tests

## 1. AI 테스트 목표

AI 테스트는 실제 OpenAI API 호출 없이 프롬프트 입력, 응답 검증, fallback 전환을 검증합니다.

## 2. Mock 테스트 대상

- valid 이벤트만 AI 입력에 포함됩니다.
- invalid와 needs_review 이벤트는 제외됩니다.
- AI 응답이 비어 있으면 fallback으로 전환합니다.
- 입력에 없는 URL이 응답에 있으면 fallback으로 전환합니다.
- 최대 글자 수를 넘으면 fallback으로 전환합니다.

## 3. 실제 API 테스트

실제 OpenAI API 테스트는 기본 CI에서 제외합니다.

권장 marker:

```text
pytest -m live_ai
```

실행 조건:

- 모델 변경 검증
- 프롬프트 품질 수동 확인
- 비용 상한 확인 후 실행

## 4. 비용 보호

- live_ai는 수동 실행만 허용합니다.
- 테스트 입력 이벤트 수를 제한합니다.
- Secret이 없으면 skip합니다.

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` live_ai 테스트 생성 여부
- `[사용자 입력 필요]` AI mock 응답 fixture 저장 여부
- `[사용자 입력 필요]` 프롬프트 품질 수동 승인 절차 필요 여부
