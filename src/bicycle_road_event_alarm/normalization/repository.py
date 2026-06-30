from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.db.models import NormalizedEvent, RawEvent
from bicycle_road_event_alarm.normalization.normalizer import (
    NormalizedEventData,
    normalize_raw_event,
)


# 모델 변환: 정규화 데이터 객체를 normalized_events ORM 모델로 바꿉니다.
def normalized_data_to_model(data: NormalizedEventData) -> NormalizedEvent:
    now = datetime.now(UTC)
    return NormalizedEvent(
        raw_event_id=data.raw_event_id,
        title=data.title,
        start_datetime=data.start_datetime,
        end_datetime=data.end_datetime,
        location_name=data.location_name,
        region=data.region,
        event_type=data.event_type,
        cyclist_impact_level=data.cyclist_impact_level,
        cyclist_impact_reason=data.cyclist_impact_reason,
        publish_candidate=data.publish_candidate,
        deterministic_duplicate_key=data.deterministic_duplicate_key,
        validation_status=data.validation_status,
        created_at=now,
        updated_at=now,
    )


# 중복 저장 방지: deterministic_duplicate_key가 이미 있으면 저장하지 않습니다.
def save_normalized_events(session: Session, raw_events: list[RawEvent]) -> int:
    saved_count = 0
    for raw_event in raw_events:
        normalized = normalize_raw_event(raw_event)
        existing_id = session.scalar(
            select(NormalizedEvent.id).where(
                NormalizedEvent.deterministic_duplicate_key
                == normalized.deterministic_duplicate_key
            )
        )
        if existing_id is not None:
            continue
        session.add(normalized_data_to_model(normalized))
        saved_count += 1
    return saved_count
