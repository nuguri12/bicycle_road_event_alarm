from __future__ import annotations

import uuid
from dataclasses import dataclass
from unittest.mock import Mock

from bicycle_road_event_alarm.messaging.publish_service import publish_message_once
from bicycle_road_event_alarm.messaging.telegram_publisher import TelegramPublishConfig


@dataclass
class FakeTelegramClient:
    calls: list[str]

    def send_message(self, *, bot_token: str, channel_id: str, text: str) -> str:
        self.calls.append(text)
        return "telegram-message-1"


def test_publish_message_once_skips_when_successful_hash_already_exists() -> None:
    session = Mock()
    session.scalar.return_value = uuid.uuid4()
    client = FakeTelegramClient(calls=[])

    result = publish_message_once(
        session,
        run_id=uuid.uuid4(),
        normalized_event_id=uuid.uuid4(),
        message="주의 구간 안내",
        config=TelegramPublishConfig(
            enabled=True,
            dry_run=False,
            bot_token="bot-token",
            channel_id="@cycling_alerts",
        ),
        client=client,
    )

    assert result.status == "skipped"
    assert result.reason == "duplicate_successful_publish"
    assert client.calls == []
    session.add.assert_not_called()


def test_publish_message_once_records_attempt_when_message_is_new() -> None:
    session = Mock()
    session.scalar.return_value = None
    client = FakeTelegramClient(calls=[])
    run_id = uuid.uuid4()
    event_id = uuid.uuid4()

    result = publish_message_once(
        session,
        run_id=run_id,
        normalized_event_id=event_id,
        message="주의 구간 안내",
        config=TelegramPublishConfig(
            enabled=True,
            dry_run=False,
            bot_token="bot-token",
            channel_id="@cycling_alerts",
        ),
        client=client,
    )

    assert result.status == "success"
    assert client.calls == ["주의 구간 안내"]
    publish_attempt = session.add.call_args.args[0]
    assert publish_attempt.run_id == run_id
    assert publish_attempt.normalized_event_id == event_id
    assert publish_attempt.telegram_channel_id == "@cycling_alerts"
    assert publish_attempt.status == "success"


def test_publish_message_once_skips_empty_message_without_recording_attempt() -> None:
    session = Mock()
    client = FakeTelegramClient(calls=[])

    result = publish_message_once(
        session,
        run_id=uuid.uuid4(),
        normalized_event_id=None,
        message="   ",
        config=TelegramPublishConfig(
            enabled=True,
            dry_run=False,
            bot_token="bot-token",
            channel_id="@cycling_alerts",
        ),
        client=client,
    )

    assert result.status == "skipped"
    assert result.reason == "empty_message"
    assert client.calls == []
    session.scalar.assert_not_called()
    session.add.assert_not_called()


def test_publish_message_once_does_not_record_dry_run_attempt() -> None:
    session = Mock()
    session.scalar.return_value = None
    client = FakeTelegramClient(calls=[])

    result = publish_message_once(
        session,
        run_id=uuid.uuid4(),
        normalized_event_id=None,
        message="주의 구간 안내",
        config=TelegramPublishConfig(
            enabled=True,
            dry_run=True,
            bot_token="bot-token",
            channel_id="@cycling_alerts",
        ),
        client=client,
    )

    assert result.status == "skipped"
    assert result.reason == "dry_run"
    assert client.calls == []
    session.add.assert_not_called()
