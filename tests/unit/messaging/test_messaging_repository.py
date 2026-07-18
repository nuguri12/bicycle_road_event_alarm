import uuid
from unittest.mock import Mock

from bicycle_road_event_alarm.messaging.repository import load_publishable_message_events


def test_load_publishable_message_events_filters_publish_candidates() -> None:
    session = Mock()
    session.execute.return_value.all.return_value = []

    events = load_publishable_message_events(session)

    assert events == []
    statement_text = str(session.execute.call_args.args[0])
    assert "normalized_events.publish_candidate" in statement_text
    assert "normalized_events.validation_status = :validation_status_1" not in statement_text


def test_load_publishable_message_events_can_scope_to_run_id() -> None:
    session = Mock()
    session.execute.return_value.all.return_value = []
    run_id = uuid.uuid4()

    events = load_publishable_message_events(session, run_id=run_id)

    assert events == []
    statement_text = str(session.execute.call_args.args[0])
    assert "raw_events.run_id = :run_id_1" in statement_text
