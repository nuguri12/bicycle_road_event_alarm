from __future__ import annotations

import uuid

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.db.models import NormalizedEvent, RawEvent, RunLog
from bicycle_road_event_alarm.messaging.message_input import MessageEvent, message_event_from_model


# 발송 후보 조회: 유효하고 publish_candidate인 normalized_events만 메시지 입력으로 변환합니다.
def load_publishable_message_events(
    session: Session,
    *,
    run_id: uuid.UUID | None = None,
) -> list[MessageEvent]:
    rows = session.execute(_publishable_events_statement(run_id=run_id)).all()
    return [
        message_event_from_model(normalized_event, source_url=source_url)
        for normalized_event, source_url in rows
    ]


def load_run_error_summary(session: Session, run_id: uuid.UUID) -> str | None:
    return session.execute(
        select(RunLog.error_summary).where(RunLog.id == run_id)
    ).scalar_one_or_none()


# 조회문 구성: run_id가 있으면 현재 배치에서 수집한 원문 이벤트만 메시지 후보로 사용합니다.
def _publishable_events_statement(
    *,
    run_id: uuid.UUID | None = None,
) -> Select[tuple[NormalizedEvent, str]]:
    statement = (
        select(NormalizedEvent, RawEvent.source_url)
        .join(RawEvent, RawEvent.id == NormalizedEvent.raw_event_id)
        .where(NormalizedEvent.publish_candidate.is_(True))
        .where(NormalizedEvent.cyclist_impact_level.in_(("low", "medium", "high")))
        .order_by(NormalizedEvent.start_datetime.asc())
    )
    if run_id is not None:
        statement = statement.where(RawEvent.run_id == run_id)
    return statement
