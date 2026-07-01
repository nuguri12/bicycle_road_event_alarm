from __future__ import annotations

from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag

from bicycle_road_event_alarm.crawler.raw_event import RawEventCandidate

SOURCE_NAME = "서울경찰청 교통정보센터"
LIST_URL = "https://spatic.go.kr/spatic/main/assem.do"


# 텍스트 추출: HTML 요소가 없거나 비어 있으면 None으로 통일합니다.
def _clean_text(element: Tag | None) -> str | None:
    if element is None:
        return None

    text = " ".join(element.get_text(" ", strip=True).split())
    if text == "":
        return None
    return text


# 목록 파서: SPATIC 목록 HTML에서 상세 페이지 URL만 추출합니다.
def parse_list_page(html: str, base_url: str = LIST_URL) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    detail_urls: list[str] = []

    for anchor in soup.select("a[href]"):
        href = anchor.get("href")
        if not isinstance(href, str):
            continue
        if "assemView" not in href:
            continue
        detail_urls.append(urljoin(base_url, href))

    return detail_urls


# 상세 파서: 원문 제목, 일시, 장소, 본문을 RawEventCandidate로 변환합니다.
def parse_detail_page(html: str, *, source_url: str) -> RawEventCandidate:
    soup = BeautifulSoup(html, "html.parser")

    title = _clean_text(soup.select_one("h1, .title, .subject"))
    body = _clean_text(soup.select_one(".content, article, .view"))
    date_text = _definition_value(soup, "일시")
    location_text = _definition_value(soup, "장소")

    return RawEventCandidate(
        source_name=SOURCE_NAME,
        source_url=source_url,
        raw_title=title,
        raw_body=body,
        raw_date_text=date_text,
        raw_location_text=location_text,
    )


# 정의 목록 파서: 상세 페이지의 dt/dd 구조에서 일시와 장소 값을 찾습니다.
def _definition_value(soup: BeautifulSoup, label: str) -> str | None:
    for term in soup.select("dt"):
        if _clean_text(term) != label:
            continue
        sibling = term.find_next_sibling("dd")
        if isinstance(sibling, Tag):
            return _clean_text(sibling)
    return None
