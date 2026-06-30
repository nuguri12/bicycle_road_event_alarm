# Crawler Tests

## 1. 크롤러 테스트 목표

크롤러 테스트는 외부 사이트 구조 변경과 네트워크 실패가 수집 로직에 미치는 영향을 빠르게 발견하기 위한 것입니다.

## 2. Fixture 테스트

대상:

- 목록 HTML에서 상세 URL 추출
- 상세 HTML에서 raw_title 추출
- raw_date_text 추출
- raw_location_text 추출
- 빈 목록 처리
- selector 실패 처리

## 3. Retry 테스트

대상:

- timeout은 재시도합니다.
- HTTP 500은 재시도합니다.
- HTTP 404는 재시도하지 않습니다.
- HTTP 429는 retry_after 정책을 따릅니다.

## 4. Live 테스트

live crawler 테스트는 기본 테스트에서 제외합니다.

권장 marker:

```text
pytest -m live_crawler
```

수동 실행 조건:

- 출처 selector 변경 확인
- 운영 전 실제 접근 가능성 확인
- robots 및 이용 조건 검토 후 실행

## 5. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 첫 crawler fixture 대상 출처
- `[사용자 입력 필요]` live_crawler marker 유지 여부
- `[사용자 입력 필요]` fixture 저장 범위
