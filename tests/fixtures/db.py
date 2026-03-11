from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from aicoding.config import get_settings
from aicoding.db.bootstrap import reset_public_schema


@pytest.fixture
def db_engine():
    engine = create_engine(get_settings().database_url, pool_pre_ping=True)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def db_session_factory(db_engine):
    return sessionmaker(bind=db_engine, expire_on_commit=False, autoflush=False)


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
    reset_public_schema(db_engine)
    db_engine.dispose()
    yield db_engine
    reset_public_schema(db_engine)
    db_engine.dispose()


@pytest.fixture
def migrated_public_schema(clean_public_schema):
    from aicoding.db.migrations import create_alembic_config, upgrade_database

    config = create_alembic_config()
    config.attributes["override_sqlalchemy_url"] = str(clean_public_schema.url.render_as_string(hide_password=False))
    upgrade_database("head", config=config)
    clean_public_schema.dispose()
    return clean_public_schema
