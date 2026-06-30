from __future__ import annotations

import time
from typing import Protocol, cast

import requests


class HttpResponse(Protocol):
    status_code: int
    text: str

    def raise_for_status(self) -> None: ...


class HttpSession(Protocol):
    def get(self, url: str, *, timeout: int, headers: dict[str, str]) -> HttpResponse: ...


# HTTP 재시도 정책: 일시적인 서버/제한 오류만 재시도 대상으로 다룹니다.
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}
DEFAULT_USER_AGENT = "bicycle-road-event-alarm/0.1"


# HTTP 클라이언트: 크롤러가 requests 구현 세부사항에 직접 의존하지 않게 감쌉니다.
class HttpClient:
    def __init__(
        self,
        *,
        session: HttpSession | None = None,
        timeout_seconds: int = 10,
        max_retries: int = 2,
        retry_sleep_seconds: float = 2.0,
        user_agent: str = DEFAULT_USER_AGENT,
    ) -> None:
        self._session = cast(HttpSession, requests.Session() if session is None else session)
        self._timeout_seconds = timeout_seconds
        self._max_retries = max_retries
        self._retry_sleep_seconds = retry_sleep_seconds
        self._headers = {"User-Agent": user_agent}

    def get_text(self, url: str) -> str:
        last_response: HttpResponse | None = None

        for attempt_index in range(self._max_retries + 1):
            response = self._session.get(
                url,
                timeout=self._timeout_seconds,
                headers=self._headers,
            )
            last_response = response

            if response.status_code not in RETRY_STATUS_CODES:
                response.raise_for_status()
                return str(response.text)

            if attempt_index < self._max_retries:
                time.sleep(self._retry_sleep_seconds)

        if last_response is None:
            raise RuntimeError("HTTP request did not produce a response")

        last_response.raise_for_status()
        return str(last_response.text)
