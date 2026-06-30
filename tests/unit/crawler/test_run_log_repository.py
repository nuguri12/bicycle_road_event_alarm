from unittest.mock import Mock

from bicycle_road_event_alarm.crawler.repository import finish_run_log, start_run_log


def test_start_run_log_adds_running_run() -> None:
    session = Mock()

    run_log = start_run_log(session)

    assert run_log.status == "running"
    assert run_log.raw_event_count == 0
    session.add.assert_called_once_with(run_log)


def test_finish_run_log_records_success_counts() -> None:
    run_log = start_run_log(Mock())

    finish_run_log(run_log, raw_event_count=3, normalized_event_count=0, published_message_count=0)

    assert run_log.status == "success"
    assert run_log.raw_event_count == 3
    assert run_log.finished_at is not None
