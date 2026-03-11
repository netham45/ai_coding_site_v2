from __future__ import annotations

from uuid import uuid4

from sqlalchemy import create_engine, text

from aicoding.db.session import current_alembic_revision
from tests.helpers.e2e import (
    build_e2e_database_name,
    create_test_database,
    derive_admin_database_url,
    drop_test_database,
    migrate_test_database,
    reserve_local_listener,
)


def _database_exists(*, admin_url: str, database_name: str) -> bool:
    engine = create_engine(admin_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            return (
                connection.execute(
                    text("select 1 from pg_database where datname = :database_name"),
                    {"database_name": database_name},
                ).scalar_one_or_none()
                == 1
            )
    finally:
        engine.dispose()


def test_build_e2e_database_name_is_unique() -> None:
    first = build_e2e_database_name()
    second = build_e2e_database_name()

    assert first != second
    assert first.startswith("aicoding_e2e_")
    assert second.startswith("aicoding_e2e_")


def test_reserve_local_listener_returns_unique_bound_ports() -> None:
    first = reserve_local_listener()
    second = reserve_local_listener()
    try:
        first_port = int(first.getsockname()[1])
        second_port = int(second.getsockname()[1])
        assert first_port != second_port
        assert first_port > 0
        assert second_port > 0
    finally:
        first.close()
        second.close()


def test_create_migrate_and_drop_test_database() -> None:
    from aicoding.config import get_settings

    configured_database_url = get_settings().database_url
    admin_url = derive_admin_database_url(configured_database_url)
    database_name = f"aicoding_e2e_fixture_{uuid4().hex}"
    database_url = create_test_database(database_url=configured_database_url, database_name=database_name)
    try:
        assert _database_exists(admin_url=admin_url, database_name=database_name) is True

        migrate_test_database(database_url=database_url)

        engine = create_engine(database_url, pool_pre_ping=True)
        try:
            assert current_alembic_revision(engine) == "0028_subtask_execution_results"
        finally:
            engine.dispose()
    finally:
        drop_test_database(database_url=configured_database_url, database_name=database_name)

    assert _database_exists(admin_url=admin_url, database_name=database_name) is False
