# Duplicate Detection Strategy

## 1. 중복 방지 목표

중복 방지는 같은 이벤트가 Telegram 메시지에 반복 표시되는 것을 막기 위한 것입니다.

크롤러 단계에서는 원문 중복 후보를 줄이고, 최종 중복 판단은 정규화와 데이터베이스 단계에서 수행합니다.

## 2. 크롤러 단계 content_hash

크롤러는 `content_hash_input`을 구성할 수 있는 원문 필드를 반환합니다.

권장 입력:

- source_name
- source_url
- raw_title
- raw_date_text
- raw_location_text

해시 목적:

- 같은 출처에서 같은 게시글을 반복 수집하는 것을 줄입니다.
- 원문 URL이 동일한 경우 빠르게 중복을 확인합니다.

## 3. 정규화 이후 duplicate key

정규화 이후에는 `deterministic_duplicate_key`를 사용합니다.

권장 입력:

- 정규화된 title
- start_datetime 날짜 부분
- location_name
- region

목적:

- 같은 행사가 여러 출처에 게시되어도 하나의 이벤트로 관리합니다.

## 4. 애매한 중복

애매한 중복 예:

- 제목은 다르지만 장소와 날짜가 같은 마라톤
- 같은 축제의 여러 세부 프로그램
- 교통 통제 공지와 행사 공지가 같은 이벤트를 가리키는 경우

처리:

- MVP에서는 자동 병합하지 않고 `needs_review` 또는 별도 후보로 둡니다.
- AI 중복 판단 보조는 Sprint 5에서 설계합니다.

## 5. 발행 중복 방지

Telegram 발행 전에는 `publish_attempts`를 조회합니다.

발행 제외 조건:

- 동일 `normalized_event_id`가 이미 `success` 상태로 발행됨
- 동일 `message_hash`가 이미 `success` 상태로 발행됨

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` content_hash 입력 필드 승인 여부
- `[사용자 입력 필요]` deterministic_duplicate_key 입력 필드 승인 여부
- `[사용자 입력 필요]` 애매한 중복을 자동 병합하지 않는 정책 승인 여부
