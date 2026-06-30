from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from bicycle_road_event_alarm.config.settings import load_settings
from bicycle_road_event_alarm.db.engine import normalize_database_url
from bicycle_road_event_alarm.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

load_dotenv()

target_metadata = Base.metadata


# DB URL 주입: Alembic 설정 파일에는 비밀값을 저장하지 않고 .env에서 읽습니다.
def database_url() -> str:
    settings = load_settings()
    if settings.supabase_database_url is None:
        raise ValueError("SUPABASE_DATABASE_URL is required to run migrations")
    return normalize_database_url(settings.supabase_database_url)


# 오프라인 마이그레이션: SQL 출력 모드에서도 동일한 metadata를 사용합니다.
def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# 온라인 마이그레이션: Supabase PostgreSQL에 직접 연결해 revision을 적용합니다.
def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
