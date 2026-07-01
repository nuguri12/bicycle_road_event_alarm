from __future__ import annotations

import uuid
from dataclasses import dataclass
from types import SimpleNamespace

import pytest
import requests

from bicycle_road_event_alarm.cli import ingest_raw_events
from bicycle_road_event_alarm.config.settings import AppSettings


@dataclass
class FakeSessionFactory:
    committed: bool = False

    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


def test_ingest_raw_events_cli_treats_source_timeout_as_empty_ingestion(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = AppSettings(
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
    session_factory = FakeSessionFactory()
    run_log = SimpleNamespace(id=uuid.uuid4())
    finished_calls: list[dict[str, object]] = []

    monkeypatch.setattr(ingest_raw_events, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(ingest_raw_events, "load_settings", lambda: settings)
    monkeypatch.setattr(
        ingest_raw_events,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        ingest_raw_events,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(ingest_raw_events, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(
        ingest_raw_events,
        "fetch_spatic_candidates",
        lambda _http_client: (_ for _ in ()).throw(requests.exceptions.ConnectTimeout("timeout")),
    )
    monkeypatch.setattr(
        ingest_raw_events,
        "finish_run_log",
        lambda _run_log, **kwargs: finished_calls.append(kwargs),
    )
    monkeypatch.setattr(
        ingest_raw_events,
        "save_raw_event_candidates",
        lambda _session, _run_id, _candidates: 99,
    )

    assert ingest_raw_events.main() == 0

    captured = capsys.readouterr()
    assert "INGEST_STATUS=skipped" in captured.out
    assert "INGEST_REASON=source_unavailable" in captured.out
    assert "RAW_EVENTS_SAVED=0" in captured.out
    assert finished_calls == [
        {
            "raw_event_count": 0,
            "normalized_event_count": 0,
            "published_message_count": 0,
            "status": "success",
            "error_summary": "source_unavailable: timeout",
        }
    ]
    assert session_factory.committed is True
