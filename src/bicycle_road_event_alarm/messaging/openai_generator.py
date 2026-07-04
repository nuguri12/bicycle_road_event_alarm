from __future__ import annotations

import json
from typing import Protocol

from bicycle_road_event_alarm.messaging.message_input import MessageEvent


class OpenAIResponse(Protocol):
    output_text: str


class OpenAIResponsesResource(Protocol):
    def create(self, **kwargs: object) -> OpenAIResponse: ...


class OpenAIClient(Protocol):
    @property
    def responses(self) -> OpenAIResponsesResource: ...


SYSTEM_INSTRUCTIONS = (
    "You write concise Korean same-day cycling alerts. "
    "Use only the structured event data provided. "
    "Do not invent dates, locations, routes, or URLs. "
    "Do not provide personalized route planning. "
    "Keep the final message readable within 15 seconds."
)


# OpenAI 메시지 생성기: Responses API 호출을 작은 wrapper로 격리합니다.
class OpenAIMessageGenerator:
    def __init__(self, *, client: OpenAIClient, model: str) -> None:
        self._client = client
        self._model = model

    def generate(self, events: list[MessageEvent]) -> str:
        response = self._client.responses.create(
            model=self._model,
            input=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": _build_user_prompt(events)},
            ],
        )
        return response.output_text.strip()


# 프롬프트 구성: raw HTML이나 비밀값 없이 구조화된 이벤트 데이터만 전달합니다.
def _build_user_prompt(events: list[MessageEvent]) -> str:
    events_json = json.dumps(
        [
            {
                "title": event.title,
                "start_datetime": event.start_datetime.isoformat(),
                "end_datetime": (
                    event.end_datetime.isoformat() if event.end_datetime is not None else None
                ),
                "location_name": event.location_name,
                "region": event.region,
                "event_type": event.event_type,
                "cyclist_impact_level": event.cyclist_impact_level,
                "cyclist_impact_reason": event.cyclist_impact_reason,
                "source_url": event.source_url,
            }
            for event in events
        ],
        ensure_ascii=False,
    )
    return (
        "다음 이벤트 목록을 자전거 이용자용 Telegram 공지로 요약해줘.\n"
        "규칙:\n"
        "- 한국어로 작성\n"
        "- 각 이벤트는 두 줄 이내로 작성\n"
        "- 위험한 이벤트부터 정렬\n"
        "- 날짜, 장소, 이유, 원문 URL 포함\n"
        "- 입력에 없는 정보는 추측하지 않기\n"
        "- 전체 메시지는 600자 이내\n\n"
        f"이벤트:\n{events_json}"
    )
