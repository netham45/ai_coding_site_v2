from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonUnavailableError
from aicoding.db.session import session_scope


def durable_write_probe(session_factory: sessionmaker[Session]) -> dict[str, object]:
    try:
        with session_scope(session_factory) as session:
            current_timestamp = session.execute(text("select now()")).scalar_one()
    except SQLAlchemyError as exc:
        raise DaemonUnavailableError() from exc

    return {"write_path": "available", "database_time": current_timestamp.isoformat()}
