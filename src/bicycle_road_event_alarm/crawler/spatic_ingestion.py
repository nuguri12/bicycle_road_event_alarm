from __future__ import annotations

from typing import Protocol

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate
from bicycle_road_event_alarm.crawler.spatic import LIST_URL, parse_detail_page, parse_list_page


class TextHttpClient(Protocol):
    def get_text(self, url: str) -> str: ...


# SPATIC 수집 흐름: 목록 페이지에서 상세 URL을 얻고 각 상세 페이지를 후보로 변환합니다.
def fetch_spatic_candidates(http_client: TextHttpClient) -> list[RawEventCandidate]:
    list_html = http_client.get_text(LIST_URL)
    detail_urls = parse_list_page(list_html)

    candidates: list[RawEventCandidate] = []
    for detail_url in detail_urls:
        detail_html = http_client.get_text(detail_url)
        candidates.append(parse_detail_page(detail_html, source_url=detail_url))

    return candidates
