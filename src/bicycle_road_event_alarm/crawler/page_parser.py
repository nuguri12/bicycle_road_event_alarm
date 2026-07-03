from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup, Tag


# 텍스트 정리: HTML 공백과 줄바꿈 차이를 안정적인 문자열로 통일합니다.
def clean_text(element: Tag | None) -> str | None:
    if element is None:
        return None

    text = " ".join(element.get_text(" ", strip=True).split())
    return text or None


# 라벨 값 추출: dt/dd, th/td, 일반 텍스트 순서를 모두 같은 방식으로 처리합니다.
def labeled_value(container: Tag, label: str) -> str | None:
    for term in container.select("dt, th"):
        if clean_text(term) != label:
            continue
        sibling = term.find_next_sibling(["dd", "td"])
        if isinstance(sibling, Tag):
            return clean_text(sibling)

    lines = text_lines(container)
    for index, line in enumerate(lines[:-1]):
        if line == label:
            return lines[index + 1]
    return None


# 줄 단위 텍스트: 실제 사이트와 fixture 모두에서 목록 카드 경계를 찾기 쉽게 만듭니다.
def text_lines(container: Tag) -> list[str]:
    text = container.get_text("\n", strip=True)
    return [line.strip() for line in text.splitlines() if line.strip()]


# 상세 링크 찾기: 같은 카드/행 안의 첫 번째 내부 링크를 출처 URL로 사용합니다.
def first_internal_link(container: Tag, *, base_url: str) -> str | None:
    for anchor in container.select("a[href]"):
        href = anchor.get("href")
        if isinstance(href, str) and href.strip():
            return urljoin(base_url, href)
    return None


# 날짜 후보 추출: 게시판형 소스에서 별도 라벨 없이 노출된 날짜를 보존합니다.
def first_date_text(text: str) -> str | None:
    match = re.search(r"\d{4}[.-]\d{2}[.-]\d{2}(?:\([^)]+\))?", text)
    return match.group(0) if match else None


def soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


RELEVANT_KEYWORDS = (
    "자전거",
    "자전거길",
    "자전거도로",
    "통제",
    "교통",
    "공사",
    "정비",
    "마라톤",
    "러닝",
    "대회",
    "퍼레이드",
    "축제",
)


# 관련성 필터: 메뉴/소개 링크가 raw_events와 OpenAI 입력으로 과수집되지 않게 막습니다.
def is_relevant_for_cyclists(text: str | None) -> bool:
    if text is None:
        return False
    return any(keyword in text for keyword in RELEVANT_KEYWORDS)
