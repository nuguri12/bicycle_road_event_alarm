from __future__ import annotations


# 제목 정리: 공백을 통일하고 제목이 없으면 본문 첫 문장을 후보로 사용합니다.
def normalize_title(raw_title: str | None, raw_body: str | None) -> str | None:
    candidate = raw_title if raw_title and raw_title.strip() else _first_sentence(raw_body)
    if candidate is None:
        return None
    normalized = " ".join(candidate.split())
    return normalized or None


# 본문 fallback: 제목이 비어 있을 때 과도하게 긴 본문 대신 첫 문장만 사용합니다.
def _first_sentence(raw_body: str | None) -> str | None:
    if raw_body is None:
        return None
    text = raw_body.strip()
    if text == "":
        return None
    for delimiter in (".", "。", "\n"):
        if delimiter in text:
            return text.split(delimiter, 1)[0]
    return text
