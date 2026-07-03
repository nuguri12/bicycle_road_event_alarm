from __future__ import annotations

import uuid
from dataclasses import dataclass
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from bicycle_road_event_alarm.cli import generate_messages
from bicycle_road_event_alarm.config.settings import AppSettings
from bicycle_road_event_alarm.messaging.message_input import GeneratedMessage
from bicycle_road_event_alarm.messaging.telegram_publisher import TelegramPublishConfig


@dataclass
class FakeSessionFactory:
    committed: bool = False
    flushed: bool = False

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


@dataclass
class PublishedCall:
    run_id: uuid.UUID
    message: str
    enabled: bool
    dry_run: bool


@dataclass
class LoadedCall:
    run_id: uuid.UUID | None


@dataclass
class GenerateCall:
    empty_reason: str


@dataclass
class FakePublishResult:
    status: str
    reason: str | None
    telegram_message_id: str | None


def make_settings(
    *,
    enable_telegram_publish: bool,
    dry_run: bool,
    telegram_bot_token: str | None,
    telegram_channel_id: str | None,
    openai_api_key: str | None,
) -> AppSettings:
    return AppSettings(
        app_env="local",
        log_level="INFO",
        enable_telegram_publish=enable_telegram_publish,
        dry_run=dry_run,
        alert_lookahead_days=14,
        max_events_per_message=5,
        request_timeout_seconds=15,
        crawler_max_retries=2,
        supabase_url=None,
        supabase_anon_key=None,
        supabase_database_url="postgresql://example",
        telegram_bot_token=telegram_bot_token,
        telegram_channel_id=telegram_channel_id,
        openai_api_key=openai_api_key,
    )


def test_generate_messages_cli_prints_telegram_publish_result_and_scopes_run_id(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = make_settings(
        enable_telegram_publish=True,
        dry_run=True,
        telegram_bot_token="bot-token",
        telegram_channel_id="@cycling_alerts",
        openai_api_key=None,
    )
    calls: list[PublishedCall] = []
    load_calls: list[LoadedCall] = []
    run_id = uuid.uuid4()
    message_run_id = uuid.uuid4()
    session_factory = FakeSessionFactory()
    run_log = SimpleNamespace(id=run_id)

    def fake_load_events(_session: object, *, run_id: uuid.UUID | None = None) -> list[object]:
        load_calls.append(LoadedCall(run_id=run_id))
        return []

    def fake_publish(
        session: object,
        *,
        run_id: uuid.UUID,
        normalized_event_id: uuid.UUID | None,
        message: str,
        config: TelegramPublishConfig,
        client: object,
    ) -> FakePublishResult:
        calls.append(
            PublishedCall(
                run_id=run_id,
                message=message,
                enabled=config.enabled,
                dry_run=config.dry_run,
            )
        )
        return FakePublishResult(status="skipped", reason="dry_run", telegram_message_id=None)

    monkeypatch.setattr(generate_messages, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(generate_messages, "load_settings", lambda: settings)
    monkeypatch.setattr(
        generate_messages,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        generate_messages,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(generate_messages, "load_publishable_message_events", fake_load_events)
    monkeypatch.setattr(generate_messages, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(generate_messages, "finish_run_log", lambda _run_log, **_kwargs: None)
    monkeypatch.setattr(
        generate_messages,
        "generate_alert_message",
        lambda _events, openai_generator=None, empty_reason="no_event": GeneratedMessage(
            text="주의 구간 안내",
            source="fallback",
            status="generated",
            event_count=1,
        ),
    )
    monkeypatch.setattr(generate_messages, "load_run_error_summary", lambda _session, _run_id: None)
    monkeypatch.setattr(
        generate_messages,
        "RequestsTelegramClient",
        lambda timeout_seconds: object(),
    )
    monkeypatch.setattr(generate_messages, "publish_message_once", fake_publish)

    assert generate_messages.main(["--run-id", str(message_run_id)]) == 0

    captured = capsys.readouterr()
    assert "TELEGRAM_STATUS=skipped" in captured.out
    assert "TELEGRAM_REASON=dry_run" in captured.out
    assert calls == [
        PublishedCall(
            run_id=run_id,
            message="주의 구간 안내",
            enabled=True,
            dry_run=True,
        )
    ]
    assert load_calls == [LoadedCall(run_id=message_run_id)]
    assert session_factory.committed is True
    assert session_factory.flushed is True


def test_generate_messages_cli_force_fallback_does_not_create_openai_generator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(
        enable_telegram_publish=False,
        dry_run=True,
        telegram_bot_token=None,
        telegram_channel_id=None,
        openai_api_key="openai-key",
    )
    session_factory = FakeSessionFactory()
    run_log = SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(generate_messages, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(generate_messages, "load_settings", lambda: settings)
    monkeypatch.setattr(
        generate_messages,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        generate_messages,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(
        generate_messages,
        "load_publishable_message_events",
        lambda _session, *, run_id=None: [],
    )
    monkeypatch.setattr(generate_messages, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(generate_messages, "finish_run_log", lambda _run_log, **_kwargs: None)
    openai_generator = Mock()
    monkeypatch.setattr(generate_messages, "OpenAIMessageGenerator", openai_generator)
    monkeypatch.setattr(
        generate_messages,
        "publish_message_once",
        lambda _session, **_kwargs: FakePublishResult(
            status="skipped",
            reason="empty_message",
            telegram_message_id=None,
        ),
    )

    assert generate_messages.main(["--force-fallback"]) == 0

    openai_generator.assert_not_called()


def test_generate_messages_cli_returns_nonzero_when_real_telegram_publish_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = make_settings(
        enable_telegram_publish=True,
        dry_run=False,
        telegram_bot_token="bot-token",
        telegram_channel_id="@cycling_alerts",
        openai_api_key=None,
    )
    session_factory = FakeSessionFactory()
    run_log = SimpleNamespace(id=uuid.uuid4())

    monkeypatch.setattr(generate_messages, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(generate_messages, "load_settings", lambda: settings)
    monkeypatch.setattr(
        generate_messages,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        generate_messages,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(
        generate_messages,
        "load_publishable_message_events",
        lambda _session, *, run_id=None: [],
    )
    monkeypatch.setattr(generate_messages, "load_run_error_summary", lambda _session, _run_id: None)
    monkeypatch.setattr(generate_messages, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(generate_messages, "finish_run_log", lambda _run_log, **_kwargs: None)
    monkeypatch.setattr(
        generate_messages,
        "generate_alert_message",
        lambda _events, openai_generator=None, empty_reason="no_event": GeneratedMessage(
            text="2026-07-03 21:30 기준 이번 주말 자전거 주의 이벤트가 없습니다.",
            source="fallback",
            status="generated",
            event_count=0,
        ),
    )
    monkeypatch.setattr(
        generate_messages,
        "publish_message_once",
        lambda _session, **_kwargs: FakePublishResult(
            status="failed",
            reason="telegram_send_failed",
            telegram_message_id=None,
        ),
    )

    assert generate_messages.main(["--run-id", str(uuid.uuid4())]) == 1
    assert session_factory.committed is True


def test_generate_messages_cli_separates_source_outage_from_true_no_event(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = make_settings(
        enable_telegram_publish=False,
        dry_run=True,
        telegram_bot_token=None,
        telegram_channel_id=None,
        openai_api_key=None,
    )
    session_factory = FakeSessionFactory()
    message_run_id = uuid.uuid4()
    ingest_run_id = uuid.uuid4()
    run_log = SimpleNamespace(id=message_run_id)
    generate_calls: list[GenerateCall] = []
    finish_calls: list[dict[str, object]] = []

    def fake_generate_alert_message(
        _events: list[object],
        *,
        openai_generator: object | None = None,
        empty_reason: str = "no_event",
    ) -> GeneratedMessage:
        generate_calls.append(GenerateCall(empty_reason=empty_reason))
        return GeneratedMessage(
            text="2026-07-03 기준 수집 소스 장애로 이벤트를 확인하지 못했습니다.",
            source="fallback",
            status="generated",
            event_count=0,
        )

    def fake_finish_run_log(_run_log: object, **kwargs: object) -> None:
        finish_calls.append(kwargs)

    monkeypatch.setattr(generate_messages, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(generate_messages, "load_settings", lambda: settings)
    monkeypatch.setattr(
        generate_messages,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        generate_messages,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(
        generate_messages,
        "load_publishable_message_events",
        lambda _session, *, run_id=None: [],
    )
    monkeypatch.setattr(
        generate_messages,
        "load_run_error_summary",
        lambda _session, run_id: "source_unavailable: hangang=timeout",
    )
    monkeypatch.setattr(generate_messages, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(generate_messages, "finish_run_log", fake_finish_run_log)
    monkeypatch.setattr(generate_messages, "generate_alert_message", fake_generate_alert_message)
    monkeypatch.setattr(
        generate_messages,
        "publish_message_once",
        lambda _session, **_kwargs: FakePublishResult(
            status="skipped",
            reason="telegram_publish_disabled",
            telegram_message_id=None,
        ),
    )

    assert generate_messages.main(["--run-id", str(ingest_run_id)]) == 0

    captured = capsys.readouterr()
    assert "MESSAGE_CONTEXT=source_unavailable" in captured.out
    assert generate_calls == [GenerateCall(empty_reason="source_unavailable")]
    assert finish_calls == [
        {
            "raw_event_count": 0,
            "normalized_event_count": 0,
            "published_message_count": 0,
            "error_summary": (
                f"message_context=source_unavailable; ingest_run_id={ingest_run_id}; "
                "source_unavailable: hangang=timeout"
            ),
        }
    ]
