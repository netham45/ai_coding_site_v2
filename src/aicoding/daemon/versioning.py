from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.branches import build_canonical_branch_name, inherited_seed_commit
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import has_unresolved_merge_conflicts
from aicoding.db.models import (
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeDependency,
    NodeLifecycleState,
    NodeVersion,
    ParentChildAuthority,
    RebuildEvent,
)
from aicoding.db.session import query_session_scope, session_scope

VERSION_STATUSES = {"authoritative", "candidate", "failed_candidate", "superseded"}


class _MissingValue:
    pass


_MISSING = _MissingValue()


@dataclass(frozen=True, slots=True)
class NodeVersionSnapshot:
    id: UUID
    logical_node_id: UUID
    parent_node_version_id: UUID | None
    tier: str
    node_kind: str
    title: str
    prompt: str
    description: str | None
    status: str
    version_number: int
    compiled_workflow_id: UUID | None
    supersedes_node_version_id: UUID | None
    active_branch_name: str | None
    branch_generation_number: int | None
    seed_commit_sha: str | None
    final_commit_sha: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "logical_node_id": str(self.logical_node_id),
            "parent_node_version_id": None if self.parent_node_version_id is None else str(self.parent_node_version_id),
            "tier": self.tier,
            "node_kind": self.node_kind,
            "title": self.title,
            "prompt": self.prompt,
            "description": self.description,
            "status": self.status,
            "version_number": self.version_number,
            "compiled_workflow_id": None if self.compiled_workflow_id is None else str(self.compiled_workflow_id),
            "supersedes_node_version_id": None if self.supersedes_node_version_id is None else str(self.supersedes_node_version_id),
            "active_branch_name": self.active_branch_name,
            "branch_generation_number": self.branch_generation_number,
            "seed_commit_sha": self.seed_commit_sha,
            "final_commit_sha": self.final_commit_sha,
        }


@dataclass(frozen=True, slots=True)
class NodeLineageSnapshot:
    logical_node_id: UUID
    authoritative_node_version_id: UUID
    latest_created_node_version_id: UUID
    versions: list[NodeVersionSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "logical_node_id": str(self.logical_node_id),
            "authoritative_node_version_id": str(self.authoritative_node_version_id),
            "latest_created_node_version_id": str(self.latest_created_node_version_id),
            "versions": [item.to_payload() for item in self.versions],
        }


def initialize_node_version(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> NodeVersionSnapshot:
    with session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is not None:
            return _snapshot(session.get(NodeVersion, selector.authoritative_node_version_id))

        node = session.get(HierarchyNode, logical_node_id)
        if node is None:
            raise DaemonNotFoundError("node not found")

        parent_version_id = _current_parent_version_id(session, node.parent_node_id)
        version = NodeVersion(
            id=uuid4(),
            logical_node_id=node.node_id,
            parent_node_version_id=parent_version_id,
            tier=node.tier,
            node_kind=node.kind,
            title=node.title,
            prompt=node.prompt,
            description=None,
            status="authoritative",
            version_number=1,
            supersedes_node_version_id=None,
            active_branch_name=build_canonical_branch_name(
                tier=node.tier,
                kind=node.kind,
                title=node.title,
                logical_node_id=node.node_id,
                version_number=1,
            ),
            branch_generation_number=1,
        )
        session.add(version)
        session.flush()
        session.add(
            LogicalNodeCurrentVersion(
                logical_node_id=node.node_id,
                authoritative_node_version_id=version.id,
                latest_created_node_version_id=version.id,
            )
        )
        session.flush()
        return _snapshot(version)


def create_superseding_node_version(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    title: str | None = None,
    prompt: str | None = None,
) -> NodeVersionSnapshot:
    with session_scope(session_factory) as session:
        version = create_superseding_node_version_in_session(
            session,
            logical_node_id=logical_node_id,
            title=title,
            prompt=prompt,
        )
        return _snapshot(version)


def create_superseding_node_version_in_session(
    session: Session,
    *,
    logical_node_id: UUID,
    title: str | None = None,
    prompt: str | None = None,
    parent_node_version_id: UUID | None | object = _MISSING,
) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    _ensure_no_active_run_conflict(session, logical_node_id)

    authoritative = session.get(NodeVersion, selector.authoritative_node_version_id)
    latest = session.get(NodeVersion, selector.latest_created_node_version_id)
    if authoritative is None or latest is None:
        raise DaemonNotFoundError("current node version records not found")
    if latest.status == "candidate":
        raise DaemonConflictError("logical node already has a live candidate version")

    node = session.get(HierarchyNode, logical_node_id)
    if node is None:
        raise DaemonNotFoundError("node not found")

    version_number = latest.version_number + 1
    resolved_parent_version_id = (
        _current_parent_version_id(session, node.parent_node_id)
        if parent_node_version_id is _MISSING
        else parent_node_version_id
    )
    version = NodeVersion(
        id=uuid4(),
        logical_node_id=logical_node_id,
        parent_node_version_id=resolved_parent_version_id,
        tier=node.tier,
        node_kind=node.kind,
        title=title or latest.title,
        prompt=prompt or latest.prompt,
        description=latest.description,
        status="candidate",
        version_number=version_number,
        supersedes_node_version_id=latest.id,
        active_branch_name=build_canonical_branch_name(
            tier=node.tier,
            kind=node.kind,
            title=title or latest.title,
            logical_node_id=logical_node_id,
            version_number=version_number,
        ),
        branch_generation_number=version_number,
        seed_commit_sha=inherited_seed_commit(latest),
        final_commit_sha=None,
    )
    session.add(version)
    session.flush()
    _clone_version_scoped_edges(session, source_version_id=latest.id, target_version_id=version.id)
    selector.latest_created_node_version_id = version.id
    session.flush()
    return version


def cutover_candidate_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> NodeLineageSnapshot:
    with session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        if version.status != "candidate":
            raise DaemonConflictError("only candidate versions may cut over")
        if has_unresolved_merge_conflicts(session, node_version_id=version.id):
            raise DaemonConflictError("candidate version has unresolved merge conflicts")
        if _rebuild_cutover_blocked(session, version_id=version.id):
            raise DaemonConflictError("candidate version rebuild lineage is not yet marked stable for cutover")

        selector = session.get(LogicalNodeCurrentVersion, version.logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")

        old_authoritative = session.get(NodeVersion, selector.authoritative_node_version_id)
        if old_authoritative is None:
            raise DaemonNotFoundError("authoritative version not found")

        old_authoritative.status = "superseded"
        version.status = "authoritative"
        selector.authoritative_node_version_id = version.id
        selector.latest_created_node_version_id = version.id

        lifecycle = session.get(NodeLifecycleState, str(version.logical_node_id))
        if lifecycle is not None and lifecycle.lifecycle_state == "COMPLETE":
            lifecycle.lifecycle_state = "DRAFT"
            lifecycle.run_status = None
            lifecycle.current_run_id = None
            lifecycle.current_task_id = None
            lifecycle.current_subtask_id = None
            lifecycle.current_subtask_attempt = None
            lifecycle.last_completed_subtask_id = None
            lifecycle.execution_cursor_json = {}
            lifecycle.is_resumable = False
            lifecycle.pause_flag_name = None

        session.flush()
        return _lineage_snapshot(session, version.logical_node_id)


def list_node_versions(session_factory: sessionmaker[Session], logical_node_id: UUID) -> list[NodeVersionSnapshot]:
    with query_session_scope(session_factory) as session:
        _require_selector(session, logical_node_id)
        rows = session.execute(
            select(NodeVersion)
            .where(NodeVersion.logical_node_id == logical_node_id)
            .order_by(NodeVersion.version_number)
        ).scalars().all()
        return [_snapshot(row) for row in rows]


def load_node_lineage(session_factory: sessionmaker[Session], logical_node_id: UUID) -> NodeLineageSnapshot:
    with query_session_scope(session_factory) as session:
        return _lineage_snapshot(session, logical_node_id)


def load_node_version(session_factory: sessionmaker[Session], version_id: UUID) -> NodeVersionSnapshot:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        return _snapshot(version)


def _lineage_snapshot(session: Session, logical_node_id: UUID) -> NodeLineageSnapshot:
    selector = _require_selector(session, logical_node_id)
    rows = session.execute(
        select(NodeVersion)
        .where(NodeVersion.logical_node_id == logical_node_id)
        .order_by(NodeVersion.version_number)
    ).scalars().all()
    return NodeLineageSnapshot(
        logical_node_id=logical_node_id,
        authoritative_node_version_id=selector.authoritative_node_version_id,
        latest_created_node_version_id=selector.latest_created_node_version_id,
        versions=[_snapshot(row) for row in rows],
    )


def _require_selector(session: Session, logical_node_id: UUID) -> LogicalNodeCurrentVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    return selector


def _snapshot(version: NodeVersion | None) -> NodeVersionSnapshot:
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return NodeVersionSnapshot(
        id=version.id,
        logical_node_id=version.logical_node_id,
        parent_node_version_id=version.parent_node_version_id,
        tier=version.tier,
        node_kind=version.node_kind,
        title=version.title,
        prompt=version.prompt,
        description=version.description,
        status=version.status,
        version_number=version.version_number,
        supersedes_node_version_id=version.supersedes_node_version_id,
        compiled_workflow_id=version.compiled_workflow_id,
        active_branch_name=version.active_branch_name,
        branch_generation_number=version.branch_generation_number,
        seed_commit_sha=version.seed_commit_sha,
        final_commit_sha=version.final_commit_sha,
    )


def _current_parent_version_id(session: Session, parent_node_id: UUID | None) -> UUID | None:
    if parent_node_id is None:
        return None
    selector = session.get(LogicalNodeCurrentVersion, parent_node_id)
    return None if selector is None else selector.authoritative_node_version_id


def _ensure_no_active_run_conflict(session: Session, logical_node_id: UUID) -> None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None:
        return
    if lifecycle.current_run_id is not None and lifecycle.run_status in {"RUNNING", "PAUSED"}:
        raise DaemonConflictError("logical node has an active or paused run; resolve it before superseding")


def _clone_version_scoped_edges(session: Session, *, source_version_id: UUID, target_version_id: UUID) -> None:
    source_children = session.execute(
        select(NodeChild).where(NodeChild.parent_node_version_id == source_version_id)
    ).scalars().all()
    for edge in source_children:
        session.add(
            NodeChild(
                parent_node_version_id=target_version_id,
                child_node_version_id=edge.child_node_version_id,
                layout_child_id=edge.layout_child_id,
                origin_type=edge.origin_type,
                ordinal=edge.ordinal,
            )
        )

    source_authority = session.get(ParentChildAuthority, source_version_id)
    if source_authority is not None:
        session.add(
            ParentChildAuthority(
                parent_node_version_id=target_version_id,
                authority_mode=source_authority.authority_mode,
                authoritative_layout_hash=source_authority.authoritative_layout_hash,
                last_reconciled_at=source_authority.last_reconciled_at,
            )
        )

    source_dependencies = session.execute(
        select(NodeDependency).where(NodeDependency.node_version_id == source_version_id)
    ).scalars().all()
    for dependency in source_dependencies:
        session.add(
            NodeDependency(
                id=uuid4(),
                node_version_id=target_version_id,
                depends_on_node_version_id=dependency.depends_on_node_version_id,
                dependency_type=dependency.dependency_type,
                required_state=dependency.required_state,
            )
        )


def _rebuild_cutover_blocked(session: Session, *, version_id: UUID) -> bool:
    events = session.execute(
        select(RebuildEvent)
        .where(RebuildEvent.target_node_version_id == version_id)
        .order_by(RebuildEvent.created_at, RebuildEvent.id)
    ).scalars().all()
    if not events:
        return False
    return not any(event.event_status == "stable" for event in events)
