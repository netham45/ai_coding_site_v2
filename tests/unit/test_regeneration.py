from __future__ import annotations

import pytest
from uuid import uuid4
from sqlalchemy import select

from aicoding.daemon.admission import add_node_dependency, admit_node_run
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.rebuild_coordination import enumerate_required_cutover_scope, inspect_cutover_readiness, inspect_rebuild_coordination
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.orchestration import apply_authority_mutation
from aicoding.daemon.regeneration import list_rebuild_events_for_node, rectify_upstream, regenerate_node_and_descendants
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version, initialize_node_version, list_node_versions
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import LogicalNodeCurrentVersion, NodeChild, NodeDependency, NodeVersion, Session as DurableSession
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_regenerate_node_and_descendants_creates_stable_candidate_subtree(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    snapshot = regenerate_node_and_descendants(db_session_factory, logical_node_id=parent.node_id, catalog=catalog)
    history = list_rebuild_events_for_node(db_session_factory, logical_node_id=parent.node_id)
    parent_versions = list_node_versions(db_session_factory, parent.node_id)
    child_versions = list_node_versions(db_session_factory, child.node.node_id)

    assert snapshot.scope == "subtree"
    assert len(snapshot.created_candidate_version_ids) == 2
    assert set(snapshot.stable_candidate_version_ids) == set(snapshot.created_candidate_version_ids)
    assert parent_versions[-1].status == "candidate"
    assert parent_versions[-1].final_commit_sha is not None
    assert child_versions[-1].status == "candidate"
    assert child_versions[-1].final_commit_sha is not None
    assert {event.event_kind for event in history.events} >= {"candidate_created", "workflow_compiled", "rectified"}

    lineage = cutover_candidate_version(db_session_factory, version_id=parent_versions[-1].id)
    assert lineage.authoritative_node_version_id == parent_versions[-1].id
    child_lineage = list_node_versions(db_session_factory, child.node.node_id)
    assert child_lineage[-1].status == "authoritative"


def test_rebuild_coordination_reports_active_run_blocker(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=child.node.node_id, catalog=catalog)
    seed_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=child.node.node_id)
    with session_scope(db_session_factory) as session:
        lifecycle = load_node_lifecycle(db_session_factory, str(child.node.node_id))
        selector = session.get(LogicalNodeCurrentVersion, child.node.node_id)
        assert lifecycle.current_run_id is not None
        assert selector is not None
        session.add(
            DurableSession(
                id=uuid4(),
                node_version_id=selector.authoritative_node_version_id,
                node_run_id=lifecycle.current_run_id,
                session_role="primary",
                provider="tmux",
                provider_session_id="tmux-child",
                tmux_session_name="tmux-child",
                cwd="/tmp",
                status="BOUND",
            )
        )
        session.flush()

    coordination = inspect_rebuild_coordination(db_session_factory, logical_node_id=child.node.node_id, scope="upstream")

    assert coordination.status == "blocked"
    assert any(item.blocker_type == "active_or_paused_run" and item.scope_role == "target" for item in coordination.blockers)
    assert any(item.blocker_type == "active_primary_sessions" and item.scope_role == "target" for item in coordination.blockers)
    with pytest.raises(DaemonConflictError, match="live runtime state blocks upstream rectification"):
        from aicoding.daemon.regeneration import rectify_upstream

        rectify_upstream(db_session_factory, logical_node_id=child.node.node_id, catalog=catalog)


def test_regenerate_node_and_descendants_cancels_active_target_and_descendants_before_rebuild(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    for node_id in (parent.node_id, child.node.node_id):
        compile_node_workflow(db_session_factory, logical_node_id=node_id, catalog=catalog)
        seed_node_lifecycle(db_session_factory, node_id=str(node_id), initial_state="DRAFT")
        transition_node_lifecycle(db_session_factory, node_id=str(node_id), target_state="COMPILED")
        transition_node_lifecycle(db_session_factory, node_id=str(node_id), target_state="READY")
        from aicoding.daemon.admission import admit_node_run

        admit_node_run(db_session_factory, node_id=node_id)

    snapshot = regenerate_node_and_descendants(
        db_session_factory,
        logical_node_id=parent.node_id,
        catalog=catalog,
        cancel_conflicting_live_state=True,
    )
    parent_lifecycle = load_node_lifecycle(db_session_factory, str(parent.node_id))
    child_lifecycle = load_node_lifecycle(db_session_factory, str(child.node.node_id))
    history = list_rebuild_events_for_node(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.scope == "subtree"
    assert len(snapshot.created_candidate_version_ids) == 2
    assert parent_lifecycle.lifecycle_state == "CANCELLED"
    assert child_lifecycle.lifecycle_state == "CANCELLED"
    assert any(event.event_kind == "live_conflict_cancelled" for event in history.events)


def test_cutover_readiness_reports_active_authoritative_run_blocker(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    from aicoding.daemon.versioning import create_superseding_node_version

    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=str(node.node_id), command="node.run.start")

    readiness = inspect_cutover_readiness(db_session_factory, version_id=candidate.id)

    assert readiness.status == "blocked"
    assert any(item.blocker_type == "authoritative_active_run" for item in readiness.blockers)


def test_rebuild_coordination_ignores_active_primary_sessions_for_completed_ancestor_runs(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    for node_id in (parent.node_id, child.node.node_id):
        compile_node_workflow(db_session_factory, logical_node_id=node_id, catalog=catalog)
        seed_node_lifecycle(db_session_factory, node_id=str(node_id), initial_state="DRAFT")
        transition_node_lifecycle(db_session_factory, node_id=str(node_id), target_state="COMPILED")
        transition_node_lifecycle(db_session_factory, node_id=str(node_id), target_state="READY")
        from aicoding.daemon.admission import admit_node_run

        admit_node_run(db_session_factory, node_id=node_id)

    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="COMPLETE")
    transition_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), target_state="COMPLETE")

    with session_scope(db_session_factory) as session:
        lifecycle = load_node_lifecycle(db_session_factory, str(parent.node_id))
        selector = session.get(LogicalNodeCurrentVersion, parent.node_id)
        assert lifecycle.current_run_id is not None
        assert selector is not None
        session.add(
            DurableSession(
                id=uuid4(),
                node_version_id=selector.authoritative_node_version_id,
                node_run_id=lifecycle.current_run_id,
                session_role="primary",
                provider="tmux",
                provider_session_id="tmux-parent",
                tmux_session_name="tmux-parent",
                cwd="/tmp",
                status="BOUND",
            )
        )
        session.flush()

    coordination = inspect_rebuild_coordination(db_session_factory, logical_node_id=child.node.node_id, scope="upstream")

    assert coordination.status == "clear"
    assert coordination.blockers == []


def test_regenerate_node_and_descendants_fresh_restarts_dependency_invalidated_sibling_without_children(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    child_under_right = create_manual_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Right Child",
        prompt="child",
        parent_node_id=right.node.node_id,
    )
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)
    transition_node_lifecycle(db_session_factory, node_id=str(right.node.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(right.node.node_id), target_state="READY")

    snapshot = regenerate_node_and_descendants(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    right_lifecycle = load_node_lifecycle(db_session_factory, str(right.node.node_id))
    right_versions = list_node_versions(db_session_factory, right.node.node_id)

    assert len(snapshot.created_candidate_version_ids) == 2
    assert snapshot.stable_candidate_version_ids == [snapshot.root_node_version_id]
    assert right_versions[-1].status == "candidate"
    assert right_lifecycle.lifecycle_state == "WAITING_ON_SIBLING_DEPENDENCY"

    with query_session_scope(db_session_factory) as session:
        right_selector = session.get(LogicalNodeCurrentVersion, right.node.node_id)
        assert right_selector is not None
        fresh_right_version_id = right_selector.latest_created_node_version_id
        old_right_version_id = right_versions[0].id
        old_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == old_right_version_id)
        ).scalars().all()
        fresh_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == fresh_right_version_id)
        ).scalars().all()
        fresh_dependencies = session.execute(
            select(NodeDependency).where(NodeDependency.node_version_id == fresh_right_version_id)
        ).scalars().all()
    history = list_rebuild_events_for_node(db_session_factory, logical_node_id=left.node.node_id)
    scope_event = next(event for event in history.events if event.event_kind == "scope_classified")
    right_create = next(
        event
        for event in history.events
        if event.event_kind == "candidate_created" and event.target_node_version_id == fresh_right_version_id
    )
    replay_blocked = next(
        event
        for event in history.events
        if event.event_kind == "replay_blocked" and event.target_node_version_id == fresh_right_version_id
    )

    assert len(old_edges) == 1
    assert old_edges[0].child_node_version_id == child_under_right.node_version_id
    assert fresh_edges == []
    assert len(fresh_dependencies) == 1
    assert right_lifecycle.node_version_id == fresh_right_version_id
    assert scope_event.details_json["dependency_invalidated_logical_node_ids"] == [str(right.node.node_id)]
    assert right_create.details_json["candidate_role"] == "dependency_invalidated_fresh_restart"
    assert right_create.details_json["replay_classification"] == "blocked_pending_parent_refresh"
    assert replay_blocked.event_status == "waiting_on_parent_refresh"


def test_rectify_upstream_remaps_dependency_invalidated_sibling_candidate_into_ancestor_lineage(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    create_manual_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Right Child",
        prompt="child",
        parent_node_id=right.node.node_id,
    )
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)

    snapshot = rectify_upstream(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    parent_versions = list_node_versions(db_session_factory, parent.node_id)
    left_versions = list_node_versions(db_session_factory, left.node.node_id)
    right_versions = list_node_versions(db_session_factory, right.node.node_id)

    assert snapshot.scope == "upstream"
    assert parent_versions[-1].status == "candidate"
    assert left_versions[-1].status == "candidate"
    assert right_versions[-1].status == "candidate"

    with query_session_scope(db_session_factory) as session:
        parent_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_versions[-1].id).order_by(NodeChild.ordinal)
        ).scalars().all()
        edge_child_version_ids = {edge.child_node_version_id for edge in parent_edges}

    assert edge_child_version_ids == {left_versions[-1].id, right_versions[-1].id}
    assert left_versions[-1].parent_node_version_id == parent_versions[-1].id
    assert right_versions[-1].parent_node_version_id == parent_versions[-1].id


def test_rectify_upstream_reuses_finalized_authoritative_target_without_superseding_it_again(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    child_candidate = create_superseding_node_version(
        db_session_factory,
        logical_node_id=child.node.node_id,
        title="Child v2",
    )
    with session_scope(db_session_factory) as session:
        child_row = session.get(NodeVersion, child_candidate.id)
        assert child_row is not None
        child_row.final_commit_sha = "b" * 40
        session.flush()
    cutover_candidate_version(db_session_factory, version_id=child_candidate.id)

    snapshot = rectify_upstream(db_session_factory, logical_node_id=child.node.node_id, catalog=catalog)
    child_versions = list_node_versions(db_session_factory, child.node.node_id)
    parent_versions = list_node_versions(db_session_factory, parent.node_id)

    assert snapshot.root_node_version_id == child_candidate.id
    assert child_versions[-1].id == child_candidate.id
    assert child_versions[-1].status == "authoritative"
    assert len(child_versions) == 2
    assert parent_versions[-1].status == "candidate"

    with query_session_scope(db_session_factory) as session:
        parent_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_versions[-1].id)
        ).scalars().all()
    assert len(parent_edges) == 1
    assert parent_edges[0].child_node_version_id == child_candidate.id


def test_enumerate_required_cutover_scope_includes_dependency_invalidated_sibling_and_ancestor_candidates(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    create_manual_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Right Child",
        prompt="child",
        parent_node_id=right.node.node_id,
    )
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)

    rectify_upstream(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    parent_candidate = list_node_versions(db_session_factory, parent.node_id)[-1]
    left_candidate = list_node_versions(db_session_factory, left.node.node_id)[-1]
    right_candidate = list_node_versions(db_session_factory, right.node.node_id)[-1]

    scope = enumerate_required_cutover_scope(db_session_factory, version_id=parent_candidate.id)

    assert scope.scope_kind == "upstream"
    assert scope.candidate_root_version_id == left_candidate.id
    assert scope.requested_node_version_id == parent_candidate.id
    assert scope.required_candidate_version_ids[-1] == parent_candidate.id
    assert set(scope.required_candidate_version_ids[:-1]) == {left_candidate.id, right_candidate.id}
    assert left.node_version_id in scope.authoritative_baseline_version_ids
    assert right.node_version_id in scope.authoritative_baseline_version_ids


def test_grouped_cutover_allows_parent_candidate_when_dependency_invalidated_sibling_requires_post_cutover_replay(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)

    rectify_upstream(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    parent_candidate = list_node_versions(db_session_factory, parent.node_id)[-1]
    left_candidate = list_node_versions(db_session_factory, left.node.node_id)[-1]
    right_candidate = list_node_versions(db_session_factory, right.node.node_id)[-1]

    readiness = inspect_cutover_readiness(db_session_factory, version_id=parent_candidate.id)
    lineage = cutover_candidate_version(db_session_factory, version_id=parent_candidate.id)

    assert readiness.status == "ready_with_follow_on_replay"
    assert lineage.authoritative_node_version_id == parent_candidate.id

    with query_session_scope(db_session_factory) as session:
        parent_selector = session.get(LogicalNodeCurrentVersion, parent.node_id)
        left_selector = session.get(LogicalNodeCurrentVersion, left.node.node_id)
        right_selector = session.get(LogicalNodeCurrentVersion, right.node.node_id)
        assert parent_selector is not None
        assert left_selector is not None
        assert right_selector is not None
        assert parent_selector.authoritative_node_version_id == parent_candidate.id
        assert left_selector.authoritative_node_version_id == left_candidate.id
        assert right_selector.authoritative_node_version_id == right_candidate.id


def test_enumerate_required_cutover_scope_returns_local_scope_for_non_rebuild_candidate(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    from aicoding.daemon.versioning import create_superseding_node_version

    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)

    scope = enumerate_required_cutover_scope(db_session_factory, version_id=candidate.id)

    assert scope.scope_kind == "local"
    assert scope.required_candidate_version_ids == [candidate.id]
    assert scope.stopping_reason == "no_rebuild_scope"


def test_cutover_readiness_reports_candidate_replay_incomplete_for_dependency_invalidated_candidate(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)

    regenerate_node_and_descendants(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    candidate_version_id = list_node_versions(db_session_factory, right.node.node_id)[-1].id

    readiness = inspect_cutover_readiness(db_session_factory, version_id=candidate_version_id)

    assert readiness.status == "blocked"
    assert any(item.blocker_type == "candidate_replay_incomplete" for item in readiness.blockers)
    assert any(item.blocker_type == "rebuild_not_stable" for item in readiness.blockers)


def test_cutover_readiness_for_upstream_candidate_aggregates_dependency_invalidated_scope_blockers(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = create_manual_node(db_session_factory, registry, kind="phase", title="Left", prompt="left", parent_node_id=parent.node_id)
    right = create_manual_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node.node_id, depends_on_node_id=left.node.node_id)

    rectify_upstream(db_session_factory, logical_node_id=left.node.node_id, catalog=catalog)
    parent_candidate = list_node_versions(db_session_factory, parent.node_id)[-1]
    right_candidate = list_node_versions(db_session_factory, right.node.node_id)[-1]

    readiness = inspect_cutover_readiness(db_session_factory, version_id=parent_candidate.id)

    assert readiness.status == "ready_with_follow_on_replay"
    assert any(item.blocker_type == "candidate_replay_incomplete" for item in readiness.blockers)
    assert any(item.blocker_type == "rebuild_not_stable" for item in readiness.blockers)
    assert any(
        item.details_json.get("scope_member_node_version_id") == str(right_candidate.id)
        for item in readiness.blockers
        if item.blocker_type == "candidate_replay_incomplete"
    )


def test_cutover_readiness_reports_authoritative_baseline_drift(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Drift", prompt="p")
    initial = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    candidate_id = uuid4()
    drift_authoritative_id = uuid4()

    with session_scope(db_session_factory) as session:
        candidate = NodeVersion(
            id=candidate_id,
            logical_node_id=node.node_id,
            parent_node_version_id=None,
            tier=initial.tier,
            node_kind=initial.node_kind,
            title="Drift v2",
            prompt=initial.prompt,
            description=None,
            status="candidate",
            version_number=2,
            compiled_workflow_id=None,
            supersedes_node_version_id=initial.id,
            active_branch_name="candidate/drift-v2",
            branch_generation_number=2,
            seed_commit_sha=None,
            final_commit_sha=None,
        )
        drift_authoritative = NodeVersion(
            id=drift_authoritative_id,
            logical_node_id=node.node_id,
            parent_node_version_id=None,
            tier=initial.tier,
            node_kind=initial.node_kind,
            title="Drift v3",
            prompt=initial.prompt,
            description=None,
            status="authoritative",
            version_number=3,
            compiled_workflow_id=None,
            supersedes_node_version_id=candidate.id,
            active_branch_name="authoritative/drift-v3",
            branch_generation_number=3,
            seed_commit_sha=None,
            final_commit_sha=None,
        )
        initial_row = session.get(NodeVersion, initial.id)
        assert initial_row is not None
        initial_row.status = "superseded"
        session.add(candidate)
        session.add(drift_authoritative)
        session.flush()

    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, node.node_id)
        assert selector is not None
        selector.authoritative_node_version_id = drift_authoritative_id
        selector.latest_created_node_version_id = drift_authoritative_id
        session.flush()

    readiness = inspect_cutover_readiness(db_session_factory, version_id=candidate_id)

    assert readiness.status == "blocked"
    assert any(item.blocker_type == "authoritative_lineage_changed_since_rebuild_started" for item in readiness.blockers)
