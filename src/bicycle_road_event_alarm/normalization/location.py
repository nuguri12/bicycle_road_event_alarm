from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ExtractedLocation:
    location_name: str | None
    region: str | None
    reason: str | None


SEOUL_KEYWORDS = (
    "한강",
    "잠실",
    "뚝섬",
    "반포",
    "여의도",
    "망원",
    "광나루",
    "청계천",
    "중랑천",
    "안양천",
)
GYEONGGI_KEYWORDS = ("고양", "하남", "구리", "남양주", "성남", "과천", "안양", "광명", "부천")
ARA_WATERWAY_LOCATION_KEYWORDS = (
    "아라",
    "계양대교",
    "시천교",
    "귤현대교",
    "목상교",
    "청운교",
    "벌말교",
    "굴포천",
    "수향원",
)
ARA_FACILITY_PATTERN = re.compile(r"-\(([^)]+)\)")
MAX_ARA_FACILITY_NAMES = 4


# 장소 추출: raw_location_text를 우선하고, 없으면 본문과 제목에서 주요 지명을 찾습니다.
def extract_location(
    raw_location_text: str | None,
    raw_body: str | None,
    raw_title: str | None,
) -> ExtractedLocation:
    if raw_location_text is not None:
        text = " ".join(raw_location_text.split())
        if text != "":
            region = _detect_region(text)
            if region is not None:
                return ExtractedLocation(
                    location_name=text,
                    region=region,
                    reason=f"{region} 주요 지명 감지",
                )
            if _is_ara_waterway_location(text):
                return ExtractedLocation(
                    location_name=text,
                    region="경기",
                    reason="아라뱃길 구간명 감지",
                )

    for source_text in (raw_body, raw_title):
        if source_text is None:
            continue
        text = " ".join(source_text.split())
        if text == "":
            continue
        ara_facility_location = _extract_ara_facility_location(text)
        if ara_facility_location is not None:
            return ExtractedLocation(
                location_name=ara_facility_location,
                region="경기",
                reason="아라뱃길 친수시설 구간명 감지",
            )
        region = _detect_region(text)
        if region is not None:
            return ExtractedLocation(
                location_name=text,
                region=region,
                reason=f"{region} 주요 지명 감지",
            )
    return ExtractedLocation(
        location_name=None,
        region=None,
        reason="구체적 장소 확인 필요",
    )


# 지역 판단: MVP는 서울/경기 주요 자전거 이동권 키워드를 우선 감지합니다.
def _detect_region(text: str) -> str | None:
    if any(keyword in text for keyword in SEOUL_KEYWORDS):
        return "서울"
    if any(keyword in text for keyword in GYEONGGI_KEYWORDS):
        return "경기"
    return None


def _is_ara_waterway_location(text: str) -> bool:
    return any(keyword in text for keyword in ARA_WATERWAY_LOCATION_KEYWORDS)


def _extract_ara_facility_location(text: str) -> str | None:
    if not _is_ara_waterway_location(text):
        return None

    names: list[str] = []
    for match in ARA_FACILITY_PATTERN.finditer(text):
        name = " ".join(match.group(1).split())
        if name == "" or name in names:
            continue
        if _is_ara_waterway_location(name) or "자전거도로" in name:
            names.append(name)

    if not names:
        return None

    displayed_names = names[:MAX_ARA_FACILITY_NAMES]
    suffix = " 등" if len(names) > MAX_ARA_FACILITY_NAMES else ""
    return f"아라뱃길 친수시설({', '.join(displayed_names)}{suffix})"
