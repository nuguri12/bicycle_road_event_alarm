# Cloudflare Scheduler

This Worker replaces GitHub Actions native `schedule` for production runs.
Cloudflare Cron Triggers call the existing GitHub Actions `workflow_dispatch`
entry point once per day.

## Schedule

Cloudflare cron uses UTC.

```toml
crons = ["30 22 * * *"]
```

This runs every day at 07:30 KST.

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

## Dispatch Payload

The Worker dispatches `.github/workflows/manual-batch.yml` on `main` with:

```json
{
  "dry_run": "false",
  "enable_telegram_publish": "true",
  "force_fallback": "false",
  "apply_migrations": "false"
}
```

## Verification

After deployment:

1. In Cloudflare, open the Worker.
2. Use the Cron Triggers test action, or wait for the next 07:30 KST run.
3. Confirm a GitHub Actions `workflow_dispatch` run is created.
4. Confirm the run logs include `TELEGRAM_STATUS=success`.
