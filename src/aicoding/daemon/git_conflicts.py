from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import LogicalNodeCurrentVersion, MergeConflict, MergeEvent, NodeVersion
from aicoding.db.session import query_session_scope, session_scope

RESOLUTION_STATUSES = {"unresolved", "resolved", "abandoned"}


@dataclass(frozen=True, slots=True)
class MergeEventSnapshot:
    id: UUID
    parent_node_version_id: UUID
    child_node_version_id: UUID
    child_final_commit_sha: str
    parent_commit_before: str
    parent_commit_after: str
    merge_order: int
    had_conflict: bool
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "child_node_version_id": str(self.child_node_version_id),
            "child_final_commit_sha": self.child_final_commit_sha,
            "parent_commit_before": self.parent_commit_before,
            "parent_commit_after": self.parent_commit_after,
            "merge_order": self.merge_order,
            "had_conflict": self.had_conflict,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class MergeConflictSnapshot:
    id: UUID
    merge_event_id: UUID
    parent_node_version_id: UUID
    child_node_version_id: UUID
    files_json: list[str]
    merge_base_sha: str | None
    resolution_summary: str | None
    resolution_status: str
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "merge_event_id": str(self.merge_event_id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "child_node_version_id": str(self.child_node_version_id),
            "files_json": self.files_json,
            "merge_base_sha": self.merge_base_sha,
            "resolution_summary": self.resolution_summary,
            "resolution_status": self.resolution_status,
            "created_at": self.created_at,
        }


def record_merge_conflict(
    session_factory: sessionmaker[Session],
    *,
    parent_node_version_id: UUID,
    child_node_version_id: UUID,
    child_final_commit_sha: str,
    parent_commit_before: str,
    parent_commit_after: str,
    merge_order: int,
    files_json: list[str],
    merge_base_sha: str | None = None,
) -> MergeConflictSnapshot:
    if not files_json:
        raise DaemonConflictError("merge conflict must include at least one conflicted file")
    with session_scope(session_factory) as session:
        event_snapshot = record_merge_event_in_session(
            session,
            parent_node_version_id=parent_node_version_id,
            child_node_version_id=child_node_version_id,
            child_final_commit_sha=child_final_commit_sha,
            parent_commit_before=parent_commit_before,
            parent_commit_after=parent_commit_after,
            merge_order=merge_order,
            had_conflict=True,
        )
        conflict = MergeConflict(
            id=uuid4(),
            merge_event_id=event_snapshot.id,
            files_json=files_json,
            merge_base_sha=merge_base_sha,
            resolution_summary=None,
            resolution_status="unresolved",
        )
        session.add(conflict)
        session.flush()
        return _merge_conflict_snapshot(session.get(MergeEvent, event_snapshot.id), conflict)


def record_merge_event(
    session_factory: sessionmaker[Session],
    *,
    parent_node_version_id: UUID,
    child_node_version_id: UUID,
    child_final_commit_sha: str,
    parent_commit_before: str,
    parent_commit_after: str,
    merge_order: int,
) -> MergeEventSnapshot:
    with session_scope(session_factory) as session:
        return record_merge_event_in_session(
            session,
            parent_node_version_id=parent_node_version_id,
            child_node_version_id=child_node_version_id,
            child_final_commit_sha=child_final_commit_sha,
            parent_commit_before=parent_commit_before,
            parent_commit_after=parent_commit_after,
            merge_order=merge_order,
            had_conflict=False,
        )


def list_merge_events_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> list[MergeEventSnapshot]:
    with query_session_scope(session_factory) as session:
        version_ids = _version_ids_for_logical_node(session, logical_node_id)
        rows = session.execute(
            select(MergeEvent)
            .where(MergeEvent.parent_node_version_id.in_(version_ids))
            .order_by(MergeEvent.created_at, MergeEvent.merge_order)
        ).scalars().all()
        return [_merge_event_snapshot(row) for row in rows]


def list_merge_conflicts_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> list[MergeConflictSnapshot]:
    with query_session_scope(session_factory) as session:
        version_ids = _version_ids_for_logical_node(session, logical_node_id)
        rows = session.execute(
            select(MergeEvent, MergeConflict)
            .join(MergeConflict, MergeConflict.merge_event_id == MergeEvent.id)
            .where(MergeEvent.parent_node_version_id.in_(version_ids))
            .order_by(MergeConflict.created_at, MergeEvent.merge_order)
        ).all()
        return [_merge_conflict_snapshot(event, conflict) for event, conflict in rows]


def list_merge_conflicts_for_version(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
) -> list[MergeConflictSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(MergeEvent, MergeConflict)
            .join(MergeConflict, MergeConflict.merge_event_id == MergeEvent.id)
            .where(MergeEvent.parent_node_version_id == node_version_id)
            .order_by(MergeConflict.created_at, MergeEvent.merge_order)
        ).all()
        return [_merge_conflict_snapshot(event, conflict) for event, conflict in rows]


def resolve_merge_conflict(
    session_factory: sessionmaker[Session],
    *,
    conflict_id: UUID,
    resolution_summary: str,
    resolution_status: str = "resolved",
) -> MergeConflictSnapshot:
    if resolution_status not in RESOLUTION_STATUSES - {"unresolved"}:
        raise DaemonConflictError(f"unsupported resolution status '{resolution_status}'")
    with session_scope(session_factory) as session:
        conflict = session.get(MergeConflict, conflict_id)
        if conflict is None:
            raise DaemonNotFoundError("merge conflict not found")
        event = session.get(MergeEvent, conflict.merge_event_id)
        if event is None:
            raise DaemonNotFoundError("merge event not found")
        conflict.resolution_summary = resolution_summary
        conflict.resolution_status = resolution_status
        session.flush()
        return _merge_conflict_snapshot(event, conflict)


def has_unresolved_merge_conflicts(session: Session, *, node_version_id: UUID) -> bool:
    return (
        session.execute(
            select(MergeConflict.id)
            .join(MergeEvent, MergeConflict.merge_event_id == MergeEvent.id)
            .where(
                MergeEvent.parent_node_version_id == node_version_id,
                MergeConflict.resolution_status == "unresolved",
            )
        ).first()
        is not None
    )


def _version_ids_for_logical_node(session: Session, logical_node_id: UUID) -> list[UUID]:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    rows = session.execute(select(NodeVersion.id).where(NodeVersion.logical_node_id == logical_node_id)).all()
    return [row[0] for row in rows]


def _require_node_version(session: Session, node_version_id: UUID) -> NodeVersion:
    version = session.get(NodeVersion, node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def record_merge_event_in_session(
    session: Session,
    *,
    parent_node_version_id: UUID,
    child_node_version_id: UUID,
    child_final_commit_sha: str,
    parent_commit_before: str,
    parent_commit_after: str,
    merge_order: int,
    had_conflict: bool,
) -> MergeEventSnapshot:
    _require_node_version(session, parent_node_version_id)
    _require_node_version(session, child_node_version_id)
    event = MergeEvent(
        id=uuid4(),
        parent_node_version_id=parent_node_version_id,
        child_node_version_id=child_node_version_id,
        child_final_commit_sha=child_final_commit_sha,
        parent_commit_before=parent_commit_before,
        parent_commit_after=parent_commit_after,
        merge_order=merge_order,
        had_conflict=had_conflict,
    )
    session.add(event)
    session.flush()
    return _merge_event_snapshot(event)


def _merge_event_snapshot(row: MergeEvent) -> MergeEventSnapshot:
    return MergeEventSnapshot(
        id=row.id,
        parent_node_version_id=row.parent_node_version_id,
        child_node_version_id=row.child_node_version_id,
        child_final_commit_sha=row.child_final_commit_sha,
        parent_commit_before=row.parent_commit_before,
        parent_commit_after=row.parent_commit_after,
        merge_order=row.merge_order,
        had_conflict=row.had_conflict,
        created_at=row.created_at.isoformat(),
    )


def _merge_conflict_snapshot(event: MergeEvent, conflict: MergeConflict) -> MergeConflictSnapshot:
    return MergeConflictSnapshot(
        id=conflict.id,
        merge_event_id=event.id,
        parent_node_version_id=event.parent_node_version_id,
        child_node_version_id=event.child_node_version_id,
        files_json=list(conflict.files_json),
        merge_base_sha=conflict.merge_base_sha,
        resolution_summary=conflict.resolution_summary,
        resolution_status=conflict.resolution_status,
        created_at=conflict.created_at.isoformat(),
    )
