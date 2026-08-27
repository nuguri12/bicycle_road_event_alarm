# Cloudflare Scheduler

This Worker is the backup daily trigger for the production GitHub Actions batch.
GitHub Actions native `schedule` remains the primary trigger, but GitHub
scheduled events are best-effort and may be dropped, so this Worker dispatches
the same workflow a few minutes later.

Current production URL:

```text
https://bicycle-road-event-alarm-scheduler.matthew-dev.workers.dev
```

## Schedule

Cloudflare cron is enabled as a backup trigger at 07:45 KST.

```toml
crons = ["45 22 * * *"]
```

The production GitHub Actions schedule is `30 22 * * *`, which runs every day at
07:30 KST. Both paths use deterministic fallback message generation so the
existing successful-message hash guard can skip duplicate sends if both triggers
run on the same day.

## GitHub Token

Create a fine-grained GitHub personal access token:

- Repository access: `nuguri12/bicycle_road_event_alarm`
- Repository permissions: `Actions: Read and write`

Set it as a Cloudflare Worker secret. Do not commit it to the repository.

```powershell
cd D:\Workspace\bicycle_road_event_alarm\cloudflare\scheduler
npm install
npx wrangler login
npx wrangler secret put GITHUB_TOKEN
npx wrangler deploy
```

Verify that the secret exists before relying on the diagnostic endpoints:

```powershell
npx wrangler secret list
```

Expected output should include `GITHUB_TOKEN` only if Cloudflare diagnostics are
still being used. Production scheduling no longer depends on this secret.

## Smoke Trigger Token

The Worker also exposes an authenticated internal smoke endpoint for manually
verifying the GitHub dispatch path:

```text
POST /__internal/run-scheduled
Authorization: Bearer <SMOKE_TRIGGER_TOKEN>
```

Set `SMOKE_TRIGGER_TOKEN` as a Cloudflare Worker secret. Do not commit it.

```powershell
npx wrangler secret put SMOKE_TRIGGER_TOKEN
```

## Dispatch Payload

The Worker dispatches `.github/workflows/manual-batch.yml` on `main` with:

```json
{
  "dry_run": "false",
  "enable_telegram_publish": "true",
  "force_fallback": "true",
  "apply_migrations": "false"
}
```

## Verification

After deployment:

1. In Cloudflare, open the Worker.
2. Confirm Cron Triggers include `45 22 * * *`.
3. Confirm GitHub Actions still owns the primary daily `schedule` run.
4. Confirm the run logs include `TELEGRAM_STATUS=success`.

For an immediate production smoke test, call the internal endpoint with the
smoke token and confirm that GitHub Actions creates a new `workflow_dispatch`
run.
