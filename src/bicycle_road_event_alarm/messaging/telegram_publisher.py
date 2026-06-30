from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import requests


@dataclass(frozen=True)
class TelegramPublishConfig:
    enabled: bool
    dry_run: bool
    bot_token: str | None
    channel_id: str | None


@dataclass(frozen=True)
class TelegramPublishResult:
    status: str
    reason: str | None
    telegram_message_id: str | None


class TelegramClient(Protocol):
    def send_message(self, *, bot_token: str, channel_id: str, text: str) -> str: ...


class RequestsTelegramClient:
    def __init__(self, *, timeout_seconds: int) -> None:
        self._timeout_seconds = timeout_seconds

    # Telegram API 호출: sendMessage 응답에서 message_id만 추출합니다.
    def send_message(self, *, bot_token: str, channel_id: str, text: str) -> str:
        response = requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={"chat_id": channel_id, "text": text},
            timeout=self._timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        return str(payload["result"]["message_id"])


# 발송 제어: 안전 플래그와 메시지 검증을 통과한 경우에만 Telegram API를 호출합니다.
def publish_telegram_message(
    message: str,
    *,
    config: TelegramPublishConfig,
    client: TelegramClient,
) -> TelegramPublishResult:
    normalized_message = message.strip()
    if normalized_message == "":
        return TelegramPublishResult(
            status="skipped",
            reason="empty_message",
            telegram_message_id=None,
        )

    if not config.enabled:
        return TelegramPublishResult(
            status="skipped",
            reason="telegram_publish_disabled",
            telegram_message_id=None,
        )

    if config.dry_run:
        return TelegramPublishResult(
            status="skipped",
            reason="dry_run",
            telegram_message_id=None,
        )

    if config.bot_token is None or config.channel_id is None:
        return TelegramPublishResult(
            status="failed",
            reason="telegram_config_missing",
            telegram_message_id=None,
        )

    telegram_message_id = client.send_message(
        bot_token=config.bot_token,
        channel_id=config.channel_id,
        text=normalized_message,
    )
    return TelegramPublishResult(
        status="success",
        reason=None,
        telegram_message_id=telegram_message_id,
    )
