from __future__ import annotations

import uuid
from dataclasses import dataclass

import pytest

from bicycle_road_event_alarm.cli import seed_publishable_fixture


@dataclass
class FakeSessionFactory:
    committed: bool = False

    def __call__(self) -> FakeSessionFactory:
        return self

    def __enter__(self) -> FakeSessionFactory:
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        return None

    def commit(self) -> None:
        self.committed = True


@dataclass(frozen=True)
class FakeSeedResult:
    run_id: uuid.UUID
    raw_event_id: uuid.UUID
    normalized_event_id: uuid.UUID
    title: str


def test_seed_publishable_fixture_cli_commits_and_prints_ids(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    session_factory = FakeSessionFactory()
    result = FakeSeedResult(
        run_id=uuid.uuid4(),
        raw_event_id=uuid.uuid4(),
        normalized_event_id=uuid.uuid4(),
        title="테스트 자전거 통제 이벤트 abcd1234",
    )

    monkeypatch.setattr(seed_publishable_fixture, "load_dotenv", lambda _path: None)
    monkeypatch.setattr(seed_publishable_fixture, "load_settings", lambda: object())
    monkeypatch.setattr(
        seed_publishable_fixture,
        "create_engine_from_settings",
        lambda _settings: object(),
    )
    monkeypatch.setattr(
        seed_publishable_fixture,
        "create_session_factory",
        lambda _engine: session_factory,
    )
    monkeypatch.setattr(
        seed_publishable_fixture,
        "seed_publishable_fixture",
        lambda _session: result,
    )

    assert seed_publishable_fixture.main() == 0

    output = capsys.readouterr().out
    assert f"FIXTURE_RUN_ID={result.run_id}" in output
    assert f"FIXTURE_NORMALIZED_EVENT_ID={result.normalized_event_id}" in output
    assert session_factory.committed is True
