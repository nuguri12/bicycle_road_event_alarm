from typing import Any

import pytest

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.db import engine as db_engine
from bicycle_road_event_alarm.db.engine import create_engine_from_settings


def test_create_engine_from_settings_requires_database_url() -> None:
    settings = load_settings({})

    with pytest.raises(ValueError, match="SUPABASE_DATABASE_URL"):
        create_engine_from_settings(settings)


def test_create_engine_from_settings_uses_psycopg_for_plain_postgresql_url() -> None:
    settings = load_settings({"SUPABASE_DATABASE_URL": "postgresql://user:pass@localhost/db"})

    engine = create_engine_from_settings(settings)

    assert engine.url.drivername == "postgresql+psycopg"


def test_create_engine_from_settings_disables_psycopg_prepared_statements(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured_options: dict[str, Any] = {}

    def fake_create_engine(*args: Any, **kwargs: Any) -> object:
        captured_options["args"] = args
        captured_options["kwargs"] = kwargs
        return object()

    monkeypatch.setattr(db_engine, "create_engine", fake_create_engine)
    settings = load_settings({"SUPABASE_DATABASE_URL": "postgresql://user:pass@localhost/db"})

    create_engine_from_settings(settings)

    assert captured_options["kwargs"]["pool_pre_ping"] is True
    assert captured_options["kwargs"]["connect_args"] == {"prepare_threshold": None}


def test_create_engine_from_settings_rejects_bracketed_password_placeholder() -> None:
    settings = load_settings(
        {"SUPABASE_DATABASE_URL": "postgresql://postgres:[YOUR-PASSWORD]@localhost/db"}
    )

    with pytest.raises(ValueError, match="bracket"):
        create_engine_from_settings(settings)
