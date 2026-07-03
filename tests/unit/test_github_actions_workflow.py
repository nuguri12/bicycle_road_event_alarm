from __future__ import annotations

from pathlib import Path

WORKFLOW_PATH = Path(".github/workflows/manual-batch.yml")


def test_manual_batch_workflow_exists_with_safe_defaults() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert 'cron: "0 22 * * 4"' in workflow
    assert "Every Friday 07:00 KST" in workflow
    assert "dry_run:" in workflow
    assert 'default: "true"' in workflow
    assert "enable_telegram_publish:" in workflow
    assert 'default: "false"' in workflow
    assert "GitHub Actions cron uses UTC" in workflow


def test_scheduled_batch_enables_real_telegram_publish() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert (
        "ENABLE_TELEGRAM_PUBLISH: "
        "${{ github.event_name == 'schedule' && 'true' || inputs.enable_telegram_publish }}"
    ) in workflow
    assert (
        "DRY_RUN: ${{ github.event_name == 'schedule' && 'false' || inputs.dry_run }}" in workflow
    )
    assert "github.event_name == 'workflow_dispatch' && inputs.force_fallback == 'true'" in workflow


def test_manual_batch_workflow_runs_project_checks_and_batch_commands() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "python -m pytest -q" in workflow
    assert "python -m ruff check ." in workflow
    assert "python -m mypy src tests" in workflow
    assert "python -m black --check ." in workflow
    assert "python -m compileall src" in workflow
    assert "python -m alembic upgrade head" in workflow
    assert "python -m bicycle_road_event_alarm.cli.ingest_raw_events" in workflow
    assert "BATCH_RUN_ID=$batch_run_id" in workflow
    assert 'normalize_events --run-id "$BATCH_RUN_ID"' in workflow
    assert 'generate_messages --run-id "$BATCH_RUN_ID"' in workflow


def test_manual_batch_workflow_uses_secrets_for_external_services() -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "SUPABASE_DATABASE_URL: ${{ secrets.SUPABASE_DATABASE_URL }}" in workflow
    assert "OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}" in workflow
    assert "TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}" in workflow
    assert "TELEGRAM_CHANNEL_ID: ${{ secrets.TELEGRAM_CHANNEL_ID }}" in workflow
