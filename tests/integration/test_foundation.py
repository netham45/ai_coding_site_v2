from __future__ import annotations


def test_daemon_foundation_endpoint_reports_shared_state(app_client) -> None:
    response = app_client.get("/foundation", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["app_name"] == "AI Coding Orchestrator"
    assert "prompt_layouts" in payload["resource_groups"]
    assert payload["db_pool_class"]
    assert payload["auth_token_file"]
    assert payload["auth_token_source"] in {"file", "settings", "generated"}
