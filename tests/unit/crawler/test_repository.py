import uuid
from datetime import UTC, datetime
from unittest.mock import Mock

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.crawler.repository import (
    candidate_to_raw_event,
    save_raw_event_candidates,
)
from bicycle_road_event_alarm.db.models import RawEvent


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


def test_save_raw_event_candidates_refreshes_existing_content_hash_for_current_run() -> None:
    old_run_id = uuid.uuid4()
    new_run_id = uuid.uuid4()
    existing = RawEvent(
        id=uuid.uuid4(),
        run_id=old_run_id,
        source_name="아라뱃길 공지",
        source_url="https://example.test/old",
        raw_title="old title",
        raw_body="old body",
        raw_date_text="2026-07-17",
        raw_location_text=None,
        content_hash="hash",
        fetched_at=datetime(2026, 7, 18, tzinfo=UTC),
        created_at=datetime(2026, 7, 18, tzinfo=UTC),
    )
    session = Mock()
    session.scalar.return_value = existing
    candidate = RawEventCandidate(
        source_name="아라뱃길 공지",
        source_url="https://example.test/current",
        raw_title="current title",
        raw_body="current body",
        raw_date_text="2026-07-19",
        raw_location_text="시천교~계양대교",
    )
    object.__setattr__(candidate, "content_hash", "hash")

    saved_count = save_raw_event_candidates(session, new_run_id, [candidate])

    assert saved_count == 0
    session.add.assert_not_called()
    assert existing.run_id == new_run_id
    assert existing.source_url == "https://example.test/current"
    assert existing.raw_title == "current title"
    assert existing.raw_body == "current body"
    assert existing.raw_date_text == "2026-07-19"
    assert existing.raw_location_text == "시천교~계양대교"
    assert existing.fetched_at > datetime(2026, 7, 18, tzinfo=UTC)


def test_save_raw_event_candidates_matches_by_source_url_when_title_changes() -> None:
    old_run_id = uuid.uuid4()
    new_run_id = uuid.uuid4()
    existing = RawEvent(
        id=uuid.uuid4(),
        run_id=old_run_id,
        source_name="아라뱃길 공지",
        source_url="https://example.test/BBSMSTR_000000000021/1217/view.do",
        raw_title="자전거도로 통행 차단 알림",
        raw_body="old body",
        raw_date_text="2026-07-17",
        raw_location_text=None,
        content_hash="old-hash",
        fetched_at=datetime(2026, 7, 18, tzinfo=UTC),
        created_at=datetime(2026, 7, 18, tzinfo=UTC),
    )
    session = Mock()
    session.scalar.return_value = existing
    candidate = RawEventCandidate(
        source_name="아라뱃길 공지",
        source_url="https://example.test/BBSMSTR_000000000021/1217/view.do",
        raw_title="[개방완료] 자전거도로 통행 차단 알림",
        raw_body="new body",
        raw_date_text="2026-07-17",
        raw_location_text="시천교~계양대교",
    )

    saved_count = save_raw_event_candidates(session, new_run_id, [candidate])

    assert saved_count == 0
    session.add.assert_not_called()
    assert existing.raw_title == "[개방완료] 자전거도로 통행 차단 알림"
    assert existing.content_hash == candidate.content_hash
    where_clause = str(session.scalar.call_args[0][0].whereclause)
    assert "source_url" in where_clause
    assert "content_hash" not in where_clause
