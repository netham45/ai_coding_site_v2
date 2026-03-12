from __future__ import annotations

import pytest

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.lifecycle import (
    bind_node_lifecycle_version,
    load_node_lifecycle,
    seed_node_lifecycle,
    transition_node_lifecycle,
    update_node_cursor,
)
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_seed_and_load_node_lifecycle(db_session_factory, migrated_public_schema) -> None:
    seeded = seed_node_lifecycle(db_session_factory, node_id="node-1", initial_state="DRAFT")
    loaded = load_node_lifecycle(db_session_factory, "node-1")

    assert seeded.lifecycle_state == "DRAFT"
    assert loaded.node_id == "node-1"
    assert loaded.execution_cursor_json == {}
    assert loaded.run_status is None


def test_transition_node_lifecycle_enforces_legal_state_machine(db_session_factory, migrated_public_schema) -> None:
    seed_node_lifecycle(db_session_factory, node_id="node-2", initial_state="DRAFT")

    with pytest.raises(DaemonConflictError):
        transition_node_lifecycle(db_session_factory, node_id="node-2", target_state="RUNNING")

    assert transition_node_lifecycle(db_session_factory, node_id="node-2", target_state="COMPILED").lifecycle_state == "COMPILED"
    assert transition_node_lifecycle(db_session_factory, node_id="node-2", target_state="READY").lifecycle_state == "READY"


def test_transition_node_lifecycle_allows_dependency_wait_reset_and_ready_reentry(
    db_session_factory, migrated_public_schema
) -> None:
    seed_node_lifecycle(db_session_factory, node_id="node-2c", initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id="node-2c", target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id="node-2c", target_state="READY")
    transition_node_lifecycle(db_session_factory, node_id="node-2c", target_state="WAITING_ON_SIBLING_DEPENDENCY")

    ready_again = transition_node_lifecycle(db_session_factory, node_id="node-2c", target_state="READY")

    assert ready_again.lifecycle_state == "READY"


def test_bind_node_lifecycle_version_records_bound_version(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Versioned", prompt="boot prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")

    rebound = bind_node_lifecycle_version(
        db_session_factory,
        node_id=str(node.node_id),
        node_version_id=version.id,
        reset_runtime=True,
    )

    assert rebound.node_version_id == version.id


def test_transition_node_lifecycle_accepts_paused_alias(db_session_factory, migrated_public_schema) -> None:
    seed_node_lifecycle(db_session_factory, node_id="node-2b", initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id="node-2b", target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id="node-2b", target_state="READY")

    from aicoding.daemon.orchestration import apply_authority_mutation

    apply_authority_mutation(db_session_factory, node_id="node-2b", command="node.run.start")
    paused = transition_node_lifecycle(
        db_session_factory,
        node_id="node-2b",
        target_state="PAUSED",
        pause_flag_name="user_review_required",
    )

    assert paused.lifecycle_state == "PAUSED_FOR_USER"
    assert paused.run_status == "PAUSED"
    assert paused.pause_flag_name == "user_review_required"


def test_update_node_cursor_requires_running_or_paused_state(db_session_factory, migrated_public_schema) -> None:
    seed_node_lifecycle(db_session_factory, node_id="node-3", initial_state="READY")

    with pytest.raises(DaemonConflictError):
        update_node_cursor(db_session_factory, node_id="node-3", current_task_id="task.bootstrap")


def test_update_node_cursor_persists_resume_safe_fields(db_session_factory, migrated_public_schema) -> None:
    seed_node_lifecycle(db_session_factory, node_id="node-4", initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id="node-4", target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id="node-4", target_state="READY")

    from aicoding.daemon.orchestration import apply_authority_mutation

    apply_authority_mutation(db_session_factory, node_id="node-4", command="node.run.start")
    updated = update_node_cursor(
        db_session_factory,
        node_id="node-4",
        current_task_id="task.execute",
        current_subtask_id="subtask.render",
        current_subtask_attempt=2,
        last_completed_subtask_id="subtask.prepare",
        execution_cursor_json={"offset": 3, "checkpoint": "render"},
        failure_count_from_children=1,
        failure_count_consecutive=2,
        defer_to_user_threshold=3,
        is_resumable=True,
        working_tree_state="clean",
    )

    assert updated.lifecycle_state == "RUNNING"
    assert updated.current_task_id == "task.execute"
    assert updated.current_subtask_id == "subtask.render"
    assert updated.current_subtask_attempt == 2
    assert updated.execution_cursor_json == {"offset": 3, "checkpoint": "render"}
    assert updated.failure_count_from_children == 1
    assert updated.working_tree_state == "clean"


def test_load_node_lifecycle_rejects_missing_record(db_session_factory, migrated_public_schema) -> None:
    with pytest.raises(DaemonNotFoundError):
        load_node_lifecycle(db_session_factory, "missing-node")
