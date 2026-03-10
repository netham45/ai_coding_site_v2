from __future__ import annotations

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from aicoding.db.base import SQLALCHEMY_NAMING_CONVENTION
from aicoding.db.session import (
    SessionUsageError,
    create_engine_from_settings,
    current_alembic_revision,
    nested_transaction,
    probe_database,
    query_session_scope,
    session_scope,
)


def _create_probe_table(db_engine, schema_name: str) -> str:
    table_name = "session_probe"
    with db_engine.begin() as connection:
        connection.execute(text(f'create table "{schema_name}"."{table_name}" (value integer not null)'))
    return f'"{schema_name}"."{table_name}"'


def test_base_metadata_uses_naming_convention() -> None:
    assert SQLALCHEMY_NAMING_CONVENTION["pk"] == "pk_%(table_name)s"
    assert SQLALCHEMY_NAMING_CONVENTION["fk"] == "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"


def test_probe_database_returns_connection_details() -> None:
    details = probe_database()
    assert details["database_name"] == "aicoding"
    assert details["current_user"] == "aicoding"
    assert "PostgreSQL" in details["server_version"]


def test_current_revision_is_none_before_migration(clean_public_schema) -> None:
    assert current_alembic_revision(clean_public_schema) is None


def test_create_engine_from_settings_raises_for_bad_url(monkeypatch) -> None:
    monkeypatch.setenv("AICODING_DATABASE_URL", "postgresql+psycopg://aicoding:wrong@localhost:5432/aicoding")
    engine = create_engine_from_settings()

    with pytest.raises(OperationalError):
        probe_database(engine)

    engine.dispose()


def test_session_scope_rolls_back_on_error(db_engine) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    with pytest.raises(RuntimeError):
        with session_scope(factory) as session:
            session.execute(text("create temporary table session_scope_check (value integer)"))
            session.execute(text("insert into session_scope_check(value) values (1)"))
            raise RuntimeError("force rollback")

    with session_scope(factory) as session:
        count = session.execute(text("select count(*) from pg_tables where tablename = 'session_scope_check'")).scalar_one()
    assert count == 0


def test_session_scope_commits_successful_transaction(db_engine, isolated_schema) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    table_name = _create_probe_table(db_engine, isolated_schema)

    with session_scope(factory) as session:
        session.execute(text(f"insert into {table_name}(value) values (1)"))

    with query_session_scope(factory) as session:
        count = session.execute(text(f"select count(*) from {table_name}")).scalar_one()

    assert count == 1


def test_query_session_scope_can_be_used_for_read_only_queries(db_engine) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    with query_session_scope(factory) as session:
        result = session.execute(text("select 1")).scalar_one()

    assert result == 1


def test_nested_transaction_rolls_back_inner_savepoint_only(db_engine, isolated_schema) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)
    table_name = _create_probe_table(db_engine, isolated_schema)

    with session_scope(factory) as session:
        session.execute(text(f"insert into {table_name}(value) values (1)"))
        with pytest.raises(RuntimeError):
            with nested_transaction(session):
                session.execute(text(f"insert into {table_name}(value) values (2)"))
                raise RuntimeError("rollback savepoint")
        session.execute(text(f"insert into {table_name}(value) values (3)"))

    with query_session_scope(factory) as session:
        values = session.execute(text(f"select value from {table_name} order by value")).scalars().all()

    assert values == [1, 3]


def test_nested_transaction_requires_active_outer_transaction(db_engine) -> None:
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    with query_session_scope(factory) as session:
        with pytest.raises(SessionUsageError):
            with nested_transaction(session):
                session.execute(text("select 1"))
