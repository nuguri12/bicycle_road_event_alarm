from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ClassificationResult:
    event_type: str
    cyclist_impact_level: str
    cyclist_impact_reason: str
    publish_candidate_impact: bool


HIGH_IMPACT_KEYWORDS = (
    "교통통제",
    "전면 통제",
    "출입 제한",
    "우회",
    "자전거도로 통제",
    "통행 차단",
)
MEDIUM_IMPACT_KEYWORDS = ("축제", "대규모 행사", "공원 행사", "마라톤")
LOW_IMPACT_KEYWORDS = ("소규모 행사", "체험 행사", "안내 부스")


# 이벤트 분류: 자전거 이동에 영향을 줄 가능성이 높은 키워드를 우선 적용합니다.
def classify_event(title: str | None, body: str | None) -> ClassificationResult:
    text = f"{title or ''} {body or ''}"

    if any(keyword in text for keyword in HIGH_IMPACT_KEYWORDS):
        return ClassificationResult(
            event_type="road_closure",
            cyclist_impact_level="high",
            cyclist_impact_reason="교통통제 또는 우회 관련 표현 감지",
            publish_candidate_impact=True,
        )
    if any(keyword in text for keyword in MEDIUM_IMPACT_KEYWORDS):
        return ClassificationResult(
            event_type="public_event",
            cyclist_impact_level="medium",
            cyclist_impact_reason="행사 또는 축제 관련 표현 감지",
            publish_candidate_impact=True,
        )
    if any(keyword in text for keyword in LOW_IMPACT_KEYWORDS):
        return ClassificationResult(
            event_type="public_event",
            cyclist_impact_level="low",
            cyclist_impact_reason="소규모 행사 표현 감지",
            publish_candidate_impact=True,
        )
    return ClassificationResult(
        event_type="unknown",
        cyclist_impact_level="unknown",
        cyclist_impact_reason="자전거 이동 영향 판단 근거 부족",
        publish_candidate_impact=False,
    )
