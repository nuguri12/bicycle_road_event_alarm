from __future__ import annotations

import hashlib
import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from bicycle_road_event_alarm.db.models import PublishAttempt
from bicycle_road_event_alarm.messaging.telegram_publisher import TelegramPublishResult


# 메시지 해시: 같은 본문은 같은 값으로 계산해 중복 발송 여부를 판단합니다.
def build_message_hash(message: str) -> str:
    return hashlib.sha256(message.strip().encode("utf-8")).hexdigest()


# 성공 이력 조회: 같은 message_hash가 이미 success면 다시 발송하지 않습니다.
def has_successful_publish(session: Session, message_hash: str) -> bool:
    existing_id = session.scalar(
        select(PublishAttempt.id)
        .where(PublishAttempt.message_hash == message_hash)
        .where(PublishAttempt.status == "success")
    )
    return existing_id is not None


# 발송 이력 기록: Telegram 결과를 publish_attempts 행으로 변환합니다.
def record_publish_attempt(
    session: Session,
    *,
    run_id: uuid.UUID,
    normalized_event_id: uuid.UUID | None,
    telegram_channel_id: str,
    message_hash: str,
    result: TelegramPublishResult,
) -> None:
    now = datetime.now(UTC)
    session.add(
        PublishAttempt(
            run_id=run_id,
            normalized_event_id=normalized_event_id,
            telegram_channel_id=telegram_channel_id,
            message_hash=message_hash,
            status=result.status,
            failure_reason=result.reason,
            attempted_at=now,
            created_at=now,
        )
    )
