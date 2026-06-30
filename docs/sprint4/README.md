# Sprint 4 Normalization Documents

## 목적

Sprint 4는 크롤러가 수집한 원문 이벤트 후보를 표준 이벤트 모델로 변환하기 위한 정규화 규칙을 확정하는 단계입니다.

## 산출물

1. [Normalization Rules](./01-normalization-rules.md)
2. [Location Extraction](./02-location-extraction.md)
3. [Event Classification](./03-event-classification.md)
4. [Duplicate Rules](./04-duplicate-rules.md)
5. [Validation Rules](./05-validation-rules.md)

## 승인 조건

Sprint 4 문서가 승인되기 전에는 정규화 코드, 위치 추출 코드, 이벤트 분류 코드, 중복 규칙 구현, 정규화 테스트 fixture 생성을 시작하지 않습니다.

## 설계 범위

- Raw Event Candidate를 Normalized Event로 변환하는 결정적 규칙만 정의합니다.
- AI 기반 중복 판단과 메시지 생성은 Sprint 5에서 다룹니다.
- 모호한 정보는 임의로 확정하지 않고 검증 상태로 표현합니다.

## 사용자 입력 필요 항목

각 문서의 `[사용자 입력 필요]` 표시 항목은 Sprint 5 또는 구현 시작 전에 확정되어야 합니다.
