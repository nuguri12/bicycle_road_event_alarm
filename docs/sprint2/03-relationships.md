# Relationships

## 1. run_logs to raw_events

관계:

- `run_logs.id` 1개는 여러 `raw_events.run_id`와 연결됩니다.

의미:

- 어떤 실행에서 어떤 원문 이벤트가 수집되었는지 추적합니다.
- 특정 GitHub Actions 실행 실패나 부분 성공을 분석할 수 있습니다.

삭제 정책:

- MVP에서는 run_logs를 삭제하지 않습니다.
- 보관 기간이 지난 실행 로그 삭제 시 연결된 raw_events 삭제 여부는 Sprint 2 승인 후 확정합니다.

## 2. raw_events to normalized_events

관계:

- `raw_events.id` 1개는 0개 또는 1개의 `normalized_events.raw_event_id`와 연결됩니다.

의미:

- 원문 이벤트가 정규화에 실패할 수 있으므로 0개 관계를 허용합니다.
- 하나의 원문 이벤트는 하나의 표준 이벤트로 정규화합니다.

삭제 정책:

- 원문 추적 가능성을 위해 raw_events를 먼저 삭제하지 않습니다.

## 3. normalized_events to publish_attempts

관계:

- `normalized_events.id` 1개는 여러 `publish_attempts.normalized_event_id`와 연결될 수 있습니다.

의미:

- 발행 실패 후 재시도할 수 있습니다.
- 같은 이벤트가 이미 성공 발행되었는지 확인할 수 있습니다.

예외:

- 빈 주말 안내 메시지는 특정 이벤트와 연결되지 않을 수 있으므로 `normalized_event_id`를 nullable로 둡니다.

## 4. run_logs to publish_attempts

관계:

- `run_logs.id` 1개는 여러 `publish_attempts.run_id`와 연결됩니다.

의미:

- 실행 단위로 발행 성공, 실패, 건너뜀 결과를 집계합니다.

## 5. 무결성 규칙

- `raw_events.run_id`는 존재하는 run_logs를 참조해야 합니다.
- `normalized_events.raw_event_id`는 존재하는 raw_events를 참조해야 합니다.
- `publish_attempts.run_id`는 존재하는 run_logs를 참조해야 합니다.
- `publish_attempts.normalized_event_id`는 null이거나 존재하는 normalized_events를 참조해야 합니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 보관 기간 만료 시 원문 이벤트를 함께 삭제할지 여부
- `[사용자 입력 필요]` 빈 주말 안내 메시지 발행 이력 저장 방식
