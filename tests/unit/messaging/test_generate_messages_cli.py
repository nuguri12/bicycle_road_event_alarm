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

    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


@dataclass
class PublishedCall:
    run_id: uuid.UUID
    message: str
    enabled: bool
    dry_run: bool


@dataclass
class FakePublishResult:
    status: str
    reason: str | None
    telegram_message_id: str | None


def test_generate_messages_cli_prints_telegram_publish_result(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    settings = AppSettings(
        app_env="local",
        log_level="INFO",
        enable_telegram_publish=True,
        dry_run=True,
        alert_lookahead_days=14,
        max_events_per_message=5,
        request_timeout_seconds=15,
        crawler_max_retries=2,
        supabase_url=None,
        supabase_anon_key=None,
        supabase_database_url="postgresql://example",
        telegram_bot_token="bot-token",
        telegram_channel_id="@cycling_alerts",
        openai_api_key=None,
    )
    calls: list[PublishedCall] = []
    run_id = uuid.uuid4()
    session_factory = FakeSessionFactory()
    run_log = SimpleNamespace(id=run_id)

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
    monkeypatch.setattr(generate_messages, "load_publishable_message_events", lambda _session: [])
    monkeypatch.setattr(generate_messages, "start_run_log", lambda _session: run_log)
    monkeypatch.setattr(generate_messages, "finish_run_log", lambda _run_log, **_kwargs: None)
    monkeypatch.setattr(
        generate_messages,
        "generate_alert_message",
        lambda _events, openai_generator=None: GeneratedMessage(
            text="주의 구간 안내",
            source="fallback",
            status="generated",
            event_count=1,
        ),
    )
    monkeypatch.setattr(
        generate_messages,
        "RequestsTelegramClient",
        lambda timeout_seconds: object(),
    )
    monkeypatch.setattr(generate_messages, "publish_message_once", fake_publish)

    assert generate_messages.main([]) == 0

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
    assert session_factory.committed is True


def test_generate_messages_cli_force_fallback_does_not_create_openai_generator(
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
    monkeypatch.setattr(generate_messages, "load_publishable_message_events", lambda _session: [])
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
