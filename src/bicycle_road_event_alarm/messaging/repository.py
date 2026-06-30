from __future__ import annotations

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.db.models import NormalizedEvent, RawEvent
from bicycle_road_event_alarm.messaging.message_input import MessageEvent, message_event_from_model


# 발송 후보 조회: 유효하고 publish_candidate인 normalized_events만 메시지 입력으로 변환합니다.
def load_publishable_message_events(session: Session) -> list[MessageEvent]:
    rows = session.execute(_publishable_events_statement()).all()
    return [
        message_event_from_model(normalized_event, source_url=source_url)
        for normalized_event, source_url in rows
    ]


# 조회문 구성: Telegram 발송 중복 제외는 Sprint 6 publish_attempts 구현에서 추가합니다.
def _publishable_events_statement() -> Select[tuple[NormalizedEvent, str]]:
    return (
        select(NormalizedEvent, RawEvent.source_url)
        .join(RawEvent, RawEvent.id == NormalizedEvent.raw_event_id)
        .where(NormalizedEvent.publish_candidate.is_(True))
        .where(NormalizedEvent.validation_status == "valid")
        .where(NormalizedEvent.cyclist_impact_level.in_(("low", "medium", "high")))
        .order_by(NormalizedEvent.start_datetime.asc())
    )
