from __future__ import annotations

import argparse
import uuid
from typing import cast

from dotenv import load_dotenv
from openai import OpenAI

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.crawler.repository import finish_run_log, start_run_log
from bicycle_road_event_alarm.db.engine import create_engine_from_settings, create_session_factory
from bicycle_road_event_alarm.messaging.openai_generator import OpenAIClient, OpenAIMessageGenerator
from bicycle_road_event_alarm.messaging.publish_service import publish_message_once
from bicycle_road_event_alarm.messaging.repository import load_publishable_message_events
from bicycle_road_event_alarm.messaging.service import generate_alert_message
from bicycle_road_event_alarm.messaging.telegram_publisher import (
    RequestsTelegramClient,
    TelegramPublishConfig,
)

DEFAULT_OPENAI_MODEL = "gpt-5.2"


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force-fallback",
        action="store_true",
        help="Skip OpenAI and use deterministic fallback message generation.",
    )
    parser.add_argument(
        "--run-id",
        type=uuid.UUID,
        default=None,
        help="Generate a message only from normalized events collected by the given run_logs.id.",
    )
    return parser.parse_args(argv)


# 실행 명령: publishable normalized_events를 읽어 알림 메시지를 생성하고 발송합니다.
def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    load_dotenv(".env")
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        run_log = start_run_log(session)
        session.flush()
        events = load_publishable_message_events(session, run_id=args.run_id)

        generator = None
        if not args.force_fallback and events and settings.openai_api_key is not None:
            generator = OpenAIMessageGenerator(
                client=cast(OpenAIClient, OpenAI(api_key=settings.openai_api_key)),
                model=DEFAULT_OPENAI_MODEL,
            )

        result = generate_alert_message(events, openai_generator=generator)
        publish_result = publish_message_once(
            session,
            run_id=run_log.id,
            normalized_event_id=None,
            message=result.text,
            config=TelegramPublishConfig(
                enabled=settings.enable_telegram_publish,
                dry_run=settings.dry_run,
                bot_token=settings.telegram_bot_token,
                channel_id=settings.telegram_channel_id,
            ),
            client=RequestsTelegramClient(timeout_seconds=settings.request_timeout_seconds),
        )
        finish_run_log(
            run_log,
            raw_event_count=0,
            normalized_event_count=0,
            published_message_count=1 if publish_result.status == "success" else 0,
        )
        session.commit()

    print(f"MESSAGE_STATUS={result.status}")
    print(f"MESSAGE_SOURCE={result.source}")
    print(f"MESSAGE_EVENT_COUNT={result.event_count}")
    print(f"TELEGRAM_STATUS={publish_result.status}")
    if publish_result.reason is not None:
        print(f"TELEGRAM_REASON={publish_result.reason}")
    if publish_result.telegram_message_id is not None:
        print(f"TELEGRAM_MESSAGE_ID={publish_result.telegram_message_id}")
    if result.text:
        print(result.text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
