from __future__ import annotations

from typing import Protocol

from bicycle_road_event_alarm.messaging.fallback_generator import generate_fallback_message
from bicycle_road_event_alarm.messaging.message_input import GeneratedMessage, MessageEvent


class MessageGenerator(Protocol):
    def generate(self, events: list[MessageEvent]) -> str: ...


# 메시지 생성 서비스: OpenAI 결과가 실패하거나 검증에 실패하면 fallback을 사용합니다.
def generate_alert_message(
    events: list[MessageEvent],
    *,
    openai_generator: MessageGenerator | None = None,
    empty_reason: str = "no_event",
) -> GeneratedMessage:
    if not events:
        return generate_fallback_message(events, empty_reason=empty_reason)

    if openai_generator is not None:
        try:
            message = openai_generator.generate(events)
        except Exception:
            message = ""

        if _is_valid_message(message, events):
            return GeneratedMessage(
                text=message.strip(),
                source="openai",
                status="generated",
                event_count=len(events),
            )

    return generate_fallback_message(events)


# 응답 검증: 빈 메시지와 원문 URL 누락을 막아 환각 위험을 줄입니다.
def _is_valid_message(message: str, events: list[MessageEvent]) -> bool:
    normalized_message = message.strip()
    if normalized_message == "":
        return False
    if len(normalized_message) > 600:
        return False
    return all(event.source_url in normalized_message for event in events)
