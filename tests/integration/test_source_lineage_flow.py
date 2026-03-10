from __future__ import annotations


def test_daemon_source_lineage_endpoints_return_captured_inputs(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Lineage Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]

    node_sources = app_client.get(f"/api/nodes/{node_id}/sources", headers={"Authorization": "Bearer change-me"})
    version_id = app_client.get(f"/api/nodes/{node_id}/versions", headers={"Authorization": "Bearer change-me"}).json()["versions"][0]["id"]
    version_sources = app_client.get(f"/api/node-versions/{version_id}/sources", headers={"Authorization": "Bearer change-me"})

    assert node_sources.status_code == 200
    assert version_sources.status_code == 200
    assert [item["relative_path"] for item in node_sources.json()["source_documents"]] == [
        "nodes/epic.yaml",
        "policies/default_runtime_policy.yaml",
        "prompts/default_prompt_refs.yaml",
        "project-policies/default_project_policy.yaml",
        "layouts/generate_phase_layout.md",
        "hooks/before_validation_default.yaml",
        "hooks/before_review_default.yaml",
        "review/review_node_output.md",
        "hooks/before_testing_default.yaml",
        "hooks/after_node_complete_build_docs.yaml",
        "hooks/after_node_complete_update_provenance.yaml",
        "hooks/default_hooks.yaml",
        "runtime/session_bootstrap.md",
        "tasks/research_context.yaml",
        "tasks/execute_node.yaml",
        "reviews/node_against_requirements.yaml",
        "testing/default_unit_test_gate.yaml",
        "tasks/validate_node.yaml",
        "tasks/review_node.yaml",
        "layouts/epic_to_phases.yaml",
    ]
    assert version_sources.json()["node_version_id"] == version_id


def test_cli_workflow_and_node_source_commands_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Source Epic", "--prompt", "top prompt"])
    node_id = create_result.json()["node_id"]
    version_id = cli_runner(["node", "versions", "--node", node_id]).json()["versions"][0]["id"]
    workflow_id = cli_runner(["workflow", "compile", "--node", node_id]).json()["compiled_workflow"]["id"]

    workflow_sources_result = cli_runner(["workflow", "sources", "--node", node_id])
    workflow_sources_by_id_result = cli_runner(["workflow", "sources", "--workflow", workflow_id])
    node_sources_result = cli_runner(["node", "sources", "--node", node_id])
    version_sources_result = cli_runner(["node", "version", "sources", "--version", version_id])

    assert workflow_sources_result.exit_code == 0
    assert workflow_sources_by_id_result.exit_code == 0
    assert node_sources_result.exit_code == 0
    assert version_sources_result.exit_code == 0
    assert workflow_sources_result.json()["node_version_id"] == version_id
    assert workflow_sources_result.json()["compiled_workflow_id"] == workflow_id
    assert workflow_sources_by_id_result.json()["compiled_workflow_id"] == workflow_id
    assert node_sources_result.json()["source_documents"][3]["relative_path"] == "project-policies/default_project_policy.yaml"
    assert version_sources_result.json()["source_documents"][0]["relative_path"] == "nodes/epic.yaml"
