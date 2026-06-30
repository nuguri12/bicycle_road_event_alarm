from __future__ import annotations

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


# 장소 추출: raw_location_text를 우선하고, 없으면 본문과 제목에서 주요 지명을 찾습니다.
def extract_location(
    raw_location_text: str | None,
    raw_body: str | None,
    raw_title: str | None,
) -> ExtractedLocation:
    for source_text in (raw_location_text, raw_body, raw_title):
        if source_text is None:
            continue
        text = " ".join(source_text.split())
        if text == "":
            continue
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
