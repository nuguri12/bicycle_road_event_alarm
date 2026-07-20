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


# 중복 저장 방지: 같은 duplicate key의 row를 최신 정규화 결과로 갱신합니다.
def save_normalized_events(session: Session, raw_events: list[RawEvent]) -> int:
    saved_count = 0
    for raw_event in raw_events:
        normalized = normalize_raw_event(raw_event)
        existing_for_raw_event = list(
            session.scalars(
                select(NormalizedEvent).where(
                    NormalizedEvent.raw_event_id == normalized.raw_event_id
                )
            ).all()
        )
        if existing_for_raw_event:
            existing_for_raw = _preferred_existing_normalized_event(
                existing_for_raw_event,
                normalized,
            )
            update_normalized_event(existing_for_raw, normalized)
            for stale in existing_for_raw_event:
                if stale is not existing_for_raw:
                    session.delete(stale)
            continue

        existing_for_duplicate_key = session.scalar(
            select(NormalizedEvent).where(
                NormalizedEvent.deterministic_duplicate_key
                == normalized.deterministic_duplicate_key
            )
        )
        if existing_for_duplicate_key is not None:
            update_normalized_event(existing_for_duplicate_key, normalized)
            continue
        session.add(normalized_data_to_model(normalized))
        saved_count += 1
    return saved_count


def _preferred_existing_normalized_event(
    existing_events: list[NormalizedEvent],
    data: NormalizedEventData,
) -> NormalizedEvent:
    return next(
        (
            event
            for event in existing_events
            if event.deterministic_duplicate_key == data.deterministic_duplicate_key
        ),
        existing_events[0],
    )


def update_normalized_event(
    existing: NormalizedEvent,
    data: NormalizedEventData,
) -> None:
    existing.raw_event_id = data.raw_event_id
    existing.title = data.title
    existing.start_datetime = data.start_datetime
    existing.end_datetime = data.end_datetime
    existing.location_name = data.location_name
    existing.region = data.region
    existing.event_type = data.event_type
    existing.cyclist_impact_level = data.cyclist_impact_level
    existing.cyclist_impact_reason = data.cyclist_impact_reason
    existing.publish_candidate = data.publish_candidate
    existing.deterministic_duplicate_key = data.deterministic_duplicate_key
    existing.validation_status = data.validation_status
    existing.updated_at = datetime.now(UTC)
