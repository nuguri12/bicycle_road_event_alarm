# Fallback Strategy

## 1. fallback 목표

AI 호출이 실패해도 Telegram 메시지 발행을 완전히 멈추지 않기 위해 결정적 fallback 메시지를 생성합니다.

## 2. fallback 발생 조건

fallback을 사용합니다.

- OpenAI API timeout
- OpenAI API rate limit
- OpenAI API 인증 또는 설정 오류
- 응답이 비어 있음
- 응답이 최대 글자 수를 초과
- 응답에 입력에 없는 날짜, 장소, URL이 포함됨
- 금지된 개인화 경로 안내가 포함됨

## 3. fallback 메시지 형식

```text
이번 주말 자전거 주의 구간

1. [HIGH] 여의도 한강공원 - 2026-07-04 오전
   마라톤 행사로 혼잡 또는 통제 가능성이 있습니다.
   원문: https://example.com/notice
```

## 4. fallback 정렬 규칙

정렬 우선순위:

1. cyclist_impact_level: high, medium, low
2. start_datetime 빠른 순
3. region
4. location_name

## 5. 빈 이벤트 목록 처리

선택 가능한 정책:

- 메시지를 발행하지 않습니다.
- "이번 주말 확인된 주요 주의 구간 없음" 메시지를 발행합니다.

MVP 기본 권장:

- 발행하지 않고 로그에 `skipped_empty_event_set`을 기록합니다.

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 빈 이벤트 목록일 때 메시지를 발행할지 여부
- `[사용자 입력 필요]` fallback 메시지에도 원문 URL을 포함할지 여부
- `[사용자 입력 필요]` AI 설정 오류 발생 시 작업을 실패 처리할지 fallback 처리할지 여부
