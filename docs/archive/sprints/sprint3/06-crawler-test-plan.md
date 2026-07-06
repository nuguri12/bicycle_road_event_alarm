# Crawler Test Plan

## 1. 테스트 목표

크롤러 테스트는 외부 사이트 변화와 네트워크 실패에 강한 수집 로직을 만드는 것을 목표로 합니다.

테스트는 실제 외부 사이트 호출보다 fixture와 mock을 우선합니다.

## 2. 단위 테스트

대상:

- 목록 페이지에서 상세 URL 추출
- 상세 페이지에서 제목, 날짜 문자열, 장소 문자열 추출
- 빈 목록 처리
- 필수 selector 누락 처리
- content_hash 입력 필드 생성

검증:

- fixture HTML에서 예상 Raw Event Candidate가 생성됩니다.
- selector 실패는 명시적 오류로 반환됩니다.

## 3. 통합 테스트

대상:

- 출처 어댑터 1개 전체 흐름
- HTTP client mock과 parser 연결
- retry 정책 적용 여부

검증:

- timeout 후 재시도합니다.
- 404는 재시도하지 않습니다.
- 500은 설정된 횟수만큼 재시도합니다.

## 4. Fixture 정책

- 출처별 목록 HTML fixture와 상세 HTML fixture를 분리합니다.
- fixture 파일명에는 출처 이름과 페이지 유형을 포함합니다.
- 개인정보나 비밀값은 fixture에 포함하지 않습니다.
- 전체 HTML이 과도하게 크면 필요한 DOM 조각만 저장합니다.

예상 구조:

```text
tests/
  fixtures/
    crawler/
      spatic_list.html
      spatic_detail.html
```

## 5. 회귀 테스트

HTML 구조가 바뀌면 다음 순서로 대응합니다.

1. 실패한 fixture 또는 실제 샘플을 확인합니다.
2. selector 변경 범위를 출처별 어댑터 안으로 제한합니다.
3. 실패 재현 테스트를 먼저 추가합니다.
4. selector를 수정합니다.
5. 관련 크롤러 테스트를 실행합니다.

## 6. 외부 사이트 호출 검증

실제 외부 사이트 호출은 기본 테스트에 포함하지 않습니다.

필요 시 별도 marker를 사용합니다.

예상 marker:

- `pytest -m live_crawler`

이 테스트는 수동으로만 실행합니다.

## 7. 사용자 입력 필요 항목

- `[사용자 입력 필요]` live crawler 테스트를 만들지 여부
- `[사용자 입력 필요]` 첫 fixture 대상 출처
- `[사용자 입력 필요]` fixture에 전체 HTML을 저장할지, 필요한 DOM 조각만 저장할지 여부
