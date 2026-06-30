import uuid
from unittest.mock import Mock

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.crawler.repository import (
    candidate_to_raw_event,
    save_raw_event_candidates,
)


def test_candidate_to_raw_event_maps_required_fields() -> None:
    run_id = uuid.uuid4()
    candidate = RawEventCandidate(
        source_name="SPATIC",
        source_url="https://example.test/detail/1",
        raw_title="title",
        raw_body="body",
        raw_date_text="2026.07.04",
        raw_location_text="한강",
    )

    raw_event = candidate_to_raw_event(run_id, candidate)

    assert raw_event.run_id == run_id
    assert raw_event.source_name == "SPATIC"
    assert raw_event.content_hash == candidate.content_hash


def test_save_raw_event_candidates_skips_existing_content_hash() -> None:
    session = Mock()
    session.scalar.return_value = uuid.uuid4()
    candidate = RawEventCandidate(
        source_name="SPATIC",
        source_url="https://example.test/detail/1",
        raw_title="title",
        raw_body="body",
        raw_date_text=None,
        raw_location_text=None,
    )

    saved_count = save_raw_event_candidates(session, uuid.uuid4(), [candidate])

    assert saved_count == 0
    session.add.assert_not_called()
