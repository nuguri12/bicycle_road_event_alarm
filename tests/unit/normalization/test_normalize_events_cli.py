from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest

from bicycle_road_event_alarm.cli import normalize_events
from bicycle_road_event_alarm.config.settings import AppSettings


@dataclass
class FakeScalarResult:
    rows: list[object]

    def all(self) -> list[object]:
        return self.rows


@dataclass
class FakeSessionFactory:
    committed: bool = False
    statement_text: str | None = None

    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def scalars(self, statement: object) -> FakeScalarResult:
        self.statement_text = str(statement)
        return FakeScalarResult([])

    def commit(self) -> None:
        self.committed = True


def make_settings() -> AppSettings:
    return AppSettings(
        app_env="local",
        log_level="INFO",
        enable_telegram_publish=False,
        dry_run=True,
        alert_lookahead_days=14,
        max_events_per_message=5,
        request_timeout_seconds=15,
        crawler_max_retries=2,
        supabase_url=None,
        supabase_anon_key=None,
        supabase_database_url="postgresql://example",
        telegram_bot_token=None,
        telegram_channel_id=None,
        openai_api_key=None,
    )


def test_normalize_events_cli_scopes_raw_events_to_run_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session_factory = FakeSessionFactory()
    run_id = uuid.uuid4()

    monkeypatch.setattr(normalize_events, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(normalize_events, "load_settings", make_settings)
    monkeypatch.setattr(
        normalize_events,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        normalize_events,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(normalize_events, "save_normalized_events", lambda _session, _rows: 0)

    assert normalize_events.main(["--run-id", str(run_id)]) == 0

    assert session_factory.statement_text is not None
    assert "raw_events.run_id = :run_id_1" in session_factory.statement_text
    assert session_factory.committed is True
