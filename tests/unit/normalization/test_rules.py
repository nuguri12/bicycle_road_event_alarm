from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from bicycle_road_event_alarm.normalization.classifier import classify_event
from bicycle_road_event_alarm.normalization.datetime import parse_event_datetime
from bicycle_road_event_alarm.normalization.location import extract_location
from bicycle_road_event_alarm.normalization.title import normalize_title

KST = ZoneInfo("Asia/Seoul")


def test_normalize_title_collapses_whitespace() -> None:
    assert normalize_title("  2026  한강   교통통제 안내  ", None) == "2026 한강 교통통제 안내"


def test_parse_event_datetime_extracts_korean_numeric_range() -> None:
    fetched_at = datetime(2026, 6, 30, tzinfo=UTC)

    result = parse_event_datetime("2026.07.04 08:00 ~ 12:00", None, None, fetched_at)

    assert result.start == datetime(2026, 7, 4, 8, 0, tzinfo=KST)
    assert result.end == datetime(2026, 7, 4, 12, 0, tzinfo=KST)


def test_parse_event_datetime_extracts_full_date_range() -> None:
    fetched_at = datetime(2026, 6, 30, tzinfo=UTC)

    result = parse_event_datetime("2026-07-01(수) ~ 2026-07-05(일)", None, None, fetched_at)

    assert result.start == datetime(2026, 7, 1, 0, 0, tzinfo=KST)
    assert result.end == datetime(2026, 7, 5, 23, 59, tzinfo=KST)


def test_parse_event_datetime_prefers_abbreviated_body_range_to_posted_date() -> None:
    fetched_at = datetime(2026, 11, 15, 21, 29, tzinfo=UTC)

    result = parse_event_datetime(
        "2026-11-06",
        "차단기간 '26. 11. 10.(화) ~ '26. 12. 31.(목)",
        "'26년 11월 아라뱃길 자전거도로 통제 일정·구간 알림",
        fetched_at,
    )

    assert result.start == datetime(2026, 11, 10, 0, 0, tzinfo=KST)
    assert result.end == datetime(2026, 12, 31, 23, 59, tzinfo=KST)


def test_extract_location_prefers_raw_location_text() -> None:
    result = extract_location("잠실대교 남단 ~ 뚝섬한강공원", None, None)

    assert result.location_name == "잠실대교 남단 ~ 뚝섬한강공원"
    assert result.region == "서울"


def test_extract_location_preserves_ara_waterway_sections() -> None:
    location_text = (
        "시천교~계양대교 남, 북측 자전거도로; "
        "굴포천 연결수로 좌안(서측) 자전거도로; "
        "아라마루 전망대 및 아라폭포"
    )

    result = extract_location(location_text, None, None)

    assert result.location_name == location_text
    assert result.region == "경기"
    assert result.reason == "아라뱃길 구간명 감지"


def test_classify_event_detects_road_closure_high_impact() -> None:
    result = classify_event("한강 교통통제 안내", "자전거도로 교통통제 예정")

    assert result.event_type == "road_closure"
    assert result.cyclist_impact_level == "high"
    assert result.publish_candidate_impact is True
