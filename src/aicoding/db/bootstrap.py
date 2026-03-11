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
        # Tests repeatedly rebuild the shared public schema. Terminate sibling
        # sessions first so cleanup does not race against stale pooled or
        # idle-in-transaction connections that still reference public objects.
        connection.execute(
            text(
                """
                select pg_terminate_backend(pid)
                from pg_stat_activity
                where datname = current_database()
                  and usename = current_user
                  and pid <> pg_backend_pid()
                """
            )
        )
        # Preserve the public schema itself. Recreating the namespace can leave
        # a migrated catalog state where pg_class/to_regclass see relations but
        # ordinary SELECT/INSERT on those same public tables fail.
        connection.execute(text("create schema if not exists public"))
        connection.execute(text("drop owned by current_user cascade"))
        connection.execute(text("create schema if not exists public"))
        connection.execute(text("grant all on schema public to public"))
