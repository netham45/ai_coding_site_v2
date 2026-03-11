from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.admission import check_node_dependency_readiness
from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.daemon.workflow_events import list_workflow_events_for_node
from aicoding.db.models import (
    DaemonMutationEvent,
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeDependencyBlocker,
    NodeLifecycleState,
    NodeVersion,
)
from aicoding.db.session import query_session_scope


@dataclass(frozen=True, slots=True)
class NodeOperatorSummarySnapshot:
    node_id: UUID
    parent_node_id: UUID | None
    kind: str
    tier: str
    title: str
    prompt: str
    created_via: str
    lifecycle_state: str | None
    run_status: str | None
    current_run_id: UUID | None
    current_subtask_id: str | None
    current_subtask_attempt: int | None
    pause_flag_name: str | None
    is_resumable: bool | None
    authoritative_node_version_id: UUID | None
    latest_created_node_version_id: UUID | None
    compiled_workflow_id: UUID | None
    active_branch_name: str | None
    seed_commit_sha: str | None
    final_commit_sha: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "parent_node_id": None if self.parent_node_id is None else str(self.parent_node_id),
            "kind": self.kind,
            "tier": self.tier,
            "title": self.title,
            "prompt": self.prompt,
            "created_via": self.created_via,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "current_run_id": None if self.current_run_id is None else str(self.current_run_id),
            "current_subtask_id": self.current_subtask_id,
            "current_subtask_attempt": self.current_subtask_attempt,
            "pause_flag_name": self.pause_flag_name,
            "is_resumable": self.is_resumable,
            "authoritative_node_version_id": None if self.authoritative_node_version_id is None else str(self.authoritative_node_version_id),
            "latest_created_node_version_id": None if self.latest_created_node_version_id is None else str(self.latest_created_node_version_id),
            "compiled_workflow_id": None if self.compiled_workflow_id is None else str(self.compiled_workflow_id),
            "active_branch_name": self.active_branch_name,
            "seed_commit_sha": self.seed_commit_sha,
            "final_commit_sha": self.final_commit_sha,
        }


@dataclass(frozen=True, slots=True)
class TreeNodeSnapshot:
    node_id: UUID
    parent_node_id: UUID | None
    depth: int
    kind: str
    tier: str
    title: str
    authoritative_node_version_id: UUID | None
    latest_created_node_version_id: UUID | None
    lifecycle_state: str | None
    run_status: str | None
    scheduling_status: str | None = None
    blocker_count: int = 0
    blocker_state: str = "none"
    has_children: bool = False
    child_count: int = 0
    child_rollups: dict[str, int] | None = None
    created_at: str = ""
    last_updated_at: str = ""

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "parent_node_id": None if self.parent_node_id is None else str(self.parent_node_id),
            "depth": self.depth,
            "kind": self.kind,
            "tier": self.tier,
            "title": self.title,
            "authoritative_node_version_id": None if self.authoritative_node_version_id is None else str(self.authoritative_node_version_id),
            "latest_created_node_version_id": None if self.latest_created_node_version_id is None else str(self.latest_created_node_version_id),
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "scheduling_status": self.scheduling_status,
            "blocker_count": self.blocker_count,
            "blocker_state": self.blocker_state,
            "has_children": self.has_children,
            "child_count": self.child_count,
            "child_rollups": {} if self.child_rollups is None else dict(self.child_rollups),
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at,
        }


@dataclass(frozen=True, slots=True)
class TreeCatalogSnapshot:
    root_node_id: UUID
    generated_at: str
    nodes: list[TreeNodeSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "root_node_id": str(self.root_node_id),
            "generated_at": self.generated_at,
            "nodes": [item.to_payload() for item in self.nodes],
        }


@dataclass(frozen=True, slots=True)
class PauseStateSnapshot:
    node_id: UUID
    lifecycle_state: str
    run_status: str | None
    current_run_id: UUID | None
    pause_flag_name: str | None
    is_resumable: bool
    pause_summary: str | None
    approval_required: bool
    approved: bool
    pause_summary_prompt: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "current_run_id": None if self.current_run_id is None else str(self.current_run_id),
            "pause_flag_name": self.pause_flag_name,
            "is_resumable": self.is_resumable,
            "pause_summary": self.pause_summary,
            "approval_required": self.approval_required,
            "approved": self.approved,
            "pause_summary_prompt": self.pause_summary_prompt,
        }


@dataclass(frozen=True, slots=True)
class NodeEventSnapshot:
    id: UUID
    node_id: str
    command: str
    event_scope: str
    previous_state: str | None
    resulting_state: str
    run_id: UUID | None
    payload_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_id": self.node_id,
            "command": self.command,
            "event_scope": self.event_scope,
            "previous_state": self.previous_state,
            "resulting_state": self.resulting_state,
            "run_id": None if self.run_id is None else str(self.run_id),
            "payload_json": self.payload_json,
            "created_at": self.created_at,
        }


def load_node_operator_summary(session_factory: sessionmaker[Session], *, node_id: UUID) -> NodeOperatorSummarySnapshot:
    with query_session_scope(session_factory) as session:
        node = session.get(HierarchyNode, node_id)
        if node is None:
            raise DaemonNotFoundError("node not found")
        lifecycle = session.get(NodeLifecycleState, str(node_id))
        selector = session.get(LogicalNodeCurrentVersion, node_id)
        version = None if selector is None else session.get(NodeVersion, selector.authoritative_node_version_id)
        return NodeOperatorSummarySnapshot(
            node_id=node.node_id,
            parent_node_id=node.parent_node_id,
            kind=node.kind,
            tier=node.tier,
            title=node.title,
            prompt=node.prompt,
            created_via=node.created_via,
            lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
            run_status=None if lifecycle is None else lifecycle.run_status,
            current_run_id=None if lifecycle is None else lifecycle.current_run_id,
            current_subtask_id=None if lifecycle is None else lifecycle.current_subtask_id,
            current_subtask_attempt=None if lifecycle is None else lifecycle.current_subtask_attempt,
            pause_flag_name=None if lifecycle is None else lifecycle.pause_flag_name,
            is_resumable=None if lifecycle is None else lifecycle.is_resumable,
            authoritative_node_version_id=None if selector is None else selector.authoritative_node_version_id,
            latest_created_node_version_id=None if selector is None else selector.latest_created_node_version_id,
            compiled_workflow_id=None if version is None else version.compiled_workflow_id,
            active_branch_name=None if version is None else version.active_branch_name,
            seed_commit_sha=None if version is None else version.seed_commit_sha,
            final_commit_sha=None if version is None else version.final_commit_sha,
        )


def load_tree_catalog(session_factory: sessionmaker[Session], *, root_node_id: UUID) -> TreeCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        root = session.get(HierarchyNode, root_node_id)
        if root is None:
            raise DaemonNotFoundError("node not found")
        rows = session.execute(select(HierarchyNode).order_by(HierarchyNode.created_at)).scalars().all()
        lifecycle_by_node_id = {
            item.node_id: item
            for item in session.execute(select(NodeLifecycleState).where(NodeLifecycleState.node_id.in_([str(row.node_id) for row in rows]))).scalars().all()
        }
        selectors = session.execute(
            select(LogicalNodeCurrentVersion).where(LogicalNodeCurrentVersion.logical_node_id.in_([row.node_id for row in rows]))
        ).scalars().all()
        selector_by_node_id = {item.logical_node_id: item for item in selectors}
        version_by_node_id = {item.logical_node_id: item.authoritative_node_version_id for item in selectors}
        version_ids = list({version_id for version_id in version_by_node_id.values()})
        version_by_id = {
            item.id: item
            for item in session.execute(select(NodeVersion).where(NodeVersion.id.in_(version_ids))).scalars().all()
        }
        blocker_rows = session.execute(
            select(NodeDependencyBlocker).where(NodeDependencyBlocker.node_version_id.in_(list(version_by_node_id.values())))
        ).scalars().all()
        blockers_by_version_id: dict[UUID, list[NodeDependencyBlocker]] = {}
        for row in blocker_rows:
            blockers_by_version_id.setdefault(row.node_version_id, []).append(row)
        children_by_parent: dict[UUID | None, list[HierarchyNode]] = {}
        for row in rows:
            children_by_parent.setdefault(row.parent_node_id, []).append(row)
        ordered: list[TreeNodeSnapshot] = []

        def visit(node: HierarchyNode, depth: int) -> None:
            lifecycle = lifecycle_by_node_id.get(str(node.node_id))
            selector = selector_by_node_id.get(node.node_id)
            version = None if selector is None else version_by_id.get(selector.authoritative_node_version_id)
            child_nodes = children_by_parent.get(node.node_id, [])
            blocker_count = len(blockers_by_version_id.get(version_by_node_id.get(node.node_id), []))
            ordered.append(
                TreeNodeSnapshot(
                    node_id=node.node_id,
                    parent_node_id=node.parent_node_id,
                    depth=depth,
                    kind=node.kind,
                    tier=node.tier,
                    title=node.title,
                    authoritative_node_version_id=None if selector is None else selector.authoritative_node_version_id,
                    latest_created_node_version_id=None if selector is None else selector.latest_created_node_version_id,
                    lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
                    run_status=None if lifecycle is None else lifecycle.run_status,
                    scheduling_status=_tree_scheduling_status(
                        lifecycle,
                        blocker_count=blocker_count,
                    ),
                    blocker_count=blocker_count,
                    blocker_state=_tree_blocker_state(lifecycle, blocker_count=blocker_count),
                    has_children=bool(child_nodes),
                    child_count=len(child_nodes),
                    child_rollups=_tree_child_rollups(children=child_nodes, lifecycle_by_node_id=lifecycle_by_node_id, blockers_by_version_id=blockers_by_version_id, version_by_node_id=version_by_node_id),
                    created_at=node.created_at.isoformat(),
                    last_updated_at=_tree_last_updated_at(node=node, lifecycle=lifecycle, selector=selector, version=version),
                )
            )
            for child in child_nodes:
                visit(child, depth + 1)

        visit(root, 0)
        return TreeCatalogSnapshot(root_node_id=root_node_id, generated_at=datetime.now(timezone.utc).isoformat(), nodes=ordered)


def _tree_scheduling_status(lifecycle: NodeLifecycleState | None, *, blocker_count: int) -> str | None:
    if lifecycle is None:
        return None
    if lifecycle.lifecycle_state == "COMPLETE":
        return "complete"
    if lifecycle.lifecycle_state == "SUPERSEDED":
        return "superseded"
    if lifecycle.lifecycle_state == "FAILED_TO_PARENT":
        return "failed"
    if lifecycle.run_status in {"PENDING", "RUNNING"}:
        return "already_running"
    if lifecycle.run_status == "PAUSED" or lifecycle.pause_flag_name is not None:
        return "paused_for_user"
    if blocker_count > 0:
        return "blocked"
    if lifecycle.lifecycle_state == "READY":
        return "ready"
    return "not_compiled"


def _tree_blocker_state(lifecycle: NodeLifecycleState | None, *, blocker_count: int) -> str:
    if lifecycle is not None and (lifecycle.run_status == "PAUSED" or lifecycle.pause_flag_name is not None):
        return "paused_for_user"
    if blocker_count > 0:
        return "blocked"
    return "none"


def _tree_child_rollups(
    *,
    children: list[HierarchyNode],
    lifecycle_by_node_id: dict[str, NodeLifecycleState],
    blockers_by_version_id: dict[UUID, list[NodeDependencyBlocker]],
    version_by_node_id: dict[UUID, UUID],
) -> dict[str, int]:
    buckets = {
        "total": len(children),
        "ready": 0,
        "running": 0,
        "paused_for_user": 0,
        "blocked": 0,
        "failed": 0,
        "complete": 0,
        "superseded": 0,
        "not_compiled": 0,
    }
    for child in children:
        lifecycle = lifecycle_by_node_id.get(str(child.node_id))
        blocker_count = len(blockers_by_version_id.get(version_by_node_id.get(child.node_id), []))
        status = _tree_scheduling_status(lifecycle, blocker_count=blocker_count) or "not_compiled"
        if status in buckets:
            buckets[status] += 1
        else:
            buckets["not_compiled"] += 1
    return buckets


def _tree_last_updated_at(
    *,
    node: HierarchyNode,
    lifecycle: NodeLifecycleState | None,
    selector: LogicalNodeCurrentVersion | None,
    version: NodeVersion | None,
) -> str:
    candidates = [node.created_at]
    if lifecycle is not None:
        candidates.extend([lifecycle.created_at, lifecycle.updated_at])
    if selector is not None:
        candidates.append(selector.updated_at)
    if version is not None:
        candidates.extend([version.created_at, version.updated_at])
    return max(candidates).isoformat()


def list_sibling_nodes(session_factory: sessionmaker[Session], *, node_id: UUID) -> list[NodeOperatorSummarySnapshot]:
    with query_session_scope(session_factory) as session:
        node = session.get(HierarchyNode, node_id)
        if node is None:
            raise DaemonNotFoundError("node not found")
        rows = session.execute(
            select(HierarchyNode).where(
                HierarchyNode.parent_node_id == node.parent_node_id,
                HierarchyNode.node_id != node_id,
            ).order_by(HierarchyNode.created_at)
        ).scalars().all()
        lifecycle_by_node_id = {
            item.node_id: item
            for item in session.execute(select(NodeLifecycleState).where(NodeLifecycleState.node_id.in_([str(row.node_id) for row in rows]))).scalars().all()
        }
        selector_by_node_id = {
            item.logical_node_id: item
            for item in session.execute(
                select(LogicalNodeCurrentVersion).where(LogicalNodeCurrentVersion.logical_node_id.in_([row.node_id for row in rows]))
            ).scalars().all()
        }
        version_ids = [item.authoritative_node_version_id for item in selector_by_node_id.values()]
        version_by_id = {
            item.id: item
            for item in session.execute(select(NodeVersion).where(NodeVersion.id.in_(version_ids))).scalars().all()
        }
        snapshots: list[NodeOperatorSummarySnapshot] = []
        for row in rows:
            lifecycle = lifecycle_by_node_id.get(str(row.node_id))
            selector = selector_by_node_id.get(row.node_id)
            version = None if selector is None else version_by_id.get(selector.authoritative_node_version_id)
            snapshots.append(
                NodeOperatorSummarySnapshot(
                    node_id=row.node_id,
                    parent_node_id=row.parent_node_id,
                    kind=row.kind,
                    tier=row.tier,
                    title=row.title,
                    prompt=row.prompt,
                    created_via=row.created_via,
                    lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
                    run_status=None if lifecycle is None else lifecycle.run_status,
                    current_run_id=None if lifecycle is None else lifecycle.current_run_id,
                    current_subtask_id=None if lifecycle is None else lifecycle.current_subtask_id,
                    current_subtask_attempt=None if lifecycle is None else lifecycle.current_subtask_attempt,
                    pause_flag_name=None if lifecycle is None else lifecycle.pause_flag_name,
                    is_resumable=None if lifecycle is None else lifecycle.is_resumable,
                    authoritative_node_version_id=None if selector is None else selector.authoritative_node_version_id,
                    latest_created_node_version_id=None if selector is None else selector.latest_created_node_version_id,
                    compiled_workflow_id=None if version is None else version.compiled_workflow_id,
                    active_branch_name=None if version is None else version.active_branch_name,
                    seed_commit_sha=None if version is None else version.seed_commit_sha,
                    final_commit_sha=None if version is None else version.final_commit_sha,
                )
            )
        return snapshots


def load_pause_state(session_factory: sessionmaker[Session], *, node_id: UUID) -> PauseStateSnapshot:
    with query_session_scope(session_factory) as session:
        lifecycle = session.get(NodeLifecycleState, str(node_id))
        if lifecycle is None:
            raise DaemonNotFoundError("node lifecycle record not found")
        return PauseStateSnapshot(
            node_id=node_id,
            lifecycle_state=lifecycle.lifecycle_state,
            run_status=lifecycle.run_status,
            current_run_id=lifecycle.current_run_id,
            pause_flag_name=lifecycle.pause_flag_name,
            is_resumable=lifecycle.is_resumable,
            pause_summary=None if not lifecycle.execution_cursor_json else dict(lifecycle.execution_cursor_json.get("pause_context", {})).get("pause_summary"),
            approval_required=bool(dict(lifecycle.execution_cursor_json or {}).get("pause_context", {}).get("approval_required", False)),
            approved=bool(dict(lifecycle.execution_cursor_json or {}).get("pause_context", {}).get("approved", False)),
            pause_summary_prompt=None if not lifecycle.execution_cursor_json else dict(lifecycle.execution_cursor_json.get("pause_context", {})).get("pause_summary_prompt"),
        )


def list_node_events(session_factory: sessionmaker[Session], *, node_id: UUID) -> list[NodeEventSnapshot]:
    workflow_events = list_workflow_events_for_node(session_factory, logical_node_id=node_id)
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(DaemonMutationEvent).where(DaemonMutationEvent.node_id == str(node_id)).order_by(DaemonMutationEvent.created_at)
        ).scalars().all()
        snapshots = [
            NodeEventSnapshot(
                id=row.id,
                node_id=row.node_id,
                command=row.command,
                event_scope="authority",
                previous_state=row.previous_state,
                resulting_state=row.resulting_state,
                run_id=row.run_id,
                payload_json=dict(row.payload_json),
                created_at=row.created_at.isoformat(),
            )
            for row in rows
        ]
    snapshots.extend(
        NodeEventSnapshot(
            id=item.id,
            node_id=str(item.logical_node_id),
            command=item.event_type,
            event_scope=item.event_scope,
            previous_state=None,
            resulting_state="PAUSED_FOR_USER" if item.event_scope == "pause" and item.event_type == "pause_entered" else "RUNNING" if item.event_type == "pause_resumed" else None,
            run_id=item.node_run_id,
            payload_json=item.payload_json,
            created_at=item.created_at,
        )
        for item in workflow_events
    )
    return sorted(snapshots, key=lambda item: item.created_at)


def load_node_dependency_snapshot(session_factory: sessionmaker[Session], *, node_id: UUID) -> dict[str, object]:
    return check_node_dependency_readiness(session_factory, node_id=node_id).to_payload()
