from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import HierarchyNode, LogicalNodeCurrentVersion, NodeChild, NodeHierarchyDefinition, NodeVersion
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import HierarchyRegistry, NodeDefinition


@dataclass(frozen=True, slots=True)
class HierarchyNodeSnapshot:
    node_id: UUID
    parent_node_id: UUID | None
    kind: str
    tier: str
    title: str
    prompt: str
    created_via: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "parent_node_id": None if self.parent_node_id is None else str(self.parent_node_id),
            "kind": self.kind,
            "tier": self.tier,
            "title": self.title,
            "prompt": self.prompt,
            "created_via": self.created_via,
        }


def sync_hierarchy_definitions(session_factory: sessionmaker[Session], registry: HierarchyRegistry) -> None:
    with session_scope(session_factory) as session:
        for record in registry.definitions.values():
            definition = record.definition
            existing = session.get(NodeHierarchyDefinition, definition.kind)
            if existing is None:
                session.add(_to_db_definition(record.definition, source_path=record.relative_path))
                continue
            existing.tier = str(definition.tier)
            existing.description = definition.description
            existing.main_prompt = definition.main_prompt
            existing.entry_task = definition.entry_task
            existing.available_tasks_json = definition.available_tasks
            existing.allow_parentless = definition.parent_constraints.allow_parentless
            existing.allowed_parent_kinds_json = definition.parent_constraints.allowed_kinds
            existing.allowed_parent_tiers_json = [str(value) for value in definition.parent_constraints.allowed_tiers]
            existing.allowed_child_kinds_json = definition.child_constraints.allowed_kinds
            existing.allowed_child_tiers_json = [str(value) for value in definition.child_constraints.allowed_tiers]
            existing.min_children = definition.child_constraints.min_children
            existing.max_children = definition.child_constraints.max_children
            existing.source_path = record.relative_path


def create_hierarchy_node(
    session_factory: sessionmaker[Session],
    registry: HierarchyRegistry,
    *,
    kind: str,
    title: str,
    prompt: str,
    parent_node_id: UUID | None = None,
) -> HierarchyNodeSnapshot:
    with session_scope(session_factory) as session:
        if kind not in registry.definitions:
            raise DaemonNotFoundError(f"unknown node kind '{kind}'")
        definition = registry.get(kind)
        existing_definition = session.get(NodeHierarchyDefinition, definition.kind)
        if existing_definition is None:
            session.add(_to_db_definition(definition, source_path=registry.definitions[kind].relative_path))
            session.flush()

        parent_kind = None
        if parent_node_id is not None:
            parent = session.get(HierarchyNode, parent_node_id)
            if parent is None:
                raise DaemonNotFoundError("parent node not found")
            parent_kind = parent.kind
        else:
            parent = None

        try:
            registry.validate_parent_child(parent_kind=parent_kind, child_kind=kind)
        except ValueError as exc:
            raise DaemonConflictError(str(exc)) from exc

        if parent is not None and parent.max_children is not None:
            child_count = session.query(HierarchyNode).where(HierarchyNode.parent_node_id == parent.node_id).count()
            if child_count >= parent.max_children:
                raise DaemonConflictError(f"parent node '{parent.node_id}' has reached its child limit")

        node = HierarchyNode(
            node_id=uuid4(),
            parent_node_id=parent_node_id,
            kind=definition.kind,
            tier=str(definition.tier),
            title=title,
            prompt=prompt,
            created_via="daemon",
            max_children=definition.child_constraints.max_children,
        )
        session.add(node)
        session.flush()
        return HierarchyNodeSnapshot(
            node_id=node.node_id,
            parent_node_id=node.parent_node_id,
            kind=node.kind,
            tier=node.tier,
            title=node.title,
            prompt=node.prompt,
            created_via=node.created_via,
        )


def get_hierarchy_node(session_factory: sessionmaker[Session], node_id: UUID) -> HierarchyNodeSnapshot:
    with query_session_scope(session_factory) as session:
        node = session.get(HierarchyNode, node_id)
        if node is None:
            raise DaemonNotFoundError("node not found")
        return HierarchyNodeSnapshot(
            node_id=node.node_id,
            parent_node_id=node.parent_node_id,
            kind=node.kind,
            tier=node.tier,
            title=node.title,
            prompt=node.prompt,
            created_via=node.created_via,
        )


def list_children(session_factory: sessionmaker[Session], node_id: UUID) -> list[HierarchyNodeSnapshot]:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, node_id)
        if selector is not None:
            rows = session.execute(
                select(HierarchyNode)
                .join(NodeVersion, NodeVersion.logical_node_id == HierarchyNode.node_id)
                .join(NodeChild, NodeChild.child_node_version_id == NodeVersion.id)
                .where(NodeChild.parent_node_version_id == selector.authoritative_node_version_id)
                .order_by(NodeChild.ordinal, HierarchyNode.created_at)
            ).scalars().all()
        else:
            rows = session.execute(
                select(HierarchyNode).where(HierarchyNode.parent_node_id == node_id).order_by(HierarchyNode.created_at)
            ).scalars().all()
        return [
            HierarchyNodeSnapshot(
                node_id=row.node_id,
                parent_node_id=row.parent_node_id,
                kind=row.kind,
                tier=row.tier,
                title=row.title,
                prompt=row.prompt,
                created_via=row.created_via,
            )
            for row in rows
        ]


def list_ancestors(session_factory: sessionmaker[Session], node_id: UUID) -> list[HierarchyNodeSnapshot]:
    with query_session_scope(session_factory) as session:
        current = session.get(HierarchyNode, node_id)
        if current is None:
            raise DaemonNotFoundError("node not found")
        ancestors: list[HierarchyNodeSnapshot] = []
        while current.parent_node_id is not None:
            current = session.get(HierarchyNode, current.parent_node_id)
            if current is None:
                break
            ancestors.append(
                HierarchyNodeSnapshot(
                    node_id=current.node_id,
                    parent_node_id=current.parent_node_id,
                    kind=current.kind,
                    tier=current.tier,
                    title=current.title,
                    prompt=current.prompt,
                    created_via=current.created_via,
                )
            )
        return ancestors


def _to_db_definition(definition: NodeDefinition, *, source_path: str) -> NodeHierarchyDefinition:
    return NodeHierarchyDefinition(
        kind=definition.kind,
        tier=str(definition.tier),
        description=definition.description,
        main_prompt=definition.main_prompt,
        entry_task=definition.entry_task,
        available_tasks_json=definition.available_tasks,
        allow_parentless=definition.parent_constraints.allow_parentless,
        allowed_parent_kinds_json=definition.parent_constraints.allowed_kinds,
        allowed_parent_tiers_json=[str(value) for value in definition.parent_constraints.allowed_tiers],
        allowed_child_kinds_json=definition.child_constraints.allowed_kinds,
        allowed_child_tiers_json=[str(value) for value in definition.child_constraints.allowed_tiers],
        min_children=definition.child_constraints.min_children,
        max_children=definition.child_constraints.max_children,
        source_path=source_path,
    )
