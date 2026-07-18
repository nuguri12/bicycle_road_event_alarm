import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

from bicycle_road_event_alarm.db.models import NormalizedEvent, RawEvent
from bicycle_road_event_alarm.normalization.normalizer import normalize_raw_event
from bicycle_road_event_alarm.normalization.repository import (
    normalized_data_to_model,
    save_normalized_events,
)


def make_repository_raw_event() -> RawEvent:
    return RawEvent(
        id=uuid.uuid4(),
        run_id=uuid.uuid4(),
        source_name="서울경찰청 교통정보센터",
        source_url="https://example.test/detail/1",
        raw_title="2026 한강 자전거 행사 교통통제 안내",
        raw_body="한강 자전거 행사로 인해 일부 구간 교통통제가 예정되어 있습니다.",
        raw_date_text="2026.07.04 08:00 ~ 12:00",
        raw_location_text="잠실대교 남단 ~ 뚝섬한강공원",
        content_hash="hash",
        fetched_at=datetime(2026, 6, 30, tzinfo=UTC),
        created_at=datetime(2026, 6, 30, tzinfo=UTC),
    )


def test_normalized_data_to_model_maps_required_fields() -> None:
    raw_event = make_repository_raw_event()
    normalized = normalize_raw_event(raw_event)

    model = normalized_data_to_model(normalized)

    assert model.raw_event_id == raw_event.id
    assert model.title == normalized.title
    assert model.deterministic_duplicate_key == normalized.deterministic_duplicate_key


def test_save_normalized_events_updates_existing_duplicate_key() -> None:
    session = Mock()
    raw_event = make_repository_raw_event()
    normalized = normalize_raw_event(raw_event)
    existing = NormalizedEvent(
        id=uuid.uuid4(),
        raw_event_id=uuid.uuid4(),
        title="old title",
        start_datetime=datetime(2026, 1, 1, tzinfo=UTC),
        end_datetime=None,
        location_name="old location",
        region="old",
        event_type="unknown",
        cyclist_impact_level="unknown",
        cyclist_impact_reason=None,
        publish_candidate=False,
        deterministic_duplicate_key=normalized.deterministic_duplicate_key,
        validation_status="invalid",
        created_at=datetime(2026, 1, 1, tzinfo=UTC),
        updated_at=datetime(2026, 1, 1, tzinfo=UTC),
    )
    session.scalar.return_value = existing

    saved_count = save_normalized_events(session, [raw_event])

    assert saved_count == 0
    session.add.assert_not_called()
    assert existing.raw_event_id == raw_event.id
    assert existing.title == normalized.title
    assert existing.start_datetime == normalized.start_datetime
    assert existing.location_name == normalized.location_name
    assert existing.publish_candidate == normalized.publish_candidate
    assert existing.validation_status == normalized.validation_status
    assert existing.updated_at > datetime(2026, 1, 1, tzinfo=UTC)
