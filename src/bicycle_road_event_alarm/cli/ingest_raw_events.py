from __future__ import annotations

from datetime import UTC, datetime

from dotenv import load_dotenv

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.crawler.http import HttpClient
from bicycle_road_event_alarm.crawler.multi_source_ingestion import (
    MultiSourceIngestionResult,
    fetch_all_source_candidates,
)
from bicycle_road_event_alarm.crawler.repository import (
    finish_run_log,
    save_raw_event_candidates,
    start_run_log,
)
from bicycle_road_event_alarm.db.engine import create_engine_from_settings, create_session_factory
from bicycle_road_event_alarm.db.models import RunLog


# 실행 명령: 환경 변수, DB 세션, 다중 출처 수집 흐름을 하나로 연결합니다.
def main() -> int:
    load_dotenv(".env")
    settings = load_settings()
    engine = create_engine_from_settings(settings)
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        run_log = start_run_log(session)
        run_id = run_log.id
        started_at = run_log.started_at
        # FK 보호: raw_events를 저장하기 전에 부모 run_logs row를 DB에 먼저 반영합니다.
        session.flush()

        try:
            ingestion_result = fetch_all_source_candidates(
                HttpClient(
                    timeout_seconds=settings.request_timeout_seconds,
                    max_retries=settings.crawler_max_retries,
                )
            )

            if ingestion_result.all_sources_failed:
                saved_count = 0
                reason = "source_unavailable"
                finish_run_log(
                    run_log,
                    raw_event_count=0,
                    normalized_event_count=0,
                    published_message_count=0,
                    status="success",
                    error_summary=f"{reason}: {_failure_summary(ingestion_result)}",
                )
                session.commit()
                print("INGEST_STATUS=skipped")
                print(f"INGEST_REASON={reason}")
                print(f"RUN_ID={run_log.id}")
                print(f"RAW_EVENTS_SAVED={saved_count}")
                return 0

            saved_count = save_raw_event_candidates(
                session, run_log.id, ingestion_result.candidates
            )
            finish_run_log(
                run_log,
                raw_event_count=saved_count,
                normalized_event_count=0,
                published_message_count=0,
                error_summary=_partial_failure_summary(ingestion_result),
            )
            session.commit()
        except Exception as exc:
            # DB 오류 시 트랜잭션이 중단 상태가 되므로, 실패 기록을 남기려면 먼저 롤백해야 합니다.
            # 이전 run_log는 commit된 적이 없어 롤백과 함께 사라지므로 같은 id로 새로 남깁니다.
            session.rollback()
            session.add(
                RunLog(
                    id=run_id,
                    status="failed",
                    started_at=started_at,
                    finished_at=datetime.now(UTC),
                    raw_event_count=0,
                    normalized_event_count=0,
                    published_message_count=0,
                    error_summary=f"unhandled_error: {exc!r}"[:2000],
                    created_at=started_at,
                )
            )
            session.commit()
            raise

    print("INGEST_STATUS=success")
    print(f"RUN_ID={run_log.id}")
    print(f"RAW_EVENTS_SAVED={saved_count}")
    return 0


def _failure_summary(result: MultiSourceIngestionResult) -> str:
    return "; ".join(f"{name}={reason}" for name, reason in result.failures.items())


def _partial_failure_summary(result: MultiSourceIngestionResult) -> str | None:
    if not result.failures:
        return None
    return f"partial_source_unavailable: {_failure_summary(result)}"


if __name__ == "__main__":
    raise SystemExit(main())
