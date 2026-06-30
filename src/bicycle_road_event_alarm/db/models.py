from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# 공통 메타데이터: Alembic과 애플리케이션이 같은 schema 정의를 참조합니다.
class Base(DeclarativeBase):
    pass


# 공통 컬럼 헬퍼: 모든 테이블의 UUID와 생성 시각을 일관되게 정의합니다.
def uuid_primary_key() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def created_at_column() -> Mapped[datetime]:
    return mapped_column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


# 실행 로그: GitHub Actions 또는 수동 실행 1회를 추적합니다.
class RunLog(Base):
    __tablename__ = "run_logs"

    id: Mapped[uuid.UUID] = uuid_primary_key()
    status: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    raw_event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    normalized_event_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published_message_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_summary: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = created_at_column()


# 원문 이벤트: 크롤러가 수집한 가공 전 이벤트 후보를 저장합니다.
class RawEvent(Base):
    __tablename__ = "raw_events"
    __table_args__ = (UniqueConstraint("content_hash", name="uq_raw_events_content_hash"),)

    id: Mapped[uuid.UUID] = uuid_primary_key()
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("run_logs.id"), nullable=False
    )
    source_name: Mapped[str] = mapped_column(Text, nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    raw_title: Mapped[str | None] = mapped_column(Text)
    raw_body: Mapped[str | None] = mapped_column(Text)
    raw_date_text: Mapped[str | None] = mapped_column(Text)
    raw_location_text: Mapped[str | None] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = created_at_column()


# 정규화 이벤트: 발송 판단과 메시지 생성에 사용할 표준 이벤트입니다.
class NormalizedEvent(Base):
    __tablename__ = "normalized_events"
    __table_args__ = (
        UniqueConstraint("deterministic_duplicate_key", name="uq_normalized_events_duplicate_key"),
    )

    id: Mapped[uuid.UUID] = uuid_primary_key()
    raw_event_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("raw_events.id"), nullable=False
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    start_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_datetime: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    location_name: Mapped[str] = mapped_column(Text, nullable=False)
    region: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    cyclist_impact_level: Mapped[str] = mapped_column(Text, nullable=False)
    cyclist_impact_reason: Mapped[str | None] = mapped_column(Text)
    publish_candidate: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deterministic_duplicate_key: Mapped[str] = mapped_column(Text, nullable=False)
    validation_status: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = created_at_column()
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


# 발송 시도: Telegram 메시지 발송 결과와 실패 사유를 남깁니다.
class PublishAttempt(Base):
    __tablename__ = "publish_attempts"
    __table_args__ = (UniqueConstraint("message_hash", name="uq_publish_attempts_message_hash"),)

    id: Mapped[uuid.UUID] = uuid_primary_key()
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("run_logs.id"), nullable=False
    )
    normalized_event_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("normalized_events.id")
    )
    telegram_channel_id: Mapped[str] = mapped_column(Text, nullable=False)
    message_hash: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    failure_reason: Mapped[str | None] = mapped_column(Text)
    attempted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = created_at_column()
