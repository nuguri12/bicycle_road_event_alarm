from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from bicycle_road_event_alarm.db.models import RawEvent
from bicycle_road_event_alarm.normalization.classifier import classify_event
from bicycle_road_event_alarm.normalization.datetime import parse_event_datetime
from bicycle_road_event_alarm.normalization.location import extract_location
from bicycle_road_event_alarm.normalization.title import normalize_title

KST = ZoneInfo("Asia/Seoul")


@dataclass(frozen=True)
class NormalizedEventData:
    raw_event_id: uuid.UUID
    title: str
    start_datetime: datetime
    end_datetime: datetime | None
    location_name: str
    region: str
    event_type: str
    cyclist_impact_level: str
    cyclist_impact_reason: str | None
    publish_candidate: bool
    deterministic_duplicate_key: str
    validation_status: str


# 정규화 조합: 원문 이벤트 하나를 normalized_events 저장 데이터로 변환합니다.
def normalize_raw_event(raw_event: RawEvent) -> NormalizedEventData:
    title = normalize_title(raw_event.raw_title, raw_event.raw_body) or "제목 확인 필요"
    parsed_datetime = parse_event_datetime(
        raw_event.raw_date_text,
        raw_event.raw_body,
        raw_event.raw_title,
        raw_event.fetched_at,
    )
    location = extract_location(
        raw_event.raw_location_text,
        raw_event.raw_body,
        raw_event.raw_title,
    )
    classification = classify_event(title, raw_event.raw_body)

    validation_status = _validation_status(parsed_datetime.start, location.location_name)
    start_datetime = parsed_datetime.start or raw_event.fetched_at or datetime.now(UTC)
    location_name = location.location_name or "장소 확인 필요"
    region = location.region or "unknown"
    duplicate_key = build_duplicate_key(title, start_datetime, location_name, region)
    publish_candidate = (
        validation_status == "valid"
        and classification.publish_candidate_impact
        and classification.cyclist_impact_level in {"low", "medium", "high"}
        and _is_active_on_fetched_kst_date(
            start_datetime, parsed_datetime.end, raw_event.fetched_at
        )
    )

    return NormalizedEventData(
        raw_event_id=raw_event.id,
        title=title,
        start_datetime=start_datetime,
        end_datetime=parsed_datetime.end,
        location_name=location_name,
        region=region,
        event_type=classification.event_type,
        cyclist_impact_level=classification.cyclist_impact_level,
        cyclist_impact_reason=classification.cyclist_impact_reason,
        publish_candidate=publish_candidate,
        deterministic_duplicate_key=duplicate_key,
        validation_status=validation_status,
    )


# 검증 상태: 날짜 누락은 invalid, 장소 누락은 needs_review로 구분합니다.
def _validation_status(start_datetime: datetime | None, location_name: str | None) -> str:
    if start_datetime is None:
        return "invalid"
    if location_name is None:
        return "needs_review"
    return "valid"


def _is_active_on_fetched_kst_date(
    start_datetime: datetime,
    end_datetime: datetime | None,
    fetched_at: datetime | None,
) -> bool:
    기준시각 = fetched_at or datetime.now(UTC)
    if 기준시각.tzinfo is None:
        기준시각 = 기준시각.replace(tzinfo=UTC)

    target_date = 기준시각.astimezone(KST).date()
    start_date = start_datetime.astimezone(KST).date()
    if end_datetime is None:
        return start_date == target_date

    end_date = end_datetime.astimezone(KST).date()
    return start_date <= target_date <= end_date


# 중복 키 생성: 제목, 날짜, 장소, 지역을 낮은 변동성의 키로 정리합니다.
def build_duplicate_key(
    title: str,
    start_datetime: datetime,
    location_name: str,
    region: str,
) -> str:
    title_key = _normalize_key_text(title)
    location_key = _normalize_key_text(location_name)
    return f"{title_key}|{start_datetime.date().isoformat()}|{location_key}|{region}"


def _normalize_key_text(value: str) -> str:
    cleaned = re.sub(r"[\[\]().,]", " ", value.lower())
    return " ".join(cleaned.split())
