from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from uuid import UUID, uuid4

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.daemon.environments import normalize_environment_relative_path
from aicoding.db.models import NodeVersion, NodeVersionSourceDocument, SourceDocument
from aicoding.db.session import query_session_scope, session_scope
from aicoding.overrides import list_override_documents
from aicoding.resources import ResourceCatalog, load_resource_catalog


@dataclass(frozen=True, slots=True)
class DiscoveredSourceInput:
    source_group: str
    relative_path: str
    doc_family: str
    source_role: str
    resolution_order: int
    merge_mode: str = "direct"


@dataclass(frozen=True, slots=True)
class SourceDocumentSnapshot:
    id: UUID
    source_group: str
    relative_path: str
    doc_family: str
    source_role: str
    merge_mode: str
    content_hash: str
    resolution_order: int
    is_resolved_input: bool

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "source_group": self.source_group,
            "relative_path": self.relative_path,
            "doc_family": self.doc_family,
            "source_role": self.source_role,
            "merge_mode": self.merge_mode,
            "content_hash": self.content_hash,
            "resolution_order": self.resolution_order,
            "is_resolved_input": self.is_resolved_input,
        }


@dataclass(frozen=True, slots=True)
class NodeVersionSourceLineageSnapshot:
    node_version_id: UUID
    logical_node_id: UUID
    source_documents: list[SourceDocumentSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "source_documents": [item.to_payload() for item in self.source_documents],
        }


def capture_node_version_source_lineage(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> NodeVersionSourceLineageSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    with session_scope(session_factory) as session:
        version = session.get(NodeVersion, node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")

        discovered = discover_node_version_sources(version, resource_catalog)
        existing_links = session.execute(
            select(NodeVersionSourceDocument).where(NodeVersionSourceDocument.node_version_id == node_version_id)
        ).scalars().all()
        for row in existing_links:
            session.delete(row)
        session.flush()

        snapshots: list[SourceDocumentSnapshot] = []
        for item in discovered:
            content = resource_catalog.read_text(item.source_group, item.relative_path)
            content_hash = sha256_text(content)
            source_document = (
                session.execute(
                    select(SourceDocument).where(
                        SourceDocument.source_group == item.source_group,
                        SourceDocument.relative_path == item.relative_path,
                        SourceDocument.content_hash == content_hash,
                    )
                )
                .scalars()
                .first()
            )
            if source_document is None:
                source_document = SourceDocument(
                    id=uuid4(),
                    source_group=item.source_group,
                    relative_path=item.relative_path,
                    doc_family=item.doc_family,
                    source_role=item.source_role,
                    merge_mode=item.merge_mode,
                    content=content,
                    content_hash=content_hash,
                )
                session.add(source_document)
                session.flush()

            link = NodeVersionSourceDocument(
                id=uuid4(),
                node_version_id=node_version_id,
                source_document_id=source_document.id,
                source_role=item.source_role,
                resolution_order=item.resolution_order,
                is_resolved_input=True,
            )
            session.add(link)
            snapshots.append(
                SourceDocumentSnapshot(
                    id=source_document.id,
                    source_group=source_document.source_group,
                    relative_path=source_document.relative_path,
                    doc_family=source_document.doc_family,
                    source_role=item.source_role,
                    merge_mode=source_document.merge_mode,
                    content_hash=source_document.content_hash,
                    resolution_order=item.resolution_order,
                    is_resolved_input=True,
                )
            )
        session.flush()
        return NodeVersionSourceLineageSnapshot(
            node_version_id=version.id,
            logical_node_id=version.logical_node_id,
            source_documents=sorted(snapshots, key=lambda item: item.resolution_order),
        )


def load_node_version_source_lineage(
    session_factory: sessionmaker[Session],
    *,
    node_version_id: UUID,
) -> NodeVersionSourceLineageSnapshot:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        rows = session.execute(
            select(NodeVersionSourceDocument, SourceDocument)
            .join(SourceDocument, NodeVersionSourceDocument.source_document_id == SourceDocument.id)
            .where(NodeVersionSourceDocument.node_version_id == node_version_id)
            .order_by(NodeVersionSourceDocument.resolution_order)
        ).all()
        return NodeVersionSourceLineageSnapshot(
            node_version_id=version.id,
            logical_node_id=version.logical_node_id,
            source_documents=[
                SourceDocumentSnapshot(
                    id=source.id,
                    source_group=source.source_group,
                    relative_path=source.relative_path,
                    doc_family=source.doc_family,
                    source_role=link.source_role,
                    merge_mode=source.merge_mode,
                    content_hash=source.content_hash,
                    resolution_order=link.resolution_order,
                    is_resolved_input=link.is_resolved_input,
                )
                for link, source in rows
            ],
        )


def discover_node_version_sources(version: NodeVersion, catalog: ResourceCatalog) -> list[DiscoveredSourceInput]:
    node_relative_path = f"nodes/{version.node_kind}.yaml"
    node_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", node_relative_path))["node_definition"]
    prompt_group, prompt_relative_path = _resolve_prompt_group(node_doc["main_prompt"], catalog)

    discovered = [
        DiscoveredSourceInput(
            source_group="yaml_builtin_system",
            relative_path=node_relative_path,
            doc_family="node_definition",
            source_role="base_definition",
            resolution_order=10,
        ),
        DiscoveredSourceInput(
            source_group="yaml_builtin_system",
            relative_path="policies/default_runtime_policy.yaml",
            doc_family="runtime_policy_definition",
            source_role="policy_definition",
            resolution_order=20,
        ),
        DiscoveredSourceInput(
            source_group="yaml_builtin_system",
            relative_path="prompts/default_prompt_refs.yaml",
            doc_family="prompt_reference_definition",
            source_role="base_definition",
            resolution_order=30,
        ),
    ]

    order = 35
    if catalog.yaml_project_policies_dir.exists():
        for path in sorted(catalog.yaml_project_policies_dir.glob("*.yaml")):
            discovered.append(
                DiscoveredSourceInput(
                    source_group="yaml_project",
                    relative_path=str(path.relative_to(catalog.yaml_project_dir)),
                    doc_family="project_policy_definition",
                    source_role="policy_definition",
                    resolution_order=order,
                )
            )
            order += 5

    for override in list_override_documents(catalog):
        discovered.append(
            DiscoveredSourceInput(
                source_group="yaml_overrides",
                relative_path=override.relative_path,
                doc_family="override_definition",
                source_role="override_definition",
                resolution_order=order,
                merge_mode=override.document.merge_mode,
            )
        )
        order += 5

    discovered.append(
        DiscoveredSourceInput(
            source_group=prompt_group,
            relative_path=prompt_relative_path,
            doc_family="prompt_template",
            source_role="prompt_template",
            resolution_order=order,
        )
    )

    order += 10
    environment_refs = _discover_environment_refs(node_doc=node_doc, catalog=catalog)
    for environment_ref in environment_refs:
        environment_relative_path = normalize_environment_relative_path(str(environment_ref))
        environment_group = "yaml_project" if (catalog.yaml_project_dir / environment_relative_path).exists() else "yaml_builtin_system"
        discovered.append(
            DiscoveredSourceInput(
                source_group=environment_group,
                relative_path=environment_relative_path,
                doc_family="environment_policy_definition",
                source_role="policy_definition",
                resolution_order=order,
            )
        )
        order += 5

    order += 10
    hook_refs = _discover_hook_refs(node_doc=node_doc, catalog=catalog)
    for hook_ref in hook_refs:
        hook_relative_path = _normalize_hook_relative_path(str(hook_ref))
        hook_doc = yaml.safe_load(catalog.read_text(_resolve_hook_source_group(hook_relative_path, catalog), hook_relative_path)) or {}
        hook_group = _resolve_hook_source_group(hook_relative_path, catalog)
        discovered.append(
            DiscoveredSourceInput(
                source_group=hook_group,
                relative_path=hook_relative_path,
                doc_family="hook_definition",
                source_role="base_definition",
                resolution_order=order,
            )
        )
        order += 5
        for run_step in hook_doc.get("run", []):
            hook_prompt = str(run_step.get("prompt", "")).strip()
            if not hook_prompt:
                continue
            prompt_group, prompt_relative_path = _resolve_prompt_group(hook_prompt, catalog)
            discovered.append(
                DiscoveredSourceInput(
                    source_group=prompt_group,
                    relative_path=prompt_relative_path,
                    doc_family="prompt_template",
                    source_role="prompt_template",
                    resolution_order=order,
                )
            )
            order += 5

    for task_name in node_doc.get("available_tasks", []):
        task_relative_path = f"tasks/{task_name}.yaml"
        task_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", task_relative_path)) or {}
        discovered.append(
            DiscoveredSourceInput(
                source_group="yaml_builtin_system",
                relative_path=task_relative_path,
                doc_family="task_definition",
                source_role="base_definition",
                resolution_order=order,
            )
        )
        order += 10
        for review_ref in task_doc.get("uses_reviews", []):
            review_relative_path = _normalize_review_relative_path(str(review_ref))
            review_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", review_relative_path)) or {}
            discovered.append(
                DiscoveredSourceInput(
                    source_group="yaml_builtin_system",
                    relative_path=review_relative_path,
                    doc_family="review_definition",
                    source_role="base_definition",
                    resolution_order=order,
                )
            )
            order += 5
            review_prompt = str(review_doc.get("prompt", "")).strip()
            if review_prompt:
                prompt_group, prompt_relative_path = _resolve_prompt_group(review_prompt, catalog)
                discovered.append(
                    DiscoveredSourceInput(
                        source_group=prompt_group,
                        relative_path=prompt_relative_path,
                        doc_family="prompt_template",
                        source_role="prompt_template",
                        resolution_order=order,
                    )
                )
                order += 5
        for testing_ref in task_doc.get("uses_testing", []):
            testing_group, testing_relative_path = _resolve_testing_source(str(testing_ref), catalog)
            discovered.append(
                DiscoveredSourceInput(
                    source_group=testing_group,
                    relative_path=testing_relative_path,
                    doc_family="testing_definition",
                    source_role="base_definition",
                    resolution_order=order,
                )
            )
            order += 5

    layout_relative_path = _default_layout_for_kind(version.node_kind)
    if layout_relative_path is not None:
        discovered.append(
            DiscoveredSourceInput(
                source_group="yaml_builtin_system",
                relative_path=layout_relative_path,
                doc_family="layout_definition",
                source_role="base_definition",
                resolution_order=order,
            )
        )
    deduped: list[DiscoveredSourceInput] = []
    seen: set[tuple[str, str]] = set()
    for item in discovered:
        key = (item.source_group, item.relative_path)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
    return deduped


def sha256_text(content: str) -> str:
    return sha256(content.encode("utf-8")).hexdigest()


def _resolve_prompt_group(prompt_path: str, catalog: ResourceCatalog) -> tuple[str, str]:
    normalized = prompt_path.removeprefix("prompts/")
    prompt_pack = "default"
    if catalog.yaml_project_policies_dir.exists():
        for path in sorted(catalog.yaml_project_policies_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8")).get("project_policy_definition", {})
            prompt_pack = raw.get("prompt_pack", prompt_pack)
    return ("prompt_project" if prompt_pack == "project" else "prompt_pack_default"), normalized


def _default_layout_for_kind(kind: str) -> str | None:
    return {
        "epic": "layouts/epic_to_phases.yaml",
        "phase": "layouts/phase_to_plans.yaml",
        "plan": "layouts/plan_to_tasks.yaml",
    }.get(kind)


def _normalize_review_relative_path(reference: str) -> str:
    relative_path = reference.removeprefix("reviews/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"reviews/{relative_path}"


def _normalize_hook_relative_path(reference: str) -> str:
    relative_path = reference.removeprefix("hooks/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"hooks/{relative_path}"


def _normalize_testing_relative_path(reference: str) -> str:
    relative_path = reference.removeprefix("testing/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"testing/{relative_path}"


def _discover_hook_refs(*, node_doc: dict[str, object], catalog: ResourceCatalog) -> list[str]:
    discovered: list[str] = []
    for ref in node_doc.get("hooks", []):
        discovered.append(_normalize_hook_relative_path(str(ref)))
    runtime_policy = yaml.safe_load(catalog.read_text("yaml_builtin_system", "policies/default_runtime_policy.yaml")) or {}
    for ref in runtime_policy.get("hook_refs", []):
        discovered.append(_normalize_hook_relative_path(str(ref)))
    if catalog.yaml_project_policies_dir.exists():
        for path in sorted(catalog.yaml_project_policies_dir.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            project_policy = raw.get("project_policy_definition", raw)
            for ref in project_policy.get("hook_refs", []):
                discovered.append(_normalize_hook_relative_path(str(ref)))
    deduped: list[str] = []
    seen: set[str] = set()
    for ref in discovered:
        if ref in seen:
            continue
        seen.add(ref)
        deduped.append(ref)
    return deduped


def _discover_environment_refs(*, node_doc: dict[str, object], catalog: ResourceCatalog) -> list[str]:
    discovered: list[str] = []
    for task_name in node_doc.get("available_tasks", []):
        task_relative_path = f"tasks/{task_name}.yaml"
        task_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", task_relative_path)) or {}
        for subtask in task_doc.get("subtasks", []):
            environment_ref = str(subtask.get("environment_policy_ref", "")).strip()
            if environment_ref:
                discovered.append(environment_ref)
    deduped: list[str] = []
    seen: set[str] = set()
    for ref in discovered:
        normalized = normalize_environment_relative_path(ref)
        if normalized in seen:
            continue
        seen.add(normalized)
        deduped.append(normalized)
    return deduped


def _resolve_hook_source_group(relative_path: str, catalog: ResourceCatalog) -> str:
    project_path = catalog.yaml_project_dir / relative_path
    if project_path.exists():
        return "yaml_project"
    return "yaml_builtin_system"


def _resolve_testing_source(reference: str, catalog: ResourceCatalog) -> tuple[str, str]:
    relative_path = _normalize_testing_relative_path(reference)
    if (catalog.yaml_project_dir / relative_path).exists():
        return "yaml_project", relative_path
    return "yaml_builtin_system", relative_path
