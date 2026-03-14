from __future__ import annotations

from datetime import datetime, timezone
from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import has_unresolved_merge_conflicts
from aicoding.daemon.run_orchestration import cancel_active_run
from aicoding.daemon.session_records import ACTIVE_SESSION_STATUSES
from aicoding.db.models import (
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeLifecycleState,
    NodeVersion,
    RebuildEvent,
    Session as DurableSession,
    SessionEvent,
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
class RebuildCoordinationCancellationSnapshot:
    node_id: UUID
    scope: str
    cancelled_node_ids: list[UUID]
    cancelled_run_ids: list[UUID]
    invalidated_session_ids: list[UUID]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "scope": self.scope,
            "cancelled_node_ids": [str(item) for item in self.cancelled_node_ids],
            "cancelled_run_ids": [str(item) for item in self.cancelled_run_ids],
            "invalidated_session_ids": [str(item) for item in self.invalidated_session_ids],
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


@dataclass(frozen=True, slots=True)
class RequiredCutoverScopeSnapshot:
    candidate_root_version_id: UUID
    requested_node_version_id: UUID
    scope_kind: str
    required_candidate_version_ids: list[UUID]
    stopping_reason: str
    authoritative_baseline_version_ids: list[UUID]

    def to_payload(self) -> dict[str, object]:
        return {
            "candidate_root_version_id": str(self.candidate_root_version_id),
            "requested_node_version_id": str(self.requested_node_version_id),
            "scope_kind": self.scope_kind,
            "required_candidate_version_ids": [str(item) for item in self.required_candidate_version_ids],
            "stopping_reason": self.stopping_reason,
            "authoritative_baseline_version_ids": [str(item) for item in self.authoritative_baseline_version_ids],
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


def enumerate_required_cutover_scope(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
) -> RequiredCutoverScopeSnapshot:
    with query_session_scope(session_factory) as session:
        return _enumerate_required_cutover_scope(session, version_id=version_id)


def require_cutover_ready(session: Session, *, version_id: UUID) -> CutoverReadinessSnapshot:
    readiness = _build_cutover_readiness_snapshot(session, version_id=version_id)
    if readiness.status in {"ready", "ready_with_follow_on_replay"}:
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


def cancel_rebuild_coordination_blockers(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    scope: str,
    summary: str,
) -> RebuildCoordinationCancellationSnapshot:
    coordination = inspect_rebuild_coordination(session_factory, logical_node_id=logical_node_id, scope=scope)
    cancelled_node_ids: list[UUID] = []
    cancelled_run_ids: list[UUID] = []
    for blocker in coordination.blockers:
        if blocker.blocker_type != "active_or_paused_run":
            continue
        if blocker.node_id in cancelled_node_ids:
            continue
        cancel_active_run(session_factory, logical_node_id=blocker.node_id, summary=summary)
        cancelled_node_ids.append(blocker.node_id)
        if blocker.current_run_id is not None:
            cancelled_run_ids.append(blocker.current_run_id)

    invalidated_session_ids: list[UUID] = []
    if cancelled_run_ids:
        cancelled_at = datetime.now(timezone.utc)
        with session_scope(session_factory) as session:
            sessions = session.execute(
                select(DurableSession).where(
                    DurableSession.node_run_id.in_(tuple(cancelled_run_ids)),
                    DurableSession.status.in_(tuple(ACTIVE_SESSION_STATUSES)),
                )
            ).scalars().all()
            for record in sessions:
                if record.id in invalidated_session_ids:
                    continue
                record.status = "CANCELLED"
                record.ended_at = cancelled_at
                session.add(
                    SessionEvent(
                        id=uuid4(),
                        session_id=record.id,
                        event_type="cancelled_for_regeneration",
                        payload_json={
                            "reason": summary,
                            "node_id": str(logical_node_id),
                            "scope": scope,
                        },
                    )
                )
                invalidated_session_ids.append(record.id)
            session.flush()

    return RebuildCoordinationCancellationSnapshot(
        node_id=logical_node_id,
        scope=scope,
        cancelled_node_ids=cancelled_node_ids,
        cancelled_run_ids=cancelled_run_ids,
        invalidated_session_ids=invalidated_session_ids,
    )


def _build_cutover_readiness_snapshot(session: Session, *, version_id: UUID) -> CutoverReadinessSnapshot:
    version = session.get(NodeVersion, version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    selector = session.get(LogicalNodeCurrentVersion, version.logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    authoritative = session.get(NodeVersion, selector.authoritative_node_version_id)
    if authoritative is None:
        raise DaemonNotFoundError("authoritative version not found")
    scope = _enumerate_required_cutover_scope(session, version_id=version_id)
    blockers: list[CutoverBlockerSnapshot] = []
    stable_rebuild_event_present = True
    unresolved_merge_conflicts = False
    for scoped_version_id in scope.required_candidate_version_ids:
        scoped_version = session.get(NodeVersion, scoped_version_id)
        if scoped_version is None:
            raise DaemonNotFoundError("node version not found")
        scoped_selector = session.get(LogicalNodeCurrentVersion, scoped_version.logical_node_id)
        if scoped_selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        scoped_blockers, scoped_stable, scoped_conflicts = _collect_cutover_blockers_for_candidate(
            session,
            requested_version_id=version_id,
            scoped_version=scoped_version,
            scoped_selector=scoped_selector,
        )
        blockers.extend(scoped_blockers)
        stable_rebuild_event_present = stable_rebuild_event_present and scoped_stable
        unresolved_merge_conflicts = unresolved_merge_conflicts or scoped_conflicts
    return CutoverReadinessSnapshot(
        logical_node_id=version.logical_node_id,
        node_version_id=version.id,
        current_authoritative_node_version_id=authoritative.id,
        status=_cutover_readiness_status(version_id=version.id, blockers=blockers),
        blockers=blockers,
        stable_rebuild_event_present=stable_rebuild_event_present,
        unresolved_merge_conflicts=unresolved_merge_conflicts,
    )


def _cutover_readiness_status(*, version_id: UUID, blockers: list[CutoverBlockerSnapshot]) -> str:
    if not blockers:
        return "ready"
    hard_blockers = [
        blocker
        for blocker in blockers
        if not _is_allowed_follow_on_replay_blocker(version_id=version_id, blocker=blocker, blockers=blockers)
    ]
    if not hard_blockers:
        return "ready_with_follow_on_replay"
    return "blocked"


def _is_allowed_follow_on_replay_blocker(
    *,
    version_id: UUID,
    blocker: CutoverBlockerSnapshot,
    blockers: list[CutoverBlockerSnapshot],
) -> bool:
    details = blocker.details_json or {}
    scope_member = details.get("scope_member_node_version_id")
    if blocker.blocker_type == "rebuild_not_stable" and scope_member == str(version_id):
        return any(
            _is_allowed_follow_on_replay_blocker(
                version_id=version_id,
                blocker=other,
                blockers=[],
            )
            for other in blockers
            if (other.details_json or {}).get("scope_member_node_version_id") != str(version_id)
        )
    if not isinstance(scope_member, str) or scope_member == str(version_id):
        return False
    if blocker.blocker_type == "candidate_replay_incomplete":
        return (
            details.get("replay_classification") == "blocked_pending_parent_refresh"
            and (
                bool(details.get("fresh_dependency_restart"))
                or details.get("candidate_role") == "dependency_invalidated_fresh_restart"
            )
        )
    if blocker.blocker_type != "rebuild_not_stable":
        return False
    return any(
        candidate_blocker.blocker_type == "candidate_replay_incomplete"
        and (candidate_blocker.details_json or {}).get("scope_member_node_version_id") == scope_member
        and _is_allowed_follow_on_replay_blocker(
            version_id=version_id,
            blocker=candidate_blocker,
            blockers=[],
        )
        for candidate_blocker in blockers
    )


def _collect_cutover_blockers_for_candidate(
    session: Session,
    *,
    requested_version_id: UUID,
    scoped_version: NodeVersion,
    scoped_selector: LogicalNodeCurrentVersion,
) -> tuple[list[CutoverBlockerSnapshot], bool, bool]:
    stable_rebuild_event_present = _stable_rebuild_event_present(session, version_id=scoped_version.id)
    unresolved_merge_conflicts = has_unresolved_merge_conflicts(session, node_version_id=scoped_version.id)
    blockers: list[CutoverBlockerSnapshot] = []
    if scoped_version.status != "candidate":
        blockers.append(
            _annotate_scope_blocker(
                CutoverBlockerSnapshot(
                    "not_candidate",
                    {
                        "node_version_id": str(scoped_version.id),
                        "version_status": scoped_version.status,
                    },
                ),
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )
    if (
        scoped_version.supersedes_node_version_id is not None
        and scoped_version.supersedes_node_version_id != scoped_selector.authoritative_node_version_id
    ):
        blockers.append(
            _annotate_scope_blocker(
                CutoverBlockerSnapshot(
                    "authoritative_lineage_changed_since_rebuild_started",
                    {
                        "candidate_node_version_id": str(scoped_version.id),
                        "candidate_baseline_node_version_id": str(scoped_version.supersedes_node_version_id),
                        "current_authoritative_node_version_id": str(scoped_selector.authoritative_node_version_id),
                    },
                ),
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )
    if unresolved_merge_conflicts:
        blockers.append(
            _annotate_scope_blocker(
                CutoverBlockerSnapshot(
                    "unresolved_merge_conflicts",
                    {"node_version_id": str(scoped_version.id)},
                ),
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )
    replay_block = _candidate_replay_blocker(session, version_id=scoped_version.id)
    if replay_block is not None:
        blockers.append(
            _annotate_scope_blocker(
                replay_block,
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )
    if not stable_rebuild_event_present and _has_rebuild_events(session, version_id=scoped_version.id):
        blockers.append(
            _annotate_scope_blocker(
                CutoverBlockerSnapshot(
                    "rebuild_not_stable",
                    {"node_version_id": str(scoped_version.id)},
                ),
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )

    authoritative = session.get(NodeVersion, scoped_selector.authoritative_node_version_id)
    if authoritative is None:
        raise DaemonNotFoundError("authoritative version not found")
    lifecycle = session.get(NodeLifecycleState, str(scoped_version.logical_node_id))
    if lifecycle is not None and lifecycle.current_run_id is not None and lifecycle.run_status in {"RUNNING", "PAUSED"}:
        blockers.append(
            _annotate_scope_blocker(
                CutoverBlockerSnapshot(
                    "authoritative_active_run",
                    {
                        "current_run_id": str(lifecycle.current_run_id),
                        "run_status": lifecycle.run_status,
                        "lifecycle_state": lifecycle.lifecycle_state,
                        "authoritative_node_version_id": str(authoritative.id),
                    },
                ),
                requested_version_id=requested_version_id,
                scoped_version_id=scoped_version.id,
            )
        )
        active_primary_sessions = _active_primary_sessions(session, lifecycle.current_run_id)
        if active_primary_sessions:
            blockers.append(
                _annotate_scope_blocker(
                    CutoverBlockerSnapshot(
                        "authoritative_active_primary_sessions",
                        {
                            "current_run_id": str(lifecycle.current_run_id),
                            "session_ids": [str(item.id) for item in active_primary_sessions],
                            "session_count": len(active_primary_sessions),
                            "authoritative_node_version_id": str(authoritative.id),
                        },
                    ),
                    requested_version_id=requested_version_id,
                    scoped_version_id=scoped_version.id,
                )
            )
    return blockers, stable_rebuild_event_present, unresolved_merge_conflicts


def _annotate_scope_blocker(
    blocker: CutoverBlockerSnapshot,
    *,
    requested_version_id: UUID,
    scoped_version_id: UUID,
) -> CutoverBlockerSnapshot:
    details_json = dict(blocker.details_json)
    details_json.setdefault("requested_node_version_id", str(requested_version_id))
    details_json.setdefault("scope_member_node_version_id", str(scoped_version_id))
    return CutoverBlockerSnapshot(blocker.blocker_type, details_json)


def _enumerate_required_cutover_scope(session: Session, *, version_id: UUID) -> RequiredCutoverScopeSnapshot:
    version = session.get(NodeVersion, version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")

    latest_event = session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == version_id,
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().first()
    if latest_event is None:
        return RequiredCutoverScopeSnapshot(
            candidate_root_version_id=version.id,
            requested_node_version_id=version.id,
            scope_kind="local",
            required_candidate_version_ids=[version.id],
            stopping_reason="no_rebuild_scope",
            authoritative_baseline_version_ids=[],
        )

    scope_events = session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.root_node_version_id == latest_event.root_node_version_id,
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at, RebuildEvent.id)
    ).scalars().all()

    candidate_version_ids: set[UUID] = set()
    authoritative_baselines: set[UUID] = set()
    scope_kind = "subtree"
    for event in scope_events:
        if event.scope == "upstream":
            scope_kind = "upstream"
        if event.event_kind == "candidate_created":
            candidate_version_ids.add(event.target_node_version_id)
            baseline = (event.details_json or {}).get("authoritative_baseline_version_id")
            if isinstance(baseline, str):
                authoritative_baselines.add(UUID(baseline))

    if not candidate_version_ids:
        candidate_version_ids.add(latest_event.target_node_version_id)

    versions = [session.get(NodeVersion, candidate_version_id) for candidate_version_id in candidate_version_ids]
    resolved_versions = [item for item in versions if item is not None]
    # Candidate replay and grouped cutover should enumerate descendants before
    # rebuilt ancestors so replay-safe ordering stays deterministic.
    ordered_candidate_ids = [
        item.id
        for item in sorted(
            resolved_versions,
            key=lambda candidate: (-_depth(session, candidate.logical_node_id), candidate.created_at, str(candidate.id)),
        )
    ]
    stopping_reason = "no_parent" if scope_kind == "subtree" else "root_reached"
    return RequiredCutoverScopeSnapshot(
        candidate_root_version_id=latest_event.root_node_version_id,
        requested_node_version_id=version.id,
        scope_kind=scope_kind,
        required_candidate_version_ids=ordered_candidate_ids,
        stopping_reason=stopping_reason,
        authoritative_baseline_version_ids=sorted(authoritative_baselines, key=str),
    )


def _cutover_conflict_message(readiness: CutoverReadinessSnapshot) -> str:
    blocker_types = [item.blocker_type for item in readiness.blockers]
    if "authoritative_lineage_changed_since_rebuild_started" in blocker_types:
        return "candidate version was built from a stale authoritative baseline; rebuild or revalidate it before cutover"
    if "unresolved_merge_conflicts" in blocker_types:
        return "candidate version has unresolved merge conflicts"
    if "candidate_replay_incomplete" in blocker_types:
        return "candidate version replay or rematerialization is incomplete"
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
        if (
            lifecycle is not None
            and lifecycle.current_run_id is not None
            and lifecycle.run_status in {"PENDING", "RUNNING", "PAUSED"}
        ):
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
        if active_primary_sessions:
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


def _candidate_replay_blocker(session: Session, *, version_id: UUID) -> CutoverBlockerSnapshot | None:
    latest = session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == version_id,
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().first()
    if latest is None:
        return None
    details_json = dict(latest.details_json or {})
    replay_classification = details_json.get("replay_classification")
    event_kind = latest.event_kind
    if replay_classification == "blocked_pending_parent_refresh" or event_kind == "replay_blocked":
        return CutoverBlockerSnapshot(
            "candidate_replay_incomplete",
            {
                "node_version_id": str(version_id),
                "event_kind": event_kind,
                "event_status": latest.event_status,
                **details_json,
            },
        )
    return None


def _has_rebuild_events(session: Session, *, version_id: UUID) -> bool:
    return session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == version_id,
            RebuildEvent.scope.in_(("subtree", "upstream")),
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().first() is not None


def _depth(session: Session, logical_node_id: UUID) -> int:
    depth = 0
    node = session.get(HierarchyNode, logical_node_id)
    while node is not None and node.parent_node_id is not None:
        depth += 1
        node = session.get(HierarchyNode, node.parent_node_id)
    return depth
