from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from pathlib import Path

from aicoding.daemon.child_reconcile import execute_child_merge_pipeline_for_version, inspect_parent_reconcile_for_version
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.lifecycle import bind_node_lifecycle_version, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import (
    bootstrap_live_git_repo,
    execute_live_merge_children_for_version,
    finalize_live_git_state_for_version,
)
from aicoding.daemon.rebuild_coordination import (
    cancel_rebuild_coordination_blockers,
    inspect_rebuild_coordination,
    record_rebuild_coordination_event,
)
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


@dataclass(frozen=True, slots=True)
class DependencyAwareScopeClassification:
    invalidated_versions: list[NodeVersion]
    reused_versions: list[NodeVersion]

    @property
    def invalidated_logical_node_ids(self) -> list[UUID]:
        return [item.logical_node_id for item in self.invalidated_versions]

    @property
    def reused_logical_node_ids(self) -> list[UUID]:
        return [item.logical_node_id for item in self.reused_versions]


def regenerate_node_and_descendants(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    trigger_reason: str = "manual_regenerate",
    catalog: ResourceCatalog | None = None,
    cancel_conflicting_live_state: bool = False,
) -> RegenerationSnapshot:
    resources = catalog or load_resource_catalog()
    coordination = inspect_rebuild_coordination(session_factory, logical_node_id=logical_node_id, scope="subtree")
    if coordination.status != "clear" and cancel_conflicting_live_state:
        cancellation = cancel_rebuild_coordination_blockers(
            session_factory,
            logical_node_id=logical_node_id,
            scope="subtree",
            summary=f"Cancelled for {trigger_reason} subtree regeneration.",
        )
        record_rebuild_coordination_event(
            session_factory,
            logical_node_id=logical_node_id,
            target_node_version_id=_load_authoritative_version_id(session_factory, logical_node_id),
            event_kind="live_conflict_cancelled",
            event_status="cancelled",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json=cancellation.to_payload(),
        )
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
        subtree_order, scope_classification = _collect_regeneration_scope_authoritative_versions(
            session,
            root_logical_node_id=logical_node_id,
        )
        invalidated_dependents = scope_classification.invalidated_versions
        candidate_by_logical: dict[UUID, NodeVersion] = {}

        for source_version in subtree_order:
            candidate = _ensure_candidate(session, source_version)
            candidate_by_logical[source_version.logical_node_id] = candidate
        for source_version in invalidated_dependents:
            candidate = _ensure_candidate(session, source_version, clone_structure=False)
            candidate_by_logical[source_version.logical_node_id] = candidate

        for source_version in list(subtree_order) + invalidated_dependents:
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

    _record_rebuild_event(
        session_factory,
        root_logical_node_id=logical_node_id,
        root_node_version_id=root_candidate.id,
        target_node_version_id=root_candidate.id,
        event_kind="scope_classified",
        event_status="resolved",
        scope="subtree",
        trigger_reason=trigger_reason,
        details_json={
            "seed_logical_node_ids": [str(item.logical_node_id) for item in subtree_order],
            "regenerated_logical_node_ids": [str(item.logical_node_id) for item in subtree_order],
            "dependency_invalidated_logical_node_ids": [str(item) for item in scope_classification.invalidated_logical_node_ids],
            "reused_authoritative_logical_node_ids": [str(item) for item in scope_classification.reused_logical_node_ids],
        },
    )

    created_ids = [item.id for item in candidate_by_logical.values()]
    for source_version in list(subtree_order) + invalidated_dependents:
        candidate = candidate_by_logical[source_version.logical_node_id]
        details_json: dict[str, object] = {
            "supersedes_node_version_id": str(source_version.id),
            "authoritative_baseline_version_id": str(source_version.id),
            "candidate_role": "regenerated_subtree_member",
            "replay_classification": "regenerate",
        }
        if source_version.logical_node_id in {item.logical_node_id for item in invalidated_dependents}:
            details_json["fresh_dependency_restart"] = True
            details_json["candidate_role"] = "dependency_invalidated_fresh_restart"
            details_json["replay_classification"] = "blocked_pending_parent_refresh"
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_candidate.id,
            target_node_version_id=candidate.id,
            event_kind="candidate_created",
            event_status="pending",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json=details_json,
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
    for source_version in invalidated_dependents:
        _place_node_in_sibling_dependency_wait(
            session_factory,
            logical_node_id=source_version.logical_node_id,
            node_version_id=candidate_by_logical[source_version.logical_node_id].id,
        )
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_candidate.id,
            target_node_version_id=candidate_by_logical[source_version.logical_node_id].id,
            event_kind="replay_blocked",
            event_status="waiting_on_parent_refresh",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={
                "blocker_type": "candidate_replay_incomplete",
                "candidate_role": "dependency_invalidated_fresh_restart",
                "replay_classification": "blocked_pending_parent_refresh",
                "authoritative_baseline_version_id": str(source_version.id),
            },
        )

    stable_ids = _rectify_versions_bottom_up(
        session_factory,
        resources=resources,
        root_logical_node_id=logical_node_id,
        root_node_version_id=root_candidate.id,
        candidate_version_ids=[candidate_by_logical[item.logical_node_id].id for item in subtree_order],
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
    subtree_snapshot = _prepare_upstream_root_snapshot(
        session_factory,
        logical_node_id=logical_node_id,
        trigger_reason=trigger_reason,
        resources=resources,
    )

    with session_scope(session_factory) as session:
        current_child_candidate = session.get(NodeVersion, subtree_snapshot.root_node_version_id)
        if current_child_candidate is None:
            raise DaemonNotFoundError("root candidate version not found")
        current_node = session.get(HierarchyNode, logical_node_id)
        if current_node is None:
            raise DaemonNotFoundError("node not found")
        scope_candidate_map = _load_latest_candidate_scope_version_ids(
            session,
            root_logical_node_id=logical_node_id,
        )
        scope_candidate_map.setdefault(logical_node_id, subtree_snapshot.root_node_version_id)

        ancestor_candidates: list[NodeVersion] = []
        while current_node.parent_node_id is not None:
            parent_authoritative = _authoritative_version(session, current_node.parent_node_id)
            parent_candidate = _ensure_candidate(session, parent_authoritative)
            parent_candidate.parent_node_version_id = _current_candidate_parent_version_id(session, current_node.parent_node_id)
            _bind_scope_candidates_to_parent_candidate(
                session,
                parent_logical_node_id=current_node.parent_node_id,
                parent_candidate_version_id=parent_candidate.id,
                logical_to_candidate_version_id=scope_candidate_map,
            )
            _apply_candidate_remap(
                session,
                node_version_id=parent_candidate.id,
                logical_to_candidate_version_id=scope_candidate_map,
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
            scope_candidate_map[parent_authoritative.logical_node_id] = parent_candidate.id
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


def _prepare_upstream_root_snapshot(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    trigger_reason: str,
    resources: ResourceCatalog,
) -> RegenerationSnapshot:
    with query_session_scope(session_factory) as session:
        root_authoritative = _authoritative_version(session, logical_node_id)
        # If the target already has a finalized authoritative version, upstream
        # rectification should rebuild ancestors from that final instead of
        # superseding the target again.
        if root_authoritative.final_commit_sha is None:
            needs_local_rebuild = True
        else:
            node = session.get(HierarchyNode, logical_node_id)
            if node is None:
                raise DaemonNotFoundError("node not found")
            descendants = session.execute(
                select(NodeChild).where(NodeChild.parent_node_version_id == root_authoritative.id)
            ).scalars().all()
            needs_local_rebuild = len(descendants) > 0 and root_authoritative.status != "authoritative"
        if needs_local_rebuild:
            return regenerate_node_and_descendants(
                session_factory,
                logical_node_id=logical_node_id,
                trigger_reason=trigger_reason,
                catalog=resources,
            )

        subtree_order = [root_authoritative]
        scope_classification = _classify_dependency_aware_scope(
            session,
            seed_logical_node_ids={logical_node_id},
        )
        invalidated_dependents = scope_classification.invalidated_versions
        candidate_by_logical: dict[UUID, NodeVersion] = {}
        for source_version in invalidated_dependents:
            candidate = _ensure_candidate(session, source_version, clone_structure=False)
            candidate_by_logical[source_version.logical_node_id] = candidate
        for source_version in invalidated_dependents:
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

    _record_rebuild_event(
        session_factory,
        root_logical_node_id=logical_node_id,
        root_node_version_id=root_authoritative.id,
        target_node_version_id=root_authoritative.id,
        event_kind="scope_classified",
        event_status="resolved",
        scope="subtree",
        trigger_reason=trigger_reason,
        details_json={
            "seed_logical_node_ids": [str(item.logical_node_id) for item in subtree_order],
            "regenerated_logical_node_ids": [],
            "dependency_invalidated_logical_node_ids": [str(item) for item in scope_classification.invalidated_logical_node_ids],
            "reused_authoritative_logical_node_ids": [str(item) for item in scope_classification.reused_logical_node_ids],
            "root_reuse_classification": "authoritative_final_reused_for_upstream_rectify",
        },
    )

    created_ids = [item.id for item in candidate_by_logical.values()]
    for source_version in invalidated_dependents:
        candidate = candidate_by_logical[source_version.logical_node_id]
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_authoritative.id,
            target_node_version_id=candidate.id,
            event_kind="candidate_created",
            event_status="pending",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={
                "supersedes_node_version_id": str(source_version.id),
                "authoritative_baseline_version_id": str(source_version.id),
                "fresh_dependency_restart": True,
                "candidate_role": "dependency_invalidated_fresh_restart",
                "replay_classification": "blocked_pending_parent_refresh",
            },
        )
        capture_node_version_source_lineage(session_factory, node_version_id=candidate.id, catalog=resources)
        attempt = compile_node_version_workflow(session_factory, version_id=candidate.id, catalog=resources)
        if attempt.status != "compiled":
            _record_rebuild_event(
                session_factory,
                root_logical_node_id=logical_node_id,
                root_node_version_id=root_authoritative.id,
                target_node_version_id=candidate.id,
                event_kind="workflow_compiled",
                event_status="failed",
                scope="subtree",
                trigger_reason=trigger_reason,
                details_json={"compile_failure": attempt.compile_failure.to_payload() if attempt.compile_failure else {}},
            )
            raise DaemonConflictError("candidate workflow compilation failed during upstream rectification")
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_authoritative.id,
            target_node_version_id=candidate.id,
            event_kind="workflow_compiled",
            event_status="compiled",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={"compiled_workflow_id": str(attempt.compiled_workflow.id) if attempt.compiled_workflow else None},
        )
        _place_node_in_sibling_dependency_wait(
            session_factory,
            logical_node_id=source_version.logical_node_id,
            node_version_id=candidate.id,
        )
        _record_rebuild_event(
            session_factory,
            root_logical_node_id=logical_node_id,
            root_node_version_id=root_authoritative.id,
            target_node_version_id=candidate.id,
            event_kind="replay_blocked",
            event_status="waiting_on_parent_refresh",
            scope="subtree",
            trigger_reason=trigger_reason,
            details_json={
                "blocker_type": "candidate_replay_incomplete",
                "candidate_role": "dependency_invalidated_fresh_restart",
                "replay_classification": "blocked_pending_parent_refresh",
                "authoritative_baseline_version_id": str(source_version.id),
            },
        )

    history = list_rebuild_events_for_node(session_factory, logical_node_id=logical_node_id).events
    return RegenerationSnapshot(
        root_node_id=logical_node_id,
        root_node_version_id=root_authoritative.id,
        scope="subtree",
        trigger_reason=trigger_reason,
        created_candidate_version_ids=created_ids,
        stable_candidate_version_ids=[],
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


def _collect_regeneration_scope_authoritative_versions(
    session: Session,
    *,
    root_logical_node_id: UUID,
) -> tuple[list[NodeVersion], DependencyAwareScopeClassification]:
    root_authoritative = _authoritative_version(session, root_logical_node_id)
    subtree_order = _collect_subtree_authoritative_versions(session, root_authoritative.id)
    scope_classification = _classify_dependency_aware_scope(
        session,
        seed_logical_node_ids={item.logical_node_id for item in subtree_order},
    )
    return subtree_order, scope_classification


def _ensure_candidate(session: Session, source_version: NodeVersion, *, clone_structure: bool = True) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, source_version.logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    latest = session.get(NodeVersion, selector.latest_created_node_version_id)
    if latest is not None and latest.status == "candidate":
        return latest
    return create_superseding_node_version_in_session(
        session,
        logical_node_id=source_version.logical_node_id,
        clone_structure=clone_structure,
        clone_dependencies=True,
    )


def _classify_dependency_aware_scope(
    session: Session,
    *,
    seed_logical_node_ids: set[UUID],
) -> DependencyAwareScopeClassification:
    if not seed_logical_node_ids:
        return DependencyAwareScopeClassification(invalidated_versions=[], reused_versions=[])
    by_logical: dict[UUID, NodeVersion] = {}
    with_parent: dict[UUID, UUID | None] = {}
    selectors = session.execute(select(LogicalNodeCurrentVersion)).scalars().all()
    authoritative_versions = [
        session.get(NodeVersion, selector.authoritative_node_version_id)
        for selector in selectors
    ]
    valid_versions = [item for item in authoritative_versions if item is not None]
    frontier = set(seed_logical_node_ids)
    invalidated: set[UUID] = set()
    touched_parent_ids: set[UUID] = set()

    for version in valid_versions:
        by_logical[version.logical_node_id] = version
        node = session.get(HierarchyNode, version.logical_node_id)
        with_parent[version.logical_node_id] = None if node is None else node.parent_node_id

    while frontier:
        current_logical_id = frontier.pop()
        current_parent_id = with_parent.get(current_logical_id)
        if current_parent_id is None:
            continue
        touched_parent_ids.add(current_parent_id)
        for version in valid_versions:
            if version.logical_node_id in seed_logical_node_ids or version.logical_node_id in invalidated:
                continue
            if with_parent.get(version.logical_node_id) != current_parent_id:
                continue
            dependencies = session.execute(
                select(NodeDependency).where(
                    NodeDependency.node_version_id == version.id,
                    NodeDependency.dependency_type == "sibling",
                )
            ).scalars().all()
            for dependency in dependencies:
                target = session.get(NodeVersion, dependency.depends_on_node_version_id)
                if target is None:
                    continue
                if target.logical_node_id != current_logical_id:
                    continue
                invalidated.add(version.logical_node_id)
                frontier.add(version.logical_node_id)
                break

    reused = [
        version
        for version in valid_versions
        if with_parent.get(version.logical_node_id) in touched_parent_ids
        and version.logical_node_id not in seed_logical_node_ids
        and version.logical_node_id not in invalidated
    ]
    return DependencyAwareScopeClassification(
        invalidated_versions=[by_logical[item] for item in sorted(invalidated, key=lambda value: str(value))],
        reused_versions=sorted(reused, key=lambda item: str(item.logical_node_id)),
    )


def _place_node_in_sibling_dependency_wait(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    node_version_id: UUID | None = None,
) -> None:
    node_id = str(logical_node_id)
    try:
        transition_node_lifecycle(
            session_factory,
            node_id=node_id,
            target_state="WAITING_ON_SIBLING_DEPENDENCY",
        )
    except DaemonNotFoundError:
        seed_node_lifecycle(
            session_factory,
            node_id=node_id,
            initial_state="WAITING_ON_SIBLING_DEPENDENCY",
        )
    if node_version_id is not None:
        bind_node_lifecycle_version(
            session_factory,
            node_id=node_id,
            node_version_id=node_version_id,
            reset_runtime=True,
        )


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


def _load_latest_candidate_scope_version_ids(
    session: Session,
    *,
    root_logical_node_id: UUID,
) -> dict[UUID, UUID]:
    subtree_order, scope_classification = _collect_regeneration_scope_authoritative_versions(
        session,
        root_logical_node_id=root_logical_node_id,
    )
    scope_logical_ids = {item.logical_node_id for item in subtree_order}
    scope_logical_ids.update(item.logical_node_id for item in scope_classification.invalidated_versions)
    latest_candidate_by_logical: dict[UUID, UUID] = {}
    for logical_node_id in scope_logical_ids:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            continue
        latest = session.get(NodeVersion, selector.latest_created_node_version_id)
        if latest is None or latest.status != "candidate":
            continue
        latest_candidate_by_logical[logical_node_id] = latest.id
    return latest_candidate_by_logical


def _bind_scope_candidates_to_parent_candidate(
    session: Session,
    *,
    parent_logical_node_id: UUID,
    parent_candidate_version_id: UUID,
    logical_to_candidate_version_id: dict[UUID, UUID],
) -> None:
    for logical_node_id, candidate_version_id in logical_to_candidate_version_id.items():
        node = session.get(HierarchyNode, logical_node_id)
        if node is None or node.parent_node_id != parent_logical_node_id:
            continue
        candidate = session.get(NodeVersion, candidate_version_id)
        if candidate is None or candidate.status != "candidate":
            continue
        candidate.parent_node_version_id = parent_candidate_version_id


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
        try:
            live_git_final_commit = _rectify_version_with_live_git_if_possible(
                session_factory,
                resources=resources,
                version_id=version_id,
                is_leaf=is_leaf,
            )
        except DaemonConflictError as exc:
            _record_rebuild_event(
                session_factory,
                root_logical_node_id=root_logical_node_id,
                root_node_version_id=root_node_version_id,
                target_node_version_id=version_id,
                event_kind="rectified",
                event_status="blocked",
                scope=scope,
                trigger_reason=trigger_reason,
                details_json={"finalized": False, "blocking_reason": str(exc)},
            )
            continue
        if live_git_final_commit is None and not is_leaf:
            try:
                snapshot = execute_child_merge_pipeline_for_version(
                    session_factory,
                    resources,
                    node_version_id=version_id,
                )
            except DaemonConflictError as exc:
                _record_rebuild_event(
                    session_factory,
                    root_logical_node_id=root_logical_node_id,
                    root_node_version_id=root_node_version_id,
                    target_node_version_id=version_id,
                    event_kind="rectified",
                    event_status="blocked",
                    scope=scope,
                    trigger_reason=trigger_reason,
                    details_json={"finalized": False, "blocking_reason": str(exc)},
                )
                continue
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


def _rectify_version_with_live_git_if_possible(
    session_factory: sessionmaker[Session],
    *,
    resources: ResourceCatalog,
    version_id: UUID,
    is_leaf: bool,
) -> str | None:
    if not _ensure_rectified_candidate_repo(session_factory, version_id=version_id):
        return None
    if is_leaf:
        return finalize_live_git_state_for_version(session_factory, node_version_id=version_id).final_commit_sha
    reconcile_snapshot = inspect_parent_reconcile_for_version(
        session_factory,
        resources,
        node_version_id=version_id,
    )
    if reconcile_snapshot.status != "ready_for_reconcile":
        raise DaemonConflictError("; ".join(reconcile_snapshot.blocking_reasons))
    ordered_children = [
        (child.child_node_version_id, str(child.final_commit_sha), int(child.merge_order))
        for child in reconcile_snapshot.child_results.children
        if child.final_commit_sha is not None and child.merge_order is not None
    ]
    if not ordered_children:
        raise DaemonConflictError("merge pipeline requires mergeable children")
    execute_live_merge_children_for_version(
        session_factory,
        node_version_id=version_id,
        ordered_child_versions=ordered_children,
    )
    return finalize_live_git_state_for_version(session_factory, node_version_id=version_id).final_commit_sha


def _ensure_rectified_candidate_repo(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
) -> bool:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        repo_path = Path.cwd() / ".runtime" / "git" / "node_versions" / str(version.id)
        if repo_path.exists() and (repo_path / ".git").exists():
            return True
        source_version = None if version.supersedes_node_version_id is None else session.get(NodeVersion, version.supersedes_node_version_id)
        source_repo_path = None
        if source_version is not None:
            candidate_source_repo = Path.cwd() / ".runtime" / "git" / "node_versions" / str(source_version.id)
            if candidate_source_repo.exists() and (candidate_source_repo / ".git").exists():
                source_repo_path = candidate_source_repo
        base_version_id = version.parent_node_version_id
    if source_repo_path is not None:
        bootstrap_live_git_repo(
            session_factory,
            version_id=version_id,
            source_repo_path=source_repo_path,
            replace_existing=True,
        )
        return True
    if base_version_id is not None:
        base_repo_path = Path.cwd() / ".runtime" / "git" / "node_versions" / str(base_version_id)
        if base_repo_path.exists() and (base_repo_path / ".git").exists():
            bootstrap_live_git_repo(
                session_factory,
                version_id=version_id,
                base_version_id=base_version_id,
                replace_existing=True,
            )
            return True
    return False


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
