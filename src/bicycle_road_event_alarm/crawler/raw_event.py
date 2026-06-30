from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


# 해시 입력 정리: 공백 차이만 있는 원문은 같은 이벤트 후보로 취급합니다.
def _normalize_hash_part(value: str | None) -> str:
    if value is None:
        return ""
    return " ".join(value.split())


# 중복 키 생성: 출처와 원문 URL, 제목, 본문을 기준으로 안정적인 content_hash를 만듭니다.
def build_content_hash(
    *,
    source_name: str,
    source_url: str,
    raw_title: str | None,
    raw_body: str | None,
) -> str:
    hash_input = "\n".join(
        (
            _normalize_hash_part(source_name),
            _normalize_hash_part(source_url),
            _normalize_hash_part(raw_title),
            _normalize_hash_part(raw_body),
        )
    )
    return hashlib.sha256(hash_input.encode("utf-8")).hexdigest()


# 원문 이벤트 후보: 크롤러가 추출한 값을 정규화 전 단계에서 보존합니다.
@dataclass(frozen=True)
class RawEventCandidate:
    source_name: str
    source_url: str
    raw_title: str | None
    raw_body: str | None
    raw_date_text: str | None
    raw_location_text: str | None
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "content_hash",
            build_content_hash(
                source_name=self.source_name,
                source_url=self.source_url,
                raw_title=self.raw_title,
                raw_body=self.raw_body,
            ),
        )
