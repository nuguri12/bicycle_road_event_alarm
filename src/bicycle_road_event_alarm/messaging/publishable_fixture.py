from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from bicycle_road_event_alarm.crawler.repository import finish_run_log, start_run_log
from bicycle_road_event_alarm.db.models import NormalizedEvent, RawEvent


@dataclass(frozen=True)
class PublishableFixtureResult:
    run_id: uuid.UUID
    raw_event_id: uuid.UUID
    normalized_event_id: uuid.UUID
    title: str


# 더미 이벤트 생성: DB/CLI 전체 흐름 검증용 publishable 이벤트 1건을 만듭니다.
def seed_publishable_fixture(session: Session) -> PublishableFixtureResult:
    fixture_id = uuid.uuid4()
    now = datetime.now(UTC)
    run_log = start_run_log(session)
    session.flush()
    raw_event_id = uuid.uuid4()
    normalized_event_id = uuid.uuid4()
    title = f"테스트 자전거 통제 이벤트 {fixture_id.hex[:8]}"

    raw_event = RawEvent(
        id=raw_event_id,
        run_id=run_log.id,
        source_name="local-fixture",
        source_url=f"https://example.test/local-fixture/{fixture_id}",
        raw_title=title,
        raw_body="한강공원 자전거도로 일부 구간에서 테스트 교통 통제가 예정되어 있습니다.",
        raw_date_text="2026.07.04 08:00 ~ 12:00",
        raw_location_text="잠실대교 남단 ~ 뚝섬한강공원",
        content_hash=f"local-fixture-{fixture_id}",
        fetched_at=now,
        created_at=now,
    )
    normalized_event = NormalizedEvent(
        id=normalized_event_id,
        raw_event_id=raw_event_id,
        title=title,
        start_datetime=datetime(2026, 7, 4, 8, 0, tzinfo=UTC),
        end_datetime=datetime(2026, 7, 4, 12, 0, tzinfo=UTC),
        location_name="잠실대교 남단 ~ 뚝섬한강공원",
        region="서울",
        event_type="traffic_control",
        cyclist_impact_level="high",
        cyclist_impact_reason="테스트 교통 통제로 자전거 이동 지연 가능성이 큽니다.",
        publish_candidate=True,
        deterministic_duplicate_key=f"local-fixture-{fixture_id}",
        validation_status="valid",
        created_at=now,
        updated_at=now,
    )

    session.add(raw_event)
    session.flush()
    session.add(normalized_event)
    finish_run_log(
        run_log,
        raw_event_count=1,
        normalized_event_count=1,
        published_message_count=0,
    )
    return PublishableFixtureResult(
        run_id=run_log.id,
        raw_event_id=raw_event_id,
        normalized_event_id=normalized_event_id,
        title=title,
    )
