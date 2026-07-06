# Regression Tests

## 1. 회귀 테스트 목표

회귀 테스트는 한 번 발견한 문제를 다시 만들지 않기 위한 테스트입니다.

## 2. 회귀 테스트 추가 기준

다음 상황에서는 회귀 테스트를 추가합니다.

- 크롤러 selector 변경으로 수집이 실패했습니다.
- 날짜 정규화가 잘못되었습니다.
- 장소 추출이 너무 넓거나 틀렸습니다.
- 중복 이벤트가 발행되었습니다.
- AI 응답 검증이 놓친 오류가 있었습니다.
- Telegram 발행 실패가 기록되지 않았습니다.

## 3. 회귀 테스트 저장 위치

권장 구조:

```text
tests/
  regression/
    test_crawler_regressions.py
    test_normalization_regressions.py
    test_publish_regressions.py
```

## 4. 운영 사고와 연결

운영 사고가 발생하면 다음을 남깁니다.

- 원인 요약
- 재현 fixture 또는 mock
- 실패하는 테스트
- 수정 후 통과 증거

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` regression 디렉터리 별도 운영 여부
- `[사용자 입력 필요]` 운영 사고마다 회귀 테스트 필수 추가 정책 승인 여부
