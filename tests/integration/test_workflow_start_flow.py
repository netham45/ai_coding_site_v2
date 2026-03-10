from __future__ import annotations


def test_daemon_workflow_start_creates_compiles_and_optionally_starts_run(app_client, migrated_public_schema) -> None:
    headers = {"Authorization": "Bearer change-me"}

    start_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "epic",
            "prompt": "Create a top-level epic from a prompt and start it.",
        },
    )
    compile_only_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "epic",
            "title": "Compile Only Startup",
            "prompt": "Create a top-level epic from a prompt without starting it.",
            "start_run": False,
        },
    )
    invalid_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "task",
            "prompt": "This should be rejected because task is not top-level.",
        },
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "started"
    assert start_response.json()["compile"]["status"] == "compiled"
    assert start_response.json()["run_admission"]["status"] == "admitted"
    assert start_response.json()["run_progress"]["run"]["trigger_reason"] == "workflow_start"
    assert start_response.json()["lifecycle"]["lifecycle_state"] == "RUNNING"

    assert compile_only_response.status_code == 200
    assert compile_only_response.json()["status"] == "compiled"
    assert compile_only_response.json()["run_admission"] is None
    assert compile_only_response.json()["run_progress"] is None
    assert compile_only_response.json()["lifecycle"]["lifecycle_state"] == "READY"

    assert invalid_response.status_code == 409


def test_cli_workflow_start_and_top_level_node_create_flags_round_trip(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    workflow_start = cli_runner(
        [
            "workflow",
            "start",
            "--kind",
            "epic",
            "--prompt",
            "Create and start a top-level epic through the CLI.",
        ]
    )
    node_create_compile = cli_runner(
        [
            "node",
            "create",
            "--kind",
            "epic",
            "--title",
            "Compile Via Node Create",
            "--prompt",
            "Compile without starting through node create.",
            "--compile",
        ]
    )

    assert workflow_start.exit_code == 0
    assert workflow_start.json()["status"] == "started"
    assert workflow_start.json()["run_progress"]["run"]["trigger_reason"] == "workflow_start"

    assert node_create_compile.exit_code == 0
    assert node_create_compile.json()["status"] == "compiled"
    assert node_create_compile.json()["run_admission"] is None
