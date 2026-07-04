from __future__ import annotations

from bs4 import Tag

from bicycle_road_event_alarm.crawler.page_parser import (
    clean_text,
    first_date_text,
    first_internal_link,
    is_relevant_for_cyclists,
    soup_from_html,
)
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate

ARA_WATERWAY_NOTICES_URL = "https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do"


# 아라뱃길 공지 파서: 공식/공개 페이지의 게시판형 링크를 원문 후보로 변환합니다.
def parse_ara_waterway_notices_page(html: str) -> list[RawEventCandidate]:
    soup = soup_from_html(html)
    rows = list(soup.select("tr, li, article"))
    candidates: list[RawEventCandidate] = []

    for row in rows:
        link = first_internal_link(row, base_url=ARA_WATERWAY_NOTICES_URL)
        title = clean_text(row.select_one("a[href]"))
        body = clean_text(row)
        if link is None or title is None or body is None:
            continue
        if not is_relevant_for_cyclists(f"{title} {body}"):
            continue

        candidates.append(
            RawEventCandidate(
                source_name="아라뱃길 공지",
                source_url=link,
                raw_title=title,
                raw_body=body,
                raw_date_text=first_date_text(body),
                raw_location_text=_location_text(row),
            )
        )

    return candidates


def _location_text(row: Tag) -> str | None:
    return clean_text(row.select_one(".place, .location"))
