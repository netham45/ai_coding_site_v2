from __future__ import annotations


def test_daemon_lifecycle_transition_and_cursor_endpoints(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Lifecycle Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    workflow_response = app_client.post(
        f"/api/nodes/{node_id}/workflow/compile",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )

    compiled_response = app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "COMPILED"},
    )
    ready_response = app_client.post(
        "/api/nodes/lifecycle/transition",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id, "target_state": "READY"},
    )
    start_response = app_client.post(
        "/api/node-runs/start",
        headers={"Authorization": "Bearer change-me"},
        json={"node_id": node_id},
    )
    cursor_response = app_client.post(
        "/api/nodes/cursor/update",
        headers={"Authorization": "Bearer change-me"},
        json={
            "node_id": node_id,
            "current_task_id": "task.execute",
            "current_subtask_id": "subtask.render",
            "current_subtask_attempt": 1,
            "execution_cursor_json": {"ordinal": 7},
            "is_resumable": True,
        },
    )
    lifecycle_response = app_client.get(
        f"/api/nodes/{node_id}/lifecycle",
        headers={"Authorization": "Bearer change-me"},
    )

    assert workflow_response.status_code == 200
    assert compiled_response.status_code == 200
    assert ready_response.status_code == 200
    assert start_response.status_code == 200
    assert cursor_response.status_code == 200
    assert lifecycle_response.status_code == 200
    assert lifecycle_response.json()["lifecycle_state"] == "RUNNING"
    assert lifecycle_response.json()["run_status"] == "RUNNING"
    assert lifecycle_response.json()["current_task_id"] == "task.execute"
    assert lifecycle_response.json()["execution_cursor_json"] == {"ordinal": 7}


def test_cli_lifecycle_and_cursor_commands_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Lifecycle", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    assert cli_runner(["workflow", "compile", "--node", node_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "COMPILED"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0

    cursor_result = cli_runner(
        [
            "node",
            "cursor",
            "update",
            "--node",
            node_id,
            "--task",
            "task.execute",
            "--subtask",
            "subtask.render",
            "--attempt",
            "2",
            "--cursor-json",
            "{\"ordinal\": 8}",
            "--resumable",
            "true",
        ]
    )
    lifecycle_result = cli_runner(["node", "lifecycle", "show", "--node", node_id])

    assert cursor_result.exit_code == 0
    assert lifecycle_result.exit_code == 0
    assert lifecycle_result.json()["lifecycle_state"] == "RUNNING"
    assert lifecycle_result.json()["current_subtask_attempt"] == 2
    assert lifecycle_result.json()["execution_cursor_json"] == {"ordinal": 8}
