from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.db.models import WorkflowEvent
from aicoding.db.session import query_session_scope


@dataclass(frozen=True, slots=True)
class WorkflowEventSnapshot:
    id: UUID
    logical_node_id: UUID
    node_version_id: UUID | None
    node_run_id: UUID | None
    event_scope: str
    event_type: str
    payload_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "logical_node_id": str(self.logical_node_id),
            "node_version_id": None if self.node_version_id is None else str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "event_scope": self.event_scope,
            "event_type": self.event_type,
            "payload_json": self.payload_json,
            "created_at": self.created_at,
        }


def record_workflow_event(
    session: Session,
    *,
    logical_node_id: UUID,
    node_version_id: UUID | None,
    node_run_id: UUID | None,
    event_scope: str,
    event_type: str,
    payload_json: dict[str, object] | None = None,
) -> WorkflowEvent:
    row = WorkflowEvent(
        id=uuid4(),
        logical_node_id=logical_node_id,
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        event_scope=event_scope,
        event_type=event_type,
        payload_json={} if payload_json is None else dict(payload_json),
    )
    session.add(row)
    session.flush()
    return row


def list_workflow_events_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> list[WorkflowEventSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(WorkflowEvent)
            .where(WorkflowEvent.logical_node_id == logical_node_id)
            .order_by(WorkflowEvent.created_at)
        ).scalars().all()
        return [_snapshot(item) for item in rows]


def _snapshot(row: WorkflowEvent) -> WorkflowEventSnapshot:
    return WorkflowEventSnapshot(
        id=row.id,
        logical_node_id=row.logical_node_id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        event_scope=row.event_scope,
        event_type=row.event_type,
        payload_json=dict(row.payload_json or {}),
        created_at=row.created_at.isoformat(),
    )
