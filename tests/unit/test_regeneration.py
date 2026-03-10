from __future__ import annotations

import pytest

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.orchestration import apply_authority_mutation
from aicoding.daemon.rebuild_coordination import inspect_cutover_readiness, inspect_rebuild_coordination
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.regeneration import list_rebuild_events_for_node, regenerate_node_and_descendants
from aicoding.daemon.versioning import cutover_candidate_version, initialize_node_version, list_node_versions
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


def test_rebuild_coordination_reports_active_run_blocker(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(child.node.node_id), target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=str(child.node.node_id), command="node.run.start")

    coordination = inspect_rebuild_coordination(db_session_factory, logical_node_id=child.node.node_id, scope="upstream")

    assert coordination.status == "blocked"
    assert any(item.blocker_type == "active_or_paused_run" and item.scope_role == "target" for item in coordination.blockers)
    with pytest.raises(DaemonConflictError, match="live runtime state blocks upstream rectification"):
        from aicoding.daemon.regeneration import rectify_upstream

        rectify_upstream(db_session_factory, logical_node_id=child.node.node_id, catalog=catalog)


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
