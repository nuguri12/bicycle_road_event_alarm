# Sprint 3 Crawler Documents

## 목적

Sprint 3는 공공 웹페이지에서 자전거 통행에 영향을 줄 수 있는 이벤트 후보를 안정적으로 수집하기 위한 크롤러 설계를 확정하는 단계입니다.

## 산출물

1. [Crawler Design](./01-crawler-design.md)
2. [Target Sources](./02-target-sources.md)
3. [Crawler Strategy](./03-crawler-strategy.md)
4. [Retry Policy](./04-retry-policy.md)
5. [Duplicate Detection Strategy](./05-duplicate-detection-strategy.md)
6. [Crawler Test Plan](./06-crawler-test-plan.md)

## 승인 조건

Sprint 3 문서가 승인되기 전에는 크롤러 코드, HTML fixture, Playwright 자동화, 실제 외부 사이트 호출 구현을 시작하지 않습니다.

## 설계 범위

- MVP에서는 공식 공공 출처만 대상으로 합니다.
- 정적 HTML은 Requests와 BeautifulSoup을 우선 사용합니다.
- JavaScript 렌더링이 필수인 출처에만 Playwright를 사용합니다.
- 크롤러는 원문 이벤트 후보를 수집하고, 정규화와 영향도 판단은 후속 모듈에 맡깁니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 4 또는 구현 시작 전에 확정되어야 합니다.
