from __future__ import annotations

import requests

from bicycle_road_event_alarm.crawler.http import HttpClient


class FakeResponse:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"HTTP {self.status_code}")


class FakeSession:
    def __init__(self, responses: list[FakeResponse]) -> None:
        self.responses = responses
        self.calls: list[str] = []

    def get(self, url: str, *, timeout: int, headers: dict[str, str]) -> FakeResponse:
        self.calls.append(url)
        return self.responses.pop(0)


def test_http_client_retries_transient_status() -> None:
    session = FakeSession([FakeResponse(500), FakeResponse(200, "ok")])
    client = HttpClient(session=session, timeout_seconds=1, max_retries=1, retry_sleep_seconds=0)

    assert client.get_text("https://example.test") == "ok"
    assert session.calls == ["https://example.test", "https://example.test"]


def test_http_client_does_not_retry_404() -> None:
    session = FakeSession([FakeResponse(404)])
    client = HttpClient(session=session, timeout_seconds=1, max_retries=2, retry_sleep_seconds=0)

    try:
        client.get_text("https://example.test/missing")
    except requests.HTTPError:
        pass

    assert session.calls == ["https://example.test/missing"]
