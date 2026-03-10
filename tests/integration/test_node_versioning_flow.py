from __future__ import annotations


def test_daemon_node_version_lineage_and_cutover(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Versioned Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]

    versions_response = app_client.get(f"/api/nodes/{node_id}/versions", headers={"Authorization": "Bearer change-me"})
    lineage_before = app_client.get(f"/api/nodes/{node_id}/lineage", headers={"Authorization": "Bearer change-me"})
    supersede_response = app_client.post(
        f"/api/nodes/{node_id}/supersede",
        headers={"Authorization": "Bearer change-me"},
        json={"title": "Versioned Epic v2"},
    )
    cutover_response = app_client.post(
        f"/api/node-versions/{supersede_response.json()['id']}/cutover",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )

    assert versions_response.status_code == 200
    assert [item["version_number"] for item in versions_response.json()["versions"]] == [1]
    assert lineage_before.status_code == 200
    assert lineage_before.json()["authoritative_node_version_id"] == lineage_before.json()["latest_created_node_version_id"]
    assert supersede_response.status_code == 200
    assert supersede_response.json()["status"] == "candidate"
    assert supersede_response.json()["version_number"] == 2
    assert cutover_response.status_code == 200
    assert cutover_response.json()["authoritative_node_version_id"] == supersede_response.json()["id"]
    statuses = {item["version_number"]: item["status"] for item in cutover_response.json()["versions"]}
    assert statuses == {1: "superseded", 2: "authoritative"}


def test_cli_node_lineage_versions_and_supersede_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Versioned", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]

    versions_result = cli_runner(["node", "versions", "--node", node_id])
    supersede_result = cli_runner(["node", "supersede", "--node", node_id, "--title", "CLI Versioned v2"])
    cutover_result = cli_runner(["node", "version", "cutover", "--version", supersede_result.json()["id"]])
    lineage_result = cli_runner(["node", "lineage", "--node", node_id])

    assert versions_result.exit_code == 0
    assert [item["version_number"] for item in versions_result.json()["versions"]] == [1]
    assert supersede_result.exit_code == 0
    assert supersede_result.json()["status"] == "candidate"
    assert cutover_result.exit_code == 0
    assert lineage_result.exit_code == 0
    assert lineage_result.json()["authoritative_node_version_id"] == supersede_result.json()["id"]
    assert [item["status"] for item in lineage_result.json()["versions"]] == ["superseded", "authoritative"]


def test_merge_conflict_blocks_cutover_until_resolved(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Conflict Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Conflict Child", "prompt": "child prompt", "parent_node_id": node_id},
    )
    child_node_id = child_response.json()["node_id"]
    child_versions = app_client.get(f"/api/nodes/{child_node_id}/versions", headers={"Authorization": "Bearer change-me"}).json()["versions"]
    child_version_id = child_versions[0]["id"]

    supersede_response = app_client.post(
        f"/api/nodes/{node_id}/supersede",
        headers={"Authorization": "Bearer change-me"},
        json={"title": "Conflict Epic v2"},
    )
    candidate_version_id = supersede_response.json()["id"]

    record_response = app_client.post(
        "/api/git/merge-conflicts/record",
        headers={"Authorization": "Bearer change-me"},
        json={
            "parent_node_version_id": candidate_version_id,
            "child_node_version_id": child_version_id,
            "child_final_commit_sha": "childfinal123",
            "parent_commit_before": "seed123",
            "parent_commit_after": "mergeattempt123",
            "merge_order": 1,
            "files_json": ["src/conflicted.py"],
        },
    )
    cutover_blocked = app_client.post(
        f"/api/node-versions/{candidate_version_id}/cutover",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    conflicts_response = app_client.get(
        f"/api/nodes/{node_id}/git/merge-conflicts",
        headers={"Authorization": "Bearer change-me"},
    )
    resolve_response = app_client.post(
        f"/api/git/merge-conflicts/{record_response.json()['id']}/resolve",
        headers={"Authorization": "Bearer change-me"},
        json={"resolution_summary": "Resolved cleanly.", "resolution_status": "resolved"},
    )
    cutover_after_resolve = app_client.post(
        f"/api/node-versions/{candidate_version_id}/cutover",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )

    assert record_response.status_code == 200
    assert cutover_blocked.status_code == 409
    assert "unresolved merge conflicts" in cutover_blocked.json()["detail"]
    assert conflicts_response.status_code == 200
    assert conflicts_response.json()["conflicts"][0]["resolution_status"] == "unresolved"
    assert resolve_response.status_code == 200
    assert resolve_response.json()["resolution_status"] == "resolved"
    assert cutover_after_resolve.status_code == 200


def test_daemon_regenerate_and_rectify_upstream_round_trip(app_client, migrated_public_schema) -> None:
    root_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Root Epic", "prompt": "root prompt"},
    )
    root_id = root_response.json()["node_id"]
    child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Child Phase", "prompt": "child prompt", "parent_node_id": root_id},
    )
    child_id = child_response.json()["node_id"]

    regenerate_response = app_client.post(
        f"/api/nodes/{root_id}/regenerate",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    rectify_response = app_client.post(
        f"/api/nodes/{child_id}/rectify-upstream",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    history_response = app_client.get(
        f"/api/nodes/{child_id}/rebuild-history",
        headers={"Authorization": "Bearer change-me"},
    )

    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["scope"] == "subtree"
    assert len(regenerate_response.json()["stable_candidate_version_ids"]) == 2
    assert rectify_response.status_code == 200
    assert rectify_response.json()["scope"] == "upstream"
    assert len(rectify_response.json()["stable_candidate_version_ids"]) >= 2
    assert history_response.status_code == 200
    assert {event["scope"] for event in history_response.json()["events"]} >= {"subtree", "upstream"}
