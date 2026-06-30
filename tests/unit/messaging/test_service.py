from datetime import UTC, datetime

from bicycle_road_event_alarm.messaging.message_input import MessageEvent
from bicycle_road_event_alarm.messaging.service import generate_alert_message


def make_service_message_event() -> MessageEvent:
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


class FailingGenerator:
    def generate(self, events: object) -> str:
        raise RuntimeError("OpenAI failed")


class InvalidGenerator:
    def generate(self, events: object) -> str:
        return "URL이 없는 잘못된 메시지"


def test_generate_alert_message_falls_back_when_openai_fails() -> None:
    result = generate_alert_message(
        [make_service_message_event()], openai_generator=FailingGenerator()
    )

    assert result.source == "fallback"
    assert result.status == "generated"
    assert "https://example.test/notice" in result.text


def test_generate_alert_message_falls_back_when_openai_omits_required_url() -> None:
    result = generate_alert_message(
        [make_service_message_event()], openai_generator=InvalidGenerator()
    )

    assert result.source == "fallback"
    assert "https://example.test/notice" in result.text
