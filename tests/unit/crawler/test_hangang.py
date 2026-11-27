from pathlib import Path

from bicycle_road_event_alarm.crawler.hangang import (
    HANGANG_EVENTS_URL,
    HANGANG_NOTICES_URL,
    parse_hangang_events_page,
    parse_hangang_notices_page,
)


def test_parse_hangang_events_page_builds_event_candidates() -> None:
    html = Path("tests/fixtures/crawler/hangang_events_list.html").read_text(encoding="utf-8")

    candidates = parse_hangang_events_page(html)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source_name == "한강공원 행사"
    assert candidate.source_url == (
        "https://hangang.seoul.go.kr/www/eventMng/detail.do?evntSn=1001"
    )
    assert candidate.raw_title == "2026 한강 자전거 퍼레이드"
    assert candidate.raw_date_text == "2026-07-04(토) ~ 2026-07-04(토) 08:00~12:00"
    assert candidate.raw_location_text == "잠실한강공원 ~ 뚝섬한강공원"
    assert "체육" in (candidate.raw_body or "")


def test_parse_hangang_notices_page_builds_notice_candidates() -> None:
    html = Path("tests/fixtures/crawler/hangang_notices_list.json").read_text(encoding="utf-8")

    candidates = parse_hangang_notices_page(html)

    assert len(candidates) == 1
    candidate = candidates[0]
    assert candidate.source_name == "한강공원 새소식"
    assert (
        candidate.source_url
        == "https://hangang.seoul.go.kr/www/bbsPost/30/list.do?mid=608#view/457099"
    )
    assert candidate.raw_title == "2026년 한강공원 자전거도로 일부 통제 안내"
    assert candidate.raw_date_text == "2026-07-01"
    assert candidate.raw_location_text is None


def test_parse_hangang_notices_page_ignores_unrelated_api_items() -> None:
    html = Path("tests/fixtures/crawler/hangang_notices_list.json").read_text(encoding="utf-8")

    candidates = parse_hangang_notices_page(html)

    assert [candidate.raw_title for candidate in candidates] == [
        "2026년 한강공원 자전거도로 일부 통제 안내"
    ]


def test_hangang_source_urls_point_to_official_hangang_pages() -> None:
    assert HANGANG_EVENTS_URL == "https://hangang.seoul.go.kr/www/eventMng/list.do?mid=538"
    assert HANGANG_NOTICES_URL == "https://seoulboard.seoul.go.kr/front/bbs.json?bbsNo=5211"


def test_hangang_notices_missing_nttno_get_distinct_fallback_source_urls() -> None:
    raw_json = """
    {
      "listVO": {
        "listObject": [
          {
            "sj": "한강공원 자전거도로 1차 통제 안내",
            "writngDe": "2026-07-01 10:11.12",
            "sumry": "자전거도로 일부 구간 통제가 예정되어 있습니다."
          },
          {
            "sj": "한강공원 자전거도로 2차 통제 안내",
            "writngDe": "2026-07-02 09:00.00",
            "sumry": "자전거도로 다른 구간도 통제가 예정되어 있습니다."
          }
        ]
      }
    }
    """

    candidates = parse_hangang_notices_page(raw_json)

    assert len(candidates) == 2
    first, second = candidates
    assert first.source_url != second.source_url
    assert first.source_url.startswith(
        "https://hangang.seoul.go.kr/www/bbsPost/30/list.do?mid=608#fallback/"
    )
    assert second.source_url.startswith(
        "https://hangang.seoul.go.kr/www/bbsPost/30/list.do?mid=608#fallback/"
    )
