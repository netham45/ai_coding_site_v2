from __future__ import annotations


def test_daemon_workflow_compile_and_inspection_endpoints_round_trip(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Workflow Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]

    compile_response = app_client.post(
        f"/api/nodes/{node_id}/workflow/compile",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    workflow_id = compile_response.json()["compiled_workflow"]["id"]
    current_response = app_client.get(f"/api/nodes/{node_id}/workflow/current", headers={"Authorization": "Bearer change-me"})
    chain_response = app_client.get(f"/api/nodes/{node_id}/workflow/chain", headers={"Authorization": "Bearer change-me"})
    sources_response = app_client.get(f"/api/workflows/{workflow_id}/sources", headers={"Authorization": "Bearer change-me"})
    hooks_response = app_client.get(f"/api/nodes/{node_id}/workflow/hooks", headers={"Authorization": "Bearer change-me"})
    failures_response = app_client.get(f"/api/nodes/{node_id}/workflow/compile-failures", headers={"Authorization": "Bearer change-me"})

    assert compile_response.status_code == 200
    assert compile_response.json()["status"] == "compiled"
    assert current_response.status_code == 200
    assert current_response.json()["id"] == workflow_id
    assert [item["task_key"] for item in current_response.json()["tasks"]] == ["research_context", "execute_node", "validate_node", "review_node"]
    assert chain_response.status_code == 200
    assert [item["task_key"] for item in chain_response.json()["chain"]] == [
        "research_context",
        "research_context",
        "execute_node",
        "validate_node",
        "review_node",
    ]
    assert len(chain_response.json()["chain"][1]["depends_on_compiled_subtask_ids"]) == 1
    assert sources_response.status_code == 200
    assert sources_response.json()["compiled_workflow_id"] == workflow_id
    assert sources_response.json()["source_documents"][0]["relative_path"] == "nodes/epic.yaml"
    assert hooks_response.status_code == 200
    assert hooks_response.json()["selected_hooks"][0]["hook_id"] == "default_hooks"
    assert hooks_response.json()["expanded_steps"][0]["source_subtask_key"] == "research_context.hook.default_hooks.1"
    assert failures_response.status_code == 200
    assert failures_response.json() == {"failures": []}


def test_cli_workflow_compile_show_chain_and_failures_round_trip(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Workflow Epic", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    compile_result = cli_runner(["workflow", "compile", "--node", node_id])
    workflow_id = compile_result.json()["compiled_workflow"]["id"]
    current_result = cli_runner(["workflow", "current", "--node", node_id])
    show_result = cli_runner(["workflow", "show", "--workflow", workflow_id])
    chain_result = cli_runner(["workflow", "chain", "--node", node_id])
    hooks_result = cli_runner(["workflow", "hooks", "--node", node_id])
    failures_result = cli_runner(["workflow", "compile-failures", "--node", node_id])

    assert compile_result.exit_code == 0
    assert compile_result.json()["status"] == "compiled"
    assert current_result.exit_code == 0
    assert current_result.json()["id"] == workflow_id
    assert show_result.exit_code == 0
    assert show_result.json()["id"] == workflow_id
    assert chain_result.exit_code == 0
    assert [item["task_key"] for item in chain_result.json()["chain"]] == [
        "research_context",
        "research_context",
        "execute_node",
        "validate_node",
        "review_node",
    ]
    assert hooks_result.exit_code == 0
    assert hooks_result.json()["expanded_steps"][0]["hook_id"] == "default_hooks"
    assert failures_result.exit_code == 0
    assert failures_result.json() == {"failures": []}
