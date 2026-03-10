from __future__ import annotations


def test_daemon_branch_seed_and_final_round_trip(app_client, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Branch Epic", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]
    version_id = app_client.get(f"/api/nodes/{node_id}/versions", headers={"Authorization": "Bearer change-me"}).json()["versions"][0]["id"]

    branch_response = app_client.get(f"/api/nodes/{node_id}/git/branch", headers={"Authorization": "Bearer change-me"})
    seed_response = app_client.post(
        f"/api/node-versions/{version_id}/git/seed",
        headers={"Authorization": "Bearer change-me"},
        json={"commit_sha": "abcdef1"},
    )
    final_response = app_client.post(
        f"/api/node-versions/{version_id}/git/final",
        headers={"Authorization": "Bearer change-me"},
        json={"commit_sha": "1234abc"},
    )

    assert branch_response.status_code == 200
    assert branch_response.json()["branch_status"] == "valid"
    assert branch_response.json()["active_branch_name"] == branch_response.json()["expected_branch_name"]
    assert seed_response.status_code == 200
    assert seed_response.json()["seed_commit_sha"] == "abcdef1"
    assert final_response.status_code == 200
    assert final_response.json()["final_commit_sha"] == "1234abc"


def test_cli_git_branch_seed_and_final_show_round_trip(cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    create_result = cli_runner(["node", "create", "--kind", "epic", "--title", "CLI Branch Epic", "--prompt", "boot prompt"])
    node_id = create_result.json()["node_id"]
    version_id = cli_runner(["node", "versions", "--node", node_id]).json()["versions"][0]["id"]

    daemon_bridge_client.client.post(
        f"/api/node-versions/{version_id}/git/seed",
        headers={"Authorization": "Bearer change-me"},
        json={"commit_sha": "abcdef1"},
    )
    daemon_bridge_client.client.post(
        f"/api/node-versions/{version_id}/git/final",
        headers={"Authorization": "Bearer change-me"},
        json={"commit_sha": "1234abc"},
    )

    branch_result = cli_runner(["git", "branch", "show", "--node", node_id])
    seed_result = cli_runner(["git", "seed", "show", "--node", node_id])
    final_result = cli_runner(["git", "final", "show", "--version", version_id])

    assert branch_result.exit_code == 0
    assert branch_result.json()["branch_status"] == "valid"
    assert seed_result.exit_code == 0
    assert seed_result.json()["seed_commit_sha"] == "abcdef1"
    assert final_result.exit_code == 0
    assert final_result.json()["final_commit_sha"] == "1234abc"
