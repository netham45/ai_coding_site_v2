from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import NodeLifecycleState
from aicoding.db.session import query_session_scope, session_scope

NODE_LIFECYCLE_STATES = {
    "DRAFT",
    "COMPILE_FAILED",
    "COMPILED",
    "READY",
    "RUNNING",
    "WAITING_ON_CHILDREN",
    "WAITING_ON_SIBLING_DEPENDENCY",
    "RECTIFYING_SELF",
    "RECTIFYING_UPSTREAM",
    "VALIDATION_PENDING",
    "REVIEW_PENDING",
    "TESTING_PENDING",
    "PAUSED_FOR_USER",
    "FAILED_TO_PARENT",
    "COMPLETE",
    "SUPERSEDED",
    "CANCELLED",
}

NODE_RUN_STATUSES = {
    "PENDING",
    "RUNNING",
    "PAUSED",
    "FAILED",
    "COMPLETE",
    "CANCELLED",
}

ALLOWED_NODE_TRANSITIONS = {
    "DRAFT": {"COMPILED", "COMPILE_FAILED", "CANCELLED"},
    "COMPILE_FAILED": {"COMPILED", "SUPERSEDED"},
    "COMPILED": {"READY"},
    "READY": {"RUNNING", "CANCELLED"},
    "RUNNING": {
        "WAITING_ON_CHILDREN",
        "WAITING_ON_SIBLING_DEPENDENCY",
        "VALIDATION_PENDING",
        "REVIEW_PENDING",
        "TESTING_PENDING",
        "PAUSED_FOR_USER",
        "FAILED_TO_PARENT",
        "RECTIFYING_SELF",
        "RECTIFYING_UPSTREAM",
        "COMPLETE",
        "CANCELLED",
    },
    "WAITING_ON_CHILDREN": {"RUNNING", "PAUSED_FOR_USER"},
    "WAITING_ON_SIBLING_DEPENDENCY": {"RUNNING", "PAUSED_FOR_USER"},
    "VALIDATION_PENDING": {"REVIEW_PENDING"},
    "REVIEW_PENDING": {"TESTING_PENDING"},
    "TESTING_PENDING": {"RUNNING"},
    "PAUSED_FOR_USER": {"RUNNING", "RECTIFYING_SELF", "RECTIFYING_UPSTREAM", "CANCELLED"},
    "RECTIFYING_SELF": {"RUNNING"},
    "RECTIFYING_UPSTREAM": {"RUNNING"},
    "FAILED_TO_PARENT": {"SUPERSEDED"},
    "COMPLETE": {"SUPERSEDED"},
    "SUPERSEDED": set(),
    "CANCELLED": set(),
}

CURSOR_MUTABLE_STATES = {"RUNNING", "PAUSED_FOR_USER"}

LIFECYCLE_STATE_ALIASES = {
    "PAUSED": "PAUSED_FOR_USER",
}


@dataclass(frozen=True, slots=True)
class NodeLifecycleSnapshot:
    node_id: str
    lifecycle_state: str
    run_status: str | None
    current_run_id: UUID | None
    current_task_id: str | None
    current_subtask_id: str | None
    current_subtask_attempt: int | None
    last_completed_subtask_id: str | None
    execution_cursor_json: dict[str, object]
    failure_count_from_children: int
    failure_count_consecutive: int
    defer_to_user_threshold: int
    is_resumable: bool
    pause_flag_name: str | None
    working_tree_state: str | None
    updated_at: datetime

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "current_run_id": None if self.current_run_id is None else str(self.current_run_id),
            "current_task_id": self.current_task_id,
            "current_subtask_id": self.current_subtask_id,
            "current_subtask_attempt": self.current_subtask_attempt,
            "last_completed_subtask_id": self.last_completed_subtask_id,
            "execution_cursor_json": self.execution_cursor_json,
            "failure_count_from_children": self.failure_count_from_children,
            "failure_count_consecutive": self.failure_count_consecutive,
            "defer_to_user_threshold": self.defer_to_user_threshold,
            "is_resumable": self.is_resumable,
            "pause_flag_name": self.pause_flag_name,
            "working_tree_state": self.working_tree_state,
            "updated_at": self.updated_at.isoformat(),
        }


def _lock_node(session: Session, node_id: str) -> None:
    session.execute(text("select pg_advisory_xact_lock(hashtext(:node_id))"), {"node_id": node_id})


def _lifecycle_query(node_id: str):
    return select(NodeLifecycleState).where(NodeLifecycleState.node_id == node_id)


def _snapshot(record: NodeLifecycleState) -> NodeLifecycleSnapshot:
    return NodeLifecycleSnapshot(
        node_id=record.node_id,
        lifecycle_state=record.lifecycle_state,
        run_status=record.run_status,
        current_run_id=record.current_run_id,
        current_task_id=record.current_task_id,
        current_subtask_id=record.current_subtask_id,
        current_subtask_attempt=record.current_subtask_attempt,
        last_completed_subtask_id=record.last_completed_subtask_id,
        execution_cursor_json=dict(record.execution_cursor_json),
        failure_count_from_children=record.failure_count_from_children,
        failure_count_consecutive=record.failure_count_consecutive,
        defer_to_user_threshold=record.defer_to_user_threshold,
        is_resumable=record.is_resumable,
        pause_flag_name=record.pause_flag_name,
        working_tree_state=record.working_tree_state,
        updated_at=record.updated_at,
    )


def _infer_run_status(target_state: str, current_run_id: UUID | None, existing_status: str | None) -> str | None:
    if target_state == "RUNNING":
        return "RUNNING"
    if target_state == "PAUSED_FOR_USER":
        return "PAUSED"
    if target_state == "FAILED_TO_PARENT":
        return "FAILED"
    if target_state == "COMPLETE":
        return "COMPLETE"
    if target_state == "CANCELLED":
        return "CANCELLED"
    if target_state in {"READY", "COMPILED", "COMPILE_FAILED", "DRAFT", "SUPERSEDED"}:
        return None if current_run_id is None else existing_status
    if current_run_id is None:
        return None
    return existing_status or "PENDING"


def _validate_transition(from_state: str, to_state: str) -> None:
    if to_state not in NODE_LIFECYCLE_STATES:
        raise DaemonConflictError(f"unsupported lifecycle state '{to_state}'")
    if from_state == to_state:
        return
    if to_state not in ALLOWED_NODE_TRANSITIONS.get(from_state, set()):
        raise DaemonConflictError(f"illegal lifecycle transition {from_state} -> {to_state}")


def _apply_transition(
    record: NodeLifecycleState,
    *,
    target_state: str,
    current_run_id: UUID | None = None,
    pause_flag_name: str | None = None,
) -> NodeLifecycleState:
    _validate_transition(record.lifecycle_state, target_state)
    if current_run_id is not None:
        record.current_run_id = current_run_id
    record.lifecycle_state = target_state
    record.run_status = _infer_run_status(target_state, record.current_run_id, record.run_status)
    record.is_resumable = target_state in {"RUNNING", "PAUSED_FOR_USER", "WAITING_ON_CHILDREN", "WAITING_ON_SIBLING_DEPENDENCY"}
    record.pause_flag_name = pause_flag_name if target_state == "PAUSED_FOR_USER" else None
    if target_state in {"COMPLETE", "FAILED_TO_PARENT", "CANCELLED", "SUPERSEDED"}:
        record.current_task_id = None
        record.current_subtask_id = None
        record.current_subtask_attempt = None
        if target_state in {"COMPLETE", "FAILED_TO_PARENT", "CANCELLED", "SUPERSEDED"}:
            record.is_resumable = False
    return record


def normalize_lifecycle_state(target_state: str) -> str:
    return LIFECYCLE_STATE_ALIASES.get(target_state, target_state)


def seed_node_lifecycle(session_factory: sessionmaker[Session], *, node_id: str, initial_state: str = "DRAFT") -> NodeLifecycleSnapshot:
    with session_scope(session_factory) as session:
        _lock_node(session, node_id)
        record = session.execute(_lifecycle_query(node_id)).scalar_one_or_none()
        if record is None:
            record = NodeLifecycleState(node_id=node_id, lifecycle_state=initial_state, execution_cursor_json={})
            session.add(record)
            session.flush()
        return _snapshot(record)


def load_node_lifecycle(session_factory: sessionmaker[Session], node_id: str) -> NodeLifecycleSnapshot:
    with query_session_scope(session_factory) as session:
        record = session.execute(_lifecycle_query(node_id)).scalar_one_or_none()
        if record is None:
            raise DaemonNotFoundError("node lifecycle record not found")
        return _snapshot(record)


def transition_node_lifecycle(
    session_factory: sessionmaker[Session],
    *,
    node_id: str,
    target_state: str,
    pause_flag_name: str | None = None,
) -> NodeLifecycleSnapshot:
    target_state = normalize_lifecycle_state(target_state)
    with session_scope(session_factory) as session:
        _lock_node(session, node_id)
        record = session.execute(_lifecycle_query(node_id)).scalar_one_or_none()
        if record is None:
            raise DaemonNotFoundError("node lifecycle record not found")
        _apply_transition(record, target_state=target_state, pause_flag_name=pause_flag_name)
        session.flush()
        return _snapshot(record)


def update_node_cursor(
    session_factory: sessionmaker[Session],
    *,
    node_id: str,
    current_task_id: str | None = None,
    current_subtask_id: str | None = None,
    current_subtask_attempt: int | None = None,
    last_completed_subtask_id: str | None = None,
    execution_cursor_json: dict[str, Any] | None = None,
    failure_count_from_children: int | None = None,
    failure_count_consecutive: int | None = None,
    defer_to_user_threshold: int | None = None,
    is_resumable: bool | None = None,
    pause_flag_name: str | None = None,
    working_tree_state: str | None = None,
) -> NodeLifecycleSnapshot:
    with session_scope(session_factory) as session:
        _lock_node(session, node_id)
        record = session.execute(_lifecycle_query(node_id)).scalar_one_or_none()
        if record is None:
            raise DaemonNotFoundError("node lifecycle record not found")
        if record.lifecycle_state not in CURSOR_MUTABLE_STATES:
            raise DaemonConflictError(f"cannot update execution cursor while node is {record.lifecycle_state}")
        if current_task_id is not None:
            record.current_task_id = current_task_id
        if current_subtask_id is not None:
            record.current_subtask_id = current_subtask_id
        if current_subtask_attempt is not None:
            record.current_subtask_attempt = current_subtask_attempt
        if last_completed_subtask_id is not None:
            record.last_completed_subtask_id = last_completed_subtask_id
        if execution_cursor_json is not None:
            record.execution_cursor_json = dict(execution_cursor_json)
        if failure_count_from_children is not None:
            record.failure_count_from_children = failure_count_from_children
        if failure_count_consecutive is not None:
            record.failure_count_consecutive = failure_count_consecutive
        if defer_to_user_threshold is not None:
            record.defer_to_user_threshold = defer_to_user_threshold
        if is_resumable is not None:
            record.is_resumable = is_resumable
        if pause_flag_name is not None and record.lifecycle_state == "PAUSED_FOR_USER":
            record.pause_flag_name = pause_flag_name
        if working_tree_state is not None:
            record.working_tree_state = working_tree_state
        session.flush()
        return _snapshot(record)
