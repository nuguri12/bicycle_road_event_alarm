from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class ParsedEventDateTime:
    start: datetime | None
    end: datetime | None


DATE_PATTERN = re.compile(
    r"(?P<year>\d{4})[.\-/](?P<month>\d{1,2})[.\-/](?P<day>\d{1,2})"
    r"(?:\s+(?P<start_hour>\d{1,2}):(?P<start_minute>\d{2}))?"
    r"(?:\s*~\s*(?P<end_hour>\d{1,2}):(?P<end_minute>\d{2}))?"
)


# 날짜 추출: 원문 날짜, 본문, 제목 순서로 명확한 숫자형 날짜를 찾습니다.
def parse_event_datetime(
    raw_date_text: str | None,
    raw_body: str | None,
    raw_title: str | None,
    fetched_at: datetime,
) -> ParsedEventDateTime:
    del fetched_at
    for source_text in (raw_date_text, raw_body, raw_title):
        if source_text is None:
            continue
        match = DATE_PATTERN.search(source_text)
        if match is None:
            continue
        return _build_datetime(match)
    return ParsedEventDateTime(start=None, end=None)


# datetime 생성: 시간 정보가 없으면 자정 시작으로 보수적으로 저장합니다.
def _build_datetime(match: re.Match[str]) -> ParsedEventDateTime:
    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    start_hour = int(match.group("start_hour") or 0)
    start_minute = int(match.group("start_minute") or 0)
    start = datetime(year, month, day, start_hour, start_minute, tzinfo=UTC)

    if match.group("end_hour") is None:
        return ParsedEventDateTime(start=start, end=None)

    end = datetime(
        year,
        month,
        day,
        int(match.group("end_hour") or 0),
        int(match.group("end_minute") or 0),
        tzinfo=UTC,
    )
    return ParsedEventDateTime(start=start, end=end)
