from __future__ import annotations

from dotenv import load_dotenv
from sqlalchemy import select

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.db.engine import create_engine_from_settings, create_session_factory
from bicycle_road_event_alarm.db.models import RawEvent
from bicycle_road_event_alarm.normalization.repository import save_normalized_events


# 실행 명령: 저장된 raw_events를 읽어 normalized_events로 변환합니다.
def main() -> int:
    load_dotenv(".env")
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        raw_events = list(session.scalars(select(RawEvent)).all())
        saved_count = save_normalized_events(session, raw_events)
        session.commit()

    print(f"NORMALIZED_EVENTS_SAVED={saved_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
