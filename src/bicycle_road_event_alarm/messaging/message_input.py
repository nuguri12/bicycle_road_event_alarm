from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from bicycle_road_event_alarm.db.models import NormalizedEvent


@dataclass(frozen=True)
class MessageEvent:
    title: str
    start_datetime: datetime
    end_datetime: datetime | None
    location_name: str
    region: str
    event_type: str
    cyclist_impact_level: str
    cyclist_impact_reason: str | None
    source_url: str


@dataclass(frozen=True)
class GeneratedMessage:
    text: str
    source: str
    status: str
    event_count: int


# 메시지 입력 변환: DB 모델에서 알림 생성에 필요한 필드만 추립니다.
def message_event_from_model(event: NormalizedEvent, *, source_url: str) -> MessageEvent:
    return MessageEvent(
        title=event.title,
        start_datetime=event.start_datetime,
        end_datetime=event.end_datetime,
        location_name=event.location_name,
        region=event.region,
        event_type=event.event_type,
        cyclist_impact_level=event.cyclist_impact_level,
        cyclist_impact_reason=event.cyclist_impact_reason,
        source_url=source_url,
    )
