from __future__ import annotations

import requests
from dotenv import load_dotenv

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.crawler.http import HttpClient
from bicycle_road_event_alarm.crawler.repository import (
    finish_run_log,
    save_raw_event_candidates,
    start_run_log,
)
from bicycle_road_event_alarm.crawler.spatic_ingestion import fetch_spatic_candidates
from bicycle_road_event_alarm.db.engine import create_engine_from_settings, create_session_factory


# 실행 명령: 환경 변수, DB 세션, SPATIC 수집 흐름을 하나로 연결합니다.
def main() -> int:
    load_dotenv(".env")
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        run_log = start_run_log(session)
        try:
            candidates = fetch_spatic_candidates(
                HttpClient(
                    timeout_seconds=settings.request_timeout_seconds,
                    max_retries=settings.crawler_max_retries,
                )
            )
        except requests.exceptions.RequestException as exc:
            saved_count = 0
            reason = "source_unavailable"
            finish_run_log(
                run_log,
                raw_event_count=0,
                normalized_event_count=0,
                published_message_count=0,
                status="success",
                error_summary=f"{reason}: {exc}",
            )
            session.commit()
            print("INGEST_STATUS=skipped")
            print(f"INGEST_REASON={reason}")
            print(f"RAW_EVENTS_SAVED={saved_count}")
            return 0

        saved_count = save_raw_event_candidates(session, run_log.id, candidates)
        finish_run_log(
            run_log,
            raw_event_count=saved_count,
            normalized_event_count=0,
            published_message_count=0,
        )
        session.commit()

    print(f"RAW_EVENTS_SAVED={saved_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
