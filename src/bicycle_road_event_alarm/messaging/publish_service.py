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


# 단일 발송 처리: 빈 메시지는 무시하고, 그 외 성공/실패/스킵 결과는 DB에 남깁니다.
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
        result = TelegramPublishResult(
            status="skipped",
            reason="duplicate_successful_publish",
            telegram_message_id=None,
        )
    else:
        result = publish_telegram_message(message, config=config, client=client)

    record_publish_attempt(
        session,
        run_id=run_id,
        normalized_event_id=normalized_event_id,
        telegram_channel_id=config.channel_id or "",
        message_hash=message_hash,
        result=result,
    )
    return result
