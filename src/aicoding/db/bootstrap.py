from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from aicoding.db.migrations import migration_status
from aicoding.db.session import current_alembic_revision, probe_database


def database_status(engine: Engine) -> dict[str, object]:
    inspector = inspect(engine)
    details = probe_database(engine)
    details["tables"] = sorted(inspector.get_table_names())
    details["views"] = sorted(inspector.get_view_names())
    details["alembic_revision"] = current_alembic_revision(engine)
    details["migration"] = migration_status(engine)
    return details


def reset_public_schema(engine: Engine) -> None:
    with engine.begin() as connection:
        connection.execute(text("drop schema if exists public cascade"))
        connection.execute(text("create schema public"))
        connection.execute(text("grant all on schema public to public"))
