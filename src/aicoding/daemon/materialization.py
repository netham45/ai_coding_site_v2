from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.admission import add_node_dependency, check_node_dependency_readiness
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import HierarchyNode, LogicalNodeCurrentVersion, NodeChild, NodeVersion, ParentChildAuthority
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import HierarchyRegistry
from aicoding.resources import ResourceCatalog


@dataclass(frozen=True, slots=True)
class MaterializedChildSnapshot:
    layout_child_id: str
    node_id: UUID
    node_version_id: UUID
    kind: str
    title: str
    lifecycle_state: str
    scheduling_status: str

    def to_payload(self) -> dict[str, object]:
        return {
            "layout_child_id": self.layout_child_id,
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "kind": self.kind,
            "title": self.title,
            "lifecycle_state": self.lifecycle_state,
            "scheduling_status": self.scheduling_status,
        }


@dataclass(frozen=True, slots=True)
class MaterializationResultSnapshot:
    parent_node_id: UUID
    parent_node_version_id: UUID
    layout_relative_path: str
    layout_hash: str
    status: str
    authority_mode: str
    child_count: int
    created_count: int
    ready_child_count: int
    blocked_child_count: int
    children: list[MaterializedChildSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_id": str(self.parent_node_id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "layout_relative_path": self.layout_relative_path,
            "layout_hash": self.layout_hash,
            "status": self.status,
            "authority_mode": self.authority_mode,
            "child_count": self.child_count,
            "created_count": self.created_count,
            "ready_child_count": self.ready_child_count,
            "blocked_child_count": self.blocked_child_count,
            "children": [item.to_payload() for item in self.children],
        }


def materialize_layout_children(
    session_factory: sessionmaker[Session],
    registry: HierarchyRegistry,
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
) -> MaterializationResultSnapshot:
    with session_scope(session_factory) as session:
        parent_node = session.get(HierarchyNode, logical_node_id)
        if parent_node is None:
            raise DaemonNotFoundError("parent node not found")
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("parent node version selector not found")
        parent_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        if parent_version is None:
            raise DaemonNotFoundError("parent node version not found")

        layout_relative_path = _default_layout_for_kind(parent_node.kind)
        if layout_relative_path is None:
            raise DaemonConflictError("no default layout is configured for this node kind")
        loaded = resources.load_text("yaml_builtin_system", layout_relative_path)
        layout_hash = sha256(loaded.content.encode("utf-8")).hexdigest()
        parsed = yaml.safe_load(loaded.content)
        children_spec = list(parsed.get("children", []))
        if not children_spec:
            raise DaemonConflictError("layout has no children")
        _validate_layout_children(children_spec)

        authority = session.get(ParentChildAuthority, parent_version.id)
        if authority is None:
            authority = ParentChildAuthority(
                parent_node_version_id=parent_version.id,
                authority_mode="layout_authoritative",
                authoritative_layout_hash=None,
            )
            session.add(authority)
            session.flush()
        if authority.authority_mode in {"manual", "hybrid"}:
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=layout_relative_path, layout_hash=layout_hash, status="reconciliation_required", authority_mode=authority.authority_mode)
        existing_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_version.id).order_by(NodeChild.ordinal)
        ).scalars().all()
        if existing_edges and authority.authoritative_layout_hash is None:
            return _existing_materialization_snapshot(
                session_factory,
                logical_node_id=logical_node_id,
                parent_version_id=parent_version.id,
                layout_relative_path=layout_relative_path,
                layout_hash=layout_hash,
                status="reconciliation_required",
                authority_mode=authority.authority_mode,
            )
        if authority.authoritative_layout_hash == layout_hash and existing_edges:
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=layout_relative_path, layout_hash=layout_hash, status="already_materialized", authority_mode=authority.authority_mode)
        if existing_edges and authority.authoritative_layout_hash not in {None, layout_hash}:
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=layout_relative_path, layout_hash=layout_hash, status="replan_required", authority_mode=authority.authority_mode)

        created_children: list[MaterializedChildSnapshot] = []
        child_version_by_layout_id: dict[str, UUID] = {}
        for child_spec in children_spec:
            created = create_hierarchy_node(
                session_factory,
                registry,
                kind=child_spec["kind"],
                title=child_spec["name"],
                prompt=child_spec["goal"],
                parent_node_id=logical_node_id,
            )
            seed_node_lifecycle(session_factory, node_id=str(created.node_id), initial_state="DRAFT")
            version = initialize_node_version(session_factory, logical_node_id=created.node_id)
            compile_node_workflow(session_factory, logical_node_id=created.node_id, catalog=resources)
            transition_node_lifecycle(session_factory, node_id=str(created.node_id), target_state="READY")
            session.add(
                NodeChild(
                    parent_node_version_id=parent_version.id,
                    child_node_version_id=version.id,
                    layout_child_id=child_spec["id"],
                    origin_type="layout_generated",
                    ordinal=child_spec.get("ordinal"),
                )
            )
            session.flush()
            child_version_by_layout_id[child_spec["id"]] = version.id
            created_children.append(
                MaterializedChildSnapshot(
                    layout_child_id=child_spec["id"],
                    node_id=created.node_id,
                    node_version_id=version.id,
                    kind=created.kind,
                    title=created.title,
                    lifecycle_state="READY",
                    scheduling_status="ready",
                )
            )

        for child_spec in children_spec:
            source_version_id = child_version_by_layout_id[child_spec["id"]]
            source_node_id = _logical_node_id_for_version(session, source_version_id)
            for dependency in child_spec.get("dependencies", []):
                target_version_id = child_version_by_layout_id[dependency]
                target_node_id = _logical_node_id_for_version(session, target_version_id)
                add_node_dependency(session_factory, node_id=source_node_id, depends_on_node_id=target_node_id, required_state="COMPLETE")

        authority.authoritative_layout_hash = layout_hash
        session.flush()

    return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=layout_relative_path, layout_hash=layout_hash, status="created", authority_mode="layout_authoritative")


def _existing_materialization_snapshot(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    parent_version_id: UUID,
    layout_relative_path: str,
    layout_hash: str,
    status: str,
    authority_mode: str,
) -> MaterializationResultSnapshot:
    with query_session_scope(session_factory) as session:
        edges = session.execute(
            select(NodeChild, NodeVersion, HierarchyNode)
            .join(NodeVersion, NodeVersion.id == NodeChild.child_node_version_id)
            .join(HierarchyNode, HierarchyNode.node_id == NodeVersion.logical_node_id)
            .where(NodeChild.parent_node_version_id == parent_version_id)
            .order_by(NodeChild.ordinal, HierarchyNode.created_at)
        ).all()
        children: list[MaterializedChildSnapshot] = []
        ready_count = 0
        blocked_count = 0
        for edge, version, node in edges:
            lifecycle = load_node_lifecycle(session_factory, str(node.node_id))
            readiness = check_node_dependency_readiness(session_factory, node_id=node.node_id)
            scheduling_status = "ready" if readiness.status == "ready" else readiness.status
            if scheduling_status == "ready":
                ready_count += 1
            else:
                blocked_count += 1
            children.append(
                MaterializedChildSnapshot(
                    layout_child_id=edge.layout_child_id,
                    node_id=node.node_id,
                    node_version_id=version.id,
                    kind=node.kind,
                    title=node.title,
                    lifecycle_state=lifecycle.lifecycle_state,
                    scheduling_status=scheduling_status,
                )
            )
        return MaterializationResultSnapshot(
            parent_node_id=logical_node_id,
            parent_node_version_id=parent_version_id,
            layout_relative_path=layout_relative_path,
            layout_hash=layout_hash,
            status=status,
            authority_mode=authority_mode,
            child_count=len(children),
            created_count=0 if status != "created" else len(children),
            ready_child_count=ready_count,
            blocked_child_count=blocked_count,
            children=children,
        )


def _default_layout_for_kind(kind: str) -> str | None:
    return {
        "epic": "layouts/epic_to_phases.yaml",
        "phase": "layouts/phase_to_plans.yaml",
        "plan": "layouts/plan_to_tasks.yaml",
    }.get(kind)


def _validate_layout_children(children_spec: list[dict[str, object]]) -> None:
    child_ids = [str(item.get("id", "")).strip() for item in children_spec]
    if any(not child_id for child_id in child_ids):
        raise DaemonConflictError("layout child id is required")
    if len(set(child_ids)) != len(child_ids):
        raise DaemonConflictError("layout child ids must be unique")
    ordinals: list[int] = []
    for item in children_spec:
        ordinal = item.get("ordinal")
        if ordinal is None:
            continue
        if not isinstance(ordinal, int):
            raise DaemonConflictError("layout child ordinal must be an integer")
        ordinals.append(ordinal)
    if len(set(ordinals)) != len(ordinals):
        raise DaemonConflictError("layout child ordinals must be unique when provided")
    dependency_targets = set(child_ids)
    adjacency: dict[str, list[str]] = {}
    for item in children_spec:
        child_id = str(item["id"])
        adjacency[child_id] = []
        for dependency in item.get("dependencies", []):
            if dependency == child_id:
                raise DaemonConflictError("layout child may not depend on itself")
            if dependency not in dependency_targets:
                raise DaemonConflictError("layout child dependency target is invalid")
            adjacency[child_id].append(str(dependency))
    _ensure_acyclic_dependencies(adjacency)


def _logical_node_id_for_version(session: Session, node_version_id: UUID) -> UUID:
    version = session.get(NodeVersion, node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version.logical_node_id


def inspect_materialized_children(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
) -> MaterializationResultSnapshot:
    with query_session_scope(session_factory) as session:
        parent_node = session.get(HierarchyNode, logical_node_id)
        if parent_node is None:
            raise DaemonNotFoundError("parent node not found")
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("parent node version selector not found")
        parent_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        if parent_version is None:
            raise DaemonNotFoundError("parent node version not found")
        layout_relative_path = _default_layout_for_kind(parent_node.kind)
        if layout_relative_path is None:
            raise DaemonConflictError("no default layout is configured for this node kind")
        loaded = resources.load_text("yaml_builtin_system", layout_relative_path)
        layout_hash = sha256(loaded.content.encode("utf-8")).hexdigest()
        authority = session.get(ParentChildAuthority, parent_version.id)
        if authority is None:
            return MaterializationResultSnapshot(
                parent_node_id=logical_node_id,
                parent_node_version_id=parent_version.id,
                layout_relative_path=layout_relative_path,
                layout_hash=layout_hash,
                status="not_materialized",
                authority_mode="layout_authoritative",
                child_count=0,
                created_count=0,
                ready_child_count=0,
                blocked_child_count=0,
                children=[],
            )
        if authority.authority_mode == "manual":
            status = "manual"
        elif authority.authority_mode == "hybrid":
            status = "reconciliation_required"
        else:
            status = "materialized" if authority.authoritative_layout_hash == layout_hash else "reconciliation_required"
        return _existing_materialization_snapshot(
            session_factory,
            logical_node_id=logical_node_id,
            parent_version_id=parent_version.id,
            layout_relative_path=layout_relative_path,
            layout_hash=layout_hash,
            status=status,
            authority_mode=authority.authority_mode,
        )


def _ensure_acyclic_dependencies(adjacency: dict[str, list[str]]) -> None:
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node_id: str) -> None:
        if node_id in visited:
            return
        if node_id in visiting:
            raise DaemonConflictError("layout child dependencies must be acyclic")
        visiting.add(node_id)
        for dependency in adjacency.get(node_id, []):
            visit(dependency)
        visiting.remove(node_id)
        visited.add(node_id)

    for node_id in adjacency:
        visit(node_id)
