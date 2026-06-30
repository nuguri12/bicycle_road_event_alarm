# Normalized Event Storage Design

## Objective

`raw_events`에 저장된 원문 이벤트를 규칙 기반으로 정규화하고, 중복 없이 `normalized_events`에 저장하는 MVP 흐름을 구현한다.

## Required Inputs

- `RawEvent` ORM 객체
- 이벤트 제목, 본문, 원문 날짜 문자열, 원문 장소 문자열
- DB session

## Expected Outputs

- `NormalizedEventData` 값 객체
- 날짜/장소/이벤트 영향도 추출 함수
- deterministic duplicate key 생성
- 중복 key 기반 저장 함수
- CLI entrypoint

## Assumptions

- OpenAI 보조 판단은 Sprint 5 범위이며 이번 단계에서는 사용하지 않는다.
- 날짜를 찾지 못하면 `validation_status=invalid`로 처리한다.
- 장소를 찾지 못하면 `validation_status=needs_review`로 처리한다.
- `publish_candidate`는 `valid`이며 영향도가 `low`, `medium`, `high` 중 하나일 때만 true다.
- 기본 테스트는 Supabase에 접속하지 않는다.

## Components

- `normalization/title.py`: 제목 정리와 fallback
- `normalization/datetime.py`: 기본 날짜/시간 문자열 파싱
- `normalization/location.py`: 서울/경기 주요 지명 추출
- `normalization/classifier.py`: 이벤트 유형과 자전거 영향도 판단
- `normalization/normalizer.py`: `RawEvent`를 `NormalizedEventData`로 변환
- `normalization/repository.py`: 중복 key 기반 DB 저장
- `cli/normalize_events.py`: `.env`와 DB session을 연결해 정규화 실행

## Testing

- fixture raw event에서 valid normalized event를 만든다.
- 날짜가 없으면 invalid가 된다.
- 장소가 없으면 needs_review가 된다.
- 같은 duplicate key가 있으면 저장하지 않는다.
