from __future__ import annotations


def test_daemon_project_policy_endpoints_and_compiled_workflow_policy_payload(app_client, migrated_public_schema) -> None:
    headers = {"Authorization": "Bearer change-me"}

    project_response = app_client.get("/api/policies/project", headers=headers)
    effective_response = app_client.get("/api/policies/effective", headers=headers)
    impact_response = app_client.get("/api/policies/impact/epic", headers=headers)

    create_response = app_client.post(
        "/api/nodes/create",
        headers=headers,
        json={"kind": "epic", "title": "Policy Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=headers, json={})

    assert project_response.status_code == 200
    assert project_response.json()["policies"][0]["policy_id"] == "default_project_policy"
    assert effective_response.status_code == 200
    assert "default_project_policy" in effective_response.json()["project_policy_ids"]
    assert impact_response.status_code == 200
    assert impact_response.json()["enabled_for_node_kind"] is True
    assert compile_response.status_code == 200
    assert compile_response.json()["compiled_workflow"]["resolved_yaml"]["effective_policy"]["project_policy_ids"] == [
        "default_project_policy"
    ]
    assert compile_response.json()["compiled_workflow"]["resolved_yaml"]["policy_impact"]["node_kind"] == "epic"


def test_cli_project_policy_commands_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    project_result = cli_runner(["yaml", "project-policy"])
    effective_result = cli_runner(["yaml", "effective-policy"])
    impact_result = cli_runner(["yaml", "policy-impact", "--kind", "epic"])

    assert project_result.exit_code == 0
    assert project_result.json()["policies"][0]["policy_id"] == "default_project_policy"
    assert effective_result.exit_code == 0
    assert "default_project_policy" in effective_result.json()["project_policy_ids"]
    assert impact_result.exit_code == 0
    assert impact_result.json()["node_kind"] == "epic"
