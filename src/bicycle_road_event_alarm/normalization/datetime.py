from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ParsedEventDateTime:
    start: datetime | None
    end: datetime | None


DATE_PATTERN = re.compile(
    r"(?P<year>\d{4})[.\-/](?P<month>\d{1,2})[.\-/](?P<day>\d{1,2})"
    r"(?:\s+(?P<start_hour>\d{1,2}):(?P<start_minute>\d{2}))?"
    r"(?:\s*~\s*(?P<end_hour>\d{1,2}):(?P<end_minute>\d{2}))?"
)
DATE_RANGE_PATTERN = re.compile(
    r"(?:['’]\s*)?(?P<start_year>\d{2}|\d{4})\s*[.\-/]\s*"
    r"(?P<start_month>\d{1,2})\s*[.\-/]\s*(?P<start_day>\d{1,2})\.?"
    r"(?:\s*\([^)]+\))?\s*~\s*(?:['’]\s*)?"
    r"(?P<end_year>\d{2}|\d{4})\s*[.\-/]\s*"
    r"(?P<end_month>\d{1,2})\s*[.\-/]\s*(?P<end_day>\d{1,2})\.?"
    r"(?:\s*\([^)]+\))?"
)
KST = ZoneInfo("Asia/Seoul")


# 날짜 추출: 원문 날짜, 본문, 제목 순서로 명확한 숫자형 날짜를 찾습니다.
def parse_event_datetime(
    raw_date_text: str | None,
    raw_body: str | None,
    raw_title: str | None,
    fetched_at: datetime,
) -> ParsedEventDateTime:
    del fetched_at
    source_texts = (raw_date_text, raw_body, raw_title)
    for source_text in source_texts:
        if source_text is None:
            continue
        range_match = DATE_RANGE_PATTERN.search(source_text)
        if range_match is not None:
            return _build_date_range(range_match)

    for source_text in source_texts:
        if source_text is None:
            continue
        match = DATE_PATTERN.search(source_text)
        if match is None:
            continue
        return _build_datetime(match)
    return ParsedEventDateTime(start=None, end=None)


def _build_date_range(match: re.Match[str]) -> ParsedEventDateTime:
    start = datetime(
        _expand_year(match.group("start_year")),
        int(match.group("start_month")),
        int(match.group("start_day")),
        0,
        0,
        tzinfo=KST,
    )
    end = datetime(
        _expand_year(match.group("end_year")),
        int(match.group("end_month")),
        int(match.group("end_day")),
        23,
        59,
        tzinfo=KST,
    )
    return ParsedEventDateTime(start=start, end=end)


def _expand_year(year: str) -> int:
    value = int(year)
    if value >= 100:
        return value
    return 2000 + value if value < 70 else 1900 + value


# datetime 생성: 시간 정보가 없으면 자정 시작으로 보수적으로 저장합니다.
def _build_datetime(match: re.Match[str]) -> ParsedEventDateTime:
    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    start_hour = int(match.group("start_hour") or 0)
    start_minute = int(match.group("start_minute") or 0)
    start = datetime(year, month, day, start_hour, start_minute, tzinfo=KST)

    if match.group("end_hour") is None:
        return ParsedEventDateTime(start=start, end=None)

    end = datetime(
        year,
        month,
        day,
        int(match.group("end_hour") or 0),
        int(match.group("end_minute") or 0),
        tzinfo=KST,
    )
    return ParsedEventDateTime(start=start, end=end)
