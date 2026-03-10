from __future__ import annotations


def test_daemon_lists_node_kinds_and_creates_nodes(app_client, migrated_public_schema) -> None:
    kinds_response = app_client.get("/api/node-kinds", headers={"Authorization": "Bearer change-me"})

    assert kinds_response.status_code == 200
    kinds_payload = kinds_response.json()
    assert kinds_payload["top_level_kinds"] == ["epic"]
    assert any(item["kind"] == "task" for item in kinds_payload["definitions"])

    epic_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Epic title", "prompt": "top-level prompt"},
    )
    assert epic_response.status_code == 200
    epic_payload = epic_response.json()

    phase_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={
            "kind": "phase",
            "title": "Phase title",
            "prompt": "phase prompt",
            "parent_node_id": epic_payload["node_id"],
        },
    )
    assert phase_response.status_code == 200

    show_response = app_client.get(f"/api/nodes/{epic_payload['node_id']}", headers={"Authorization": "Bearer change-me"})
    lifecycle_response = app_client.get(
        f"/api/nodes/{epic_payload['node_id']}/lifecycle",
        headers={"Authorization": "Bearer change-me"},
    )
    versions_response = app_client.get(
        f"/api/nodes/{epic_payload['node_id']}/versions",
        headers={"Authorization": "Bearer change-me"},
    )
    children_response = app_client.get(f"/api/nodes/{epic_payload['node_id']}/children", headers={"Authorization": "Bearer change-me"})
    ancestors_response = app_client.get(
        f"/api/nodes/{phase_response.json()['node_id']}/ancestors",
        headers={"Authorization": "Bearer change-me"},
    )

    assert show_response.status_code == 200
    assert show_response.json()["kind"] == "epic"
    assert lifecycle_response.status_code == 200
    assert lifecycle_response.json()["lifecycle_state"] == "DRAFT"
    assert versions_response.status_code == 200
    assert [item["version_number"] for item in versions_response.json()["versions"]] == [1]
    assert [child["kind"] for child in children_response.json()] == ["phase"]
    assert [ancestor["kind"] for ancestor in ancestors_response.json()] == ["epic"]

    tree_response = app_client.get(f"/api/nodes/{epic_payload['node_id']}/tree", headers={"Authorization": "Bearer change-me"})
    siblings_response = app_client.get(
        f"/api/nodes/{phase_response.json()['node_id']}/siblings",
        headers={"Authorization": "Bearer change-me"},
    )
    summary_response = app_client.get(f"/api/nodes/{epic_payload['node_id']}/summary", headers={"Authorization": "Bearer change-me"})

    assert tree_response.status_code == 200
    assert [item["title"] for item in tree_response.json()["nodes"]] == ["Epic title", "Phase title"]
    assert siblings_response.status_code == 200
    assert siblings_response.json() == []
    assert summary_response.status_code == 200
    assert summary_response.json()["lifecycle_state"] == "DRAFT"

    materialization_response = app_client.get(
        f"/api/nodes/{epic_payload['node_id']}/children/materialization",
        headers={"Authorization": "Bearer change-me"},
    )
    assert materialization_response.status_code == 200
    assert materialization_response.json()["authority_mode"] == "manual"
    assert materialization_response.json()["status"] == "manual"


def test_daemon_rejects_invalid_hierarchy_creation(app_client, migrated_public_schema) -> None:
    task_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "task", "title": "Task title", "prompt": "leaf prompt"},
    )
    assert task_response.status_code == 409

    epic_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Epic title", "prompt": "top-level prompt"},
    )
    assert epic_response.status_code == 200

    invalid_child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={
            "kind": "task",
            "title": "Task title",
            "prompt": "leaf prompt",
            "parent_node_id": epic_response.json()["node_id"],
        },
    )
    assert invalid_child_response.status_code == 409


def test_manual_child_creation_after_layout_materialization_enters_hybrid_mode(app_client, migrated_public_schema) -> None:
    parent_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Hybrid Parent", "prompt": "top-level prompt"},
    )
    parent_id = parent_response.json()["node_id"]

    materialize_response = app_client.post(
        f"/api/nodes/{parent_id}/children/materialize",
        headers={"Authorization": "Bearer change-me"},
    )
    manual_child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={
            "kind": "phase",
            "title": "Manual Extra Phase",
            "prompt": "manual prompt",
            "parent_node_id": parent_id,
        },
    )
    inspection_response = app_client.get(
        f"/api/nodes/{parent_id}/children/materialization",
        headers={"Authorization": "Bearer change-me"},
    )

    assert materialize_response.status_code == 200
    assert manual_child_response.status_code == 200
    assert inspection_response.status_code == 200
    payload = inspection_response.json()
    assert payload["authority_mode"] == "hybrid"
    assert payload["status"] == "reconciliation_required"
    assert payload["child_count"] == 3
