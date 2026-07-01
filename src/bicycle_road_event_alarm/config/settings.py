from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


# 설정 모델: 배치 실행에 필요한 환경 변수 값을 한곳에서 다룹니다.
@dataclass(frozen=True)
class AppSettings:
    app_env: str
    log_level: str
    enable_telegram_publish: bool
    dry_run: bool
    alert_lookahead_days: int
    max_events_per_message: int
    request_timeout_seconds: int
    crawler_max_retries: int
    supabase_url: str | None
    supabase_anon_key: str | None
    supabase_database_url: str | None
    telegram_bot_token: str | None
    telegram_channel_id: str | None
    openai_api_key: str | None


# 문자열 변환: 환경 변수의 boolean 값을 명확하게 해석합니다.
def _parse_bool(name: str, value: str) -> bool:
    normalized_value = value.strip().lower()
    if normalized_value in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized_value in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value")


# 숫자 검증: 음수나 0으로 인해 배치가 비정상 동작하지 않게 막습니다.
def _parse_positive_int(name: str, value: str) -> int:
    try:
        parsed_value = int(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be an integer") from exc

    if parsed_value <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return parsed_value


# 선택값 정리: 빈 문자열은 미설정 값으로 취급합니다.
def _optional_value(env: Mapping[str, str], name: str) -> str | None:
    value = env.get(name)
    if value is None or value.strip() == "":
        return None
    return value.strip()


# 설정 로딩: 기본값은 안전 모드이며 실제 발송은 명시적으로 켜야 합니다.
def load_settings(env: Mapping[str, str] | None = None) -> AppSettings:
    source_env = os.environ if env is None else env

    return AppSettings(
        app_env=source_env.get("APP_ENV", "local").strip().lower(),
        log_level=source_env.get("LOG_LEVEL", "INFO").strip().upper(),
        enable_telegram_publish=_parse_bool(
            "ENABLE_TELEGRAM_PUBLISH", source_env.get("ENABLE_TELEGRAM_PUBLISH", "false")
        ),
        dry_run=_parse_bool("DRY_RUN", source_env.get("DRY_RUN", "true")),
        alert_lookahead_days=_parse_positive_int(
            "ALERT_LOOKAHEAD_DAYS", source_env.get("ALERT_LOOKAHEAD_DAYS", "14")
        ),
        max_events_per_message=_parse_positive_int(
            "MAX_EVENTS_PER_MESSAGE", source_env.get("MAX_EVENTS_PER_MESSAGE", "5")
        ),
        request_timeout_seconds=_parse_positive_int(
            "REQUEST_TIMEOUT_SECONDS", source_env.get("REQUEST_TIMEOUT_SECONDS", "30")
        ),
        crawler_max_retries=_parse_positive_int(
            "CRAWLER_MAX_RETRIES", source_env.get("CRAWLER_MAX_RETRIES", "3")
        ),
        supabase_url=_optional_value(source_env, "SUPABASE_URL"),
        supabase_anon_key=_optional_value(source_env, "SUPABASE_ANON_KEY"),
        supabase_database_url=_optional_value(source_env, "SUPABASE_DATABASE_URL"),
        telegram_bot_token=_optional_value(source_env, "TELEGRAM_BOT_TOKEN"),
        telegram_channel_id=_optional_value(source_env, "TELEGRAM_CHANNEL_ID"),
        openai_api_key=_optional_value(source_env, "OPENAI_API_KEY"),
    )


# 런타임 점검: 실제 발송/운영에 필요한 사용자 입력값을 실행 전에 확인합니다.
def missing_runtime_secrets(settings: AppSettings) -> tuple[str, ...]:
    required_values = [("SUPABASE_DATABASE_URL", settings.supabase_database_url)]

    if settings.enable_telegram_publish and not settings.dry_run:
        required_values.extend(
            [
                ("TELEGRAM_BOT_TOKEN", settings.telegram_bot_token),
                ("TELEGRAM_CHANNEL_ID", settings.telegram_channel_id),
            ]
        )

    required_values.append(("OPENAI_API_KEY", settings.openai_api_key))

    return tuple(name for name, value in required_values if value is None)
