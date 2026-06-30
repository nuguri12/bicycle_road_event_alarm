from pathlib import Path

from bicycle_road_event_alarm.crawler.spatic import LIST_URL
from bicycle_road_event_alarm.crawler.spatic_ingestion import fetch_spatic_candidates


class FakeHttpClient:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.pages = {
            LIST_URL: Path("tests/fixtures/crawler/spatic_list.html").read_text(encoding="utf-8"),
            "https://www.spatic.go.kr/spatic/main/assemView.do?assemId=202606300001": Path(
                "tests/fixtures/crawler/spatic_detail.html"
            ).read_text(encoding="utf-8"),
        }

    def get_text(self, url: str) -> str:
        self.calls.append(url)
        return self.pages[url]


def test_fetch_spatic_candidates_fetches_list_then_details() -> None:
    http_client = FakeHttpClient()

    candidates = fetch_spatic_candidates(http_client)

    assert len(candidates) == 1
    assert candidates[0].raw_title == "2026 한강 자전거 행사 교통통제 안내"
    assert http_client.calls == [
        LIST_URL,
        "https://www.spatic.go.kr/spatic/main/assemView.do?assemId=202606300001",
    ]
