from __future__ import annotations

from sqlalchemy import Connection, Engine, text


# 연결 확인: 가장 작은 쿼리로 DB 연결과 인증 상태를 검증합니다.
def check_database_connection(connection: Connection) -> bool:
    result = connection.execute(text("SELECT 1")).scalar_one()
    return bool(result == 1)


# 엔진 확인: 실제 Supabase 연결 검증용으로 connection 생명주기를 감쌉니다.
def check_database_engine(engine: Engine) -> bool:
    with engine.connect() as connection:
        return check_database_connection(connection)
