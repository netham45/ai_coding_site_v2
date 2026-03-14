from __future__ import annotations

from aicoding.daemon.admission import add_node_dependency, admit_node_run, check_node_dependency_readiness
from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.incremental_parent_merge import process_next_incremental_child_merge, record_completed_child_for_incremental_merge
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import bootstrap_live_git_repo, stage_live_git_change
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import LogicalNodeCurrentVersion
from aicoding.db.session import query_session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_dependency_endpoints_and_cli_round_trip(app_client, auth_headers, cli_runner, daemon_bridge_client, migrated_public_schema, monkeypatch) -> None:
    left = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Left", "prompt": "boot prompt"},
    ).json()["node_id"]
    right = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Right", "prompt": "boot prompt"},
    ).json()["node_id"]
    for node_id in (left, right):
        app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
        app_client.post(
            "/api/nodes/lifecycle/transition",
            headers=auth_headers,
            json={"node_id": node_id, "target_state": "READY"},
        )

    add_response = app_client.post(
        "/api/nodes/dependencies/add",
        headers=auth_headers,
        json={"node_id": right, "depends_on_node_id": left, "required_state": "COMPLETE"},
    )
    validation_response = app_client.get(f"/api/nodes/{right}/dependency-validate", headers=auth_headers)
    status_response = app_client.get(f"/api/nodes/{right}/dependency-status", headers=auth_headers)
    start_response = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": right})

    assert add_response.status_code == 200
    assert add_response.json()["dependency_type"] == "sibling"
    assert validation_response.json()["status"] == "valid"
    assert status_response.json()["status"] == "blocked"
    assert start_response.json()["status"] == "blocked"
    assert start_response.json()["reason"] == "blocked"

    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)
    dependencies_result = cli_runner(["node", "dependencies", "--node", right])
    validate_result = cli_runner(["node", "dependency-validate", "--node", right])
    blockers_result = cli_runner(["node", "blockers", "--node", right])
    blocked_start_result = cli_runner(["node", "run", "start", "--node", right])

    assert dependencies_result.exit_code == 0
    assert len(dependencies_result.json()["dependencies"]) == 1
    assert validate_result.exit_code == 0
    assert validate_result.json()["status"] == "valid"
    assert blockers_result.exit_code == 0
    assert blocked_start_result.exit_code == 4
    assert blocked_start_result.stderr_json()["error"] == "daemon_conflict"
    assert blocked_start_result.stderr_json()["details"]["response"]["status"] == "blocked"

    app_client.post("/api/nodes/lifecycle/transition", headers=auth_headers, json={"node_id": left, "target_state": "RUNNING"})
    app_client.post("/api/nodes/lifecycle/transition", headers=auth_headers, json={"node_id": left, "target_state": "COMPLETE"})
    start_after_complete = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": right})

    assert start_after_complete.json()["status"] == "admitted"
    assert start_after_complete.json()["current_state"] == "RUNNING"


def test_sibling_dependency_requires_incremental_merge_before_admission(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="READY")

    left = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Left",
        prompt="boot prompt",
        parent_node_id=parent.node_id,
    )
    seed_node_lifecycle(db_session_factory, node_id=str(left.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=left.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=left.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="READY")

    right = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Right",
        prompt="boot prompt",
        parent_node_id=parent.node_id,
    )
    seed_node_lifecycle(db_session_factory, node_id=str(right.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=right.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=right.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(right.node_id), target_state="READY")
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    with query_session_scope(db_session_factory) as session:
        left_selector = session.get(LogicalNodeCurrentVersion, left.node_id)
        assert left_selector is not None
        left_version_id = left_selector.authoritative_node_version_id

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=left_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=left_version_id,
        files={"shared.txt": "base\nleft final\n"},
        message="Left final",
        record_as_final=True,
    )
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="COMPLETE")

    readiness_after_complete = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)
    blocked_admission = admit_node_run(db_session_factory, node_id=right.node_id)

    assert readiness_after_complete.status == "blocked"
    assert readiness_after_complete.blockers[0].blocker_kind == "blocked_on_incremental_merge"
    assert blocked_admission.status == "blocked"

    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=left_version_id)
    merge_result = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    readiness_after_merge = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)
    admitted_after_merge = admit_node_run(db_session_factory, node_id=right.node_id)

    assert merge_result is not None
    assert merge_result.status == "merged"
    assert readiness_after_merge.status == "ready"
    assert admitted_after_merge.status == "admitted"


def test_pause_and_lifecycle_blockers_are_exposed(app_client, auth_headers, migrated_public_schema) -> None:
    node_id = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Blocked Node", "prompt": "boot prompt"},
    ).json()["node_id"]

    compile_response = app_client.get(f"/api/nodes/{node_id}/blockers", headers=auth_headers)
    app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    app_client.post(
        "/api/nodes/lifecycle/transition",
        headers=auth_headers,
        json={"node_id": node_id, "target_state": "READY"},
    )
    app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": node_id})
    app_client.post("/api/nodes/pause", headers=auth_headers, json={"node_id": node_id})
    paused_response = app_client.get(f"/api/nodes/{node_id}/blockers", headers=auth_headers)

    assert compile_response.status_code == 200
    assert {item["blocker_kind"] for item in compile_response.json()} >= {"not_compiled", "lifecycle_not_ready"}
    assert paused_response.status_code == 200
    paused_kinds = {item["blocker_kind"] for item in paused_response.json()}
    assert "pause_gate_active" in paused_kinds
    assert "manual_pause" in {item["details_json"].get("pause_flag_name") for item in paused_response.json()}
