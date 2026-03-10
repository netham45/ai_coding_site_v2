from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Select, select, text
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.lifecycle import _apply_transition
from aicoding.db.models import DaemonMutationEvent, DaemonNodeState
from aicoding.db.session import query_session_scope, session_scope
from aicoding.db.models import NodeLifecycleState


@dataclass(frozen=True, slots=True)
class AuthorityStateSnapshot:
    node_id: str
    authority: str
    current_state: str
    current_run_id: UUID
    last_command: str
    last_event_id: UUID
    updated_at: datetime
    event_count: int

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "authority": self.authority,
            "current_state": self.current_state,
            "current_run_id": str(self.current_run_id),
            "last_command": self.last_command,
            "last_event_id": str(self.last_event_id),
            "updated_at": self.updated_at.isoformat(),
            "event_count": self.event_count,
        }


def _lock_node(session: Session, node_id: str) -> None:
    session.execute(text("select pg_advisory_xact_lock(hashtext(:node_id))"), {"node_id": node_id})


def _node_state_query(node_id: str) -> Select[tuple[DaemonNodeState]]:
    return select(DaemonNodeState).where(DaemonNodeState.node_id == node_id)


def _event_count(session: Session, node_id: str) -> int:
    return (
        session.query(DaemonMutationEvent)
        .where(DaemonMutationEvent.node_id == node_id)
        .count()
    )


def load_authority_state(session_factory: sessionmaker[Session], node_id: str) -> AuthorityStateSnapshot:
    with query_session_scope(session_factory) as session:
        state = session.execute(_node_state_query(node_id)).scalar_one_or_none()
        if state is None or state.current_run_id is None:
            raise DaemonNotFoundError("node authority record not found")
        lifecycle = session.get(NodeLifecycleState, node_id)
        return AuthorityStateSnapshot(
            node_id=state.node_id,
            authority=state.authority,
            current_state=_canonical_state(lifecycle.lifecycle_state if lifecycle is not None else state.lifecycle_state),
            current_run_id=state.current_run_id,
            last_command=state.last_command,
            last_event_id=state.last_event_id,
            updated_at=state.updated_at,
            event_count=_event_count(session, node_id),
        )


def apply_authority_mutation(
    session_factory: sessionmaker[Session],
    *,
    node_id: str,
    command: str,
) -> AuthorityStateSnapshot:
    with session_scope(session_factory) as session:
        _lock_node(session, node_id)
        state = session.execute(_node_state_query(node_id)).scalar_one_or_none()

        if command == "node.run.start":
            lifecycle = session.get(NodeLifecycleState, node_id)
            if state is not None and state.current_run_id is not None:
                raise DaemonConflictError("node already has an active durable run")
            if lifecycle is None:
                lifecycle = NodeLifecycleState(node_id=node_id, lifecycle_state="READY", execution_cursor_json={})
                session.add(lifecycle)
            previous_state = state.lifecycle_state if state is not None else None
            run_id = uuid4()
            _apply_transition(lifecycle, target_state="RUNNING", current_run_id=run_id)
            resulting_state = "active"
            current_state = lifecycle.lifecycle_state
        elif command == "node.pause":
            if state is None or state.current_run_id is None:
                raise DaemonNotFoundError("node has no durable run to pause")
            lifecycle = session.get(NodeLifecycleState, node_id)
            if lifecycle is None:
                raise DaemonNotFoundError("node lifecycle record not found")
            if state.lifecycle_state == "paused":
                raise DaemonConflictError("node run is already paused")
            previous_state = state.lifecycle_state
            run_id = state.current_run_id
            _apply_transition(lifecycle, target_state="PAUSED_FOR_USER", pause_flag_name="manual_pause")
            resulting_state = "paused"
            current_state = lifecycle.lifecycle_state
        elif command == "node.resume":
            if state is None or state.current_run_id is None:
                raise DaemonNotFoundError("node has no durable run to resume")
            lifecycle = session.get(NodeLifecycleState, node_id)
            if lifecycle is None:
                raise DaemonNotFoundError("node lifecycle record not found")
            if state.lifecycle_state != "paused" and lifecycle.lifecycle_state != "RUNNING":
                raise DaemonConflictError("node run is not paused")
            previous_state = state.lifecycle_state
            run_id = state.current_run_id
            if lifecycle.lifecycle_state != "RUNNING":
                _apply_transition(lifecycle, target_state="RUNNING", current_run_id=run_id)
            resulting_state = "active"
            current_state = lifecycle.lifecycle_state
        elif command == "node.cancel":
            if state is None or state.current_run_id is None:
                raise DaemonNotFoundError("node has no durable run to cancel")
            lifecycle = session.get(NodeLifecycleState, node_id)
            if lifecycle is None:
                raise DaemonNotFoundError("node lifecycle record not found")
            if state.lifecycle_state == "cancelled":
                raise DaemonConflictError("node run is already cancelled")
            previous_state = state.lifecycle_state
            run_id = state.current_run_id
            if lifecycle.lifecycle_state != "CANCELLED":
                _apply_transition(lifecycle, target_state="CANCELLED")
            resulting_state = "cancelled"
            current_state = lifecycle.lifecycle_state
        else:
            raise DaemonConflictError(f"unsupported command: {command}")

        event_id = uuid4()
        event = DaemonMutationEvent(
            id=event_id,
            node_id=node_id,
            command=command,
            previous_state=previous_state,
            resulting_state=resulting_state,
            run_id=run_id,
            payload_json={"authority": "daemon"},
        )
        session.add(event)

        if state is None:
            state = DaemonNodeState(
                node_id=node_id,
                current_run_id=run_id,
                lifecycle_state=resulting_state,
                authority="daemon",
                last_command=command,
                last_event_id=event_id,
            )
            session.add(state)
        else:
            state.current_run_id = run_id
            state.lifecycle_state = resulting_state
            state.authority = "daemon"
            state.last_command = command
            state.last_event_id = event_id

        session.flush()
        return AuthorityStateSnapshot(
            node_id=state.node_id,
            authority=state.authority,
            current_state=current_state,
            current_run_id=state.current_run_id,
            last_command=state.last_command,
            last_event_id=state.last_event_id,
            updated_at=state.updated_at,
            event_count=_event_count(session, node_id),
        )


def _canonical_state(state: str) -> str:
    return {
        "active": "RUNNING",
        "paused": "PAUSED_FOR_USER",
        "cancelled": "CANCELLED",
    }.get(state, state)
