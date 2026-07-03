from datetime import UTC, datetime

from bicycle_road_event_alarm.messaging.fallback_generator import generate_fallback_message
from bicycle_road_event_alarm.messaging.message_input import MessageEvent


def make_message_event(
    *,
    title: str = "잠실 자전거도로 교통통제",
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
        cyclist_impact_reason="교통통제 또는 행사 관련 표현 감지",
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


def test_generate_fallback_message_includes_generated_date_for_empty_events() -> None:
    기준시각 = datetime(2026, 7, 1, 14, 30, tzinfo=UTC)

    result = generate_fallback_message(
        [],
        generated_at=기준시각,
    )

    assert result.status == "generated"
    assert result.text == "2026-07-01 23:30 기준 이번 주말 자전거 주의 이벤트가 없습니다."
    assert result.event_count == 0


def test_generate_fallback_message_distinguishes_source_outage_from_no_event() -> None:
    result = generate_fallback_message(
        [],
        generated_at=datetime(2026, 7, 1, 14, 30, tzinfo=UTC),
        empty_reason="source_unavailable",
    )

    assert result.status == "generated"
    assert "2026-07-01" in result.text
    assert "확인하지 못했습니다" in result.text
    assert "수집 소스" in result.text
    assert "이벤트가 없습니다" not in result.text
    assert result.event_count == 0


def test_generate_fallback_message_keeps_partial_outage_quiet_for_users() -> None:
    기준시각 = datetime(2026, 7, 1, 14, 30, tzinfo=UTC)

    result = generate_fallback_message(
        [],
        generated_at=기준시각,
        empty_reason="partial_source_unavailable",
    )

    assert result.status == "generated"
    assert result.text == "2026-07-01 23:30 기준 이번 주말 자전거 주의 이벤트가 없습니다."
    assert result.event_count == 0
