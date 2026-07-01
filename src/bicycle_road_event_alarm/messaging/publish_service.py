from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from bicycle_road_event_alarm.messaging.publish_history import (
    build_message_hash,
    has_successful_publish,
    record_publish_attempt,
)
from bicycle_road_event_alarm.messaging.telegram_publisher import (
    TelegramClient,
    TelegramPublishConfig,
    TelegramPublishResult,
    publish_telegram_message,
)


# 단일 발송 처리: 성공 이력이 있는 메시지는 외부 호출 없이 중복 발송을 막습니다.
def publish_message_once(
    session: Session,
    *,
    run_id: uuid.UUID,
    normalized_event_id: uuid.UUID | None,
    message: str,
    config: TelegramPublishConfig,
    client: TelegramClient,
) -> TelegramPublishResult:
    if message.strip() == "":
        return TelegramPublishResult(
            status="skipped",
            reason="empty_message",
            telegram_message_id=None,
        )

    message_hash = build_message_hash(message)
    if has_successful_publish(session, message_hash):
        return TelegramPublishResult(
            status="skipped",
            reason="duplicate_successful_publish",
            telegram_message_id=None,
        )

    result = publish_telegram_message(message, config=config, client=client)
    if result.status in {"success", "failed"}:
        record_publish_attempt(
            session,
            run_id=run_id,
            normalized_event_id=normalized_event_id,
            telegram_channel_id=config.channel_id or "",
            message_hash=message_hash,
            result=result,
        )
    return result
