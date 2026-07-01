"""Allow failed publish attempts while deduplicating successful messages.

Revision ID: 0002_publish_attempt_success_index
Revises: 0001_initial_schema
Create Date: 2026-07-01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0002_publish_attempt_success_index"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint(
        "uq_publish_attempts_message_hash",
        "publish_attempts",
        type_="unique",
    )
    op.create_index(
        "uq_publish_attempts_success_message_hash",
        "publish_attempts",
        ["message_hash"],
        unique=True,
        postgresql_where=sa.text("status = 'success'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_publish_attempts_success_message_hash",
        table_name="publish_attempts",
    )
    op.create_unique_constraint(
        "uq_publish_attempts_message_hash",
        "publish_attempts",
        ["message_hash"],
    )
