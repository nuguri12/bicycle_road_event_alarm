from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.db.models import RawEvent, RunLog


# 실행 로그 시작: 수집 배치 1회를 running 상태로 기록합니다.
def start_run_log(session: Session) -> RunLog:
    now = datetime.now(UTC)
    run_log = RunLog(
        id=uuid.uuid4(),
        status="running",
        started_at=now,
        finished_at=None,
        raw_event_count=0,
        normalized_event_count=0,
        published_message_count=0,
        error_summary=None,
        created_at=now,
    )
    session.add(run_log)
    return run_log


# 실행 로그 종료: 저장 결과 count와 종료 상태를 run_logs에 반영합니다.
def finish_run_log(
    run_log: RunLog,
    *,
    raw_event_count: int,
    normalized_event_count: int,
    published_message_count: int,
    status: str = "success",
    error_summary: str | None = None,
) -> None:
    run_log.status = status
    run_log.finished_at = datetime.now(UTC)
    run_log.raw_event_count = raw_event_count
    run_log.normalized_event_count = normalized_event_count
    run_log.published_message_count = published_message_count
    run_log.error_summary = error_summary


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


# 중복 저장 방지: 이미 같은 content_hash가 있으면 기존 row를 현재 수집 run의 관측값으로 갱신합니다.
def save_raw_event_candidates(
    session: Session,
    run_id: uuid.UUID,
    candidates: list[RawEventCandidate],
) -> int:
    saved_count = 0

    for candidate in candidates:
        existing = session.scalar(
            select(RawEvent).where(RawEvent.content_hash == candidate.content_hash)
        )
        if existing is not None:
            refresh_existing_raw_event(existing, run_id, candidate)
            continue

        session.add(candidate_to_raw_event(run_id, candidate))
        saved_count += 1

    return saved_count


def refresh_existing_raw_event(
    raw_event: RawEvent,
    run_id: uuid.UUID,
    candidate: RawEventCandidate,
) -> None:
    raw_event.run_id = run_id
    raw_event.source_name = candidate.source_name
    raw_event.source_url = candidate.source_url
    raw_event.raw_title = candidate.raw_title
    raw_event.raw_body = candidate.raw_body
    raw_event.raw_date_text = candidate.raw_date_text
    raw_event.raw_location_text = candidate.raw_location_text
    raw_event.fetched_at = datetime.now(UTC)
