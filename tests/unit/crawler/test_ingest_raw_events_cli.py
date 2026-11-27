from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import SimpleNamespace

import pytest

from bicycle_road_event_alarm.cli import ingest_raw_events
from bicycle_road_event_alarm.config.settings import AppSettings
from bicycle_road_event_alarm.crawler.multi_source_ingestion import MultiSourceIngestionResult
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.db.models import RunLog


@dataclass
class FakeSessionFactory:
    committed: bool = False
    flushed: bool = False
    rolled_back: bool = False
    added: list[RunLog] = field(default_factory=list)

    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True

    def flush(self) -> None:
        self.flushed = True

    def rollback(self) -> None:
        self.rolled_back = True

    def add(self, obj: RunLog) -> None:
        self.added.append(obj)


def test_ingest_raw_events_cli_treats_all_source_failures_as_empty_ingestion(
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
    run_log = SimpleNamespace(id=uuid.uuid4(), started_at=datetime(2026, 7, 1, tzinfo=UTC))
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
        "fetch_all_source_candidates",
        lambda _http_client: MultiSourceIngestionResult(
            candidates=[],
            failures={
                "hangang_events": "timeout",
                "hangang_notices": "timeout",
                "ara_waterway_notices": "timeout",
            },
        ),
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
    assert f"RUN_ID={run_log.id}" in captured.out
    assert "RAW_EVENTS_SAVED=0" in captured.out
    assert finished_calls == [
        {
            "raw_event_count": 0,
            "normalized_event_count": 0,
            "published_message_count": 0,
            "status": "success",
            "error_summary": (
                "source_unavailable: hangang_events=timeout; "
                "hangang_notices=timeout; ara_waterway_notices=timeout"
            ),
        }
    ]
    assert session_factory.committed is True


def test_ingest_raw_events_cli_saves_candidates_when_any_source_succeeds(
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
    run_log = SimpleNamespace(id=uuid.uuid4(), started_at=datetime(2026, 7, 1, tzinfo=UTC))
    finished_calls: list[dict[str, object]] = []
    candidate = RawEventCandidate(
        source_name="한강공원 행사",
        source_url="https://hangang.seoul.go.kr/event/1",
        raw_title="title",
        raw_body="body",
        raw_date_text=None,
        raw_location_text=None,
    )

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
        "fetch_all_source_candidates",
        lambda _http_client: MultiSourceIngestionResult(
            candidates=[candidate],
            failures={"ara_waterway_notices": "timeout"},
        ),
    )
    monkeypatch.setattr(
        ingest_raw_events,
        "finish_run_log",
        lambda _run_log, **kwargs: finished_calls.append(kwargs),
    )
    monkeypatch.setattr(
        ingest_raw_events,
        "save_raw_event_candidates",
        lambda session, _run_id, candidates: len(candidates) if session.flushed else -1,
    )

    assert ingest_raw_events.main() == 0

    captured = capsys.readouterr()
    assert "INGEST_STATUS=success" in captured.out
    assert f"RUN_ID={run_log.id}" in captured.out
    assert "RAW_EVENTS_SAVED=1" in captured.out
    assert session_factory.flushed is True
    assert finished_calls == [
        {
            "raw_event_count": 1,
            "normalized_event_count": 0,
            "published_message_count": 0,
            "error_summary": "partial_source_unavailable: ara_waterway_notices=timeout",
        }
    ]


def test_ingest_raw_events_cli_records_failed_run_log_on_unhandled_error(
    monkeypatch: pytest.MonkeyPatch,
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
    run_log = SimpleNamespace(id=uuid.uuid4(), started_at=datetime(2026, 7, 1, tzinfo=UTC))
    candidate = RawEventCandidate(
        source_name="한강공원 행사",
        source_url="https://hangang.seoul.go.kr/event/1",
        raw_title="title",
        raw_body="body",
        raw_date_text=None,
        raw_location_text=None,
    )

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
        "fetch_all_source_candidates",
        lambda _http_client: MultiSourceIngestionResult(candidates=[candidate], failures={}),
    )

    def _boom(_session: object, _run_id: object, _candidates: object) -> int:
        raise RuntimeError("duplicate key value violates unique constraint")

    monkeypatch.setattr(ingest_raw_events, "save_raw_event_candidates", _boom)

    with pytest.raises(RuntimeError):
        ingest_raw_events.main()

    assert session_factory.rolled_back is True
    assert session_factory.committed is True
    assert len(session_factory.added) == 1
    failed_log = session_factory.added[0]
    assert failed_log.id == run_log.id
    assert failed_log.status == "failed"
    assert failed_log.error_summary is not None
    assert "duplicate key value" in failed_log.error_summary
