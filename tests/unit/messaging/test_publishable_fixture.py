from __future__ import annotations

from unittest.mock import Mock

from bicycle_road_event_alarm.messaging.publishable_fixture import seed_publishable_fixture


def test_seed_publishable_fixture_adds_raw_and_normalized_event_models() -> None:
    session = Mock()

    result = seed_publishable_fixture(session)

    added_models = [call.args[0] for call in session.add.call_args_list]
    assert result.raw_event_id is not None
    assert result.normalized_event_id is not None
    assert result.title.startswith("테스트 자전거 통제 이벤트")
    assert len(added_models) == 3
    assert added_models[1].source_name == "local-fixture"
    assert added_models[2].publish_candidate is True
    assert added_models[2].validation_status == "valid"


def test_seed_publishable_fixture_flushes_raw_event_before_normalized_event() -> None:
    session = Mock()

    seed_publishable_fixture(session)

    method_order = [call[0] for call in session.method_calls]
    flush_indexes = [
        index for index, method_name in enumerate(method_order) if method_name == "flush"
    ]
    assert len(flush_indexes) == 2
    assert method_order[:5] == ["add", "flush", "add", "flush", "add"]
