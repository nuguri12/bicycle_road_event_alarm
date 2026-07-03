from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from typing import Protocol

from bicycle_road_event_alarm.crawler.ara_waterway import (
    ARA_WATERWAY_NOTICES_URL,
    parse_ara_waterway_notices_page,
)
from bicycle_road_event_alarm.crawler.hangang import (
    HANGANG_EVENTS_URL,
    HANGANG_NOTICES_URL,
    parse_hangang_events_page,
    parse_hangang_notices_page,
)
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate


class TextHttpClient(Protocol):
    def get_text(self, url: str) -> str: ...


@dataclass(frozen=True)
class SourceDefinition:
    name: str
    url: str
    parser: Callable[[str], list[RawEventCandidate]]


@dataclass(frozen=True)
class MultiSourceIngestionResult:
    candidates: list[RawEventCandidate]
    failures: dict[str, str]

    @property
    def all_sources_failed(self) -> bool:
        return len(self.failures) > 0 and len(self.candidates) == 0


DEFAULT_SOURCES = (
    SourceDefinition(
        name="hangang_events",
        url=HANGANG_EVENTS_URL,
        parser=parse_hangang_events_page,
    ),
    SourceDefinition(
        name="hangang_notices",
        url=HANGANG_NOTICES_URL,
        parser=parse_hangang_notices_page,
    ),
    SourceDefinition(
        name="ara_waterway_notices",
        url=ARA_WATERWAY_NOTICES_URL,
        parser=parse_ara_waterway_notices_page,
    ),
)


# 다중 소스 수집: 한 소스가 실패해도 나머지 소스는 계속 수집합니다.
def fetch_all_source_candidates(
    http_client: TextHttpClient,
    *,
    sources: Sequence[SourceDefinition] = DEFAULT_SOURCES,
) -> MultiSourceIngestionResult:
    candidates: list[RawEventCandidate] = []
    failures: dict[str, str] = {}

    for source in sources:
        try:
            html = http_client.get_text(source.url)
            candidates.extend(source.parser(html))
        except Exception as exc:
            failures[source.name] = str(exc)

    return MultiSourceIngestionResult(candidates=candidates, failures=failures)
