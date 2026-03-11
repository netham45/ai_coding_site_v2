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
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import bootstrap_live_git_repo, refresh_child_live_git_from_parent_head, stage_live_git_change
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import IncrementalChildMergeState, LogicalNodeCurrentVersion, ParentIncrementalMergeLane
from aicoding.db.session import query_session_scope
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


def test_admit_node_run_reports_active_conflict_before_lifecycle_gate(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = _create_runnable_node(db_session_factory, registry, kind="epic", title="Runnable")

    first_admission = admit_node_run(db_session_factory, node_id=node.node_id)
    second_admission = admit_node_run(db_session_factory, node_id=node.node_id)

    assert first_admission.status == "admitted"
    assert second_admission.status == "blocked"
    assert second_admission.reason == "active_run_conflict"
    assert second_admission.current_run_id == first_admission.current_run_id
