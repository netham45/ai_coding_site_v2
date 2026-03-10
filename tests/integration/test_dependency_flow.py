from __future__ import annotations


def test_dependency_endpoints_and_cli_round_trip(app_client, auth_headers, cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    left = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Left", "prompt": "boot prompt"},
    ).json()["node_id"]
    right = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Right", "prompt": "boot prompt"},
    ).json()["node_id"]
    for node_id in (left, right):
        app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
        app_client.post(
            "/api/nodes/lifecycle/transition",
            headers=auth_headers,
            json={"node_id": node_id, "target_state": "READY"},
        )

    add_response = app_client.post(
        "/api/nodes/dependencies/add",
        headers=auth_headers,
        json={"node_id": right, "depends_on_node_id": left, "required_state": "COMPLETE"},
    )
    validation_response = app_client.get(f"/api/nodes/{right}/dependency-validate", headers=auth_headers)
    status_response = app_client.get(f"/api/nodes/{right}/dependency-status", headers=auth_headers)
    start_response = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": right})

    assert add_response.status_code == 200
    assert add_response.json()["dependency_type"] == "sibling"
    assert validation_response.json()["status"] == "valid"
    assert status_response.json()["status"] == "blocked"
    assert start_response.json()["status"] == "blocked"
    assert start_response.json()["reason"] == "blocked"

    app_client.post("/api/nodes/lifecycle/transition", headers=auth_headers, json={"node_id": left, "target_state": "RUNNING"})
    app_client.post("/api/nodes/lifecycle/transition", headers=auth_headers, json={"node_id": left, "target_state": "COMPLETE"})
    start_after_complete = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": right})

    assert start_after_complete.json()["status"] == "admitted"
    assert start_after_complete.json()["current_state"] == "RUNNING"

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    dependencies_result = cli_runner(["node", "dependencies", "--node", right])
    validate_result = cli_runner(["node", "dependency-validate", "--node", right])
    blockers_result = cli_runner(["node", "blockers", "--node", right])

    assert dependencies_result.exit_code == 0
    assert len(dependencies_result.json()["dependencies"]) == 1
    assert validate_result.exit_code == 0
    assert validate_result.json()["status"] == "valid"
    assert blockers_result.exit_code == 0
