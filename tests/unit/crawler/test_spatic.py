from pathlib import Path

from bicycle_road_event_alarm.crawler.spatic import parse_detail_page, parse_list_page


def test_parse_list_page_extracts_detail_urls() -> None:
    html = Path("tests/fixtures/crawler/spatic_list.html").read_text(encoding="utf-8")

    urls = parse_list_page(html)

    assert urls == ["https://spatic.go.kr/spatic/main/assemView.do?assemId=202606300001"]


def test_parse_detail_page_builds_raw_event_candidate() -> None:
    html = Path("tests/fixtures/crawler/spatic_detail.html").read_text(encoding="utf-8")

    candidate = parse_detail_page(
        html,
        source_url="https://www.spatic.go.kr/spatic/main/assemView.do?assemId=202606300001",
    )

    assert candidate.source_name == "서울경찰청 교통정보센터"
    assert candidate.raw_title == "2026 한강 자전거 행사 교통통제 안내"
    assert candidate.raw_date_text == "2026.07.04 08:00 ~ 12:00"
    assert candidate.raw_location_text == "잠실대교 남단 ~ 뚝섬한강공원"
    assert candidate.raw_body is not None
    assert "교통통제" in candidate.raw_body
