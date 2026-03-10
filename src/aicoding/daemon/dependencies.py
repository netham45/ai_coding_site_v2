from __future__ import annotations

from fastapi import Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from aicoding.config import Settings
from aicoding.daemon.auth import get_auth_context
from aicoding.daemon.background import BackgroundTaskRegistry
from aicoding.daemon.errors import DaemonUnavailableError
from aicoding.daemon.models import AuthContextResponse
from aicoding.hierarchy import HierarchyRegistry
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.db.session import query_session_scope
from aicoding.resources import ResourceCatalog


def get_settings_dependency(request: Request) -> Settings:
    return request.app.state.settings


def get_auth_context_dependency(request: Request) -> AuthContextResponse:
    return get_auth_context(request)


def get_db_engine(request: Request) -> Engine:
    return request.app.state.db_engine


def get_db_session_factory(request: Request) -> sessionmaker:
    return request.app.state.db_session_factory


def get_db_session(request: Request):
    factory: sessionmaker[Session] = request.app.state.db_session_factory
    with query_session_scope(factory) as session:
        yield session


def get_resource_catalog(request: Request) -> ResourceCatalog:
    return request.app.state.resource_catalog


def get_hierarchy_registry(request: Request) -> HierarchyRegistry:
    return request.app.state.hierarchy_registry


def get_background_registry(request: Request) -> BackgroundTaskRegistry:
    return request.app.state.background_registry


def get_session_adapter(request: Request) -> SessionAdapter:
    return request.app.state.session_adapter


def get_session_poller(request: Request) -> SessionPoller:
    return request.app.state.session_poller


def ensure_database_available(request: Request) -> None:
    engine: Engine = request.app.state.db_engine
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
    except SQLAlchemyError as exc:
        raise DaemonUnavailableError() from exc
