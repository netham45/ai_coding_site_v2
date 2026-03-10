from __future__ import annotations

import pytest

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.lifecycle import (
    load_node_lifecycle,
    seed_node_lifecycle,
    transition_node_lifecycle,
    update_node_cursor,
)


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
