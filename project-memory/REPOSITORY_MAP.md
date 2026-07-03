# Repository Map

Last updated: 2026-07-03

## Entry Points

- `src/bicycle_road_event_alarm/cli/ingest_raw_events.py`
- `src/bicycle_road_event_alarm/cli/normalize_events.py`
- `src/bicycle_road_event_alarm/cli/generate_messages.py`
- `src/bicycle_road_event_alarm/cli/seed_publishable_fixture.py`

## Runtime Workflow

- `.github/workflows/manual-batch.yml`
- Tests for workflow assumptions: `tests/unit/test_github_actions_workflow.py`

## Database

- Models: `src/bicycle_road_event_alarm/db/models.py`
- Engine/session: `src/bicycle_road_event_alarm/db/engine.py`
- Migrations: `migrations/versions/`
- Alembic config: `alembic.ini`, `migrations/env.py`

## Crawling

- Multi-source orchestration: `src/bicycle_road_event_alarm/crawler/multi_source_ingestion.py`
- HTTP wrapper: `src/bicycle_road_event_alarm/crawler/http.py`
- Hangang parser: `src/bicycle_road_event_alarm/crawler/hangang.py`
- Ara Waterway parser: `src/bicycle_road_event_alarm/crawler/ara_waterway.py`
- SPATIC reference parser: `src/bicycle_road_event_alarm/crawler/spatic.py`
- Crawler tests: `tests/unit/crawler/`
- HTML fixtures: `tests/fixtures/crawler/`

## Normalization

- Normalizer modules: `src/bicycle_road_event_alarm/normalization/`
- Normalization tests: `tests/unit/normalization/`

## Messaging And Publishing

- Message service: `src/bicycle_road_event_alarm/messaging/service.py`
- Fallback generator: `src/bicycle_road_event_alarm/messaging/fallback_generator.py`
- OpenAI wrapper: `src/bicycle_road_event_alarm/messaging/openai_generator.py`
- Telegram publisher: `src/bicycle_road_event_alarm/messaging/telegram_publisher.py`
- Publish dedupe/history: `src/bicycle_road_event_alarm/messaging/publish_service.py`, `publish_history.py`
- Messaging tests: `tests/unit/messaging/`

## Configuration

- Settings loader: `src/bicycle_road_event_alarm/config/settings.py`
- Local env example: `.env.example`
- Local real `.env` exists but is ignored by Git. Do not print or commit secrets.

## Existing Docs

- Main README: `README.md`
- Previous handoff: `docs/handoff-current-status.md`
- Risk review: `docs/remaining-risk-opinion.md`
- Sprint docs: `docs/sprint*/`

Some older docs may be stale or contain mojibake. Prefer this `project-memory/` directory for current navigation and state.
