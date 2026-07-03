import requests

from bicycle_road_event_alarm.crawler.multi_source_ingestion import (
    SourceDefinition,
    fetch_all_source_candidates,
)
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int | None]] = []

    def get_text(self, url: str, *, timeout_seconds: int | None = None) -> str:
        self.calls.append((url, timeout_seconds))
        if url == "https://example.test/failing":
            raise requests.exceptions.ConnectTimeout("timeout")
        return f"<html>{url}</html>"


def test_fetch_all_source_candidates_keeps_successful_sources_after_one_failure() -> None:
    http_client = FakeHttpClient()
    sources = [
        SourceDefinition(
            name="failing",
            url="https://example.test/failing",
            parser=lambda _html: [],
            timeout_seconds=5,
        ),
        SourceDefinition(
            name="working",
            url="https://example.test/working",
            parser=lambda _html: [
                RawEventCandidate(
                    source_name="working",
                    source_url="https://example.test/working/1",
                    raw_title="title",
                    raw_body="body",
                    raw_date_text=None,
                    raw_location_text=None,
                )
            ],
        ),
    ]

    result = fetch_all_source_candidates(http_client, sources=sources)

    assert len(result.candidates) == 1
    assert result.failures == {"failing": "timeout"}
    assert result.all_sources_failed is False
    assert http_client.calls == [
        ("https://example.test/failing", 5),
        ("https://example.test/working", None),
    ]


def test_fetch_all_source_candidates_marks_all_failed_only_when_every_source_fails() -> None:
    http_client = FakeHttpClient()
    sources = [
        SourceDefinition(
            name="failing",
            url="https://example.test/failing",
            parser=lambda _html: [],
        )
    ]

    result = fetch_all_source_candidates(http_client, sources=sources)

    assert result.candidates == []
    assert result.failures == {"failing": "timeout"}
    assert result.all_sources_failed is True
