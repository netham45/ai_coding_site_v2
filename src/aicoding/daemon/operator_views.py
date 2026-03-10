from __future__ import annotations

from dataclasses import dataclass
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
    lifecycle_state: str | None
    run_status: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "parent_node_id": None if self.parent_node_id is None else str(self.parent_node_id),
            "depth": self.depth,
            "kind": self.kind,
            "tier": self.tier,
            "title": self.title,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
        }


@dataclass(frozen=True, slots=True)
class TreeCatalogSnapshot:
    root_node_id: UUID
    nodes: list[TreeNodeSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "root_node_id": str(self.root_node_id),
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
        children_by_parent: dict[UUID | None, list[HierarchyNode]] = {}
        for row in rows:
            children_by_parent.setdefault(row.parent_node_id, []).append(row)
        ordered: list[TreeNodeSnapshot] = []

        def visit(node: HierarchyNode, depth: int) -> None:
            lifecycle = lifecycle_by_node_id.get(str(node.node_id))
            ordered.append(
                TreeNodeSnapshot(
                    node_id=node.node_id,
                    parent_node_id=node.parent_node_id,
                    depth=depth,
                    kind=node.kind,
                    tier=node.tier,
                    title=node.title,
                    lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
                    run_status=None if lifecycle is None else lifecycle.run_status,
                )
            )
            for child in children_by_parent.get(node.node_id, []):
                visit(child, depth + 1)

        visit(root, 0)
        return TreeCatalogSnapshot(root_node_id=root_node_id, nodes=ordered)


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
