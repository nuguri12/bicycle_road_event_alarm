from sqlalchemy import UniqueConstraint

from bicycle_road_event_alarm.db.models import Base


def test_metadata_contains_mvp_tables() -> None:
    assert set(Base.metadata.tables) == {
        "run_logs",
        "raw_events",
        "normalized_events",
        "publish_attempts",
    }


def test_raw_events_contains_required_source_columns() -> None:
    table = Base.metadata.tables["raw_events"]

    for column_name in (
        "id",
        "run_id",
        "source_name",
        "source_url",
        "content_hash",
        "fetched_at",
        "created_at",
    ):
        assert column_name in table.columns
        assert table.columns[column_name].nullable is False


def test_normalized_events_have_duplicate_key_constraint() -> None:
    table = Base.metadata.tables["normalized_events"]

    constraints = {
        constraint.name
        for constraint in table.constraints
        if isinstance(constraint, UniqueConstraint)
    }

    assert "uq_normalized_events_duplicate_key" in constraints
