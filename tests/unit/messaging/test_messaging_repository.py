from unittest.mock import Mock

from bicycle_road_event_alarm.messaging.repository import load_publishable_message_events


def test_load_publishable_message_events_filters_publish_candidates() -> None:
    session = Mock()
    session.execute.return_value.all.return_value = []

    events = load_publishable_message_events(session)

    assert events == []
    statement_text = str(session.execute.call_args.args[0])
    assert "normalized_events.publish_candidate" in statement_text
    assert "normalized_events.validation_status = :validation_status_1" in statement_text
