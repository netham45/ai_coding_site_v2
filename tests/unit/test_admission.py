from __future__ import annotations

import pytest
from sqlalchemy import select

from aicoding.daemon.admission import (
    add_node_dependency,
    admit_node_run,
    check_node_dependency_readiness,
    list_node_blockers,
    list_node_dependencies,
    validate_node_dependency_graph,
)
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.incremental_parent_merge import process_next_incremental_child_merge, record_completed_child_for_incremental_merge
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import bootstrap_live_git_repo, refresh_child_live_git_from_parent_head, stage_live_git_change
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.materialization import materialize_layout_children
from aicoding.daemon.regeneration import _record_rebuild_event
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import (
    DaemonNodeState,
    IncrementalChildMergeState,
    LogicalNodeCurrentVersion,
    NodeLifecycleState,
    NodeVersion,
    ParentChildAuthority,
    ParentIncrementalMergeLane,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_runnable_node(db_session_factory, registry, *, kind: str, title: str, parent_node_id=None):
    node = create_hierarchy_node(
        db_session_factory,
        registry,
        kind=kind,
        title=title,
        prompt="boot prompt",
        parent_node_id=parent_node_id,
    )
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=load_resource_catalog())
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    return node


def _create_compiled_node(db_session_factory, registry, *, kind: str, title: str, parent_node_id=None):
    node = create_hierarchy_node(
        db_session_factory,
        registry,
        kind=kind,
        title=title,
        prompt="boot prompt",
        parent_node_id=parent_node_id,
    )
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=load_resource_catalog())
    return node


def _authoritative_version_id(db_session_factory, node_id):
    with query_session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, node_id)
        assert selector is not None
        return selector.authoritative_node_version_id


def test_add_and_list_sibling_dependency(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)

    dependency = add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    listed = list_node_dependencies(db_session_factory, node_id=right.node_id)

    assert dependency.dependency_type == "sibling"
    assert len(listed) == 1
    assert listed[0].depends_on_node_version_id == dependency.depends_on_node_version_id


def test_add_dependency_rejects_invalid_relative(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = _create_runnable_node(db_session_factory, registry, kind="phase", title="Child", parent_node_id=parent.node_id)

    with pytest.raises(DaemonConflictError):
        add_node_dependency(db_session_factory, node_id=child.node_id, depends_on_node_id=parent.node_id)


def test_dependency_readiness_blocks_until_target_complete(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)
    blockers = list_node_blockers(db_session_factory, node_id=right.node_id)

    assert readiness.status == "blocked"
    assert blockers[0].blocker_kind == "blocked_on_dependency"


def test_sibling_dependency_requires_incremental_merge_after_target_complete(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="COMPLETE")

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "blocked"
    assert readiness.blockers[0].blocker_kind == "blocked_on_incremental_merge"


def test_sibling_dependency_becomes_ready_after_incremental_merge_success(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    left_version_id = _authoritative_version_id(db_session_factory, left.node_id)

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
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=left_version_id)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "ready"
    assert readiness.blockers == []


def test_non_leaf_sibling_dependency_becomes_ready_after_incremental_merge_success(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    plan = _create_runnable_node(db_session_factory, registry, kind="plan", title="Left Plan", parent_node_id=left.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    left_version_id = _authoritative_version_id(db_session_factory, left.node_id)
    right_version_id = _authoritative_version_id(db_session_factory, right.node_id)
    plan_version_id = _authoritative_version_id(db_session_factory, plan.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=left_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=right_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=plan_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=plan_version_id,
        files={"shared.txt": "base\nplan final\n"},
        message="Plan final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=plan_version_id)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=left_version_id)
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="COMPLETE")
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    stale_readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)
    refreshed_status = refresh_child_live_git_from_parent_head(db_session_factory, child_version_id=right_version_id)
    refreshed_readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert stale_readiness.status == "blocked"
    assert stale_readiness.blockers[0].blocker_kind == "blocked_on_parent_refresh"
    assert refreshed_status.seed_commit_sha == refreshed_status.head_commit_sha
    assert refreshed_readiness.status == "ready"


def test_sibling_dependency_reports_conflicted_incremental_merge(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    left_version_id = _authoritative_version_id(db_session_factory, left.node_id)

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
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=left_version_id)

    # Force a conflict-classified merge row without needing a second child in this admission-focused test.
    from aicoding.db.session import session_scope
    with session_scope(db_session_factory) as session:
        merge_row = session.execute(select(IncrementalChildMergeState).where(IncrementalChildMergeState.child_node_version_id == left_version_id)).scalar_one()
        merge_row.status = "conflicted"
        lane = session.get(ParentIncrementalMergeLane, parent_version.id)
        assert lane is not None
        lane.status = "blocked"
        lane.blocked_reason = "merge_conflict"
        session.flush()

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "blocked"
    assert readiness.blockers[0].blocker_kind == "blocked_on_merge_conflict"


def test_sibling_dependency_blocks_on_parent_refresh_until_child_bootstrap_is_refreshed(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    left_version_id = _authoritative_version_id(db_session_factory, left.node_id)
    right_version_id = _authoritative_version_id(db_session_factory, right.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=left_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=right_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=left_version_id,
        files={"shared.txt": "base\nleft final\n"},
        message="Left final",
        record_as_final=True,
    )
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="COMPLETE")
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=left_version_id)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    stale_readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)
    refreshed_status = refresh_child_live_git_from_parent_head(db_session_factory, child_version_id=right_version_id)
    refreshed_readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert stale_readiness.status == "blocked"
    assert stale_readiness.blockers[0].blocker_kind == "blocked_on_parent_refresh"
    assert refreshed_status.seed_commit_sha == refreshed_status.head_commit_sha
    assert refreshed_readiness.status == "ready"


def test_dependency_readiness_marks_impossible_wait_for_failed_target(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=str(left.node_id), target_state="FAILED_TO_PARENT")

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "impossible_wait"
    assert readiness.blockers[0].blocker_kind == "impossible_wait"


def test_validate_dependency_graph_rejects_cycle(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    with pytest.raises(DaemonConflictError):
        add_node_dependency(db_session_factory, node_id=left.node_id, depends_on_node_id=right.node_id)

    validation = validate_node_dependency_graph(db_session_factory, node_id=right.node_id)
    assert validation.status == "valid"


def test_admit_node_run_blocks_unsatisfied_dependency(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    admission = admit_node_run(db_session_factory, node_id=right.node_id)

    assert admission.status == "blocked"
    assert admission.reason == "blocked"


def test_admit_node_run_accepts_ready_unblocked_node(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = _create_runnable_node(db_session_factory, registry, kind="epic", title="Runnable")

    admission = admit_node_run(db_session_factory, node_id=node.node_id)

    assert admission.status == "admitted"
    assert admission.current_state == "RUNNING"
    assert admission.current_run_id is not None


def test_admit_node_run_promotes_compiled_manual_child_when_otherwise_ready(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = _create_runnable_node(db_session_factory, registry, kind="epic", title="Parent")
    child = _create_compiled_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Compiled Child",
        parent_node_id=parent.node_id,
    )

    admission = admit_node_run(db_session_factory, node_id=child.node_id)
    lifecycle = load_node_lifecycle(db_session_factory, str(child.node_id))

    assert admission.status == "admitted"
    assert admission.current_state == "RUNNING"
    assert admission.current_run_id is not None
    assert lifecycle.lifecycle_state == "RUNNING"


def test_admit_node_run_reports_active_conflict_before_lifecycle_gate(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = _create_runnable_node(db_session_factory, registry, kind="epic", title="Runnable")

    first_admission = admit_node_run(db_session_factory, node_id=node.node_id)
    second_admission = admit_node_run(db_session_factory, node_id=node.node_id)

    assert first_admission.status == "admitted"
    assert second_admission.status == "blocked"
    assert second_admission.reason == "active_run_conflict"
    assert second_admission.current_run_id == first_admission.current_run_id


def test_admit_node_run_ignores_stale_live_runtime_rows_after_version_change(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = _create_runnable_node(db_session_factory, registry, kind="epic", title="Runnable")
    version_one_id = _authoritative_version_id(db_session_factory, node.node_id)
    version_two = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)

    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, node.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, version_one_id)
        new_version = session.get(NodeVersion, version_two.id)
        assert old_version is not None and new_version is not None
        old_version.status = "superseded"
        new_version.status = "authoritative"
        selector.authoritative_node_version_id = new_version.id
        selector.latest_created_node_version_id = new_version.id
        new_version.compiled_workflow_id = old_version.compiled_workflow_id
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        assert lifecycle is not None
        lifecycle.node_version_id = old_version.id
        lifecycle.current_run_id = version_one_id
        lifecycle.run_status = "RUNNING"
        lifecycle.lifecycle_state = "RUNNING"
        daemon_state = DaemonNodeState(
            node_id=str(node.node_id),
            node_version_id=old_version.id,
            current_run_id=version_one_id,
            lifecycle_state="active",
            authority="daemon",
            last_command="node.run.start",
            last_event_id=version_one_id,
        )
        session.merge(daemon_state)
        session.flush()

    admission = admit_node_run(db_session_factory, node_id=node.node_id)

    assert admission.status == "admitted"
    assert admission.node_version_id == version_two.id


def test_dependency_invalidated_manual_restart_reports_child_tree_rebuild_required(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    first_materialization = materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=right.node_id,
    )
    assert first_materialization.child_count > 0

    fresh = create_superseding_node_version(
        db_session_factory,
        logical_node_id=right.node_id,
        clone_structure=False,
    )
    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, right.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        fresh_version = session.get(NodeVersion, fresh.id)
        lifecycle = session.get(NodeLifecycleState, str(right.node_id))
        assert old_version is not None
        assert fresh_version is not None
        assert lifecycle is not None
        session.merge(
            ParentChildAuthority(
                parent_node_version_id=old_version.id,
                authority_mode="manual",
                authoritative_layout_hash=None,
            )
        )
        old_version.status = "superseded"
        fresh_version.status = "authoritative"
        fresh_version.compiled_workflow_id = old_version.compiled_workflow_id
        selector.authoritative_node_version_id = fresh.id
        selector.latest_created_node_version_id = fresh.id
        lifecycle.node_version_id = fresh.id
        lifecycle.lifecycle_state = "WAITING_ON_SIBLING_DEPENDENCY"
        lifecycle.run_status = "IDLE"
        lifecycle.current_run_id = None
        session.flush()

    _record_rebuild_event(
        db_session_factory,
        root_logical_node_id=right.node_id,
        root_node_version_id=fresh.id,
        target_node_version_id=fresh.id,
        event_kind="candidate_created",
        event_status="pending",
        scope="subtree",
        trigger_reason="test_manual_tree_rebuild_gate",
        details_json={
            "supersedes_node_version_id": str(first_materialization.parent_node_version_id),
            "fresh_dependency_restart": True,
        },
    )

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "blocked"
    assert [item.blocker_kind for item in readiness.blockers] == [
        "child_tree_rebuild_required",
        "lifecycle_not_ready",
    ]
    assert readiness.blockers[0].details_json["authority_mode"] == "manual"


def test_dependency_invalidated_manual_restart_clears_rebuild_blocker_after_manual_child_rebuild(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    left = _create_runnable_node(db_session_factory, registry, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_node(db_session_factory, registry, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(db_session_factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    first_materialization = materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=right.node_id,
    )
    assert first_materialization.child_count > 0

    fresh = create_superseding_node_version(
        db_session_factory,
        logical_node_id=right.node_id,
        clone_structure=False,
    )
    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, right.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        fresh_version = session.get(NodeVersion, fresh.id)
        lifecycle = session.get(NodeLifecycleState, str(right.node_id))
        assert old_version is not None
        assert fresh_version is not None
        assert lifecycle is not None
        session.merge(
            ParentChildAuthority(
                parent_node_version_id=old_version.id,
                authority_mode="manual",
                authoritative_layout_hash=None,
            )
        )
        old_version.status = "superseded"
        fresh_version.status = "authoritative"
        fresh_version.compiled_workflow_id = old_version.compiled_workflow_id
        selector.authoritative_node_version_id = fresh.id
        selector.latest_created_node_version_id = fresh.id
        lifecycle.node_version_id = fresh.id
        lifecycle.lifecycle_state = "WAITING_ON_SIBLING_DEPENDENCY"
        lifecycle.run_status = "IDLE"
        lifecycle.current_run_id = None
        session.flush()

    _record_rebuild_event(
        db_session_factory,
        root_logical_node_id=right.node_id,
        root_node_version_id=fresh.id,
        target_node_version_id=fresh.id,
        event_kind="candidate_created",
        event_status="pending",
        scope="subtree",
        trigger_reason="test_manual_tree_rebuild_gate",
        details_json={
            "supersedes_node_version_id": str(first_materialization.parent_node_version_id),
            "fresh_dependency_restart": True,
        },
    )

    create_manual_node(
        db_session_factory,
        registry,
        kind=first_materialization.children[0].kind,
        title="Rebuilt Manual Task",
        prompt="rebuild child tree manually",
        parent_node_id=right.node_id,
    )

    readiness = check_node_dependency_readiness(db_session_factory, node_id=right.node_id)

    assert readiness.status == "blocked"
    assert [item.blocker_kind for item in readiness.blockers] == ["lifecycle_not_ready"]
