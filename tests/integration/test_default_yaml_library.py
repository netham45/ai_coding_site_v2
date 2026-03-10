from __future__ import annotations

import pytest


@pytest.mark.parametrize(
    ("kind", "title"),
    [
        ("epic", "Library Epic"),
        ("phase", "Library Phase"),
        ("plan", "Library Plan"),
        ("task", "Library Task"),
    ],
)
def test_default_node_kinds_compile_against_authored_builtin_library(
    app_client,
    migrated_public_schema,
    kind: str,
    title: str,
) -> None:
    headers = {"Authorization": "Bearer change-me"}
    parent_id = None
    if kind == "phase":
        parent_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "epic", "title": "Parent Epic", "prompt": "boot prompt"},
        ).json()["node_id"]
    elif kind == "plan":
        epic_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "epic", "title": "Parent Epic", "prompt": "boot prompt"},
        ).json()["node_id"]
        parent_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "phase", "title": "Parent Phase", "prompt": "boot prompt", "parent_node_id": epic_id},
        ).json()["node_id"]
    elif kind == "task":
        epic_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "epic", "title": "Parent Epic", "prompt": "boot prompt"},
        ).json()["node_id"]
        phase_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "phase", "title": "Parent Phase", "prompt": "boot prompt", "parent_node_id": epic_id},
        ).json()["node_id"]
        parent_id = app_client.post(
            "/api/nodes/create",
            headers=headers,
            json={"kind": "plan", "title": "Parent Plan", "prompt": "boot prompt", "parent_node_id": phase_id},
        ).json()["node_id"]

    payload = {"kind": kind, "title": title, "prompt": "boot prompt"}
    if parent_id is not None:
        payload["parent_node_id"] = parent_id
    create_response = app_client.post("/api/nodes/create", headers=headers, json=payload)
    node_id = create_response.json()["node_id"]
    compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=headers, json={})

    assert create_response.status_code == 200
    assert compile_response.status_code == 200
    assert compile_response.json()["status"] == "compiled"
    assert compile_response.json()["compiled_workflow"]["task_count"] >= 1
