from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import has_unresolved_merge_conflicts
from aicoding.daemon.session_records import ACTIVE_SESSION_STATUSES
from aicoding.db.models import (
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeLifecycleState,
    NodeVersion,
    RebuildEvent,
    Session as DurableSession,
)
from aicoding.db.session import query_session_scope, session_scope


@dataclass(frozen=True, slots=True)
class RebuildCoordinationBlockerSnapshot:
    blocker_type: str
    node_id: UUID
    node_version_id: UUID
    node_kind: str
    node_title: str
    scope_role: str
    lifecycle_state: str | None
    run_status: str | None
    current_run_id: UUID | None
    active_primary_session_count: int
    active_primary_session_ids: list[UUID]

    def to_payload(self) -> dict[str, object]:
        return {
            "blocker_type": self.blocker_type,
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_kind": self.node_kind,
            "node_title": self.node_title,
            "scope_role": self.scope_role,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "current_run_id": None if self.current_run_id is None else str(self.current_run_id),
            "active_primary_session_count": self.active_primary_session_count,
            "active_primary_session_ids": [str(item) for item in self.active_primary_session_ids],
        }


@dataclass(frozen=True, slots=True)
class RebuildCoordinationSnapshot:
    node_id: UUID
    scope: str
    status: str
    blockers: list[RebuildCoordinationBlockerSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "scope": self.scope,
            "status": self.status,
            "blockers": [item.to_payload() for item in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class CutoverBlockerSnapshot:
    blocker_type: str
    details_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "blocker_type": self.blocker_type,
            "details_json": self.details_json,
        }


@dataclass(frozen=True, slots=True)
class CutoverReadinessSnapshot:
    logical_node_id: UUID
    node_version_id: UUID
    current_authoritative_node_version_id: UUID
    status: str
    blockers: list[CutoverBlockerSnapshot]
    stable_rebuild_event_present: bool
    unresolved_merge_conflicts: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "logical_node_id": str(self.logical_node_id),
            "node_version_id": str(self.node_version_id),
            "current_authoritative_node_version_id": str(self.current_authoritative_node_version_id),
            "status": self.status,
            "blockers": [item.to_payload() for item in self.blockers],
            "stable_rebuild_event_present": self.stable_rebuild_event_present,
            "unresolved_merge_conflicts": self.unresolved_merge_conflicts,
        }


def inspect_rebuild_coordination(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    scope: str,
) -> RebuildCoordinationSnapshot:
    if scope not in {"subtree", "upstream"}:
        raise DaemonConflictError("rebuild coordination scope must be subtree or upstream")
    with query_session_scope(session_factory) as session:
        blockers = _collect_rebuild_coordination_blockers(session, logical_node_id=logical_node_id, scope=scope)
        return RebuildCoordinationSnapshot(
            node_id=logical_node_id,
            scope=scope,
            status="clear" if not blockers else "blocked",
            blockers=blockers,
        )


def inspect_cutover_readiness(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
) -> CutoverReadinessSnapshot:
    with query_session_scope(session_factory) as session:
        return _build_cutover_readiness_snapshot(session, version_id=version_id)


def require_cutover_ready(session: Session, *, version_id: UUID) -> CutoverReadinessSnapshot:
    readiness = _build_cutover_readiness_snapshot(session, version_id=version_id)
    if readiness.status == "ready":
        return readiness
    raise DaemonConflictError(_cutover_conflict_message(readiness))


def record_rebuild_coordination_event(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    target_node_version_id: UUID,
    event_kind: str,
    event_status: str,
    scope: str,
    trigger_reason: str,
    details_json: dict[str, object],
) -> None:
    with session_scope(session_factory) as session:
        session.add(
            RebuildEvent(
                id=uuid4(),
                root_logical_node_id=logical_node_id,
                root_node_version_id=target_node_version_id,
                target_node_version_id=target_node_version_id,
                event_kind=event_kind,
                event_status=event_status,
                scope=scope,
                trigger_reason=trigger_reason,
                details_json=details_json,
            )
        )
        session.flush()


def _build_cutover_readiness_snapshot(session: Session, *, version_id: UUID) -> CutoverReadinessSnapshot:
    version = session.get(NodeVersion, version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    selector = session.get(LogicalNodeCurrentVersion, version.logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")

    stable_rebuild_event_present = _stable_rebuild_event_present(session, version_id=version.id)
    unresolved_merge_conflicts = has_unresolved_merge_conflicts(session, node_version_id=version.id)
    blockers: list[CutoverBlockerSnapshot] = []
    if version.status != "candidate":
        blockers.append(CutoverBlockerSnapshot("not_candidate", {"version_status": version.status}))
    if unresolved_merge_conflicts:
        blockers.append(
            CutoverBlockerSnapshot(
                "unresolved_merge_conflicts",
                {"node_version_id": str(version.id)},
            )
        )
    if not stable_rebuild_event_present and _has_rebuild_events(session, version_id=version.id):
        blockers.append(
            CutoverBlockerSnapshot(
                "rebuild_not_stable",
                {"node_version_id": str(version.id)},
            )
        )

    authoritative = session.get(NodeVersion, selector.authoritative_node_version_id)
    if authoritative is None:
        raise DaemonNotFoundError("authoritative version not found")
    lifecycle = session.get(NodeLifecycleState, str(version.logical_node_id))
    if lifecycle is not None and lifecycle.current_run_id is not None and lifecycle.run_status in {"RUNNING", "PAUSED"}:
        blockers.append(
            CutoverBlockerSnapshot(
                "authoritative_active_run",
                {
                    "current_run_id": str(lifecycle.current_run_id),
                    "run_status": lifecycle.run_status,
                    "lifecycle_state": lifecycle.lifecycle_state,
                    "authoritative_node_version_id": str(authoritative.id),
                },
            )
        )
        active_primary_sessions = _active_primary_sessions(session, lifecycle.current_run_id)
        if active_primary_sessions:
            blockers.append(
                CutoverBlockerSnapshot(
                    "authoritative_active_primary_sessions",
                    {
                        "current_run_id": str(lifecycle.current_run_id),
                        "session_ids": [str(item.id) for item in active_primary_sessions],
                        "session_count": len(active_primary_sessions),
                        "authoritative_node_version_id": str(authoritative.id),
                    },
                )
            )
    return CutoverReadinessSnapshot(
        logical_node_id=version.logical_node_id,
        node_version_id=version.id,
        current_authoritative_node_version_id=authoritative.id,
        status="ready" if not blockers else "blocked",
        blockers=blockers,
        stable_rebuild_event_present=stable_rebuild_event_present,
        unresolved_merge_conflicts=unresolved_merge_conflicts,
    )


def _cutover_conflict_message(readiness: CutoverReadinessSnapshot) -> str:
    blocker_types = [item.blocker_type for item in readiness.blockers]
    if "unresolved_merge_conflicts" in blocker_types:
        return "candidate version has unresolved merge conflicts"
    if "rebuild_not_stable" in blocker_types:
        return "candidate version rebuild lineage is not yet marked stable for cutover"
    if "authoritative_active_primary_sessions" in blocker_types:
        return "authoritative version still has active primary sessions; resolve them before cutover"
    if "authoritative_active_run" in blocker_types:
        return "authoritative version still has an active or paused run; resolve it before cutover"
    if "not_candidate" in blocker_types:
        return "only candidate versions may cut over"
    return "candidate version is not ready for cutover"


def _collect_rebuild_coordination_blockers(
    session: Session,
    *,
    logical_node_id: UUID,
    scope: str,
) -> list[RebuildCoordinationBlockerSnapshot]:
    target_nodes = _coordination_scope_nodes(session, logical_node_id=logical_node_id, scope=scope)
    blockers: list[RebuildCoordinationBlockerSnapshot] = []
    for node, scope_role in target_nodes:
        selector = session.get(LogicalNodeCurrentVersion, node.node_id)
        if selector is None:
            continue
        authoritative = session.get(NodeVersion, selector.authoritative_node_version_id)
        if authoritative is None:
            continue
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        active_primary_sessions: list[DurableSession] = []
        if lifecycle is not None and lifecycle.current_run_id is not None:
            active_primary_sessions = _active_primary_sessions(session, lifecycle.current_run_id)
        if lifecycle is not None and lifecycle.current_run_id is not None and lifecycle.run_status in {"RUNNING", "PAUSED"}:
            blockers.append(
                RebuildCoordinationBlockerSnapshot(
                    blocker_type="active_or_paused_run",
                    node_id=node.node_id,
                    node_version_id=authoritative.id,
                    node_kind=node.kind,
                    node_title=node.title,
                    scope_role=scope_role,
                    lifecycle_state=lifecycle.lifecycle_state,
                    run_status=lifecycle.run_status,
                    current_run_id=lifecycle.current_run_id,
                    active_primary_session_count=len(active_primary_sessions),
                    active_primary_session_ids=[item.id for item in active_primary_sessions],
                )
            )
        elif active_primary_sessions:
            blockers.append(
                RebuildCoordinationBlockerSnapshot(
                    blocker_type="active_primary_sessions",
                    node_id=node.node_id,
                    node_version_id=authoritative.id,
                    node_kind=node.kind,
                    node_title=node.title,
                    scope_role=scope_role,
                    lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
                    run_status=None if lifecycle is None else lifecycle.run_status,
                    current_run_id=None if lifecycle is None else lifecycle.current_run_id,
                    active_primary_session_count=len(active_primary_sessions),
                    active_primary_session_ids=[item.id for item in active_primary_sessions],
                )
            )
    return blockers


def _coordination_scope_nodes(session: Session, *, logical_node_id: UUID, scope: str) -> list[tuple[HierarchyNode, str]]:
    root_node = session.get(HierarchyNode, logical_node_id)
    if root_node is None:
        raise DaemonNotFoundError("node not found")
    nodes: list[tuple[HierarchyNode, str]] = [(root_node, "target")]
    visited = {root_node.node_id}
    descendant_ids = _descendant_node_ids(session, root_node.node_id)
    for descendant_id in descendant_ids:
        if descendant_id in visited:
            continue
        descendant = session.get(HierarchyNode, descendant_id)
        if descendant is None:
            continue
        visited.add(descendant.node_id)
        nodes.append((descendant, "descendant"))
    if scope == "upstream":
        cursor = root_node
        while cursor.parent_node_id is not None:
            parent = session.get(HierarchyNode, cursor.parent_node_id)
            if parent is None:
                break
            if parent.node_id not in visited:
                visited.add(parent.node_id)
                nodes.append((parent, "ancestor"))
            cursor = parent
    return nodes


def _descendant_node_ids(session: Session, logical_node_id: UUID) -> list[UUID]:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        return []
    ordered: list[UUID] = []

    def visit(version_id: UUID) -> None:
        edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == version_id).order_by(NodeChild.ordinal, NodeChild.created_at)
        ).scalars().all()
        for edge in edges:
            child_version = session.get(NodeVersion, edge.child_node_version_id)
            if child_version is None:
                continue
            ordered.append(child_version.logical_node_id)
            child_selector = session.get(LogicalNodeCurrentVersion, child_version.logical_node_id)
            if child_selector is None:
                continue
            visit(child_selector.authoritative_node_version_id)

    visit(selector.authoritative_node_version_id)
    return ordered


def _active_primary_sessions(session: Session, node_run_id: UUID) -> list[DurableSession]:
    return session.execute(
        select(DurableSession).where(
            DurableSession.node_run_id == node_run_id,
            DurableSession.session_role == "primary",
            DurableSession.status.in_(ACTIVE_SESSION_STATUSES),
        )
    ).scalars().all()


def _stable_rebuild_event_present(session: Session, *, version_id: UUID) -> bool:
    return session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == version_id,
            RebuildEvent.event_status == "stable",
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().first() is not None


def _has_rebuild_events(session: Session, *, version_id: UUID) -> bool:
    return session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == version_id,
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().first() is not None
