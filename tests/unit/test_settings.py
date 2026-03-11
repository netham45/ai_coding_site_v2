from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from aicoding.config import Settings, get_settings


def test_settings_read_environment(monkeypatch) -> None:
    monkeypatch.setenv("AICODING_ENV", "test")
    monkeypatch.setenv("AICODING_DATABASE_URL", "postgresql+psycopg://example")
    monkeypatch.setenv("AICODING_DAEMON_PORT", "9001")
    monkeypatch.setenv("AICODING_DAEMON_REQUEST_TIMEOUT_SECONDS", "45")
    monkeypatch.setenv("AICODING_LOG_LEVEL", "warning")

    settings = get_settings()

    assert settings.env == "test"
    assert settings.database_url == "postgresql+psycopg://example"
    assert settings.daemon_port == 9001
    assert settings.normalized_log_level == "WARNING"
    assert settings.daemon_request_timeout_seconds == 45
    assert settings.database.pool_size == 5
    assert settings.daemon.base_url == "http://127.0.0.1:9001"
    assert settings.daemon.request_timeout_seconds == 45


def test_settings_default_to_tmux_session_backend(monkeypatch) -> None:
    monkeypatch.delenv("AICODING_SESSION_BACKEND", raising=False)
    get_settings.cache_clear()
    settings = Settings(database_url="postgresql+psycopg://user:pass@localhost:5432/aicoding")

    assert settings.session.model_dump()["backend"] == "tmux"


def test_settings_build_typed_submodels() -> None:
    settings = Settings(
        database_url="postgresql+psycopg://user:pass@localhost:5432/aicoding",
        daemon_host="0.0.0.0",
        daemon_port=8123,
        session_backend="tmux",
        auth_token="secret",
        workspace_root=Path("/tmp/workspace"),
    )

    assert settings.database.model_dump() == {
        "url": "postgresql+psycopg://user:pass@localhost:5432/aicoding",
        "pool_size": 5,
        "max_overflow": 10,
        "pool_timeout": 30,
        "echo": False,
    }
    assert settings.daemon.base_url == "http://0.0.0.0:8123"
    assert settings.session.model_dump() == {
        "backend": "tmux",
        "poll_interval_seconds": 1.0,
        "idle_threshold_seconds": 30.0,
        "max_nudge_count": 2,
    }
    assert settings.auth.token == "secret"
    assert settings.daemon.request_timeout_seconds == 30.0
    assert settings.workspace_root == Path("/tmp/workspace")


def test_settings_reject_invalid_values() -> None:
    with pytest.raises(ValidationError):
        Settings(database_url="not-a-url")

    with pytest.raises(ValidationError):
        Settings(log_level="loud")

    with pytest.raises(ValidationError):
        Settings(session_backend="screen")  # type: ignore[arg-type]
