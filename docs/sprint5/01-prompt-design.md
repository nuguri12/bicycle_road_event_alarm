# Prompt Design

## 1. 프롬프트 목표

프롬프트는 검증된 이벤트 목록을 주말 라이딩 전용 짧은 Telegram 메시지로 변환합니다.

목표:

- 15초 안에 읽을 수 있습니다.
- 피해야 할 지역과 시간대가 먼저 보입니다.
- 불확실한 정보를 단정하지 않습니다.
- 원문에서 제공된 날짜, 장소, URL을 바꾸지 않습니다.
- 개인화 경로 안내나 지도 앱 역할을 하지 않습니다.

## 2. 입력 데이터

AI에 전달하는 이벤트는 다음 조건을 만족해야 합니다.

- validation_status가 `valid`
- publish_candidate가 true
- cyclist_impact_level이 `low`, `medium`, `high` 중 하나
- source_url이 존재

입력 필드:

- title
- start_datetime
- end_datetime
- location_name
- region
- event_type
- cyclist_impact_level
- cyclist_impact_reason
- source_url

AI에 전달하지 않는 데이터:

- raw HTML
- API Key
- Telegram Bot Token
- Supabase 연결 문자열
- 발행 이력 내부 ID

## 3. 시스템 지시문 초안

```text
You write concise Korean weekend cycling alerts.
Your only job is to tell cyclists which areas to avoid before leaving home.
Use only the structured event data provided.
Do not invent dates, locations, routes, or URLs.
Do not provide personalized route planning.
Keep the final message readable within 15 seconds.
```

## 4. 사용자 메시지 템플릿 초안

```text
다음 이벤트 목록을 자전거 이용자용 Telegram 공지로 요약해줘.

규칙:
- 한국어로 작성
- 가장 위험한 이벤트부터 정렬
- 각 이벤트는 한 줄 또는 짧은 문장으로 작성
- 피해야 할 장소, 날짜/시간, 이유를 포함
- 원문 URL은 유지
- 확실하지 않은 내용은 추측하지 말 것
- 전체 메시지는 600자 이내

이벤트:
{events_json}
```

## 5. 출력 형식

권장 형식:

```text
이번 주말 자전거 주의 구간

1. [영향도] 장소 - 날짜/시간
   이유: 짧은 설명
   원문: URL

특이사항이 적으면 한 줄 요약으로 마무리
```

## 6. 사용자 입력 필요 항목

- `[사용자 입력 필요]` 최종 메시지 최대 글자 수 600자 승인 여부
- `[사용자 입력 필요]` 메시지 톤: 경고형, 친근한 안내형, 중립 보고형 중 선택
- `[사용자 입력 필요]` 원문 URL을 모든 이벤트에 포함할지 여부
