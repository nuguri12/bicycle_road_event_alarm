import uuid
from datetime import UTC, datetime

from bicycle_road_event_alarm.db.models import RawEvent
from bicycle_road_event_alarm.normalization.normalizer import normalize_raw_event


def make_raw_event(
    *,
    raw_title: str | None = "2026 한강 자전거 행사 교통통제 안내",
    raw_date_text: str | None = "2026.07.04 08:00 ~ 12:00",
    raw_location_text: str | None = "잠실대교 남단 ~ 뚝섬한강공원",
    raw_body: str | None = "한강 자전거 행사로 인해 일부 구간 교통통제가 예정되어 있습니다.",
    fetched_at: datetime = datetime(2026, 7, 3, 22, 30, tzinfo=UTC),
) -> RawEvent:
    return RawEvent(
        id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        source_name="서울경찰청 교통정보센터",
        source_url="https://example.test/detail/1",
        raw_title=raw_title,
        raw_body=raw_body,
        raw_date_text=raw_date_text,
        raw_location_text=raw_location_text,
        content_hash="hash",
        fetched_at=fetched_at,
        created_at=datetime(2026, 6, 30, tzinfo=UTC),
    )


def test_normalize_raw_event_builds_valid_publish_candidate() -> None:
    normalized = normalize_raw_event(make_raw_event())

    assert normalized.title == "2026 한강 자전거 행사 교통통제 안내"
    assert normalized.region == "서울"
    assert normalized.event_type == "road_closure"
    assert normalized.cyclist_impact_level == "high"
    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is True
    assert normalized.deterministic_duplicate_key


def test_normalize_raw_event_rejects_non_today_event_for_publish() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_date_text="2026.07.06 08:00 ~ 12:00",
            fetched_at=datetime(2026, 7, 4, 22, 30, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_allows_active_date_range_for_today_publish() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_date_text="2026-07-01(수) ~ 2026-07-05(일)",
            fetched_at=datetime(2026, 7, 4, 22, 30, tzinfo=UTC),
        )
    )

    assert normalized.validation_status == "valid"
    assert normalized.publish_candidate is True


def test_normalize_raw_event_marks_missing_date_invalid() -> None:
    normalized = normalize_raw_event(make_raw_event(raw_date_text=None))

    assert normalized.validation_status == "invalid"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_marks_missing_location_needs_review() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title="2026 자전거 행사 교통통제 안내",
            raw_location_text=None,
            raw_body="일부 구간 교통통제가 예정되어 있습니다.",
        )
    )

    assert normalized.validation_status == "needs_review"
    assert normalized.publish_candidate is False


def test_normalize_raw_event_publishes_direct_bicycle_road_closure_without_location() -> None:
    normalized = normalize_raw_event(
        make_raw_event(
            raw_title="아라뱃길 자전거도로 통행 차단 알림",
            raw_location_text=None,
            raw_body="자전거도로 일부 구간 통행 차단 예정입니다.",
        )
    )

    assert normalized.validation_status == "needs_review"
    assert normalized.location_name == "구간 확인 필요"
    assert normalized.publish_candidate is True
