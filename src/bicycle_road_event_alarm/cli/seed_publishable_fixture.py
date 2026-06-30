from __future__ import annotations

from dotenv import load_dotenv

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.db.engine import create_engine_from_settings, create_session_factory
from bicycle_road_event_alarm.messaging.publishable_fixture import seed_publishable_fixture


# 실행 명령: Supabase에 DB/CLI 검증용 publishable 더미 이벤트를 1건 추가합니다.
def main() -> int:
    load_dotenv(".env")
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        result = seed_publishable_fixture(session)
        session.commit()

    print(f"FIXTURE_RUN_ID={result.run_id}")
    print(f"FIXTURE_RAW_EVENT_ID={result.raw_event_id}")
    print(f"FIXTURE_NORMALIZED_EVENT_ID={result.normalized_event_id}")
    print(f"FIXTURE_TITLE={result.title}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
