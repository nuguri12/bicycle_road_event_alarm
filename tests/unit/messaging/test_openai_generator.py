from datetime import UTC, datetime

from bicycle_road_event_alarm.messaging.message_input import MessageEvent
from bicycle_road_event_alarm.messaging.openai_generator import (
    OpenAIMessageGenerator,
    OpenAIResponsesResource,
)


def make_openai_message_event() -> MessageEvent:
    return MessageEvent(
        title="한강 자전거도로 교통통제",
        start_datetime=datetime(2026, 7, 4, 8, 0, tzinfo=UTC),
        end_datetime=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        location_name="잠실대교 남단 ~ 뚝섬한강공원",
        region="서울",
        event_type="road_closure",
        cyclist_impact_level="high",
        cyclist_impact_reason="교통통제 또는 우회 관련 표현 감지",
        source_url="https://example.test/notice",
    )


class FakeResponse:
    output_text = "OpenAI 생성 메시지\n원문: https://example.test/notice"


class FakeResponsesResource:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> FakeResponse:
        self.calls.append(kwargs)
        return FakeResponse()


class FakeOpenAIClient:
    def __init__(self) -> None:
        self.fake_responses = FakeResponsesResource()
        self.responses: OpenAIResponsesResource = self.fake_responses


def test_openai_generator_uses_responses_client() -> None:
    client = FakeOpenAIClient()
    generator = OpenAIMessageGenerator(client=client, model="test-model")

    message = generator.generate([make_openai_message_event()])

    assert "OpenAI 생성 메시지" in message
    assert client.fake_responses.calls[0]["model"] == "test-model"
    assert "https://example.test/notice" in str(client.fake_responses.calls[0]["input"])
