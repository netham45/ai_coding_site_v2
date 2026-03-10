from __future__ import annotations

import pytest
from sqlalchemy.exc import SQLAlchemyError

from aicoding.daemon.database import durable_write_probe
from aicoding.daemon.dependencies import get_db_session
from aicoding.daemon.errors import DaemonUnavailableError


class TrackingSession:
    def __init__(self, *, fail_on_execute: bool = False) -> None:
        self.closed = False
        self.begin_calls = 0
        self.fail_on_execute = fail_on_execute

    def begin(self):
        self.begin_calls += 1
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, statement):
        if self.fail_on_execute:
            raise SQLAlchemyError("probe failed")

        class Result:
            @staticmethod
            def scalar_one():
                class Timestamp:
                    @staticmethod
                    def isoformat() -> str:
                        return "2026-03-08T00:00:00+00:00"

                return Timestamp()

        return Result()

    def close(self) -> None:
        self.closed = True


def test_durable_write_probe_uses_transactional_session_boundary() -> None:
    session = TrackingSession()
    payload = durable_write_probe(lambda: session)

    assert payload["write_path"] == "available"
    assert session.begin_calls == 1
    assert session.closed is True


def test_durable_write_probe_translates_sqlalchemy_errors() -> None:
    with pytest.raises(DaemonUnavailableError):
        durable_write_probe(lambda: TrackingSession(fail_on_execute=True))


def test_get_db_session_closes_factory_session_after_yield() -> None:
    session = TrackingSession()

    class AppState:
        db_session_factory = lambda self=None: session

    class App:
        state = AppState()

    class Request:
        app = App()

    generator = get_db_session(Request())
    yielded = next(generator)
    assert yielded is session

    with pytest.raises(StopIteration):
        next(generator)

    assert session.closed is True
