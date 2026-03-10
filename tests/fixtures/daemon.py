from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from aicoding.auth import read_token_file
from aicoding.daemon.app import create_app
from tests.helpers.daemon import DaemonBridgeClient


@pytest.fixture
def daemon_token(tmp_path: Path, monkeypatch) -> str:
    token_file = tmp_path / ".runtime" / "daemon.token"
    monkeypatch.setenv("AICODING_AUTH_TOKEN_FILE", str(token_file))
    monkeypatch.setenv("AICODING_AUTH_TOKEN", "change-me")
    return "change-me"


@pytest.fixture
def auth_headers(daemon_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {daemon_token}"}


@pytest.fixture
def app_client(daemon_token: str, migrated_public_schema) -> TestClient:
    with TestClient(create_app()) as client:
        yield client


@pytest.fixture
def live_daemon_token(app_client, daemon_token: str) -> str:
    token_file = Path(app_client.app.state.settings.auth.token_file)
    return read_token_file(token_file) or daemon_token


@pytest.fixture
def daemon_bridge_client(app_client, live_daemon_token: str) -> DaemonBridgeClient:
    return DaemonBridgeClient(client=app_client, token=live_daemon_token)
