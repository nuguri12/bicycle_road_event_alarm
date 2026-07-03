import importlib.util
from pathlib import Path

from bicycle_road_event_alarm.db.models import Base

MIGRATION_VERSION_PATH = Path("migrations/versions")


def test_initial_migration_revision_matches_model_tables() -> None:
    migration_path = Path("migrations/versions/0001_initial_schema.py")
    spec = importlib.util.spec_from_file_location("initial_schema", migration_path)

    assert spec is not None
    assert spec.loader is not None

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.revision == "0001_initial_schema"
    assert set(module.MVP_TABLE_NAMES) == set(Base.metadata.tables)


def test_migration_revision_ids_fit_alembic_version_column() -> None:
    for migration_path in MIGRATION_VERSION_PATH.glob("*.py"):
        if migration_path.name == "__init__.py":
            continue

        spec = importlib.util.spec_from_file_location(migration_path.stem, migration_path)
        assert spec is not None
        assert spec.loader is not None

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert len(module.revision) <= 32, migration_path.name
