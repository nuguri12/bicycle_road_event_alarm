from pathlib import Path

from bicycle_road_event_alarm.crawler.ara_waterway import (
    ARA_WATERWAY_NOTICES_URL,
    enrich_ara_waterway_candidates_with_details,
    parse_ara_waterway_notice_detail_page,
    parse_ara_waterway_notices_page,
)

DETAIL_HTML = Path("tests/fixtures/crawler/ara_waterway_notice_detail.html").read_text(
    encoding="utf-8"
)


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, int | None]] = []

    def get_text(self, url: str, *, timeout_seconds: int | None = None) -> str:
        self.calls.append((url, timeout_seconds))
        return DETAIL_HTML


def test_parse_ara_waterway_notices_page_builds_notice_candidates() -> None:
    html = Path("tests/fixtures/crawler/ara_waterway_notices_list.html").read_text(encoding="utf-8")

    candidates = parse_ara_waterway_notices_page(html)

    assert len(candidates) == 2
    candidate = candidates[0]
    assert candidate.source_name == "아라뱃길 공지"
    assert (
        candidate.raw_title == "자전거도로, 아라마루 전망대 및 아라폭포 통행 차단 알림 "
        "(6.19. 18:00 ~ 기상 여건 완화 시) [개방완료]"
    )
    assert candidate.raw_date_text == "2026-06-19"
    assert candidate.raw_location_text is None
    assert (
        candidate.source_url
        == "https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/1223/view.do"
    )

    assert candidates[1].raw_location_text == "시천교-계양대교 구간"


def test_parse_ara_waterway_notices_page_ignores_unrelated_links() -> None:
    html = """
    <html><body>
      <nav><a href="/intro">자전거길 소개</a></nav>
      <div class="board notice list"><ul>
        <li class="point">
          <div class="ntt_sj left">
            <a href="#" onclick="bbsMstrView('3002'); return false;">
              <strong>아라뱃길 자전거길 통제 안내</strong>
            </a>
          </div>
          <p class="frst_register_nm">2026-07-02</p>
        </li>
      </ul></div>
    </ul></body></html>
    """

    candidates = parse_ara_waterway_notices_page(html)

    assert [candidate.raw_title for candidate in candidates] == ["아라뱃길 자전거길 통제 안내"]


def test_ara_waterway_source_url_is_public_waterway_site() -> None:
    assert (
        ARA_WATERWAY_NOTICES_URL
        == "https://www.kwater.or.kr/giwaterway/ara/bbs/BBSMSTR_000000000021/lst.do"
    )


def test_parse_ara_waterway_notice_detail_page_extracts_control_sections() -> None:
    html = DETAIL_HTML

    location_text = parse_ara_waterway_notice_detail_page(html)

    assert (
        location_text == "수향원 인근 (계양대교 북단); 청운교 남단 ~ 목상교 남단 ~ 야생화테라스쉼터"
    )


def test_enrich_ara_waterway_candidates_with_details_prefers_detail_sections() -> None:
    html = Path("tests/fixtures/crawler/ara_waterway_notices_list.html").read_text(encoding="utf-8")
    candidates = parse_ara_waterway_notices_page(html)
    http_client = FakeHttpClient()

    enriched = enrich_ara_waterway_candidates_with_details(
        candidates,
        http_client,
        timeout_seconds=10,
    )

    assert (
        enriched[0].raw_location_text
        == "수향원 인근 (계양대교 북단); 청운교 남단 ~ 목상교 남단 ~ 야생화테라스쉼터"
    )
    assert http_client.calls == [
        (
            "https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/1223/view.do",
            10,
        ),
        (
            "https://www.kwater.or.kr/giwaterway/ara/BBSMSTR_000000000021/1214/view.do",
            10,
        ),
    ]
