from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.orchestration import apply_authority_mutation, load_authority_state
from aicoding.daemon.run_orchestration import ensure_node_run_started
from aicoding.db.models import (
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeDependency,
    NodeDependencyBlocker,
    NodeLifecycleState,
    NodeVersion,
)
from aicoding.db.session import query_session_scope, session_scope


DEPENDENCY_REQUIRED_STATES = {"COMPLETE"}
INVALID_BLOCKER_KINDS = {"invalid_structure", "invalid_target", "invalid_cycle", "invalid_authority"}
IMPOSSIBLE_WAIT_STATES = {"FAILED_TO_PARENT", "SUPERSEDED", "CANCELLED", "COMPILE_FAILED"}


@dataclass(frozen=True, slots=True)
class NodeDependencySnapshot:
    id: UUID
    node_version_id: UUID
    depends_on_node_version_id: UUID
    dependency_type: str
    required_state: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "depends_on_node_version_id": str(self.depends_on_node_version_id),
            "dependency_type": self.dependency_type,
            "required_state": self.required_state,
        }


@dataclass(frozen=True, slots=True)
class DependencyBlockerSnapshot:
    blocker_kind: str
    dependency_id: UUID | None
    node_version_id: UUID
    target_node_version_id: UUID | None
    details_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "blocker_kind": self.blocker_kind,
            "dependency_id": None if self.dependency_id is None else str(self.dependency_id),
            "node_version_id": str(self.node_version_id),
            "target_node_version_id": None if self.target_node_version_id is None else str(self.target_node_version_id),
            "details_json": self.details_json,
        }


@dataclass(frozen=True, slots=True)
class DependencyGraphValidationSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    dependencies: list[NodeDependencySnapshot]
    blockers: list[DependencyBlockerSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "dependencies": [item.to_payload() for item in self.dependencies],
            "blockers": [item.to_payload() for item in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class DependencyReadinessSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    blockers: list[DependencyBlockerSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "blockers": [item.to_payload() for item in self.blockers],
        }


@dataclass(frozen=True, slots=True)
class NodeRunAdmissionSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    reason: str | None
    current_state: str | None
    current_run_id: UUID | None
    blockers: list[DependencyBlockerSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "reason": self.reason,
            "current_state": self.current_state,
            "current_run_id": None if self.current_run_id is None else str(self.current_run_id),
            "blockers": [item.to_payload() for item in self.blockers],
        }


def add_node_dependency(
    session_factory: sessionmaker[Session],
    *,
    node_id: UUID,
    depends_on_node_id: UUID,
    required_state: str = "COMPLETE",
) -> NodeDependencySnapshot:
    if required_state not in DEPENDENCY_REQUIRED_STATES:
        raise DaemonConflictError(f"unsupported dependency required state '{required_state}'")
    with session_scope(session_factory) as session:
        node_version = _authoritative_version(session, node_id)
        target_version = _authoritative_version(session, depends_on_node_id)
        dependency_type = _classify_dependency_type(session, node_id=node_id, depends_on_node_id=depends_on_node_id)
        if session.execute(
            select(NodeDependency).where(
                NodeDependency.node_version_id == node_version.id,
                NodeDependency.depends_on_node_version_id == target_version.id,
            )
        ).scalar_one_or_none():
            raise DaemonConflictError("dependency already exists")
        row = NodeDependency(
            id=uuid4(),
            node_version_id=node_version.id,
            depends_on_node_version_id=target_version.id,
            dependency_type=dependency_type,
            required_state=required_state,
        )
        session.add(row)
        session.flush()
        validation = _validate_dependency_graph(session, node_id=node_id, persist=True)
        if validation.status != "valid":
            raise DaemonConflictError("dependency graph became invalid after adding the edge")
        return _dependency_snapshot(row)


def list_node_dependencies(session_factory: sessionmaker[Session], *, node_id: UUID) -> list[NodeDependencySnapshot]:
    with query_session_scope(session_factory) as session:
        node_version = _authoritative_version(session, node_id)
        rows = session.execute(
            select(NodeDependency)
            .where(NodeDependency.node_version_id == node_version.id)
            .order_by(NodeDependency.created_at, NodeDependency.id)
        ).scalars().all()
        return [_dependency_snapshot(row) for row in rows]


def validate_node_dependency_graph(
    session_factory: sessionmaker[Session],
    *,
    node_id: UUID,
) -> DependencyGraphValidationSnapshot:
    with session_scope(session_factory) as session:
        return _validate_dependency_graph(session, node_id=node_id, persist=True)


def check_node_dependency_readiness(
    session_factory: sessionmaker[Session],
    *,
    node_id: UUID,
) -> DependencyReadinessSnapshot:
    with session_scope(session_factory) as session:
        node_version = _authoritative_version(session, node_id)
        lifecycle = session.get(NodeLifecycleState, str(node_id))
        validation = _validate_dependency_graph(session, node_id=node_id, persist=False)
        if validation.status != "valid":
            blockers = _persist_blockers(
                session,
                node_version_id=node_version.id,
                blockers=validation.blockers,
            )
            status = "invalid"
            if any(item.blocker_kind == "invalid_cycle" for item in blockers):
                status = "invalid"
            return DependencyReadinessSnapshot(
                node_id=node_id,
                node_version_id=node_version.id,
                status=status,
                blockers=blockers,
            )

        dependencies = _dependencies_for_version(session, node_version.id)
        blockers: list[DependencyBlockerSnapshot] = []
        for dependency in dependencies:
            target = _resolve_authoritative_target(session, dependency)
            if target is None:
                blockers.append(
                    DependencyBlockerSnapshot(
                        blocker_kind="invalid_authority",
                        dependency_id=dependency.id,
                        node_version_id=node_version.id,
                        target_node_version_id=dependency.depends_on_node_version_id,
                        details_json={"dependency_id": str(dependency.id)},
                    )
                )
                continue
            target_lifecycle = session.get(NodeLifecycleState, str(target.logical_node_id))
            current_state = None if target_lifecycle is None else target_lifecycle.lifecycle_state
            if current_state in IMPOSSIBLE_WAIT_STATES:
                blockers.append(
                    DependencyBlockerSnapshot(
                        blocker_kind="impossible_wait",
                        dependency_id=dependency.id,
                        node_version_id=node_version.id,
                        target_node_version_id=target.id,
                        details_json={
                            "required_state": dependency.required_state,
                            "target_state": current_state,
                        },
                    )
                )
                continue
            if current_state != dependency.required_state:
                blockers.append(
                    DependencyBlockerSnapshot(
                        blocker_kind="blocked_on_dependency",
                        dependency_id=dependency.id,
                        node_version_id=node_version.id,
                        target_node_version_id=target.id,
                        details_json={
                            "required_state": dependency.required_state,
                            "target_state": current_state,
                        },
                    )
                )
        blockers = _runtime_blockers(node_version=node_version, lifecycle=lifecycle, blockers=blockers)
        blockers = _persist_blockers(session, node_version_id=node_version.id, blockers=blockers)
        if any(item.blocker_kind == "impossible_wait" for item in blockers):
            status = "impossible_wait"
        elif blockers:
            status = "blocked"
        else:
            status = "ready"
        return DependencyReadinessSnapshot(
            node_id=node_id,
            node_version_id=node_version.id,
            status=status,
            blockers=blockers,
        )


def list_node_blockers(session_factory: sessionmaker[Session], *, node_id: UUID) -> list[DependencyBlockerSnapshot]:
    return check_node_dependency_readiness(session_factory, node_id=node_id).blockers


def admit_node_run(
    session_factory: sessionmaker[Session],
    *,
    node_id: UUID,
    trigger_reason: str = "manual_start",
) -> NodeRunAdmissionSnapshot:
    readiness = check_node_dependency_readiness(session_factory, node_id=node_id)
    with query_session_scope(session_factory) as session:
        node_version = _authoritative_version(session, node_id)
        lifecycle = session.get(NodeLifecycleState, str(node_id))
        try:
            authority = load_authority_state(session_factory, str(node_id))
        except DaemonNotFoundError:
            authority = None
        if authority is not None:
            return NodeRunAdmissionSnapshot(
                node_id=node_id,
                node_version_id=node_version.id,
                status="blocked",
                reason="active_run_conflict",
                current_state=authority.current_state,
                current_run_id=authority.current_run_id,
                blockers=[
                    DependencyBlockerSnapshot(
                        blocker_kind="already_running",
                        dependency_id=None,
                        node_version_id=node_version.id,
                        target_node_version_id=None,
                        details_json={
                            "current_run_id": None if authority.current_run_id is None else str(authority.current_run_id),
                            "current_state": authority.current_state,
                        },
                    )
                ],
            )
    if readiness.status != "ready":
        return NodeRunAdmissionSnapshot(
            node_id=node_id,
            node_version_id=readiness.node_version_id,
            status="blocked",
            reason=readiness.status,
            current_state="READY",
            current_run_id=None,
            blockers=readiness.blockers,
        )
    authority = apply_authority_mutation(session_factory, node_id=str(node_id), command="node.run.start")
    ensure_node_run_started(
        session_factory,
        logical_node_id=node_id,
        run_id=authority.current_run_id,
        trigger_reason=trigger_reason,
    )
    return NodeRunAdmissionSnapshot(
        node_id=node_id,
        node_version_id=readiness.node_version_id,
        status="admitted",
        reason=None,
        current_state=authority.current_state,
        current_run_id=authority.current_run_id,
        blockers=[],
    )


def _validate_dependency_graph(session: Session, *, node_id: UUID, persist: bool) -> DependencyGraphValidationSnapshot:
    node_version = _authoritative_version(session, node_id)
    dependencies = _dependencies_for_version(session, node_version.id)
    blockers: list[DependencyBlockerSnapshot] = []
    seen_pairs: set[tuple[UUID, UUID]] = set()
    for dependency in dependencies:
        pair = (dependency.node_version_id, dependency.depends_on_node_version_id)
        if pair in seen_pairs:
            blockers.append(
                DependencyBlockerSnapshot(
                    blocker_kind="invalid_target",
                    dependency_id=dependency.id,
                    node_version_id=node_version.id,
                    target_node_version_id=dependency.depends_on_node_version_id,
                    details_json={"reason": "duplicate_edge"},
                )
            )
        seen_pairs.add(pair)
        try:
            _validate_dependency_row(session, node_id=node_id, dependency=dependency)
        except (DaemonConflictError, DaemonNotFoundError) as exc:
            blockers.append(
                DependencyBlockerSnapshot(
                    blocker_kind="invalid_structure",
                    dependency_id=dependency.id,
                    node_version_id=node_version.id,
                    target_node_version_id=dependency.depends_on_node_version_id,
                    details_json={"message": str(exc)},
                )
            )

    if not blockers and _has_cycle(session, node_version.id):
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="invalid_cycle",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={"message": "dependency cycle detected"},
            )
        )

    if persist:
        blockers = _persist_blockers(session, node_version_id=node_version.id, blockers=blockers)
    status = "valid" if not blockers else blockers[0].blocker_kind
    return DependencyGraphValidationSnapshot(
        node_id=node_id,
        node_version_id=node_version.id,
        status=status,
        dependencies=[_dependency_snapshot(row) for row in dependencies],
        blockers=blockers,
    )


def _validate_dependency_row(session: Session, *, node_id: UUID, dependency: NodeDependency) -> None:
    target = _resolve_authoritative_target(session, dependency)
    if target is None:
        raise DaemonConflictError("dependency target has no authoritative version")
    expected_type = _classify_dependency_type(session, node_id=node_id, depends_on_node_id=target.logical_node_id)
    if expected_type != dependency.dependency_type:
        raise DaemonConflictError("dependency type no longer matches current hierarchy relationship")


def _classify_dependency_type(session: Session, *, node_id: UUID, depends_on_node_id: UUID) -> str:
    if node_id == depends_on_node_id:
        raise DaemonConflictError("node may not depend on itself")
    node = session.get(HierarchyNode, node_id)
    target = session.get(HierarchyNode, depends_on_node_id)
    if node is None or target is None:
        raise DaemonNotFoundError("dependency node not found")
    if node.parent_node_id == target.node_id:
        raise DaemonConflictError("parent dependencies are not allowed")
    if target.parent_node_id == node.node_id:
        return "child"
    if node.parent_node_id == target.parent_node_id:
        return "sibling"
    raise DaemonConflictError("dependency target must be a sibling or child")


def _has_cycle(session: Session, start_node_version_id: UUID) -> bool:
    graph: dict[UUID, list[UUID]] = {}
    rows = session.execute(select(NodeDependency)).scalars().all()
    for row in rows:
        graph.setdefault(row.node_version_id, []).append(row.depends_on_node_version_id)

    visiting: set[UUID] = set()
    visited: set[UUID] = set()

    def visit(node_version_id: UUID) -> bool:
        if node_version_id in visiting:
            return True
        if node_version_id in visited:
            return False
        visiting.add(node_version_id)
        for target in graph.get(node_version_id, []):
            if visit(target):
                return True
        visiting.remove(node_version_id)
        visited.add(node_version_id)
        return False

    return visit(start_node_version_id)


def _persist_blockers(
    session: Session,
    *,
    node_version_id: UUID,
    blockers: list[DependencyBlockerSnapshot],
) -> list[DependencyBlockerSnapshot]:
    existing = session.execute(
        select(NodeDependencyBlocker).where(NodeDependencyBlocker.node_version_id == node_version_id)
    ).scalars().all()
    for row in existing:
        session.delete(row)
    session.flush()
    persisted: list[DependencyBlockerSnapshot] = []
    for blocker in blockers:
        row = NodeDependencyBlocker(
            id=uuid4(),
            node_version_id=node_version_id,
            dependency_id=blocker.dependency_id,
            blocker_kind=blocker.blocker_kind,
            target_node_version_id=blocker.target_node_version_id,
            details_json=blocker.details_json,
        )
        session.add(row)
        persisted.append(
            DependencyBlockerSnapshot(
                blocker_kind=row.blocker_kind,
                dependency_id=row.dependency_id,
                node_version_id=row.node_version_id,
                target_node_version_id=row.target_node_version_id,
                details_json=row.details_json,
            )
        )
    session.flush()
    return persisted


def _dependencies_for_version(session: Session, node_version_id: UUID) -> list[NodeDependency]:
    return session.execute(
        select(NodeDependency)
        .where(NodeDependency.node_version_id == node_version_id)
        .order_by(NodeDependency.created_at, NodeDependency.id)
    ).scalars().all()


def _resolve_authoritative_target(session: Session, dependency: NodeDependency) -> NodeVersion | None:
    target_version = session.get(NodeVersion, dependency.depends_on_node_version_id)
    if target_version is None:
        return None
    selector = session.get(LogicalNodeCurrentVersion, target_version.logical_node_id)
    if selector is None:
        return None
    return session.get(NodeVersion, selector.authoritative_node_version_id)


def _authoritative_version(session: Session, node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _runtime_blockers(
    *,
    node_version: NodeVersion,
    lifecycle: NodeLifecycleState | None,
    blockers: list[DependencyBlockerSnapshot],
) -> list[DependencyBlockerSnapshot]:
    if node_version.compiled_workflow_id is None:
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="not_compiled",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={"message": "node version has no compiled workflow"},
            )
        )
    if lifecycle is None:
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="lifecycle_not_ready",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={"message": "node lifecycle row is missing"},
            )
        )
        return blockers
    if lifecycle.pause_flag_name:
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="pause_gate_active",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={
                    "pause_flag_name": lifecycle.pause_flag_name,
                    "run_status": lifecycle.run_status,
                    "is_resumable": lifecycle.is_resumable,
                },
            )
        )
    if lifecycle.run_status in {"PENDING", "RUNNING"}:
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="already_running",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={
                    "run_status": lifecycle.run_status,
                    "current_run_id": None if lifecycle.current_run_id is None else str(lifecycle.current_run_id),
                },
            )
        )
    if lifecycle.lifecycle_state not in {"READY", "RUNNING", "PAUSED_FOR_USER", "COMPLETE"}:
        blockers.append(
            DependencyBlockerSnapshot(
                blocker_kind="lifecycle_not_ready",
                dependency_id=None,
                node_version_id=node_version.id,
                target_node_version_id=None,
                details_json={"lifecycle_state": lifecycle.lifecycle_state},
            )
        )
    return blockers


def _dependency_snapshot(row: NodeDependency) -> NodeDependencySnapshot:
    return NodeDependencySnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        depends_on_node_version_id=row.depends_on_node_version_id,
        dependency_type=row.dependency_type,
        required_state=row.required_state,
    )


def _blocker_snapshot(row: NodeDependencyBlocker) -> DependencyBlockerSnapshot:
    return DependencyBlockerSnapshot(
        blocker_kind=row.blocker_kind,
        dependency_id=row.dependency_id,
        node_version_id=row.node_version_id,
        target_node_version_id=row.target_node_version_id,
        details_json=row.details_json,
    )
