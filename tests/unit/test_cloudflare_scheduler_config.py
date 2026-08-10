from pathlib import Path


def test_cloudflare_scheduler_persists_worker_logs() -> None:
    config = Path("cloudflare/scheduler/wrangler.toml").read_text()

    assert "[observability]" in config
    assert "enabled = true" in config
    assert "head_sampling_rate = 1" in config
