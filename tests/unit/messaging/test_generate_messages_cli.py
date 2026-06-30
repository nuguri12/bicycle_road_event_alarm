from __future__ import annotations

from dataclasses import dataclass

import pytest

from bicycle_road_event_alarm.cli import generate_messages
from bicycle_road_event_alarm.config.settings import AppSettings
from bicycle_road_event_alarm.messaging.message_input import GeneratedMessage
from bicycle_road_event_alarm.messaging.telegram_publisher import TelegramPublishConfig


@dataclass
class FakeSessionFactory:
    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None


@dataclass
class PublishedCall:
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

    def fake_publish(
        message: str,
        *,
        config: TelegramPublishConfig,
        client: object,
    ) -> FakePublishResult:
        calls.append(
            PublishedCall(
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
        lambda _engine: FakeSessionFactory(),
    )
    monkeypatch.setattr(generate_messages, "load_publishable_message_events", lambda _session: [])
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
    monkeypatch.setattr(generate_messages, "publish_telegram_message", fake_publish)

    assert generate_messages.main() == 0

    captured = capsys.readouterr()
    assert "TELEGRAM_STATUS=skipped" in captured.out
    assert "TELEGRAM_REASON=dry_run" in captured.out
    assert calls == [PublishedCall(message="주의 구간 안내", enabled=True, dry_run=True)]
