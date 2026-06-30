from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.db.models import RawEvent


# 모델 변환: 원문 후보를 raw_events 테이블에 저장 가능한 ORM 객체로 바꿉니다.
def candidate_to_raw_event(run_id: uuid.UUID, candidate: RawEventCandidate) -> RawEvent:
    now = datetime.now(UTC)
    return RawEvent(
        run_id=run_id,
        source_name=candidate.source_name,
        source_url=candidate.source_url,
        raw_title=candidate.raw_title,
        raw_body=candidate.raw_body,
        raw_date_text=candidate.raw_date_text,
        raw_location_text=candidate.raw_location_text,
        content_hash=candidate.content_hash,
        fetched_at=now,
        created_at=now,
    )


# 중복 저장 방지: 이미 같은 content_hash가 있으면 새 레코드를 추가하지 않습니다.
def save_raw_event_candidates(
    session: Session,
    run_id: uuid.UUID,
    candidates: list[RawEventCandidate],
) -> int:
    saved_count = 0

    for candidate in candidates:
        existing_id = session.scalar(
            select(RawEvent.id).where(RawEvent.content_hash == candidate.content_hash)
        )
        if existing_id is not None:
            continue

        session.add(candidate_to_raw_event(run_id, candidate))
        saved_count += 1

    return saved_count
