from __future__ import annotations

from dataclasses import dataclass

import pytest
import requests

from bicycle_road_event_alarm.messaging.telegram_publisher import (
    RequestsTelegramClient,
    TelegramPublishConfig,
    publish_telegram_message,
)


@dataclass
class FakeTelegramClient:
    calls: list[tuple[str, str, str]]

    def send_message(self, *, bot_token: str, channel_id: str, text: str) -> str:
        self.calls.append((bot_token, channel_id, text))
        return "telegram-message-1"


def test_publish_telegram_message_skips_when_publish_disabled() -> None:
    client = FakeTelegramClient(calls=[])
    config = TelegramPublishConfig(
        enabled=False,
        dry_run=False,
        bot_token="bot-token",
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message("주의 구간 안내", config=config, client=client)

    assert result.status == "skipped"
    assert result.reason == "telegram_publish_disabled"
    assert client.calls == []


def test_publish_telegram_message_skips_external_call_in_dry_run() -> None:
    client = FakeTelegramClient(calls=[])
    config = TelegramPublishConfig(
        enabled=True,
        dry_run=True,
        bot_token="bot-token",
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message("주의 구간 안내", config=config, client=client)

    assert result.status == "skipped"
    assert result.reason == "dry_run"
    assert client.calls == []


def test_publish_telegram_message_sends_when_enabled_and_not_dry_run() -> None:
    client = FakeTelegramClient(calls=[])
    config = TelegramPublishConfig(
        enabled=True,
        dry_run=False,
        bot_token="bot-token",
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message("주의 구간 안내", config=config, client=client)

    assert result.status == "success"
    assert result.reason is None
    assert result.telegram_message_id == "telegram-message-1"
    assert client.calls == [("bot-token", "@cycling_alerts", "주의 구간 안내")]


def test_publish_telegram_message_skips_without_call_for_empty_message() -> None:
    client = FakeTelegramClient(calls=[])
    config = TelegramPublishConfig(
        enabled=True,
        dry_run=False,
        bot_token="bot-token",
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message("   ", config=config, client=client)

    assert result.status == "skipped"
    assert result.reason == "empty_message"
    assert client.calls == []


def test_publish_telegram_message_fails_without_call_when_config_missing() -> None:
    client = FakeTelegramClient(calls=[])
    config = TelegramPublishConfig(
        enabled=True,
        dry_run=False,
        bot_token=None,
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message("주의 구간 안내", config=config, client=client)

    assert result.status == "failed"
    assert result.reason == "telegram_config_missing"
    assert client.calls == []


def test_publish_telegram_message_returns_failed_when_client_raises() -> None:
    class FailingTelegramClient:
        def send_message(self, *, bot_token: str, channel_id: str, text: str) -> str:
            raise requests.HTTPError(
                "400 Client Error for url: https://api.telegram.org/botsecret-token/sendMessage"
            )

    config = TelegramPublishConfig(
        enabled=True,
        dry_run=False,
        bot_token="secret-token",
        channel_id="@cycling_alerts",
    )

    result = publish_telegram_message(
        "주의 구간 안내",
        config=config,
        client=FailingTelegramClient(),
    )

    assert result.status == "failed"
    assert result.reason == "telegram_send_failed"
    assert result.telegram_message_id is None


def test_requests_telegram_client_posts_send_message_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    class FakeResponse:
        def raise_for_status(self) -> None:
            return None

        def json(self) -> dict[str, object]:
            return {"result": {"message_id": 123}}

    def fake_post(url: str, *, json: dict[str, str], timeout: int) -> FakeResponse:
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(
        "bicycle_road_event_alarm.messaging.telegram_publisher.requests.post",
        fake_post,
    )

    client = RequestsTelegramClient(timeout_seconds=15)
    message_id = client.send_message(
        bot_token="bot-token",
        channel_id="@cycling_alerts",
        text="주의 구간 안내",
    )

    assert message_id == "123"
    assert captured == {
        "url": "https://api.telegram.org/botbot-token/sendMessage",
        "json": {"chat_id": "@cycling_alerts", "text": "주의 구간 안내"},
        "timeout": 15,
    }
