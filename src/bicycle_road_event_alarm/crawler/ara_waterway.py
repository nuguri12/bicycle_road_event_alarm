from __future__ import annotations

import re
from dataclasses import replace
from typing import Protocol
from urllib.parse import urljoin

from bs4 import Tag

from bicycle_road_event_alarm.crawler.page_parser import (
    clean_text,
    is_relevant_for_cyclists,
    soup_from_html,
)
from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate

ARA_WATERWAY_NOTICES_URL = "https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do"
ARA_WATERWAY_DETAIL_BASE_URL = "https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/"
DETAIL_ONCLICK_PATTERN = re.compile(r"bbsMstrView\('(?P<notice_id>\d+)'\)")


class TextHttpClient(Protocol):
    def get_text(self, url: str, *, timeout_seconds: int | None = None) -> str: ...


# 아라뱃길 공지 파서: 공식/공개 페이지의 게시판형 링크를 원문 후보로 변환합니다.
def parse_ara_waterway_notices_page(html: str) -> list[RawEventCandidate]:
    soup = soup_from_html(html)
    rows = [
        row
        for row in soup.select("div.board.notice.list > ul > li")
        if "thead" not in _class_names(row) and row.select_one(".ntt_sj")
    ]
    candidates: list[RawEventCandidate] = []

    for row in rows:
        link = _detail_url(row)
        title = _title_text(row)
        date_text = clean_text(row.select_one(".frst_register_nm"))
        body = _body_text(row, title=title, date_text=date_text)
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
                raw_date_text=date_text,
                raw_location_text=_location_text(row),
            )
        )

    return candidates


def enrich_ara_waterway_candidates_with_details(
    candidates: list[RawEventCandidate],
    http_client: TextHttpClient,
    *,
    timeout_seconds: int | None = None,
) -> list[RawEventCandidate]:
    enriched: list[RawEventCandidate] = []
    for candidate in candidates:
        detail_html = _detail_html(candidate, http_client, timeout_seconds=timeout_seconds)
        if detail_html is None:
            enriched.append(candidate)
            continue
        detail_location = parse_ara_waterway_notice_detail_page(detail_html)
        detail_body = _detail_body_text(detail_html)
        enriched.append(
            replace(
                candidate,
                raw_body=_combined_body(candidate.raw_body, detail_body),
                raw_location_text=detail_location or candidate.raw_location_text,
            )
        )

    return enriched


def parse_ara_waterway_notice_detail_page(html: str) -> str | None:
    soup = soup_from_html(html)
    content = soup.select_one(".ntt_cn")
    if content is None:
        return None

    sections: list[str] = []
    lines = [line.strip() for line in content.get_text("\n", strip=True).splitlines()]
    for index, line in enumerate(lines):
        match = re.search(r"(?:통제|차단)\s*구간\s*[:：]\s*(?P<section>.+)", line.strip())
        if match is not None:
            section = " ".join(match.group("section").split())
            if section:
                sections.append(section)
            continue

        if _is_section_label(line):
            sections.extend(_following_section_lines(lines[index + 1 :]))

    return "; ".join(sections) if sections else None


def _detail_html(
    candidate: RawEventCandidate,
    http_client: TextHttpClient,
    *,
    timeout_seconds: int | None,
) -> str | None:
    try:
        detail_html = http_client.get_text(candidate.source_url, timeout_seconds=timeout_seconds)
    except Exception:
        return None
    return detail_html


def _class_names(row: Tag) -> set[str]:
    class_attribute = row.get("class")
    if class_attribute is None:
        return set()
    if isinstance(class_attribute, str):
        return {class_attribute}
    return {str(class_name) for class_name in class_attribute}


def _detail_url(row: Tag) -> str | None:
    anchor = row.select_one(".ntt_sj a[onclick]")
    if anchor is None:
        return None
    onclick = anchor.get("onclick")
    if not isinstance(onclick, str):
        return None
    match = DETAIL_ONCLICK_PATTERN.search(onclick)
    if match is None:
        return None
    return urljoin(ARA_WATERWAY_DETAIL_BASE_URL, f"{match.group('notice_id')}/view.do")


def _title_text(row: Tag) -> str | None:
    title_element = row.select_one(".ntt_sj strong") or row.select_one(".ntt_sj a")
    if title_element is None:
        return None
    title = title_element.get_text(" ", strip=True)
    title = re.sub(r"\s*\[(?:new|secret)\]\s*", " ", title, flags=re.IGNORECASE)
    return " ".join(title.split()) or None


def _detail_body_text(html: str) -> str | None:
    soup = soup_from_html(html)
    content = soup.select_one(".ntt_cn") or soup.select_one(".texts")
    if content is None:
        return None
    body = content.get_text(" ", strip=True)
    return " ".join(body.split()) or None


def _combined_body(raw_body: str | None, detail_body: str | None) -> str | None:
    parts = [part for part in (raw_body, detail_body) if part]
    return " ".join(parts) if parts else None


def _is_section_label(line: str) -> bool:
    label = line.strip().strip("<>[](){}").replace(" ", "")
    return label in {"통제구간", "차단구간"}


def _following_section_lines(lines: list[str]) -> list[str]:
    sections: list[str] = []
    for line in lines:
        normalized = " ".join(line.split())
        if not normalized:
            continue
        if re.search(r"(?:통제|차단)\s*(?:사유|일시|기간)|문의", normalized):
            break
        label = normalized.strip().strip("<>[](){}").replace(" ", "")
        if label in {"통제기간", "차단기간", "통제사유", "차단사유"}:
            break
        section = normalized.lstrip("- ").strip()
        if section:
            sections.append(section)
    return sections


def _body_text(row: Tag, *, title: str | None, date_text: str | None) -> str | None:
    number_text = clean_text(row.select_one(".ntt_no"))
    parts = [part for part in (number_text, title, date_text) if part]
    return " ".join(parts) if parts else None


def _location_text(row: Tag) -> str | None:
    explicit_location = clean_text(row.select_one(".place, .location"))
    if explicit_location:
        return explicit_location

    title = _title_text(row)
    if title is None:
        return None

    parenthesized_locations = [
        match.group(1).strip()
        for match in re.finditer(r"\(([^)]*(?:구간|인근|북단|남단)[^)]*)\)", title)
    ]
    if parenthesized_locations:
        return "; ".join(parenthesized_locations)

    prefix_match = re.search(
        r"(?P<section>[가-힣A-Za-z0-9·\s]+(?:~|-)[가-힣A-Za-z0-9·\s]+구간)",
        title,
    )
    if prefix_match:
        return " ".join(prefix_match.group("section").split())

    return None
