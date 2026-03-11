from __future__ import annotations

import re

from fastapi.testclient import TestClient

from aicoding.daemon.app import create_app


def test_daemon_serves_frontend_index_with_bootstrap_payload(migrated_public_schema) -> None:
    with TestClient(create_app()) as app_client:
        response = app_client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert '<div id="root"></div>' in response.text
    assert "window.__AICODING_DAEMON_BOOTSTRAP__" in response.text
    assert '"apiBaseUrl":"/api"' in response.text
    assert '"apiToken":"change-me"' in response.text


def test_daemon_serves_frontend_assets_from_compiled_bundle(migrated_public_schema) -> None:
    with TestClient(create_app()) as app_client:
        index_response = app_client.get("/")
        asset_match = re.search(r'src="(/assets/[^"]+)"', index_response.text)
        assert asset_match is not None

        asset_response = app_client.get(asset_match.group(1))

    assert asset_response.status_code == 200
    assert "javascript" in asset_response.headers["content-type"]
    assert "react" in asset_response.text.lower()


def test_daemon_frontend_routes_use_spa_fallback(migrated_public_schema) -> None:
    with TestClient(create_app()) as app_client:
        response = app_client.get("/projects/repo_alpha/nodes/node-root/overview")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "window.__AICODING_DAEMON_BOOTSTRAP__" in response.text


def test_daemon_frontend_routes_fail_clearly_when_bundle_missing(monkeypatch, migrated_public_schema) -> None:
    monkeypatch.setattr("aicoding.daemon.frontend_runtime.resolve_frontend_dist_dir", lambda: None)

    with TestClient(create_app()) as app_client:
        index_response = app_client.get("/")
        asset_response = app_client.get("/assets/index-missing.js")

    assert index_response.status_code == 503
    assert "npm run build" in index_response.text
    assert asset_response.status_code == 503
    assert "npm run build" in asset_response.text
