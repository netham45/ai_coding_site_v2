from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from aicoding.config import get_settings
from tests.helpers.e2e import build_e2e_database_name, create_test_database, drop_test_database, migrate_test_database


@pytest.fixture
def isolated_database_url(monkeypatch):
    base_database_url = get_settings().database_url
    database_name = build_e2e_database_name(prefix="aicoding_test")
    database_url = create_test_database(database_url=base_database_url, database_name=database_name)
    monkeypatch.setenv("AICODING_DATABASE_URL", database_url)
    get_settings.cache_clear()
    try:
        yield database_url
    finally:
        get_settings.cache_clear()
        drop_test_database(database_url=base_database_url, database_name=database_name)


@pytest.fixture
def db_engine(isolated_database_url):
    engine = create_engine(isolated_database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session_factory(migrated_public_schema):
    return sessionmaker(bind=migrated_public_schema, expire_on_commit=False, autoflush=False)


@pytest.fixture
def db_session(db_session_factory):
    session = db_session_factory()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def isolated_schema(db_engine):
    schema_name = f"test_{uuid4().hex}"
    with db_engine.begin() as connection:
        connection.execute(text(f'create schema "{schema_name}"'))
    try:
        yield schema_name
    finally:
        with db_engine.begin() as connection:
            connection.execute(text(f'drop schema if exists "{schema_name}" cascade'))


@pytest.fixture
def clean_public_schema(db_engine):
    yield db_engine


@pytest.fixture
def migrated_public_schema(clean_public_schema):
    database_url = str(clean_public_schema.url.render_as_string(hide_password=False))
    migrate_test_database(database_url=database_url)
    clean_public_schema.dispose()
    migrated_engine = create_engine(database_url, pool_pre_ping=True)
    try:
        yield migrated_engine
    finally:
        migrated_engine.dispose()
