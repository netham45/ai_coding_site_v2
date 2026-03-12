from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import UUID

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.config import get_settings
from aicoding.daemon.admission import add_node_dependency, check_node_dependency_readiness
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import HierarchyNode, LogicalNodeCurrentVersion, NodeChild, NodeVersion, ParentChildAuthority, RebuildEvent, WorkflowEvent
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import HierarchyRegistry
from aicoding.resources import ResourceCatalog
from aicoding.yaml_schemas import LayoutDefinitionDocument


@dataclass(frozen=True, slots=True)
class MaterializedChildSnapshot:
    layout_child_id: str
    node_id: UUID
    node_version_id: UUID
    kind: str
    title: str
    lifecycle_state: str
    scheduling_status: str
    scheduling_reason: str | None
    blockers: list[dict[str, object]]

    def to_payload(self) -> dict[str, object]:
        return {
            "layout_child_id": self.layout_child_id,
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "kind": self.kind,
            "title": self.title,
            "lifecycle_state": self.lifecycle_state,
            "scheduling_status": self.scheduling_status,
            "scheduling_reason": self.scheduling_reason,
            "blockers": self.blockers,
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


@dataclass(frozen=True, slots=True)
class ChildReconciliationInspectionSnapshot:
    parent_node_id: UUID
    parent_node_version_id: UUID
    authority_mode: str
    materialization_status: str
    available_decisions: list[str]
    manual_child_count: int
    layout_generated_child_count: int
    layout_relative_path: str
    layout_hash: str
    children: list[MaterializedChildSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_id": str(self.parent_node_id),
            "parent_node_version_id": str(self.parent_node_version_id),
            "authority_mode": self.authority_mode,
            "materialization_status": self.materialization_status,
            "available_decisions": self.available_decisions,
            "manual_child_count": self.manual_child_count,
            "layout_generated_child_count": self.layout_generated_child_count,
            "layout_relative_path": self.layout_relative_path,
            "layout_hash": self.layout_hash,
            "children": [item.to_payload() for item in self.children],
        }


@dataclass(frozen=True, slots=True)
class ResolvedMaterializationLayout:
    relative_path: str
    content: str


@dataclass(frozen=True, slots=True)
class LayoutRegistrationSnapshot:
    node_id: UUID
    node_version_id: UUID
    status: str
    source_path: str
    registered_path: str
    layout_relative_path: str
    layout_hash: str
    child_count: int
    workflow_event_id: UUID

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "status": self.status,
            "source_path": self.source_path,
            "registered_path": self.registered_path,
            "layout_relative_path": self.layout_relative_path,
            "layout_hash": self.layout_hash,
            "child_count": self.child_count,
            "workflow_event_id": str(self.workflow_event_id),
        }


def register_generated_layout(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    file_path: str,
) -> LayoutRegistrationSnapshot:
    source_path = Path(file_path).expanduser()
    if not source_path.exists() or not source_path.is_file():
        raise DaemonNotFoundError("layout file not found")

    try:
        content = source_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise DaemonConflictError(f"unable to read layout file: {exc}") from exc

    try:
        parsed = yaml.safe_load(content)
        document = LayoutDefinitionDocument.model_validate(parsed)
    except Exception as exc:
        raise DaemonConflictError(f"layout file is invalid: {exc}") from exc

    layout_hash = sha256(content.encode("utf-8")).hexdigest()
    workspace_root = get_settings().workspace_root or Path.cwd()
    registered_path = workspace_root / "layouts" / "generated_layout.yaml"
    registered_path.parent.mkdir(parents=True, exist_ok=True)

    with session_scope(session_factory) as session:
        parent_node = session.get(HierarchyNode, logical_node_id)
        if parent_node is None:
            raise DaemonNotFoundError("parent node not found")
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("parent node version selector not found")
        node_version_id = selector.authoritative_node_version_id
        registered_path.write_text(content, encoding="utf-8")
        event = record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=node_version_id,
            node_run_id=None,
            event_scope="child_layout",
            event_type="registered_generated_layout",
            payload_json={
                "source_path": str(source_path.resolve()),
                "registered_path": str(registered_path),
                "layout_relative_path": "layouts/generated_layout.yaml",
                "layout_hash": layout_hash,
                "child_count": len(document.children),
            },
        )

    return LayoutRegistrationSnapshot(
        node_id=logical_node_id,
        node_version_id=node_version_id,
        status="registered",
        source_path=str(source_path.resolve()),
        registered_path=str(registered_path),
        layout_relative_path="layouts/generated_layout.yaml",
        layout_hash=layout_hash,
        child_count=len(document.children),
        workflow_event_id=event.id,
    )


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

        resolved_layout = _resolve_materialization_layout(
            session_factory=session_factory,
            logical_node_id=logical_node_id,
            resources=resources,
            parent_kind=parent_node.kind,
        )
        layout_hash = sha256(resolved_layout.content.encode("utf-8")).hexdigest()
        parsed = yaml.safe_load(resolved_layout.content)
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
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=resolved_layout.relative_path, layout_hash=layout_hash, status="reconciliation_required", authority_mode=authority.authority_mode)
        existing_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_version.id).order_by(NodeChild.ordinal)
        ).scalars().all()
        if existing_edges and authority.authoritative_layout_hash is None:
            return _existing_materialization_snapshot(
                session_factory,
                logical_node_id=logical_node_id,
                parent_version_id=parent_version.id,
                layout_relative_path=resolved_layout.relative_path,
                layout_hash=layout_hash,
                status="reconciliation_required",
                authority_mode=authority.authority_mode,
            )
        if authority.authoritative_layout_hash == layout_hash and existing_edges:
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=resolved_layout.relative_path, layout_hash=layout_hash, status="already_materialized", authority_mode=authority.authority_mode)
        if existing_edges and authority.authoritative_layout_hash not in {None, layout_hash}:
            return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=resolved_layout.relative_path, layout_hash=layout_hash, status="replan_required", authority_mode=authority.authority_mode)

        created_children: list[MaterializedChildSnapshot] = []
        child_version_by_layout_id: dict[str, UUID] = {}
        for child_spec in children_spec:
            created = create_hierarchy_node(
                session_factory,
                registry,
                kind=child_spec["kind"],
                title=child_spec["name"],
                prompt=_child_prompt_from_layout(parent_version=parent_version, child_spec=child_spec),
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
                    scheduling_reason=None,
                    blockers=[],
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

    return _existing_materialization_snapshot(session_factory, logical_node_id=logical_node_id, parent_version_id=parent_version.id, layout_relative_path=resolved_layout.relative_path, layout_hash=layout_hash, status="created", authority_mode="layout_authoritative")


def _child_prompt_from_layout(*, parent_version: NodeVersion, child_spec: dict[str, object]) -> str:
    goal = str(child_spec.get("goal", "")).strip()
    parent_prompt = parent_version.prompt.strip()
    acceptance = [str(item).strip() for item in child_spec.get("acceptance", []) if str(item).strip()]
    parts = [goal] if goal else []
    if parent_prompt:
        parts.extend(["", f"Parent {parent_version.node_kind.title()} Request:", parent_prompt])
    if acceptance:
        parts.extend(["", "Child Acceptance Criteria:"])
        parts.extend(f"- {item}" for item in acceptance)
    return "\n".join(parts).strip()


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
            scheduling_status = _child_scheduling_status(lifecycle_state=lifecycle.lifecycle_state, run_status=lifecycle.run_status, readiness_status=readiness.status, blockers=readiness.blockers)
            scheduling_reason = None if not readiness.blockers else readiness.blockers[0].blocker_kind
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
                    scheduling_reason=scheduling_reason,
                    blockers=[item.to_payload() for item in readiness.blockers],
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


def _child_scheduling_status(
    *,
    lifecycle_state: str,
    run_status: str | None,
    readiness_status: str,
    blockers,
) -> str:
    if lifecycle_state == "COMPLETE":
        return "complete"
    if lifecycle_state == "SUPERSEDED":
        return "superseded"
    if lifecycle_state == "FAILED_TO_PARENT":
        return "failed"
    if run_status in {"PENDING", "RUNNING"}:
        return "already_running"
    if run_status == "PAUSED":
        return "paused_for_user"
    if readiness_status == "impossible_wait":
        return "failed"
    if blockers:
        blocker_kind = blockers[0].blocker_kind
        if blocker_kind in {"blocked_on_dependency", "blocked_on_incremental_merge", "blocked_on_parent_refresh", "blocked_on_merge_conflict"}:
            return "blocked_on_dependency"
        if blocker_kind in {"pause_gate_active", "user_gate_required"}:
            return "paused_for_user"
    if lifecycle_state != "READY":
        return "not_compiled"
    return "ready"


def _default_layout_for_kind(kind: str) -> str | None:
    return {
        "epic": "layouts/epic_to_phases.yaml",
        "phase": "layouts/phase_to_plans.yaml",
        "plan": "layouts/plan_to_tasks.yaml",
    }.get(kind)


def _resolve_materialization_layout(
    *,
    session_factory: sessionmaker[Session],
    logical_node_id: UUID,
    resources: ResourceCatalog,
    parent_kind: str,
) -> ResolvedMaterializationLayout:
    workspace_root = get_settings().workspace_root or Path.cwd()
    generated_layout_path = workspace_root / "layouts" / "generated_layout.yaml"
    if generated_layout_path.exists():
        generated_content = generated_layout_path.read_text(encoding="utf-8")
        generated_hash = sha256(generated_content.encode("utf-8")).hexdigest()
        if _generated_layout_is_registered(
            session_factory,
            logical_node_id=logical_node_id,
            layout_hash=generated_hash,
        ):
            return ResolvedMaterializationLayout(
                relative_path="layouts/generated_layout.yaml",
                content=generated_content,
            )

    layout_relative_path = _default_layout_for_kind(parent_kind)
    if layout_relative_path is None:
        raise DaemonConflictError("no default layout is configured for this node kind")
    loaded = resources.load_text("yaml_builtin_system", layout_relative_path)
    return ResolvedMaterializationLayout(
        relative_path=layout_relative_path,
        content=loaded.content,
    )


def _generated_layout_is_registered(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    layout_hash: str,
) -> bool:
    with query_session_scope(session_factory) as session:
        row = (
            session.execute(
                select(WorkflowEvent)
                .where(
                    WorkflowEvent.logical_node_id == logical_node_id,
                    WorkflowEvent.event_scope == "child_layout",
                    WorkflowEvent.event_type == "registered_generated_layout",
                )
                .order_by(WorkflowEvent.created_at.desc())
            )
            .scalars()
            .first()
        )
        if row is None:
            return False
        return str((row.payload_json or {}).get("layout_hash", "")) == layout_hash


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
        resolved_layout = _resolve_materialization_layout(
            session_factory=session_factory,
            logical_node_id=logical_node_id,
            resources=resources,
            parent_kind=parent_node.kind,
        )
        layout_hash = sha256(resolved_layout.content.encode("utf-8")).hexdigest()
        authority = session.get(ParentChildAuthority, parent_version.id)
        if authority is None:
            return MaterializationResultSnapshot(
                parent_node_id=logical_node_id,
                parent_node_version_id=parent_version.id,
                layout_relative_path=resolved_layout.relative_path,
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
            layout_relative_path=resolved_layout.relative_path,
            layout_hash=layout_hash,
            status=status,
            authority_mode=authority.authority_mode,
        )


def inspect_child_reconciliation(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
) -> ChildReconciliationInspectionSnapshot:
    materialization = inspect_materialized_children(session_factory, resources, logical_node_id=logical_node_id)
    manual_child_count = sum(1 for child in materialization.children if child.layout_child_id.startswith("manual-"))
    layout_generated_child_count = materialization.child_count - manual_child_count
    available_decisions: list[str] = []
    with query_session_scope(session_factory) as session:
        parent_version = session.get(NodeVersion, materialization.parent_node_version_id)
        assert parent_version is not None
        rebuild_required = _manual_or_hybrid_rebuild_required(session, parent_version=parent_version)
        prior_authority_mode = _prior_manual_or_hybrid_authority_mode(session, parent_version=parent_version)
    if materialization.authority_mode == "hybrid":
        available_decisions.append("preserve_manual")
    elif materialization.authority_mode == "manual" and materialization.status == "manual":
        available_decisions.append("preserve_manual")
    elif rebuild_required:
        available_decisions.append("preserve_manual")
    return ChildReconciliationInspectionSnapshot(
        parent_node_id=materialization.parent_node_id,
        parent_node_version_id=materialization.parent_node_version_id,
        authority_mode=materialization.authority_mode if not rebuild_required else (prior_authority_mode or materialization.authority_mode),
        materialization_status="reconciliation_required" if rebuild_required else materialization.status,
        available_decisions=available_decisions,
        manual_child_count=manual_child_count,
        layout_generated_child_count=layout_generated_child_count,
        layout_relative_path=materialization.layout_relative_path,
        layout_hash=materialization.layout_hash,
        children=materialization.children,
    )


def reconcile_child_authority(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
    decision: str,
) -> ChildReconciliationInspectionSnapshot:
    if decision != "preserve_manual":
        raise DaemonConflictError(f"unsupported reconciliation decision '{decision}'")
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
        authority = session.get(ParentChildAuthority, parent_version.id)
        rebuild_required = _manual_or_hybrid_rebuild_required(session, parent_version=parent_version)
        if authority is None and not rebuild_required:
            raise DaemonConflictError("parent has no child authority record to reconcile")
        edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == parent_version.id).order_by(NodeChild.ordinal)
        ).scalars().all()
        if not edges and rebuild_required:
            if authority is None:
                authority = ParentChildAuthority(
                    parent_node_version_id=parent_version.id,
                    authority_mode="manual",
                    authoritative_layout_hash=None,
                )
                session.add(authority)
            authority.authority_mode = "manual"
            authority.authoritative_layout_hash = None
            authority.last_reconciled_at = datetime.now(timezone.utc)
            session.flush()
            return_after_commit = True
        else:
            return_after_commit = False
        if not edges and not return_after_commit:
            raise DaemonConflictError("parent has no child structure to reconcile")
        if return_after_commit:
            pass
        elif authority.authority_mode not in {"hybrid", "manual"}:
            raise DaemonConflictError("preserve_manual is only valid for manual or hybrid child authority")
        else:
            for edge in edges:
                edge.origin_type = "manual"
                edge.layout_child_id = f"manual-{edge.child_node_version_id}"
            authority.authority_mode = "manual"
            authority.authoritative_layout_hash = None
            authority.last_reconciled_at = datetime.now(timezone.utc)
            session.flush()

    return inspect_child_reconciliation(session_factory, resources, logical_node_id=logical_node_id)


def _manual_or_hybrid_rebuild_required(session: Session, *, parent_version: NodeVersion) -> bool:
    prior_authority_mode = _prior_manual_or_hybrid_authority_mode(session, parent_version=parent_version)
    if prior_authority_mode not in {"manual", "hybrid"}:
        return False
    return not _manual_or_hybrid_rebuild_satisfied(session, parent_version=parent_version)


def _manual_or_hybrid_rebuild_satisfied(session: Session, *, parent_version: NodeVersion) -> bool:
    authority = session.get(ParentChildAuthority, parent_version.id)
    if authority is None or authority.authority_mode not in {"manual", "hybrid"}:
        return False
    current_child_edge = session.execute(
        select(NodeChild.child_node_version_id).where(NodeChild.parent_node_version_id == parent_version.id).limit(1)
    ).first()
    if current_child_edge is not None:
        return True
    return authority.authority_mode == "manual" and authority.last_reconciled_at is not None


def _prior_manual_or_hybrid_authority_mode(session: Session, *, parent_version: NodeVersion) -> str | None:
    if parent_version.supersedes_node_version_id is None:
        return None
    if not _is_dependency_invalidated_fresh_restart(session, node_version_id=parent_version.id):
        return None
    authority = session.get(ParentChildAuthority, parent_version.supersedes_node_version_id)
    if authority is None:
        return None
    return authority.authority_mode


def _is_dependency_invalidated_fresh_restart(session: Session, *, node_version_id: UUID) -> bool:
    events = session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == node_version_id,
            RebuildEvent.event_kind == "candidate_created",
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().all()
    for event in events:
        if bool((event.details_json or {}).get("fresh_dependency_restart")):
            return True
    return False


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
