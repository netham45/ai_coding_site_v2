from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.daemon.hierarchy import HierarchyNodeSnapshot, create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.versioning import initialize_node_version
from aicoding.db.models import LogicalNodeCurrentVersion, NodeChild, ParentChildAuthority
from aicoding.db.session import session_scope
from aicoding.hierarchy import HierarchyRegistry


@dataclass(frozen=True, slots=True)
class ManualNodeCreationSnapshot:
    node: HierarchyNodeSnapshot
    node_version_id: UUID
    parent_authority_mode: str | None


def create_manual_node(
    session_factory: sessionmaker[Session],
    registry: HierarchyRegistry,
    *,
    kind: str,
    title: str,
    prompt: str,
    parent_node_id: UUID | None = None,
) -> ManualNodeCreationSnapshot:
    node = create_hierarchy_node(
        session_factory,
        registry,
        kind=kind,
        title=title,
        prompt=prompt,
        parent_node_id=parent_node_id,
    )
    seed_node_lifecycle(session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(session_factory, logical_node_id=node.node_id)

    parent_authority_mode = None
    if parent_node_id is not None:
        parent_authority_mode = _record_manual_child_edge(
            session_factory,
            parent_node_id=parent_node_id,
            child_node_version_id=version.id,
        )

    return ManualNodeCreationSnapshot(
        node=node,
        node_version_id=version.id,
        parent_authority_mode=parent_authority_mode,
    )


def _record_manual_child_edge(
    session_factory: sessionmaker[Session],
    *,
    parent_node_id: UUID,
    child_node_version_id: UUID,
) -> str:
    with session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, parent_node_id)
        if selector is None:
            raise DaemonNotFoundError("parent node version selector not found")
        parent_version_id = selector.authoritative_node_version_id
        existing_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_version_id).order_by(NodeChild.ordinal)
        ).scalars().all()
        authority = session.get(ParentChildAuthority, parent_version_id)
        authority_mode = _next_authority_mode(existing_edges, authority)
        if authority is None:
            authority = ParentChildAuthority(
                parent_node_version_id=parent_version_id,
                authority_mode=authority_mode,
                authoritative_layout_hash=None,
            )
            session.add(authority)
            session.flush()
        else:
            authority.authority_mode = authority_mode
            if authority_mode != "layout_authoritative":
                authority.authoritative_layout_hash = None

        next_ordinal = _next_child_ordinal(existing_edges)
        session.add(
            NodeChild(
                parent_node_version_id=parent_version_id,
                child_node_version_id=child_node_version_id,
                layout_child_id=f"manual-{child_node_version_id}",
                origin_type="manual",
                ordinal=next_ordinal,
            )
        )
        session.flush()
        return authority.authority_mode


def _next_authority_mode(existing_edges: list[NodeChild], authority: ParentChildAuthority | None) -> str:
    if authority is not None:
        if authority.authority_mode == "layout_authoritative":
            return "hybrid"
        return authority.authority_mode
    if not existing_edges:
        return "manual"
    if all(edge.origin_type == "manual" for edge in existing_edges):
        return "manual"
    return "hybrid"


def _next_child_ordinal(existing_edges: list[NodeChild]) -> int:
    ordinals = [edge.ordinal for edge in existing_edges if edge.ordinal is not None]
    return 1 if not ordinals else max(ordinals) + 1
