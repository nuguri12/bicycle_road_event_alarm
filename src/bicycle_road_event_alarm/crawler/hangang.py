from __future__ import annotations

import hashlib
import json
import re
from urllib.parse import urljoin

from bs4 import Tag

from bicycle_road_event_alarm.crawler.page_parser import (
    clean_text,
    first_date_text,
    first_internal_link,
    is_relevant_for_cyclists,
    labeled_value,
    soup_from_html,
    text_lines,
)
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate

HANGANG_EVENTS_URL = "https://hangang.seoul.go.kr/www/eventMng/list.do?mid=538"
HANGANG_NOTICES_PUBLIC_URL = "https://hangang.seoul.go.kr/www/bbsPost/30/list.do?mid=608"
HANGANG_NOTICES_URL = "https://seoulboard.seoul.go.kr/front/bbs.json?bbsNo=5211"


# 한강 행사 파서: 행사 카드의 제목, 기간, 시간, 장소를 원문 후보로 보존합니다.
def parse_hangang_events_page(html: str) -> list[RawEventCandidate]:
    soup = soup_from_html(html)
    containers = list(soup.select("article, li, .event-card"))
    if not containers:
        containers = [soup.body or soup]

    candidates: list[RawEventCandidate] = []
    for container in containers:
        lines = text_lines(container)
        if "기간" not in lines or "장소" not in lines:
            continue
        if "마감" in lines:
            continue

        title = _event_title(container, lines)
        if title is None:
            continue
        body = clean_text(container)
        if not is_relevant_for_cyclists(" ".join(part for part in (title, body) if part)):
            continue

        period = labeled_value(container, "기간")
        time_text = labeled_value(container, "시간")
        location = labeled_value(container, "장소")
        date_text = " ".join(part for part in (period, time_text) if part)

        candidates.append(
            RawEventCandidate(
                source_name="한강공원 행사",
                source_url=_event_source_url(container),
                raw_title=title,
                raw_body=body,
                raw_date_text=date_text or None,
                raw_location_text=location,
            )
        )

    return candidates


# 한강 새소식 파서: 서울시 공통 보드 JSON에서 공지 제목과 게시일을 원문 후보로 보존합니다.
def parse_hangang_notices_page(html: str) -> list[RawEventCandidate]:
    if html.lstrip().startswith("{"):
        return _parse_hangang_notices_json(html)

    soup = soup_from_html(html)
    rows = list(soup.select("tr, li"))
    candidates: list[RawEventCandidate] = []

    for row in rows:
        link = first_internal_link(row, base_url=HANGANG_NOTICES_URL)
        title = clean_text(row.select_one("a[href]"))
        body = clean_text(row)
        if link is None or title is None or body is None:
            continue
        if "bbsPost/30/view.do" not in link:
            continue
        if not is_relevant_for_cyclists(f"{title} {body}"):
            continue

        candidates.append(
            RawEventCandidate(
                source_name="한강공원 새소식",
                source_url=link,
                raw_title=title,
                raw_body=body,
                raw_date_text=first_date_text(body),
                raw_location_text=None,
            )
        )

    return candidates


def _parse_hangang_notices_json(raw_json: str) -> list[RawEventCandidate]:
    data = json.loads(raw_json)
    candidates: list[RawEventCandidate] = []

    for item in _notice_items(data):
        title = _string_value(item.get("sj"))
        body = _notice_body(item)
        if title is None or body is None:
            continue
        if not is_relevant_for_cyclists(f"{title} {body}"):
            continue

        candidates.append(
            RawEventCandidate(
                source_name="한강공원 새소식",
                source_url=_notice_source_url(item),
                raw_title=title,
                raw_body=body,
                raw_date_text=first_date_text(body),
                raw_location_text=None,
            )
        )

    return candidates


def _notice_items(data: object) -> list[dict[str, object]]:
    if not isinstance(data, dict):
        return []

    items: list[dict[str, object]] = []
    for section_name in ("noticeListVO", "listVO"):
        section = data.get(section_name)
        if not isinstance(section, dict):
            continue
        section_items = section.get("listObject")
        if not isinstance(section_items, list):
            continue
        items.extend(item for item in section_items if isinstance(item, dict))
    return items


def _notice_body(item: dict[str, object]) -> str | None:
    parts = [
        _string_value(item.get("sj")),
        _string_value(item.get("sumry")),
        _string_value(item.get("organDept")),
        _string_value(item.get("writngDe")),
    ]
    body = " ".join(part for part in parts if part and part != "-")
    return body or None


def _notice_source_url(item: dict[str, object]) -> str:
    ntt_no = item.get("nttNo")
    if isinstance(ntt_no, int | str) and str(ntt_no).strip():
        return f"{HANGANG_NOTICES_PUBLIC_URL}#view/{ntt_no}"
    # nttNo가 없는 공지는 제목+작성일 기반 안정적 식별자를 붙여, 같은 fallback URL을
    # 공유하는 서로 다른 공지가 raw_events에서 한 row로 뭉개지지 않게 합니다.
    fallback_key = f"{_string_value(item.get('sj'))}|{_string_value(item.get('writngDe'))}"
    fallback_id = hashlib.sha256(fallback_key.encode("utf-8")).hexdigest()[:16]
    return f"{HANGANG_NOTICES_PUBLIC_URL}#fallback/{fallback_id}"


def _string_value(value: object) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _event_title(container: Tag, lines: list[str]) -> str | None:
    heading = clean_text(container.select_one("h1, h2, h3, h4, strong, .title, .subject"))
    if heading is not None:
        return heading

    ignored = {"기간", "시간", "참여", "장소", "네이버 길찾기", "카카오 길찾기"}
    for line in lines:
        if line in ignored:
            continue
        if first_date_text(line):
            continue
        return line
    return None


def _event_source_url(container: Tag) -> str:
    for anchor in container.select("a[href]"):
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        detail_match = re.search(r"goDetail\('?(?P<id>\d+)'?\)", href)
        if detail_match:
            return (
                "https://hangang.seoul.go.kr/www/eventMng/detail.do?"
                f"evntSn={detail_match.group('id')}"
            )
        if href.strip():
            return urljoin(HANGANG_EVENTS_URL, href)
    return HANGANG_EVENTS_URL
