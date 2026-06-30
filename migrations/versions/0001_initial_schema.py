"""Create initial MVP event tables.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-06-30
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None

MVP_TABLE_NAMES = (
    "run_logs",
    "raw_events",
    "normalized_events",
    "publish_attempts",
)


# 스키마 생성: 문서화된 MVP 테이블과 제약조건을 Supabase에 적용합니다.
def upgrade() -> None:
    op.create_table(
        "run_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_event_count", sa.Integer(), nullable=False),
        sa.Column("normalized_event_count", sa.Integer(), nullable=False),
        sa.Column("published_message_count", sa.Integer(), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "raw_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_name", sa.Text(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("raw_title", sa.Text(), nullable=True),
        sa.Column("raw_body", sa.Text(), nullable=True),
        sa.Column("raw_date_text", sa.Text(), nullable=True),
        sa.Column("raw_location_text", sa.Text(), nullable=True),
        sa.Column("content_hash", sa.Text(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["run_id"], ["run_logs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_hash", name="uq_raw_events_content_hash"),
    )

    op.create_table(
        "normalized_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("raw_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("start_datetime", sa.DateTime(timezone=True), nullable=False),
        sa.Column("end_datetime", sa.DateTime(timezone=True), nullable=True),
        sa.Column("location_name", sa.Text(), nullable=False),
        sa.Column("region", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("cyclist_impact_level", sa.Text(), nullable=False),
        sa.Column("cyclist_impact_reason", sa.Text(), nullable=True),
        sa.Column("publish_candidate", sa.Boolean(), nullable=False),
        sa.Column("deterministic_duplicate_key", sa.Text(), nullable=False),
        sa.Column("validation_status", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["raw_event_id"], ["raw_events.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "deterministic_duplicate_key", name="uq_normalized_events_duplicate_key"
        ),
    )

    op.create_table(
        "publish_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("normalized_event_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("telegram_channel_id", sa.Text(), nullable=False),
        sa.Column("message_hash", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("failure_reason", sa.Text(), nullable=True),
        sa.Column("attempted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["normalized_event_id"], ["normalized_events.id"]),
        sa.ForeignKeyConstraint(["run_id"], ["run_logs.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("message_hash", name="uq_publish_attempts_message_hash"),
    )


# 스키마 롤백: 참조 관계의 역순으로 테이블을 제거합니다.
def downgrade() -> None:
    op.drop_table("publish_attempts")
    op.drop_table("normalized_events")
    op.drop_table("raw_events")
    op.drop_table("run_logs")
