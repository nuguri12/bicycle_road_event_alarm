from pathlib import Path


def test_cloudflare_scheduler_persists_worker_logs() -> None:
    config = Path("cloudflare/scheduler/wrangler.toml").read_text(encoding="utf-8")

    assert "[observability]" in config
    assert "enabled = true" in config
    assert "head_sampling_rate = 1" in config


def test_cloudflare_scheduler_cron_is_backup_daily_0215_kst() -> None:
    config = Path("cloudflare/scheduler/wrangler.toml").read_text(encoding="utf-8")

    assert 'crons = ["15 17 * * *"]' in config


def test_github_actions_native_schedule_is_daily_0200_kst() -> None:
    workflow = Path(".github/workflows/manual-batch.yml").read_text(encoding="utf-8")

    assert 'cron: "0 17 * * *"' in workflow
    assert "github.event_name == 'schedule' && 'true'" in workflow
    assert "github.event_name == 'schedule' && 'false'" in workflow
    assert "FORCE_FALLBACK: ${{ github.event_name == 'schedule' && 'true'" in workflow
