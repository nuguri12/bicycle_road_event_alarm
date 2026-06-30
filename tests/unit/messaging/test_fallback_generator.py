from datetime import UTC, datetime

from bicycle_road_event_alarm.messaging.fallback_generator import generate_fallback_message
from bicycle_road_event_alarm.messaging.message_input import MessageEvent


def make_message_event(
    *,
    title: str = "한강 자전거도로 교통통제",
    impact: str = "high",
    start: datetime = datetime(2026, 7, 4, 8, 0, tzinfo=UTC),
    source_url: str = "https://example.test/notice",
) -> MessageEvent:
    return MessageEvent(
        title=title,
        start_datetime=start,
        end_datetime=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        location_name="잠실대교 남단 ~ 뚝섬한강공원",
        region="서울",
        event_type="road_closure",
        cyclist_impact_level=impact,
        cyclist_impact_reason="교통통제 또는 우회 관련 표현 감지",
        source_url=source_url,
    )


def test_generate_fallback_message_sorts_by_impact_then_datetime() -> None:
    low = make_message_event(
        title="낮은 영향 행사",
        impact="low",
        start=datetime(2026, 7, 3, 8, 0, tzinfo=UTC),
        source_url="https://example.test/low",
    )
    high = make_message_event(title="높은 영향 통제", impact="high")

    result = generate_fallback_message([low, high])

    assert result.status == "generated"
    assert result.source == "fallback"
    assert result.event_count == 2
    assert result.text.index("높은 영향 통제") < result.text.index("낮은 영향 행사")
    assert "https://example.test/notice" in result.text
    assert "https://example.test/low" in result.text


def test_generate_fallback_message_skips_empty_events() -> None:
    result = generate_fallback_message([])

    assert result.status == "skipped_empty_event_set"
    assert result.text == ""
    assert result.event_count == 0
