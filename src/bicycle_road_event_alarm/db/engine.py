from __future__ import annotations

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from bicycle_road_event_alarm.config.settings import AppSettings


# 드라이버 정규화: Supabase 기본 URL을 설치된 psycopg 드라이버 형식으로 맞춥니다.
def normalize_database_url(database_url: str) -> str:
    if "[" in database_url or "]" in database_url:
        raise ValueError(
            "SUPABASE_DATABASE_URL contains bracket placeholders; replace them with the "
            "actual password or URL-encode literal bracket characters"
        )

    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    return database_url


# 엔진 생성: Supabase PostgreSQL 접속 문자열이 있을 때만 SQLAlchemy engine을 만듭니다.
def create_engine_from_settings(settings: AppSettings) -> Engine:
    if settings.supabase_database_url is None:
        raise ValueError("SUPABASE_DATABASE_URL is required to create a database engine")

    return create_engine(normalize_database_url(settings.supabase_database_url), pool_pre_ping=True)


# 세션 팩토리: 배치 작업과 테스트에서 동일한 방식으로 DB 세션을 생성합니다.
def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
