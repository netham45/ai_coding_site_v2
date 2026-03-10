from __future__ import annotations

import pytest
import httpx

from aicoding.cli.daemon_client import DaemonClient, build_daemon_base_url, build_daemon_client
from aicoding.config import Settings
from aicoding.errors import CommandExecutionError


def test_build_daemon_base_url_uses_settings() -> None:
    settings = Settings(daemon_host="127.0.0.2", daemon_port=9999)

    assert build_daemon_base_url(settings) == "http://127.0.0.2:9999"


def test_build_daemon_client_uses_settings_timeout_and_token(monkeypatch) -> None:
    settings = Settings(
        daemon_host="127.0.0.2",
        daemon_port=9999,
        daemon_request_timeout_seconds=42,
        auth_token="secret-token",
    )

    monkeypatch.setattr("aicoding.cli.daemon_client.load_auth_token", lambda settings=None: "secret-token")

    client = build_daemon_client(settings)

    assert client.base_url == "http://127.0.0.2:9999"
    assert client.timeout_seconds == 42
    assert client.token == "secret-token"


def test_daemon_client_unavailable_raises_structured_error() -> None:
    client = DaemonClient(base_url="http://127.0.0.1:9", token="token", timeout_seconds=0.01)

    with pytest.raises(CommandExecutionError) as exc:
        client.request("GET", "/healthz")

    assert exc.value.code == "daemon_unavailable"


def test_daemon_client_maps_conflict_to_structured_error(monkeypatch) -> None:
    response = httpx.Response(409, json={"detail": "already running"})

    class StubClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, json=None, headers=None):
            return response

    monkeypatch.setattr(httpx, "Client", StubClient)

    client = DaemonClient(base_url="http://daemon", token="token")

    with pytest.raises(CommandExecutionError) as exc:
        client.request("POST", "/api/nodes/retry", json_payload={})

    assert exc.value.code == "daemon_conflict"
    assert exc.value.exit_code == 4


def test_daemon_client_maps_not_found_to_structured_error(monkeypatch) -> None:
    response = httpx.Response(404, json={"detail": "missing"})

    class StubClient:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def request(self, method, url, json=None, headers=None):
            return response

    monkeypatch.setattr(httpx, "Client", StubClient)

    client = DaemonClient(base_url="http://daemon", token="token")

    with pytest.raises(CommandExecutionError) as exc:
        client.request("GET", "/api/nodes/missing")

    assert exc.value.code == "not_found"
    assert exc.value.exit_code == 4
