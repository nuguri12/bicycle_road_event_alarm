from __future__ import annotations

import uuid
from datetime import date
from unittest.mock import Mock

from bicycle_road_event_alarm.messaging.publish_history import (
    build_message_hash,
    has_successful_publish,
    record_publish_attempt,
)
from bicycle_road_event_alarm.messaging.telegram_publisher import TelegramPublishResult


def test_build_message_hash_is_stable_for_same_message_text() -> None:
    message = "주의 구간 안내\n원문: https://example.test/1"
    first_hash = build_message_hash(message, on_date=date(2026, 10, 24))
    second_hash = build_message_hash(message, on_date=date(2026, 10, 24))

    assert first_hash == second_hash
    assert len(first_hash) == 64


def test_build_message_hash_allows_same_alert_on_next_kst_date() -> None:
    first_hash = build_message_hash("주의 구간 안내", on_date=date(2026, 10, 24))
    next_day_hash = build_message_hash("주의 구간 안내", on_date=date(2026, 10, 25))

    assert first_hash != next_day_hash


def test_has_successful_publish_checks_success_status_for_message_hash() -> None:
    session = Mock()
    session.scalar.return_value = uuid.uuid4()

    exists = has_successful_publish(session, "message-hash")

    assert exists is True
    statement_text = str(session.scalar.call_args.args[0])
    assert "publish_attempts.message_hash" in statement_text
    assert "publish_attempts.status = :status_1" in statement_text


def test_record_publish_attempt_adds_publish_attempt_model() -> None:
    session = Mock()
    run_id = uuid.uuid4()
    event_id = uuid.uuid4()

    record_publish_attempt(
        session,
        run_id=run_id,
        normalized_event_id=event_id,
        telegram_channel_id="@cycling_alerts",
        message_hash="message-hash",
        result=TelegramPublishResult(
            status="success",
            reason=None,
            telegram_message_id="123",
        ),
    )

    publish_attempt = session.add.call_args.args[0]
    assert publish_attempt.run_id == run_id
    assert publish_attempt.normalized_event_id == event_id
    assert publish_attempt.telegram_channel_id == "@cycling_alerts"
    assert publish_attempt.message_hash == "message-hash"
    assert publish_attempt.status == "success"
    assert publish_attempt.failure_reason is None
