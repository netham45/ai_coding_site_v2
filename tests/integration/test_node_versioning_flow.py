from __future__ import annotations

from sqlalchemy import select
from uuid import UUID

from aicoding.daemon.admission import add_node_dependency
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.materialization import materialize_layout_children
from aicoding.daemon.orchestration import apply_authority_mutation
from aicoding.daemon.regeneration import _record_rebuild_event
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.db.models import LogicalNodeCurrentVersion, NodeChild, NodeLifecycleState, NodeVersion, ParentChildAuthority
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


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


def test_rectify_upstream_endpoint_remaps_dependency_invalidated_sibling_candidate_into_parent_candidate(
    app_client, db_session_factory, migrated_public_schema
) -> None:
    root_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Root Epic", "prompt": "root prompt"},
    )
    parent_id = root_response.json()["node_id"]
    left_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Left Phase", "prompt": "left prompt", "parent_node_id": parent_id},
    )
    right_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Right Phase", "prompt": "right prompt", "parent_node_id": parent_id},
    )
    right_child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "plan", "title": "Right Child", "prompt": "child prompt", "parent_node_id": right_response.json()["node_id"]},
    )
    assert right_child_response.status_code == 200

    add_node_dependency(
        db_session_factory,
        node_id=UUID(right_response.json()["node_id"]),
        depends_on_node_id=UUID(left_response.json()["node_id"]),
    )

    rectify_response = app_client.post(
        f"/api/nodes/{left_response.json()['node_id']}/rectify-upstream",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    assert rectify_response.status_code == 200

    parent_uuid = UUID(parent_id)
    left_uuid = UUID(left_response.json()["node_id"])
    right_uuid = UUID(right_response.json()["node_id"])

    with query_session_scope(db_session_factory) as session:
        parent_selector = session.get(LogicalNodeCurrentVersion, parent_uuid)
        left_selector = session.get(LogicalNodeCurrentVersion, left_uuid)
        right_selector = session.get(LogicalNodeCurrentVersion, right_uuid)
        assert parent_selector is not None
        assert left_selector is not None
        assert right_selector is not None
        parent_candidate = session.get(NodeVersion, parent_selector.latest_created_node_version_id)
        left_candidate = session.get(NodeVersion, left_selector.latest_created_node_version_id)
        right_candidate = session.get(NodeVersion, right_selector.latest_created_node_version_id)
        assert parent_candidate is not None
        assert left_candidate is not None
        assert right_candidate is not None
        parent_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_candidate.id).order_by(NodeChild.ordinal)
        ).scalars().all()
        edge_child_version_ids = {edge.child_node_version_id for edge in parent_edges}

    assert edge_child_version_ids == {left_candidate.id, right_candidate.id}
    assert left_candidate.parent_node_version_id == parent_candidate.id
    assert right_candidate.parent_node_version_id == parent_candidate.id


def test_child_reconciliation_endpoint_allows_empty_dependency_invalidated_manual_restart(
    app_client, db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    phase = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Phase", prompt="phase", parent_node_id=parent.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(phase.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=phase.node_id)

    first = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=phase.node_id)
    superseding = create_superseding_node_version(db_session_factory, logical_node_id=phase.node_id, clone_structure=False)
    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, phase.node_id)
        old_version = session.get(NodeVersion, first.parent_node_version_id)
        fresh_version = session.get(NodeVersion, superseding.id)
        lifecycle = session.get(NodeLifecycleState, str(phase.node_id))
        assert selector is not None
        assert old_version is not None
        assert fresh_version is not None
        assert lifecycle is not None
        authority = session.get(ParentChildAuthority, old_version.id)
        assert authority is not None
        authority.authority_mode = "manual"
        authority.authoritative_layout_hash = None
        old_version.status = "superseded"
        fresh_version.status = "authoritative"
        selector.authoritative_node_version_id = fresh_version.id
        selector.latest_created_node_version_id = fresh_version.id
        lifecycle.node_version_id = fresh_version.id
        lifecycle.lifecycle_state = "WAITING_ON_SIBLING_DEPENDENCY"
        lifecycle.run_status = "IDLE"
        lifecycle.current_run_id = None
        session.flush()
    _record_rebuild_event(
        db_session_factory,
        root_logical_node_id=phase.node_id,
        root_node_version_id=superseding.id,
        target_node_version_id=superseding.id,
        event_kind="candidate_created",
        event_status="pending",
        scope="subtree",
        trigger_reason="test_manual_rebuild_surface",
        details_json={"supersedes_node_version_id": str(first.parent_node_version_id), "fresh_dependency_restart": True},
    )

    headers = {"Authorization": "Bearer change-me"}
    inspection_response = app_client.get(
        f"/api/nodes/{phase.node_id}/children/reconciliation",
        headers=headers,
    )
    reconcile_response = app_client.post(
        f"/api/nodes/{phase.node_id}/children/reconcile",
        headers=headers,
        json={"decision": "preserve_manual"},
    )
    dependency_response = app_client.get(
        f"/api/nodes/{phase.node_id}/dependency-status",
        headers=headers,
    )

    assert inspection_response.status_code == 200
    assert inspection_response.json()["available_decisions"] == ["preserve_manual"]
    assert inspection_response.json()["materialization_status"] == "reconciliation_required"
    assert inspection_response.json()["authority_mode"] == "manual"

    assert reconcile_response.status_code == 200
    assert reconcile_response.json()["materialization_status"] == "manual"
    assert reconcile_response.json()["authority_mode"] == "manual"
    assert reconcile_response.json()["children"] == []

    assert dependency_response.status_code == 200
    assert dependency_response.json()["status"] == "blocked"
    assert [item["blocker_kind"] for item in dependency_response.json()["blockers"]] == [
        "not_compiled",
        "lifecycle_not_ready",
    ]


def test_rebuild_coordination_endpoint_reports_live_blockers_and_blocked_regenerate(app_client, db_session_factory, migrated_public_schema) -> None:
    root_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Blocked Root", "prompt": "root prompt"},
    )
    child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Blocked Child", "prompt": "child prompt", "parent_node_id": root_response.json()["node_id"]},
    )
    child_id = child_response.json()["node_id"]

    seed_node_lifecycle(db_session_factory, node_id=child_id, initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=child_id, target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=child_id, target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=child_id, command="node.run.start")

    coordination_response = app_client.get(
        f"/api/nodes/{child_id}/rebuild-coordination?scope=upstream",
        headers={"Authorization": "Bearer change-me"},
    )
    blocked_rectify = app_client.post(
        f"/api/nodes/{child_id}/rectify-upstream",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    history_response = app_client.get(
        f"/api/nodes/{child_id}/rebuild-history",
        headers={"Authorization": "Bearer change-me"},
    )

    assert coordination_response.status_code == 200
    assert coordination_response.json()["status"] == "blocked"
    assert any(item["blocker_type"] == "active_or_paused_run" for item in coordination_response.json()["blockers"])
    assert blocked_rectify.status_code == 409
    assert "live runtime state blocks upstream rectification" in blocked_rectify.json()["detail"]
    assert any(event["event_kind"] == "live_conflict_blocked" and event["scope"] == "upstream" for event in history_response.json()["events"])


def test_regenerate_endpoint_cancels_live_subtree_and_supersede_can_request_same_behavior(
    app_client, db_session_factory, migrated_public_schema
) -> None:
    root_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Live Root", "prompt": "root prompt"},
    )
    child_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Live Child", "prompt": "child prompt", "parent_node_id": root_response.json()["node_id"]},
    )
    root_id = root_response.json()["node_id"]
    child_id = child_response.json()["node_id"]

    for node_id in (root_id, child_id):
        app_client.post(
            f"/api/nodes/{node_id}/workflow/compile",
            headers={"Authorization": "Bearer change-me"},
            json={},
        )
        seed_node_lifecycle(db_session_factory, node_id=node_id, initial_state="DRAFT")
        transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPILED")
        transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="READY")
        app_client.post(
            "/api/node-runs/start",
            headers={"Authorization": "Bearer change-me"},
            json={"node_id": node_id},
        )

    supersede_response = app_client.post(
        f"/api/nodes/{root_id}/supersede",
        headers={"Authorization": "Bearer change-me"},
        json={"title": "Live Root v2", "cancel_active_subtree": True},
    )
    regenerate_response = app_client.post(
        f"/api/nodes/{root_id}/regenerate",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    root_lifecycle = app_client.get(f"/api/nodes/{root_id}/lifecycle", headers={"Authorization": "Bearer change-me"})
    child_lifecycle = app_client.get(f"/api/nodes/{child_id}/lifecycle", headers={"Authorization": "Bearer change-me"})
    history_response = app_client.get(f"/api/nodes/{root_id}/rebuild-history", headers={"Authorization": "Bearer change-me"})

    assert supersede_response.status_code == 200
    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["scope"] == "subtree"
    assert root_lifecycle.json()["lifecycle_state"] == "CANCELLED"
    assert child_lifecycle.json()["lifecycle_state"] == "CANCELLED"
    assert any(event["event_kind"] == "live_conflict_cancelled" for event in history_response.json()["events"])


def test_cutover_readiness_endpoint_reports_live_blockers(app_client, db_session_factory, migrated_public_schema) -> None:
    create_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Cutover Blocked", "prompt": "boot prompt"},
    )
    node_id = create_response.json()["node_id"]

    supersede_response = app_client.post(
        f"/api/nodes/{node_id}/supersede",
        headers={"Authorization": "Bearer change-me"},
        json={"title": "Cutover Blocked v2"},
    )
    candidate_version_id = supersede_response.json()["id"]

    seed_node_lifecycle(db_session_factory, node_id=node_id, initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=node_id, command="node.run.start")

    readiness_response = app_client.get(
        f"/api/node-versions/{candidate_version_id}/cutover-readiness",
        headers={"Authorization": "Bearer change-me"},
    )
    blocked_cutover = app_client.post(
        f"/api/node-versions/{candidate_version_id}/cutover",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    history_response = app_client.get(
        f"/api/nodes/{node_id}/rebuild-history",
        headers={"Authorization": "Bearer change-me"},
    )

    assert readiness_response.status_code == 200
    assert readiness_response.json()["status"] == "blocked"
    assert any(item["blocker_type"] == "authoritative_active_run" for item in readiness_response.json()["blockers"])
    assert blocked_cutover.status_code == 409
    assert "active or paused run" in blocked_cutover.json()["detail"]
    assert any(event["event_kind"] == "cutover_blocked" and event["scope"] == "cutover" for event in history_response.json()["events"])


def test_regeneration_history_and_cutover_readiness_report_dependency_invalidated_replay_state(
    app_client, db_session_factory, migrated_public_schema
) -> None:
    parent_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Replay Parent", "prompt": "parent prompt"},
    )
    parent_id = parent_response.json()["node_id"]
    left_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Replay Left", "prompt": "left prompt", "parent_node_id": parent_id},
    )
    right_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Replay Right", "prompt": "right prompt", "parent_node_id": parent_id},
    )
    left_id = left_response.json()["node_id"]
    right_id = right_response.json()["node_id"]
    add_node_dependency(db_session_factory, node_id=right_id, depends_on_node_id=left_id)

    regenerate_response = app_client.post(
        f"/api/nodes/{left_id}/regenerate",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    history_response = app_client.get(
        f"/api/nodes/{left_id}/rebuild-history",
        headers={"Authorization": "Bearer change-me"},
    )
    right_versions_response = app_client.get(
        f"/api/nodes/{right_id}/versions",
        headers={"Authorization": "Bearer change-me"},
    )
    right_candidate_id = right_versions_response.json()["versions"][-1]["id"]
    readiness_response = app_client.get(
        f"/api/node-versions/{right_candidate_id}/cutover-readiness",
        headers={"Authorization": "Bearer change-me"},
    )

    assert regenerate_response.status_code == 200
    assert regenerate_response.json()["stable_candidate_version_ids"] == [regenerate_response.json()["root_node_version_id"]]
    assert history_response.status_code == 200
    assert any(
        event["event_kind"] == "scope_classified"
        and event["details_json"]["dependency_invalidated_logical_node_ids"] == [right_id]
        for event in history_response.json()["events"]
    )
    assert any(
        event["event_kind"] == "replay_blocked"
        and event["details_json"]["replay_classification"] == "blocked_pending_parent_refresh"
        for event in history_response.json()["events"]
    )
    assert readiness_response.status_code == 200
    assert readiness_response.json()["status"] == "blocked"
    assert any(item["blocker_type"] == "candidate_replay_incomplete" for item in readiness_response.json()["blockers"])


def test_parent_cutover_readiness_api_aggregates_dependency_invalidated_scope_blockers(
    app_client, db_session_factory, migrated_public_schema
) -> None:
    parent_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "epic", "title": "Parent", "prompt": "parent prompt"},
    )
    parent_id = parent_response.json()["node_id"]
    left_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Left", "prompt": "left prompt", "parent_node_id": parent_id},
    )
    right_response = app_client.post(
        "/api/nodes/create",
        headers={"Authorization": "Bearer change-me"},
        json={"kind": "phase", "title": "Right", "prompt": "right prompt", "parent_node_id": parent_id},
    )
    left_id = left_response.json()["node_id"]
    right_id = right_response.json()["node_id"]
    add_node_dependency(db_session_factory, node_id=right_id, depends_on_node_id=left_id)

    rectify_response = app_client.post(
        f"/api/nodes/{left_id}/rectify-upstream",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )
    parent_versions_response = app_client.get(
        f"/api/nodes/{parent_id}/versions",
        headers={"Authorization": "Bearer change-me"},
    )
    right_versions_response = app_client.get(
        f"/api/nodes/{right_id}/versions",
        headers={"Authorization": "Bearer change-me"},
    )
    parent_candidate_id = parent_versions_response.json()["versions"][-1]["id"]
    right_candidate_id = right_versions_response.json()["versions"][-1]["id"]
    readiness_response = app_client.get(
        f"/api/node-versions/{parent_candidate_id}/cutover-readiness",
        headers={"Authorization": "Bearer change-me"},
    )
    cutover_response = app_client.post(
        f"/api/node-versions/{parent_candidate_id}/cutover",
        headers={"Authorization": "Bearer change-me"},
        json={},
    )

    assert rectify_response.status_code == 200
    assert readiness_response.status_code == 200
    assert readiness_response.json()["status"] == "ready_with_follow_on_replay"
    assert any(
        item["blocker_type"] == "candidate_replay_incomplete"
        and item["details_json"].get("scope_member_node_version_id") == right_candidate_id
        for item in readiness_response.json()["blockers"]
    )
    assert cutover_response.status_code == 200
