from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.child_reconcile import execute_child_merge_pipeline_for_version
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.rebuild_coordination import inspect_rebuild_coordination, record_rebuild_coordination_event
from aicoding.daemon.versioning import create_superseding_node_version_in_session
from aicoding.daemon.workflows import compile_node_version_workflow
from aicoding.db.models import (
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeDependency,
    NodeVersion,
    ParentChildAuthority,
    RebuildEvent,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.source_lineage import capture_node_version_source_lineage


@dataclass(frozen=True, slots=True)
class RebuildEventSnapshot:
    id: UUID
    root_logical_node_id: UUID
    root_node_version_id: UUID
    target_node_version_id: UUID
    event_kind: str
    event_status: str
    scope: str
    trigger_reason: str
    details_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "root_logical_node_id": str(self.root_logical_node_id),
            "root_node_version_id": str(self.root_node_version_id),
            "target_node_version_id": str(self.target_node_version_id),
            "event_kind": self.event_kind,
            "event_status": self.event_status,
            "scope": self.scope,
            "trigger_reason": self.trigger_reason,
            "details_json": self.details_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class RebuildHistorySnapshot:
    node_id: UUID
    events: list[RebuildEventSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "events": [item.to_payload() for item in self.events],
        }


@dataclass(frozen=True, slots=True)
class RegenerationSnapshot:
    root_node_id: UUID
    root_node_version_id: UUID
    scope: str
    trigger_reason: str
    created_candidate_version_ids: list[UUID]
    stable_candidate_version_ids: list[UUID]
    rebuild_history: list[RebuildEventSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "root_node_id": str(self.root_node_id),
            "root_node_version_id": str(self.root_node_version_id),
            "scope": self.scope,
            "trigger_reason": self.trigger_reason,
            "created_candidate_version_ids": [str(item) for item in self.created_candidate_version_ids],
            "stable_candidate_version_ids": [str(item) for item in self.stable_candidate_version_ids],
            "rebuild_history": [item.to_payload() for item in self.rebuild_history],
        }


def regenerate_node_and_descendants(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    trigger_reason: str = "manual_regenerate",
    catalog: ResourceCatalog | None = None,
) -> RegenerationSnapshot:
    resources = catalog or load_resource_catalog()
    coordination = inspect_rebuild_coordination(session_factory, logical_node_id=logical_node_id, scope="subtree")
    if coordination.status != "clear":
        root_authoritative_id = _load_authoritative_version_id(session_factory, logical_node_id)
        record_rebuild_coordination_event(
            session_factory,
            logical_node_id=logical_node_id,
            target_node_version_id=root_authoritative_id,
            event_kind="live_conflict_blocked",
            event_status="blocked",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json=coordination.to_payload(),
        )
        raise DaemonConflictError("live runtime state blocks subtree rebuild; inspect rebuild coordination")
    with session_scope(session_factory) as session:
        root_authoritative = _authoritative_version(session, logical_node_id)
        subtree_order = _collect_subtree_authoritative_versions(session, root_authoritative.id)
        candidate_by_logical: dict[UUID, NodeVersion] = {}
        source_by_logical: dict[UUID, NodeVersion] = {}

        for source_version in subtree_order:
            source_by_logical[source_version.logical_node_id] = source_version
            candidate = _ensure_candidate(session, source_version)
            candidate_by_logical[source_version.logical_node_id] = candidate

        for source_version in subtree_order:
            candidate = candidate_by_logical[source_version.logical_node_id]
            node = session.get(HierarchyNode, source_version.logical_node_id)
            if node is None:
                raise DaemonNotFoundError("node not found")
            candidate.parent_node_version_id = (
                None
                if node.parent_node_id is None or node.parent_node_id not in candidate_by_logical
                else candidate_by_logical[node.parent_node_id].id
            )
            _apply_candidate_remap(
                session,
                node_version_id=candidate.id,
                logical_to_candidate_version_id={key: value.id for key, value in candidate_by_logical.items()},
            )

        session.flush()
        root_candidate = candidate_by_logical[logical_node_id]

    created_ids = [item.id for item in candidate_by_logical.values()]
    for source_version in subtree_order:
        candidate = candidate_by_logical[source_version.logical_node_id]
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_candidate.id,
            target_node_version_id=candidate.id,
            event_kind="candidate_created",
            event_status="pending",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={"supersedes_node_version_id": str(source_version.id)},
        )
    for version_id in created_ids:
        capture_node_version_source_lineage(session_factory, node_version_id=version_id, catalog=resources)
        attempt = compile_node_version_workflow(session_factory, version_id=version_id, catalog=resources)
        if attempt.status != "compiled":
            _record_rebuild_event(
                session_factory,
                root_logical_node_id=logical_node_id,
                root_node_version_id=root_candidate.id,
                target_node_version_id=version_id,
                event_kind="workflow_compiled",
                event_status="failed",
                scope="subtree",
                trigger_reason=trigger_reason,
                details_json={"compile_failure": attempt.compile_failure.to_payload() if attempt.compile_failure else {}},
            )
            raise DaemonConflictError("candidate workflow compilation failed during regeneration")
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_candidate.id,
            target_node_version_id=version_id,
            event_kind="workflow_compiled",
            event_status="compiled",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={"compiled_workflow_id": str(attempt.compiled_workflow.id) if attempt.compiled_workflow else None},
        )

    stable_ids = _rectify_versions_bottom_up(
        session_factory,
        resources=resources,
        root_logical_node_id=logical_node_id,
        root_node_version_id=root_candidate.id,
        candidate_version_ids=created_ids,
        trigger_reason=trigger_reason,
        scope="subtree",
    )
    history = list_rebuild_events_for_node(session_factory, logical_node_id=logical_node_id).events
    return RegenerationSnapshot(
        root_node_id=logical_node_id,
        root_node_version_id=root_candidate.id,
        scope="subtree",
        trigger_reason=trigger_reason,
        created_candidate_version_ids=created_ids,
        stable_candidate_version_ids=stable_ids,
        rebuild_history=history,
    )


def rectify_upstream(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    trigger_reason: str = "manual_rectify_upstream",
    catalog: ResourceCatalog | None = None,
) -> RegenerationSnapshot:
    resources = catalog or load_resource_catalog()
    coordination = inspect_rebuild_coordination(session_factory, logical_node_id=logical_node_id, scope="upstream")
    if coordination.status != "clear":
        root_authoritative_id = _load_authoritative_version_id(session_factory, logical_node_id)
        record_rebuild_coordination_event(
            session_factory,
            logical_node_id=logical_node_id,
            target_node_version_id=root_authoritative_id,
            event_kind="live_conflict_blocked",
            event_status="blocked",
            scope="upstream",
            trigger_reason=trigger_reason,
            details_json=coordination.to_payload(),
        )
        raise DaemonConflictError("live runtime state blocks upstream rectification; inspect rebuild coordination")
    subtree_snapshot = regenerate_node_and_descendants(
        session_factory,
        logical_node_id=logical_node_id,
        trigger_reason=trigger_reason,
        catalog=resources,
    )

    with session_scope(session_factory) as session:
        current_child_candidate = session.get(NodeVersion, subtree_snapshot.root_node_version_id)
        if current_child_candidate is None:
            raise DaemonNotFoundError("root candidate version not found")
        current_node = session.get(HierarchyNode, logical_node_id)
        if current_node is None:
            raise DaemonNotFoundError("node not found")

        ancestor_candidates: list[NodeVersion] = []
        while current_node.parent_node_id is not None:
            parent_authoritative = _authoritative_version(session, current_node.parent_node_id)
            parent_candidate = _ensure_candidate(session, parent_authoritative)
            parent_candidate.parent_node_version_id = _current_candidate_parent_version_id(session, current_node.parent_node_id)
            _apply_candidate_remap(
                session,
                node_version_id=parent_candidate.id,
                logical_to_candidate_version_id={current_child_candidate.logical_node_id: current_child_candidate.id},
            )
            _record_rebuild_event_in_session(
                session,
                root_logical_node_id=logical_node_id,
                root_node_version_id=subtree_snapshot.root_node_version_id,
                target_node_version_id=parent_candidate.id,
                event_kind="candidate_created",
                event_status="pending",
                scope="upstream",
                trigger_reason=trigger_reason,
                details_json={"supersedes_node_version_id": str(parent_authoritative.id)},
            )
            ancestor_candidates.append(parent_candidate)
            current_child_candidate = parent_candidate
            current_node = session.get(HierarchyNode, current_node.parent_node_id)
            if current_node is None:
                raise DaemonNotFoundError("ancestor node not found")
        session.flush()

    ancestor_ids = [item.id for item in ancestor_candidates]
    for version_id in ancestor_ids:
        capture_node_version_source_lineage(session_factory, node_version_id=version_id, catalog=resources)
        attempt = compile_node_version_workflow(session_factory, version_id=version_id, catalog=resources)
        if attempt.status != "compiled":
            _record_rebuild_event(
                session_factory,
                root_logical_node_id=logical_node_id,
                root_node_version_id=subtree_snapshot.root_node_version_id,
                target_node_version_id=version_id,
                event_kind="workflow_compiled",
                event_status="failed",
                scope="upstream",
                trigger_reason=trigger_reason,
                details_json={"compile_failure": attempt.compile_failure.to_payload() if attempt.compile_failure else {}},
            )
            raise DaemonConflictError("ancestor workflow compilation failed during upstream rectification")
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=subtree_snapshot.root_node_version_id,
            target_node_version_id=version_id,
            event_kind="workflow_compiled",
            event_status="compiled",
            scope="upstream",
            trigger_reason=trigger_reason,
            details_json={"compiled_workflow_id": str(attempt.compiled_workflow.id) if attempt.compiled_workflow else None},
        )

    stable_ids = list(subtree_snapshot.stable_candidate_version_ids)
    if ancestor_ids:
        stable_ids.extend(
            _rectify_versions_bottom_up(
                session_factory,
                resources=resources,
                root_logical_node_id=logical_node_id,
                root_node_version_id=subtree_snapshot.root_node_version_id,
                candidate_version_ids=ancestor_ids,
                trigger_reason=trigger_reason,
                scope="upstream",
            )
        )
    history = list_rebuild_events_for_node(session_factory, logical_node_id=logical_node_id).events
    return RegenerationSnapshot(
        root_node_id=logical_node_id,
        root_node_version_id=subtree_snapshot.root_node_version_id,
        scope="upstream",
        trigger_reason=trigger_reason,
        created_candidate_version_ids=subtree_snapshot.created_candidate_version_ids + ancestor_ids,
        stable_candidate_version_ids=stable_ids,
        rebuild_history=history,
    )


def list_rebuild_events_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> RebuildHistorySnapshot:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(RebuildEvent)
            .where(RebuildEvent.root_logical_node_id == logical_node_id)
            .order_by(RebuildEvent.created_at, RebuildEvent.id)
        ).scalars().all()
        return RebuildHistorySnapshot(
            node_id=logical_node_id,
            events=[_rebuild_event_snapshot(row) for row in rows],
        )


def _collect_subtree_authoritative_versions(session: Session, root_version_id: UUID) -> list[NodeVersion]:
    ordered: list[NodeVersion] = []

    def visit(version_id: UUID) -> None:
        version = session.get(NodeVersion, version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        ordered.append(version)
        children = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == version_id).order_by(NodeChild.ordinal, NodeChild.created_at)
        ).scalars().all()
        for edge in children:
            child_version = session.get(NodeVersion, edge.child_node_version_id)
            if child_version is None:
                raise DaemonNotFoundError("child node version not found")
            selector = session.get(LogicalNodeCurrentVersion, child_version.logical_node_id)
            if selector is None:
                continue
            visit(selector.authoritative_node_version_id)

    visit(root_version_id)
    return list(reversed(ordered))


def _ensure_candidate(session: Session, source_version: NodeVersion) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, source_version.logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    latest = session.get(NodeVersion, selector.latest_created_node_version_id)
    if latest is not None and latest.status == "candidate":
        return latest
    return create_superseding_node_version_in_session(session, logical_node_id=source_version.logical_node_id)


def _apply_candidate_remap(
    session: Session,
    *,
    node_version_id: UUID,
    logical_to_candidate_version_id: dict[UUID, UUID],
) -> None:
    edges = session.execute(select(NodeChild).where(NodeChild.parent_node_version_id == node_version_id)).scalars().all()
    for edge in edges:
        child_version = session.get(NodeVersion, edge.child_node_version_id)
        if child_version is None:
            continue
        replacement = logical_to_candidate_version_id.get(child_version.logical_node_id)
        if replacement is not None:
            edge.child_node_version_id = replacement

    dependencies = session.execute(select(NodeDependency).where(NodeDependency.node_version_id == node_version_id)).scalars().all()
    for dependency in dependencies:
        target = session.get(NodeVersion, dependency.depends_on_node_version_id)
        if target is None:
            continue
        replacement = logical_to_candidate_version_id.get(target.logical_node_id)
        if replacement is not None:
            dependency.depends_on_node_version_id = replacement

    authority = session.get(ParentChildAuthority, node_version_id)
    if authority is None:
        session.add(ParentChildAuthority(parent_node_version_id=node_version_id, authority_mode="manual"))


def _rectify_versions_bottom_up(
    session_factory: sessionmaker[Session],
    *,
    resources: ResourceCatalog,
    root_logical_node_id: UUID,
    root_node_version_id: UUID,
    candidate_version_ids: list[UUID],
    trigger_reason: str,
    scope: str,
) -> list[UUID]:
    ordered_ids = _sort_versions_for_rectify(session_factory, candidate_version_ids)
    stable_ids: list[UUID] = []
    for version_id in ordered_ids:
        with session_scope(session_factory) as session:
            version = session.get(NodeVersion, version_id)
            if version is None:
                raise DaemonNotFoundError("node version not found")
            if version.seed_commit_sha is None:
                version.seed_commit_sha = sha256(f"seed:{version.id}:{version.logical_node_id}:{version.version_number}".encode("utf-8")).hexdigest()
            child_count = session.execute(
                select(NodeChild).where(NodeChild.parent_node_version_id == version.id)
            ).scalars().all()
            is_leaf = len(child_count) == 0
            if is_leaf:
                version.final_commit_sha = sha256(
                    f"final:{version.id}:{version.seed_commit_sha}:{version.compiled_workflow_id}".encode("utf-8")
                ).hexdigest()
            session.flush()
        if not is_leaf:
            snapshot = execute_child_merge_pipeline_for_version(
                session_factory,
                resources,
                node_version_id=version_id,
            )
            with session_scope(session_factory) as session:
                version = session.get(NodeVersion, version_id)
                if version is None:
                    raise DaemonNotFoundError("node version not found")
                parent_commit_after = snapshot.merge_events[-1].parent_commit_after if snapshot.merge_events else version.seed_commit_sha
                version.final_commit_sha = sha256(
                    f"final:{version.id}:{parent_commit_after}:{version.compiled_workflow_id}".encode("utf-8")
                ).hexdigest()
                session.flush()
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=root_logical_node_id,
            root_node_version_id=root_node_version_id,
            target_node_version_id=version_id,
            event_kind="rectified",
            event_status="stable",
            scope=scope,
            trigger_reason=trigger_reason,
            details_json={"finalized": True},
        )
        stable_ids.append(version_id)
    return stable_ids


def _sort_versions_for_rectify(session_factory: sessionmaker[Session], version_ids: list[UUID]) -> list[UUID]:
    with query_session_scope(session_factory) as session:
        versions = [session.get(NodeVersion, version_id) for version_id in version_ids]
        if any(version is None for version in versions):
            raise DaemonNotFoundError("node version not found")
        return [
            version.id
            for version in sorted(
                [version for version in versions if version is not None],
                key=lambda item: (_depth(session, item.logical_node_id), item.created_at),
                reverse=True,
            )
        ]


def _depth(session: Session, logical_node_id: UUID) -> int:
    depth = 0
    node = session.get(HierarchyNode, logical_node_id)
    while node is not None and node.parent_node_id is not None:
        depth += 1
        node = session.get(HierarchyNode, node.parent_node_id)
    return depth


def _current_candidate_parent_version_id(session: Session, logical_node_id: UUID) -> UUID | None:
    node = session.get(HierarchyNode, logical_node_id)
    if node is None or node.parent_node_id is None:
        return None
    selector = session.get(LogicalNodeCurrentVersion, node.parent_node_id)
    if selector is None:
        return None
    latest = session.get(NodeVersion, selector.latest_created_node_version_id)
    if latest is None:
        return selector.authoritative_node_version_id
    return latest.id if latest.status == "candidate" else selector.authoritative_node_version_id


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("authoritative node version not found")
    return version


def _load_authoritative_version_id(session_factory: sessionmaker[Session], logical_node_id: UUID) -> UUID:
    with query_session_scope(session_factory) as session:
        return _authoritative_version(session, logical_node_id).id


def _record_rebuild_event(
    session_factory: sessionmaker[Session],
    *,
    root_logical_node_id: UUID,
    root_node_version_id: UUID,
    target_node_version_id: UUID,
    event_kind: str,
    event_status: str,
    scope: str,
    trigger_reason: str,
    details_json: dict[str, object],
) -> RebuildEventSnapshot:
    with session_scope(session_factory) as session:
        return _record_rebuild_event_in_session(
            session,
            root_logical_node_id=root_logical_node_id,
            root_node_version_id=root_node_version_id,
            target_node_version_id=target_node_version_id,
            event_kind=event_kind,
            event_status=event_status,
            scope=scope,
            trigger_reason=trigger_reason,
            details_json=details_json,
        )


def _record_rebuild_event_in_session(
    session: Session,
    *,
    root_logical_node_id: UUID,
    root_node_version_id: UUID,
    target_node_version_id: UUID,
    event_kind: str,
    event_status: str,
    scope: str,
    trigger_reason: str,
    details_json: dict[str, object],
) -> RebuildEventSnapshot:
    event = RebuildEvent(
        id=uuid4(),
        root_logical_node_id=root_logical_node_id,
        root_node_version_id=root_node_version_id,
        target_node_version_id=target_node_version_id,
        event_kind=event_kind,
        event_status=event_status,
        scope=scope,
        trigger_reason=trigger_reason,
        details_json=details_json,
    )
    session.add(event)
    session.flush()
    return _rebuild_event_snapshot(event)


def _rebuild_event_snapshot(event: RebuildEvent) -> RebuildEventSnapshot:
    return RebuildEventSnapshot(
        id=event.id,
        root_logical_node_id=event.root_logical_node_id,
        root_node_version_id=event.root_node_version_id,
        target_node_version_id=event.target_node_version_id,
        event_kind=event.event_kind,
        event_status=event.event_status,
        scope=event.scope,
        trigger_reason=event.trigger_reason,
        details_json=dict(event.details_json or {}),
        created_at=event.created_at.isoformat(),
    )
