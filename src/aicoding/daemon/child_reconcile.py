from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import (
    MergeEventSnapshot,
    has_unresolved_merge_conflicts,
    record_merge_event_in_session,
)
from aicoding.db.models import (
    ChildSessionResult,
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeDependency,
    NodeLifecycleState,
    NodeRun,
    NodeRunState,
    NodeVersion,
    ParentChildAuthority,
    Session as DaemonSession,
    SubtaskAttempt,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog

ACTIVE_RUN_STATUSES = {"PENDING", "RUNNING", "PAUSED"}
MERGEABLE_RECONCILE_STATUSES = {"ready_for_reconcile", "superseded_with_authoritative_replacement"}
RECONCILE_PROMPT_GROUP = "prompt_pack_default"
RECONCILE_PROMPT_PATH = "execution/reconcile_parent_after_merge.md"


@dataclass(frozen=True, slots=True)
class ChildResultSnapshot:
    layout_child_id: str
    child_node_id: UUID
    child_node_version_id: UUID
    edge_child_node_version_id: UUID
    origin_type: str
    ordinal: int | None
    child_kind: str
    child_title: str
    lifecycle_state: str | None
    run_status: str | None
    final_commit_sha: str | None
    latest_summary: str | None
    latest_child_session_summary: str | None
    reconcile_status: str
    merge_order: int | None
    dependency_child_node_ids: list[UUID]
    blocking_reasons: list[str]

    def to_payload(self) -> dict[str, object]:
        return {
            "layout_child_id": self.layout_child_id,
            "child_node_id": str(self.child_node_id),
            "child_node_version_id": str(self.child_node_version_id),
            "edge_child_node_version_id": str(self.edge_child_node_version_id),
            "origin_type": self.origin_type,
            "ordinal": self.ordinal,
            "child_kind": self.child_kind,
            "child_title": self.child_title,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "final_commit_sha": self.final_commit_sha,
            "latest_summary": self.latest_summary,
            "latest_child_session_summary": self.latest_child_session_summary,
            "reconcile_status": self.reconcile_status,
            "merge_order": self.merge_order,
            "dependency_child_node_ids": [str(item) for item in self.dependency_child_node_ids],
            "blocking_reasons": self.blocking_reasons,
        }


@dataclass(frozen=True, slots=True)
class ChildResultCollectionSnapshot:
    parent_node_id: UUID
    parent_node_version_id: UUID
    authority_mode: str
    status: str
    ready_child_count: int
    waiting_child_count: int
    failed_child_count: int
    paused_child_count: int
    invalid_child_count: int
    reusable_final_count: int
    children: list[ChildResultSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_id": str(self.parent_node_id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "authority_mode": self.authority_mode,
            "status": self.status,
            "ready_child_count": self.ready_child_count,
            "waiting_child_count": self.waiting_child_count,
            "failed_child_count": self.failed_child_count,
            "paused_child_count": self.paused_child_count,
            "invalid_child_count": self.invalid_child_count,
            "reusable_final_count": self.reusable_final_count,
            "children": [item.to_payload() for item in self.children],
        }


@dataclass(frozen=True, slots=True)
class ParentReconcileSnapshot:
    parent_node_id: UUID
    parent_node_version_id: UUID
    status: str
    seed_commit_sha: str | None
    prompt_relative_path: str
    prompt_text: str
    child_results: ChildResultCollectionSnapshot
    blocking_reasons: list[str]
    merge_events: list[MergeEventSnapshot]
    last_reconciled_at: str | None
    context_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_id": str(self.parent_node_id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "status": self.status,
            "seed_commit_sha": self.seed_commit_sha,
            "prompt_relative_path": self.prompt_relative_path,
            "prompt_text": self.prompt_text,
            "child_results": self.child_results.to_payload(),
            "blocking_reasons": self.blocking_reasons,
            "merge_events": [item.to_payload() for item in self.merge_events],
            "last_reconciled_at": self.last_reconciled_at,
            "context_json": self.context_json,
        }


def collect_child_results(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> ChildResultCollectionSnapshot:
    with query_session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, logical_node_id=logical_node_id)
        child_edges = _load_child_edges(session, parent_version.id)
        children = _build_child_results(session, child_edges, resolve_authoritative=True)
        return _collection_snapshot(parent_node.node_id, parent_version.id, authority, children)


def collect_child_results_for_version(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
) -> ChildResultCollectionSnapshot:
    with query_session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, node_version_id=node_version_id)
        child_edges = _load_child_edges(session, parent_version.id)
        children = _build_child_results(session, child_edges, resolve_authoritative=False)
        return _collection_snapshot(parent_node.node_id, parent_version.id, authority, children)


def inspect_parent_reconcile(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
) -> ParentReconcileSnapshot:
    with query_session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, logical_node_id=logical_node_id)
        child_edges = _load_child_edges(session, parent_version.id)
        children = _build_child_results(session, child_edges, resolve_authoritative=True)
        collection = _collection_snapshot(parent_node.node_id, parent_version.id, authority, children)
        blocking_reasons = _reconcile_blockers(parent_version, children, session=session)
        prompt = resources.load_text(RECONCILE_PROMPT_GROUP, RECONCILE_PROMPT_PATH)
        return ParentReconcileSnapshot(
            parent_node_id=parent_node.node_id,
            parent_node_version_id=parent_version.id,
            status="ready_for_reconcile" if not blocking_reasons else "blocked",
            seed_commit_sha=parent_version.seed_commit_sha,
            prompt_relative_path=RECONCILE_PROMPT_PATH,
            prompt_text=prompt.content,
            child_results=collection,
            blocking_reasons=blocking_reasons,
            merge_events=[],
            last_reconciled_at=None if authority.last_reconciled_at is None else authority.last_reconciled_at.isoformat(),
            context_json=_build_reconcile_context(parent_version, collection, [], blocking_reasons),
        )


def inspect_parent_reconcile_for_version(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    node_version_id: UUID,
) -> ParentReconcileSnapshot:
    with query_session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, node_version_id=node_version_id)
        child_edges = _load_child_edges(session, parent_version.id)
        children = _build_child_results(session, child_edges, resolve_authoritative=False)
        collection = _collection_snapshot(parent_node.node_id, parent_version.id, authority, children)
        blocking_reasons = _reconcile_blockers(parent_version, children, session=session)
        prompt = resources.load_text(RECONCILE_PROMPT_GROUP, RECONCILE_PROMPT_PATH)
        return ParentReconcileSnapshot(
            parent_node_id=parent_node.node_id,
            parent_node_version_id=parent_version.id,
            status="ready_for_reconcile" if not blocking_reasons else "blocked",
            seed_commit_sha=parent_version.seed_commit_sha,
            prompt_relative_path=RECONCILE_PROMPT_PATH,
            prompt_text=prompt.content,
            child_results=collection,
            blocking_reasons=blocking_reasons,
            merge_events=[],
            last_reconciled_at=None if authority.last_reconciled_at is None else authority.last_reconciled_at.isoformat(),
            context_json=_build_reconcile_context(parent_version, collection, [], blocking_reasons),
        )


def execute_child_merge_pipeline(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
) -> ParentReconcileSnapshot:
    prompt = resources.load_text(RECONCILE_PROMPT_GROUP, RECONCILE_PROMPT_PATH)
    with session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, logical_node_id=logical_node_id)
        return _execute_child_merge_pipeline_for_bundle(
            session,
            parent_node=parent_node,
            parent_version=parent_version,
            authority=authority,
            prompt_text=prompt.content,
            resolve_authoritative=True,
        )


def execute_child_merge_pipeline_for_version(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    node_version_id: UUID,
) -> ParentReconcileSnapshot:
    prompt = resources.load_text(RECONCILE_PROMPT_GROUP, RECONCILE_PROMPT_PATH)
    with session_scope(session_factory) as session:
        parent_node, parent_version, authority = _parent_bundle(session, node_version_id=node_version_id)
        return _execute_child_merge_pipeline_for_bundle(
            session,
            parent_node=parent_node,
            parent_version=parent_version,
            authority=authority,
            prompt_text=prompt.content,
            resolve_authoritative=False,
        )


def _execute_child_merge_pipeline_for_bundle(
    session: Session,
    *,
    parent_node: HierarchyNode,
    parent_version: NodeVersion,
    authority: ParentChildAuthority,
    prompt_text: str,
    resolve_authoritative: bool = False,
) -> ParentReconcileSnapshot:
    child_edges = _load_child_edges(session, parent_version.id)
    children = _build_child_results(session, child_edges, resolve_authoritative=resolve_authoritative)
    collection = _collection_snapshot(parent_node.node_id, parent_version.id, authority, children)
    blocking_reasons = _reconcile_blockers(parent_version, children, session=session)
    if blocking_reasons:
        raise DaemonConflictError("; ".join(blocking_reasons))
    mergeable_children = [item for item in children if item.merge_order is not None]
    ordered_children = sorted(mergeable_children, key=lambda item: int(item.merge_order or 0))

    parent_commit_before = parent_version.seed_commit_sha
    merge_events: list[MergeEventSnapshot] = []
    for child in ordered_children:
        child_final_commit_sha = child.final_commit_sha
        if parent_commit_before is None or child_final_commit_sha is None:
            raise DaemonConflictError("merge pipeline requires recorded parent seed and child final commits")
        parent_commit_after = sha256(
            f"{parent_version.id}:{parent_commit_before}:{child_final_commit_sha}:{child.merge_order}".encode("utf-8")
        ).hexdigest()
        merge_events.append(
            record_merge_event_in_session(
                session,
                parent_node_version_id=parent_version.id,
                child_node_version_id=child.child_node_version_id,
                child_final_commit_sha=child_final_commit_sha,
                parent_commit_before=parent_commit_before,
                parent_commit_after=parent_commit_after,
                merge_order=int(child.merge_order),
                had_conflict=False,
            )
        )
        parent_commit_before = parent_commit_after

    authority.last_reconciled_at = datetime.now(timezone.utc)
    _persist_reconcile_context(
        session,
        logical_node_id=parent_node.node_id,
        parent_version_id=parent_version.id,
        context_json=_build_reconcile_context(parent_version, collection, merge_events, []),
    )
    session.flush()
    return ParentReconcileSnapshot(
        parent_node_id=parent_node.node_id,
        parent_node_version_id=parent_version.id,
        status="merged",
        seed_commit_sha=parent_version.seed_commit_sha,
        prompt_relative_path=RECONCILE_PROMPT_PATH,
        prompt_text=prompt_text,
        child_results=collection,
        blocking_reasons=[],
        merge_events=merge_events,
        last_reconciled_at=authority.last_reconciled_at.isoformat(),
        context_json=_build_reconcile_context(parent_version, collection, merge_events, []),
    )


def _parent_bundle(
    session: Session,
    *,
    logical_node_id: UUID | None = None,
    node_version_id: UUID | None = None,
) -> tuple[HierarchyNode, NodeVersion, ParentChildAuthority]:
    if logical_node_id is None and node_version_id is None:
        raise DaemonConflictError("parent bundle requires logical node id or node version id")
    if node_version_id is not None:
        parent_version = session.get(NodeVersion, node_version_id)
        if parent_version is None:
            raise DaemonNotFoundError("parent node version not found")
        parent_node = session.get(HierarchyNode, parent_version.logical_node_id)
        if parent_node is None:
            raise DaemonNotFoundError("parent node not found")
    else:
        assert logical_node_id is not None
        parent_node = session.get(HierarchyNode, logical_node_id)
        if parent_node is None:
            raise DaemonNotFoundError("parent node not found")
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("parent node version selector not found")
        parent_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        if parent_version is None:
            raise DaemonNotFoundError("parent node version not found")
    authority = session.get(ParentChildAuthority, parent_version.id)
    if authority is None:
        authority = ParentChildAuthority(parent_node_version_id=parent_version.id, authority_mode="manual")
        session.add(authority)
        session.flush()
    return parent_node, parent_version, authority


def _load_child_edges(session: Session, parent_version_id: UUID) -> list[NodeChild]:
    return session.execute(
        select(NodeChild).where(NodeChild.parent_node_version_id == parent_version_id).order_by(NodeChild.ordinal, NodeChild.created_at)
    ).scalars().all()


def _build_child_results(
    session: Session,
    child_edges: list[NodeChild],
    *,
    resolve_authoritative: bool,
) -> list[ChildResultSnapshot]:
    provisional: list[dict[str, object]] = []
    node_id_by_version_id: dict[UUID, UUID] = {}
    edge_by_child_node_id: dict[UUID, NodeChild] = {}
    for edge in child_edges:
        edge_version = session.get(NodeVersion, edge.child_node_version_id)
        if edge_version is None:
            raise DaemonNotFoundError("child node version not found")
        edge_by_child_node_id[edge_version.logical_node_id] = edge
        selector = session.get(LogicalNodeCurrentVersion, edge_version.logical_node_id)
        if resolve_authoritative and selector is None:
            provisional.append(
                {
                    "layout_child_id": edge.layout_child_id,
                    "child_node_id": edge_version.logical_node_id,
                    "child_node_version_id": edge.child_node_version_id,
                    "edge_child_node_version_id": edge.child_node_version_id,
                    "origin_type": edge.origin_type,
                    "ordinal": edge.ordinal,
                    "child_kind": edge_version.node_kind,
                    "child_title": edge_version.title,
                    "lifecycle_state": None,
                    "run_status": None,
                    "final_commit_sha": None,
                    "latest_summary": None,
                    "latest_child_session_summary": None,
                    "reconcile_status": "invalid_authority",
                    "dependency_child_node_ids": [],
                    "blocking_reasons": ["authoritative child version selector missing"],
                }
            )
            continue
        if resolve_authoritative:
            assert selector is not None
            version = session.get(NodeVersion, selector.authoritative_node_version_id)
            if version is None:
                raise DaemonNotFoundError("authoritative child node version not found")
        else:
            version = edge_version
        node = session.get(HierarchyNode, version.logical_node_id)
        lifecycle = session.get(NodeLifecycleState, str(version.logical_node_id)) if resolve_authoritative else None
        latest_run = (
            session.execute(
                select(NodeRun).where(NodeRun.node_version_id == version.id).order_by(NodeRun.run_number.desc())
            ).scalars().first()
            if resolve_authoritative
            else None
        )
        latest_summary = (
            session.execute(
                select(SubtaskAttempt.summary)
                .join(NodeRun, NodeRun.id == SubtaskAttempt.node_run_id)
                .where(
                    NodeRun.node_version_id == version.id,
                    SubtaskAttempt.summary.is_not(None),
                )
                .order_by(SubtaskAttempt.created_at.desc())
            ).scalar()
            if resolve_authoritative
            else None
        )
        dependency_child_node_ids = _dependency_child_node_ids(session, version.id, edge_by_child_node_id)
        blocking_reasons = _classify_blocking_reasons(version, lifecycle, latest_run)
        reconcile_status = _classify_reconcile_status(
            version=version,
            edge=edge,
            lifecycle=lifecycle,
            latest_run=latest_run,
            blocking_reasons=blocking_reasons,
        )
        node_id_by_version_id[version.id] = version.logical_node_id
        provisional.append(
            {
                "layout_child_id": edge.layout_child_id,
                "child_node_id": version.logical_node_id,
                "child_node_version_id": version.id,
                "edge_child_node_version_id": edge.child_node_version_id,
                "origin_type": edge.origin_type,
                "ordinal": edge.ordinal,
                "child_kind": version.node_kind,
                "child_title": version.title if node is None else node.title,
                "lifecycle_state": None if lifecycle is None else lifecycle.lifecycle_state,
                "run_status": None if latest_run is None else latest_run.run_status,
                "final_commit_sha": version.final_commit_sha,
                "latest_summary": latest_summary,
                "latest_child_session_summary": _latest_child_session_summary(session, version.id),
                "reconcile_status": reconcile_status,
                "dependency_child_node_ids": dependency_child_node_ids,
                "blocking_reasons": blocking_reasons,
                "created_at": edge.created_at,
            }
        )

    merge_orders = _calculate_merge_orders(provisional)
    snapshots: list[ChildResultSnapshot] = []
    for item in provisional:
        child_node_id = item["child_node_id"]
        snapshots.append(
            ChildResultSnapshot(
                layout_child_id=str(item["layout_child_id"]),
                child_node_id=child_node_id,
                child_node_version_id=item["child_node_version_id"],
                edge_child_node_version_id=item["edge_child_node_version_id"],
                origin_type=str(item["origin_type"]),
                ordinal=item["ordinal"],
                child_kind=str(item["child_kind"]),
                child_title=str(item["child_title"]),
                lifecycle_state=item["lifecycle_state"],
                run_status=item["run_status"],
                final_commit_sha=item["final_commit_sha"],
                latest_summary=item["latest_summary"],
                latest_child_session_summary=item["latest_child_session_summary"],
                reconcile_status=str(item["reconcile_status"]),
                merge_order=merge_orders.get(child_node_id),
                dependency_child_node_ids=list(item["dependency_child_node_ids"]),
                blocking_reasons=list(item["blocking_reasons"]),
            )
        )
    return sorted(snapshots, key=lambda item: (item.merge_order is None, item.merge_order or 0, item.ordinal or 0, item.child_title))


def _dependency_child_node_ids(
    session: Session,
    child_node_version_id: UUID,
    edge_by_child_node_id: dict[UUID, NodeChild],
) -> list[UUID]:
    dependencies = session.execute(
        select(NodeDependency).where(NodeDependency.node_version_id == child_node_version_id).order_by(NodeDependency.created_at)
    ).scalars().all()
    dependency_ids: list[UUID] = []
    for dependency in dependencies:
        target = session.get(NodeVersion, dependency.depends_on_node_version_id)
        if target is None:
            continue
        if target.logical_node_id in edge_by_child_node_id:
            dependency_ids.append(target.logical_node_id)
    return dependency_ids


def _classify_blocking_reasons(
    version: NodeVersion,
    lifecycle: NodeLifecycleState | None,
    latest_run: NodeRun | None,
) -> list[str]:
    reasons: list[str] = []
    lifecycle_state = None if lifecycle is None else lifecycle.lifecycle_state
    run_status = None if latest_run is None else latest_run.run_status
    if lifecycle_state in {"FAILED_TO_PARENT"} or run_status == "FAILED":
        reasons.append("child failed")
    if lifecycle_state in {"PAUSED_FOR_USER"} or run_status == "PAUSED":
        reasons.append("child paused")
    if version.final_commit_sha is None and lifecycle_state == "COMPLETE":
        reasons.append("child final commit missing")
    if version.final_commit_sha is not None and not reasons:
        return reasons
    if lifecycle_state not in {None, "COMPLETE"} and not (
        version.final_commit_sha is not None and lifecycle_state == "SUPERSEDED"
    ) and not reasons:
        reasons.append("child not complete")
    return reasons


def _classify_reconcile_status(
    *,
    version: NodeVersion,
    edge: NodeChild,
    lifecycle: NodeLifecycleState | None,
    latest_run: NodeRun | None,
    blocking_reasons: list[str],
) -> str:
    if blocking_reasons:
        lifecycle_state = None if lifecycle is None else lifecycle.lifecycle_state
        if "child failed" in blocking_reasons:
            return "failed"
        if "child paused" in blocking_reasons:
            return "paused"
        if lifecycle_state == "COMPLETE" and version.final_commit_sha is None:
            return "invalid_authority"
        if version.id != edge.child_node_version_id and version.final_commit_sha is not None:
            return "superseded_with_authoritative_replacement"
        return "waiting"
    if version.id != edge.child_node_version_id:
        return "superseded_with_authoritative_replacement"
    return "ready_for_reconcile"


def _calculate_merge_orders(children: list[dict[str, object]]) -> dict[UUID, int]:
    eligible = [item for item in children if item["reconcile_status"] in MERGEABLE_RECONCILE_STATUSES]
    adjacency: dict[UUID, set[UUID]] = {}
    indegree: dict[UUID, int] = {}
    by_id: dict[UUID, dict[str, object]] = {}
    for item in eligible:
        child_node_id = item["child_node_id"]
        by_id[child_node_id] = item
        adjacency[child_node_id] = set()
        indegree[child_node_id] = 0
    for item in eligible:
        child_node_id = item["child_node_id"]
        for dependency_child_node_id in item["dependency_child_node_ids"]:
            if dependency_child_node_id not in adjacency:
                continue
            adjacency[dependency_child_node_id].add(child_node_id)
            indegree[child_node_id] += 1
    ordered: list[UUID] = []
    ready = [node_id for node_id, degree in indegree.items() if degree == 0]
    while ready:
        ready.sort(key=lambda node_id: _merge_order_sort_key(by_id[node_id]))
        current = ready.pop(0)
        ordered.append(current)
        for follower in sorted(adjacency[current], key=lambda node_id: _merge_order_sort_key(by_id[node_id])):
            indegree[follower] -= 1
            if indegree[follower] == 0:
                ready.append(follower)
    if len(ordered) != len(eligible):
        raise DaemonConflictError("child dependency graph for reconciliation is cyclic")
    return {node_id: index + 1 for index, node_id in enumerate(ordered)}


def _merge_order_sort_key(item: dict[str, object]) -> tuple[int, datetime, str]:
    ordinal = item["ordinal"]
    created_at = item["created_at"]
    child_node_id = item["child_node_id"]
    return (1_000_000 if ordinal is None else int(ordinal), created_at, str(child_node_id))


def _collection_snapshot(
    parent_node_id: UUID,
    parent_node_version_id: UUID,
    authority: ParentChildAuthority,
    children: list[ChildResultSnapshot],
) -> ChildResultCollectionSnapshot:
    ready_count = sum(1 for item in children if item.reconcile_status in MERGEABLE_RECONCILE_STATUSES)
    waiting_count = sum(1 for item in children if item.reconcile_status == "waiting")
    failed_count = sum(1 for item in children if item.reconcile_status == "failed")
    paused_count = sum(1 for item in children if item.reconcile_status == "paused")
    invalid_count = sum(1 for item in children if item.reconcile_status == "invalid_authority")
    status = "ready_for_reconcile" if children and (ready_count == len(children)) else "blocked"
    return ChildResultCollectionSnapshot(
        parent_node_id=parent_node_id,
        parent_node_version_id=parent_node_version_id,
        authority_mode=authority.authority_mode,
        status=status,
        ready_child_count=ready_count,
        waiting_child_count=waiting_count,
        failed_child_count=failed_count,
        paused_child_count=paused_count,
        invalid_child_count=invalid_count,
        reusable_final_count=sum(1 for item in children if item.final_commit_sha),
        children=children,
    )


def _reconcile_blockers(
    parent_version: NodeVersion,
    children: list[ChildResultSnapshot],
    *,
    session: Session,
) -> list[str]:
    blockers: list[str] = []
    if not children:
        blockers.append("parent has no authoritative children to reconcile")
    if parent_version.seed_commit_sha is None:
        blockers.append("parent seed commit is not recorded")
    if has_unresolved_merge_conflicts(session, node_version_id=parent_version.id):
        blockers.append("parent has unresolved merge conflicts")
    for child in children:
        if child.reconcile_status not in MERGEABLE_RECONCILE_STATUSES:
            blockers.append(f"child {child.layout_child_id} is {child.reconcile_status}")
    return blockers


def _build_reconcile_context(
    parent_version: NodeVersion,
    child_results: ChildResultCollectionSnapshot,
    merge_events: list[MergeEventSnapshot],
    blocking_reasons: list[str],
) -> dict[str, object]:
    return {
        "parent_node_version_id": str(parent_version.id),
        "seed_commit_sha": parent_version.seed_commit_sha,
        "final_commit_sha": parent_version.final_commit_sha,
        "status": "ready_for_reconcile" if not blocking_reasons else "blocked",
        "blocking_reasons": blocking_reasons,
        "child_results": child_results.to_payload(),
        "merge_events": [item.to_payload() for item in merge_events],
        "reconcile_prompt_relative_path": RECONCILE_PROMPT_PATH,
    }


def _persist_reconcile_context(
    session: Session,
    *,
    logical_node_id: UUID,
    parent_version_id: UUID,
    context_json: dict[str, object],
) -> None:
    active_run = session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == parent_version_id, NodeRun.run_status.in_(ACTIVE_RUN_STATUSES))
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if active_run is None:
        return
    state = session.get(NodeRunState, active_run.id)
    if state is None:
        return
    cursor = dict(state.execution_cursor_json or {})
    cursor["parent_reconcile_context"] = context_json
    state.execution_cursor_json = cursor
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is not None:
        lifecycle.execution_cursor_json = dict(cursor)


def _latest_child_session_summary(session: Session, node_version_id: UUID) -> str | None:
    row = session.execute(
        select(ChildSessionResult.result_json)
        .join(DaemonSession, DaemonSession.id == ChildSessionResult.child_session_id)
        .where(DaemonSession.node_version_id == node_version_id)
        .order_by(ChildSessionResult.created_at.desc())
    ).first()
    if row is None:
        return None
    payload = dict(row[0])
    summary = payload.get("summary")
    return None if summary is None else str(summary)
