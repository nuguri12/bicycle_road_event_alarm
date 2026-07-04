from pathlib import Path

from bicycle_road_event_alarm.crawler.ara_waterway import (
    ARA_WATERWAY_NOTICES_URL,
    parse_ara_waterway_notices_page,
)


def test_parse_ara_waterway_notices_page_builds_notice_candidates() -> None:
    html = Path("tests/fixtures/crawler/ara_waterway_notices_list.html").read_text(encoding="utf-8")

    candidates = parse_ara_waterway_notices_page(html)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source_name == "아라뱃길 공지"
    assert candidate.raw_title == "아라뱃길 자전거길 정비 작업 안내"
    assert candidate.raw_date_text == "2026-07-02"
    assert candidate.raw_location_text == "계양대교 인근 아라자전거길"
    assert candidate.source_url == "https://www.kwater.or.kr/notice/3001"


def test_parse_ara_waterway_notices_page_ignores_unrelated_links() -> None:
    html = """
    <html><body><ul>
      <li><a href="/intro">Read Articles</a></li>
      <li><a href="/notice/3002">아라뱃길 자전거길 통제 안내</a></li>
    </ul></body></html>
    """

    candidates = parse_ara_waterway_notices_page(html)

    assert [candidate.raw_title for candidate in candidates] == ["아라뱃길 자전거길 통제 안내"]


def test_ara_waterway_source_url_is_public_waterway_site() -> None:
    assert (
        ARA_WATERWAY_NOTICES_URL
        == "https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do"
    )
