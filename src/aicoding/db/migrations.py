from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy.engine import Engine

from aicoding.db.session import current_alembic_revision

REVISION_ID_PATTERN = re.compile(r"^\d{4}_[a-z0-9_]+$")
ALEMBIC_INI_PATH = Path("alembic.ini")
VERSIONS_PATH = Path("alembic/versions")


def create_alembic_config(path: str | Path = ALEMBIC_INI_PATH) -> Config:
    return Config(str(path))


@lru_cache(maxsize=4)
def _cached_expected_revision(config_path: str) -> str | None:
    script = ScriptDirectory.from_config(create_alembic_config(config_path))
    heads = script.get_heads()
    if not heads:
        return None
    if len(heads) != 1:
        raise RuntimeError(f"Expected a single Alembic head, found {len(heads)}: {heads}")
    return heads[0]


def list_revision_files(versions_path: Path = VERSIONS_PATH) -> list[Path]:
    return sorted(path for path in versions_path.glob("*.py") if path.name != "__init__.py")


def list_revision_ids(versions_path: Path = VERSIONS_PATH) -> list[str]:
    return [path.stem for path in list_revision_files(versions_path)]


def validate_revision_identifiers(versions_path: Path = VERSIONS_PATH) -> list[str]:
    invalid = []
    for revision_id in list_revision_ids(versions_path):
        if not REVISION_ID_PATTERN.match(revision_id):
            invalid.append(revision_id)
    return invalid


def expected_database_revision(config: Config | None = None) -> str | None:
    if config is None:
        return _cached_expected_revision(str(ALEMBIC_INI_PATH))

    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    if not heads:
        return None
    if len(heads) != 1:
        raise RuntimeError(f"Expected a single Alembic head, found {len(heads)}: {heads}")
    return heads[0]


def migration_status(engine: Engine, config: Config | None = None) -> dict[str, object]:
    current_revision = current_alembic_revision(engine)
    expected_revision = expected_database_revision(config)
    if current_revision is None:
        status = "uninitialized"
    elif current_revision == expected_revision:
        status = "up_to_date"
    else:
        status = "outdated"

    return {
        "current_revision": current_revision,
        "expected_revision": expected_revision,
        "status": status,
        "compatible": current_revision == expected_revision,
    }


def migration_history(config: Config | None = None) -> list[str]:
    active_config = config or create_alembic_config()
    script = ScriptDirectory.from_config(active_config)
    return [revision.revision for revision in reversed(list(script.walk_revisions(base="base", head="heads")))]


def upgrade_database(revision: str = "head", *, config: Config | None = None) -> None:
    command.upgrade(config or create_alembic_config(), revision)


def downgrade_database(revision: str = "base", *, config: Config | None = None) -> None:
    command.downgrade(config or create_alembic_config(), revision)
