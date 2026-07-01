from __future__ import annotations

from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from bicycle_road_event_alarm.messaging.message_input import GeneratedMessage, MessageEvent

IMPACT_ORDER = {"high": 0, "medium": 1, "low": 2}
KST = ZoneInfo("Asia/Seoul")


# fallback 메시지 생성: OpenAI 없이도 발송 가능한 결정론적 한국어 알림을 만듭니다.
def generate_fallback_message(
    events: list[MessageEvent],
    *,
    generated_at: datetime | None = None,
) -> GeneratedMessage:
    if not events:
        기준일 = _format_generated_date(generated_at)
        return GeneratedMessage(
            text=f"{기준일} 기준 이번 주말 자전거 주의 이벤트가 없습니다.",
            source="fallback",
            status="generated",
            event_count=0,
        )

    sorted_events = sorted(
        events,
        key=lambda event: (
            IMPACT_ORDER.get(event.cyclist_impact_level, 99),
            event.start_datetime,
            event.region,
            event.location_name,
        ),
    )
    lines = ["이번 주말 자전거 주의 구간", ""]

    for index, event in enumerate(sorted_events, start=1):
        lines.extend(_event_lines(index, event))

    return GeneratedMessage(
        text="\n".join(lines).strip(),
        source="fallback",
        status="generated",
        event_count=len(events),
    )


# 기준일 표시: GitHub runner가 UTC여도 운영자가 보는 한국 날짜로 기록합니다.
def _format_generated_date(generated_at: datetime | None) -> str:
    기준시각 = generated_at or datetime.now(UTC)
    if 기준시각.tzinfo is None:
        기준시각 = 기준시각.replace(tzinfo=UTC)
    return 기준시각.astimezone(KST).date().isoformat()


# 이벤트 출력: 각 이벤트를 지정된 블록으로 정리해 15초 안에 읽기 쉽게 만듭니다.
def _event_lines(index: int, event: MessageEvent) -> list[str]:
    time_text = _format_time_range(event)
    reason = event.cyclist_impact_reason or "자전거 이동 영향 가능성이 있습니다."
    return [
        f"{index}. [{event.cyclist_impact_level.upper()}] {event.location_name} - {time_text}",
        f"   {event.title}",
        f"   이유: {reason}",
        f"   원문: {event.source_url}",
        "",
    ]


# 시간 표시: 종료 시간이 있으면 범위로, 없으면 시작 시간만 표시합니다.
def _format_time_range(event: MessageEvent) -> str:
    start_text = event.start_datetime.strftime("%Y-%m-%d %H:%M")
    if event.end_datetime is None:
        return start_text
    return f"{start_text}~{event.end_datetime.strftime('%H:%M')}"
