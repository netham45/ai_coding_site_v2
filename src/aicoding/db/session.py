from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from aicoding.config import get_settings


class SessionUsageError(RuntimeError):
    """Raised when a session helper is used outside its expected boundary."""


def create_engine_from_settings(*, echo: bool | None = None) -> Engine:
    settings = get_settings()
    database = settings.database
    return create_engine(
        database.url,
        echo=database.echo if echo is None else echo,
        pool_pre_ping=True,
        pool_size=database.pool_size,
        max_overflow=database.max_overflow,
        pool_timeout=database.pool_timeout,
    )


def create_session_factory(*, engine: Engine | None = None, echo: bool | None = None) -> sessionmaker[Session]:
    active_engine = engine or create_engine_from_settings(echo=echo)
    return sessionmaker(bind=active_engine, autoflush=False, autocommit=False, expire_on_commit=False)


@contextmanager
def query_session_scope(factory: sessionmaker[Session] | None = None) -> Iterator[Session]:
    session_factory = factory or create_session_factory()
    session = session_factory()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def session_scope(factory: sessionmaker[Session] | None = None) -> Iterator[Session]:
    with query_session_scope(factory) as session:
        with session.begin():
            yield session


@contextmanager
def nested_transaction(session: Session) -> Iterator[Session]:
    if not session.in_transaction():
        raise SessionUsageError("Nested transaction requires an active outer transaction.")

    with session.begin_nested():
        yield session


def probe_database(engine: Engine | None = None) -> dict[str, object]:
    active_engine = engine or create_engine_from_settings()
    with active_engine.connect() as connection:
        row = connection.execute(
            text(
                """
                select
                    current_database() as database_name,
                    current_user as current_user,
                    current_schema() as current_schema,
                    version() as server_version
                """
            )
        ).mappings().one()
    return dict(row)


def current_alembic_revision(engine: Engine | None = None) -> str | None:
    active_engine = engine or create_engine_from_settings()
    with active_engine.connect() as connection:
        try:
            return connection.execute(text("select version_num from alembic_version")).scalar_one_or_none()
        except SQLAlchemyError:
            return None
