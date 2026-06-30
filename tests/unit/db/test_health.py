from sqlalchemy import create_engine

from bicycle_road_event_alarm.db.health import check_database_connection


def test_check_database_connection_executes_select_one() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")

    with engine.connect() as connection:
        assert check_database_connection(connection) is True
