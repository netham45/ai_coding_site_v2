from __future__ import annotations

from dataclasses import replace

from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_daemon_override_endpoints_and_cli_round_trip(
    app_client,
    auth_headers,
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_tasks.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - review_node",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    (overrides_root / "tasks" / "review_node_reviews.yaml").write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: review_node",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: append_list",
                "value:",
                "  uses_reviews:",
                "    - policy_compliance_review",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    app_client.app.state.resource_catalog = catalog
    app_client.app.state.hierarchy_registry = load_hierarchy_registry(catalog)

    create_response = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Override Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    override_chain_response = app_client.get(f"/api/nodes/{node_id}/yaml/override-chain", headers=auth_headers)
    resolved_response = app_client.get(
        f"/api/nodes/{node_id}/yaml/resolved?family=task_definition&document_id=review_node",
        headers=auth_headers,
    )

    assert compile_response.status_code == 200
    assert [task["task_key"] for task in compile_response.json()["compiled_workflow"]["tasks"]] == [
        "research_context",
        "review_node",
        "execute_node",
    ]
    assert override_chain_response.status_code == 200
    assert {
        item["override_relative_path"] for item in override_chain_response.json()["applied_overrides"]
    } == {"nodes/epic_tasks.yaml", "tasks/review_node_reviews.yaml"}
    assert resolved_response.status_code == 200
    assert resolved_response.json()["resolved_documents"][0]["resolved_document"]["uses_reviews"] == [
        "reviews/node_against_requirements.yaml",
        "policy_compliance_review",
    ]

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    override_result = cli_runner(["yaml", "override-chain", "--node", node_id])
    resolved_result = cli_runner(["yaml", "resolved", "--node", node_id, "--family", "task_definition", "--id", "review_node"])

    assert override_result.exit_code == 0
    assert {
        item["override_relative_path"] for item in override_result.json()["applied_overrides"]
    } == {"nodes/epic_tasks.yaml", "tasks/review_node_reviews.yaml"}
    assert resolved_result.exit_code == 0
    assert resolved_result.json()["resolved_documents"][0]["target_id"] == "review_node"
