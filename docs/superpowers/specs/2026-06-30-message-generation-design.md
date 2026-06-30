# Message Generation Design

## Objective

`normalized_events` 중 발송 후보를 한국어 자전거 주의 알림 메시지로 변환한다. OpenAI 생성기를 우선 사용할 수 있게 하되, 실패하거나 대상이 없을 때도 결정론적 fallback으로 안전하게 동작한다.

## Required Inputs

- `NormalizedEvent` ORM 객체 목록
- `.env`의 `OPENAI_API_KEY`
- 선택 OpenAI model 설정

## Expected Outputs

- 메시지 입력 DTO
- fallback 메시지 생성기
- OpenAI Responses API wrapper
- OpenAI 실패 시 fallback으로 전환하는 service
- CLI entrypoint

## Assumptions

- Telegram 발송과 `publish_attempts` 기록은 Sprint 6에서 구현한다.
- 이번 단계는 메시지 생성과 검증까지만 담당한다.
- 빈 이벤트 목록은 메시지를 발행하지 않고 `skipped_empty_event_set`으로 처리한다.
- 테스트는 OpenAI API를 실제 호출하지 않는다.

## Components

- `messaging/message_input.py`: normalized event를 메시지 입력 DTO로 변환
- `messaging/fallback_generator.py`: 정렬된 deterministic Korean message 생성
- `messaging/openai_generator.py`: OpenAI Responses API client wrapper
- `messaging/service.py`: OpenAI 우선, 실패 시 fallback orchestration
- `messaging/repository.py`: publishable normalized events 조회
- `cli/generate_messages.py`: 로컬 실행 entrypoint

## Testing

- fallback은 영향도와 날짜순으로 정렬한다.
- 빈 이벤트 목록은 skip 결과가 된다.
- OpenAI 생성기가 실패하면 fallback을 사용한다.
- OpenAI 응답이 필수 URL을 누락하면 fallback을 사용한다.
