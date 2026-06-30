import pytest

from bicycle_road_event_alarm.config.settings import load_settings, missing_runtime_secrets


def test_load_settings_uses_safe_defaults() -> None:
    settings = load_settings({})

    assert settings.app_env == "local"
    assert settings.log_level == "INFO"
    assert settings.enable_telegram_publish is False
    assert settings.dry_run is True
    assert settings.alert_lookahead_days == 14
    assert settings.max_events_per_message == 5
    assert settings.request_timeout_seconds == 15
    assert settings.crawler_max_retries == 2


def test_load_settings_rejects_invalid_boolean() -> None:
    with pytest.raises(ValueError, match="ENABLE_TELEGRAM_PUBLISH"):
        load_settings({"ENABLE_TELEGRAM_PUBLISH": "maybe"})


def test_missing_runtime_secrets_reports_required_values_for_real_publish() -> None:
    settings = load_settings({"ENABLE_TELEGRAM_PUBLISH": "true", "DRY_RUN": "false"})

    assert missing_runtime_secrets(settings) == (
        "SUPABASE_DATABASE_URL",
        "TELEGRAM_BOT_TOKEN",
        "TELEGRAM_CHANNEL_ID",
        "OPENAI_API_KEY",
    )
