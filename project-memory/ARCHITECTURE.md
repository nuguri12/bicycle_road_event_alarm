# Architecture

Last updated: 2026-07-05

## System Shape

This is a Cloudflare-triggered scheduled batch service, not a long-running server.

GitHub Actions runs a Python CLI pipeline:

```text
public sources
  -> ingest_raw_events
  -> raw_events
  -> normalize_events --run-id
  -> normalized_events
  -> KST same-day publish candidate filter
  -> generate_messages --run-id
  -> OpenAI or fallback message
  -> Telegram publisher
  -> publish_attempts
```

## Major Components

- `crawler`: fetches and parses source pages into raw event candidates.
- `normalization`: converts raw events into deterministic normalized event rows.
- `messaging`: builds message DTOs, generates OpenAI/fallback messages, handles Telegram publishing, and records publish attempts.
- `db`: SQLAlchemy models, engine/session helpers, migrations.
- `cli`: executable batch entry points.
- `.github/workflows/manual-batch.yml`: CI validation plus runtime batch orchestration.

## Runtime Sources

Current runtime ingestion uses:

- Hangang park events
- Hangang park notices via Seoulboard JSON API (`bbsNo=5211`)
- Ara Waterway notices via official K-water 경인아라뱃길 notice URL

SPATIC parser code remains in the repository for reference/regression, but runtime ingestion no longer calls SPATIC.

## External Services

- Supabase PostgreSQL stores run logs, raw events, normalized events, and publish attempts.
- OpenAI is used for message generation when publishable events exist and API configuration is available.
- Telegram Bot API publishes the generated message to a private channel.
- Cloudflare Workers Cron schedules the production batch.
- GitHub Actions runs the batch through `workflow_dispatch`.

## Failure Semantics

- Full source outage:
  - Ingest exits successfully but records `source_unavailable`.
  - Message context becomes `source_unavailable`.
  - User-facing fallback says events could not be checked.
- Partial source outage:
  - Ingest records `partial_source_unavailable`.
  - Message context stays visible in CLI/DB.
  - User-facing no-event message does not mention the auxiliary outage.
- True no-event:
  - Ingest succeeds without source outage.
  - No KST same-day publishable normalized events are found.
  - A dated KST no-event fallback message is generated.

## Safety Defaults

Manual workflow dispatch is safe by default: dry-run and Telegram publishing disabled.

Cloudflare-triggered workflow dispatches are production mode by design: Telegram publishing enabled and dry-run disabled.
