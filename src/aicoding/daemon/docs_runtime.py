from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import UUID, uuid4

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.history import list_prompt_history, list_summary_history
from aicoding.daemon.operator_views import load_node_operator_summary, load_tree_catalog
from aicoding.daemon.provenance import show_node_rationale
from aicoding.daemon.review_runtime import list_review_results_for_node, load_review_summary_for_node
from aicoding.daemon.testing_runtime import list_test_results_for_node, load_testing_summary_for_node
from aicoding.db.models import CompiledWorkflow, DocumentationOutput, LogicalNodeCurrentVersion, NodeVersion
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.yaml_schemas import DocsDefinitionDocument

NODE_BUILD_SCOPES = {"local", "entity_history", "custom"}
TREE_BUILD_SCOPES = {"merged", "rationale_view", "custom"}


@dataclass(frozen=True, slots=True)
class DocumentationOutputSnapshot:
    id: UUID
    logical_node_id: UUID
    node_version_id: UUID
    doc_definition_id: str | None
    scope: str
    view_name: str
    output_path: str
    content: str
    content_hash: str
    metadata_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "logical_node_id": str(self.logical_node_id),
            "node_version_id": str(self.node_version_id),
            "doc_definition_id": self.doc_definition_id,
            "scope": self.scope,
            "view_name": self.view_name,
            "output_path": self.output_path,
            "content": self.content,
            "content_hash": self.content_hash,
            "metadata_json": self.metadata_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class DocumentationCatalogSnapshot:
    node_id: UUID
    documents: list[DocumentationOutputSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"node_id": str(self.node_id), "documents": [item.to_payload() for item in self.documents]}


@dataclass(frozen=True, slots=True)
class DocumentationBuildSnapshot:
    node_id: UUID
    node_version_id: UUID
    mode: str
    documents: list[DocumentationOutputSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "mode": self.mode,
            "documents": [item.to_payload() for item in self.documents],
        }


def build_node_docs(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    scope: str | None = None,
    catalog: ResourceCatalog | None = None,
) -> DocumentationBuildSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        workflow = _compiled_workflow(session, version)
        definitions = _selected_doc_definitions(workflow, resource_catalog, scope=scope, allowed_scopes=NODE_BUILD_SCOPES)
        if not definitions:
            raise DaemonConflictError("no documentation definitions resolved for node build")
        documents = [
            _persist_doc_output(
                session,
                logical_node_id=logical_node_id,
                node_version_id=version.id,
                document=doc,
                content=_render_node_doc(
                    session_factory,
                    logical_node_id=logical_node_id,
                    doc_definition=doc,
                ),
            )
            for doc in definitions
        ]
        session.flush()
        return DocumentationBuildSnapshot(node_id=logical_node_id, node_version_id=version.id, mode="node", documents=documents)


def build_tree_docs(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    scope: str | None = None,
    catalog: ResourceCatalog | None = None,
) -> DocumentationBuildSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        workflow = _compiled_workflow(session, version)
        definitions = _selected_doc_definitions(workflow, resource_catalog, scope=scope, allowed_scopes=TREE_BUILD_SCOPES)
        if not definitions:
            raise DaemonConflictError("no documentation definitions resolved for tree build")
        documents = [
            _persist_doc_output(
                session,
                logical_node_id=logical_node_id,
                node_version_id=version.id,
                document=doc,
                content=_render_tree_doc(
                    session_factory,
                    logical_node_id=logical_node_id,
                    doc_definition=doc,
                ),
            )
            for doc in definitions
        ]
        session.flush()
        return DocumentationBuildSnapshot(node_id=logical_node_id, node_version_id=version.id, mode="tree", documents=documents)


def list_docs_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> DocumentationCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(DocumentationOutput)
            .where(DocumentationOutput.node_version_id == version.id)
            .order_by(DocumentationOutput.created_at, DocumentationOutput.id)
        ).scalars().all()
        return DocumentationCatalogSnapshot(node_id=logical_node_id, documents=[_snapshot(row) for row in rows])


def show_docs_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    scope: str,
) -> DocumentationOutputSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        row = session.execute(
            select(DocumentationOutput)
            .where(DocumentationOutput.node_version_id == version.id, DocumentationOutput.scope == scope)
            .order_by(DocumentationOutput.created_at.desc(), DocumentationOutput.id.desc())
        ).scalars().first()
        if row is None:
            raise DaemonNotFoundError("documentation output not found")
        return _snapshot(row)


def _selected_doc_definitions(
    workflow: CompiledWorkflow,
    catalog: ResourceCatalog,
    *,
    scope: str | None,
    allowed_scopes: set[str],
) -> list[DocsDefinitionDocument]:
    resolved_yaml = dict(workflow.resolved_yaml or {})
    refs = list(dict(resolved_yaml.get("effective_policy") or {}).get("docs_refs") or [])
    for item in list(resolved_yaml.get("resolved_documents") or []):
        if item.get("target_family") != "task_definition":
            continue
        refs.extend(str(ref) for ref in item.get("resolved_document", {}).get("uses_docs", []) if str(ref).strip())
    documents: list[DocsDefinitionDocument] = []
    seen: set[str] = set()
    for ref in refs:
        normalized = _normalize_doc_ref(ref)
        if normalized in seen:
            continue
        seen.add(normalized)
        documents.append(_load_doc_definition(catalog, normalized))
    selected = [item for item in documents if item.scope in allowed_scopes]
    selected = _augment_with_default_doc_views(catalog, selected=selected, scope=scope, allowed_scopes=allowed_scopes)
    return selected


def _augment_with_default_doc_views(
    catalog: ResourceCatalog,
    *,
    selected: list[DocsDefinitionDocument],
    scope: str | None,
    allowed_scopes: set[str],
) -> list[DocsDefinitionDocument]:
    desired_scopes = {scope} if scope is not None else set(allowed_scopes)
    all_documents = _load_all_doc_definitions(catalog)
    by_id = {item.id: item for item in selected}
    present_scopes = {item.scope for item in selected}
    for document in all_documents:
        if document.scope not in desired_scopes:
            continue
        if document.id in by_id:
            continue
        # Documentation generation should always be able to materialize the
        # canonical built-in views for the requested scope set even when the
        # effective project policy only references a narrower custom view.
        if scope is None and document.scope in present_scopes:
            continue
        by_id[document.id] = document
        present_scopes.add(document.scope)
    return list(by_id.values())


def _load_all_doc_definitions(catalog: ResourceCatalog) -> list[DocsDefinitionDocument]:
    documents: list[DocsDefinitionDocument] = []
    for base in (catalog.yaml_builtin_system_dir / "docs", catalog.yaml_project_dir / "docs"):
        if not base.exists():
            continue
        for path in sorted(base.glob("*.yaml")):
            raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            documents.append(DocsDefinitionDocument.model_validate(raw))
    return documents


def _load_doc_definition(catalog: ResourceCatalog, relative_path: str) -> DocsDefinitionDocument:
    if (catalog.yaml_project_dir / relative_path).exists():
        raw = yaml.safe_load(catalog.read_text("yaml_project", relative_path)) or {}
        return DocsDefinitionDocument.model_validate(raw)
    raw = yaml.safe_load(catalog.read_text("yaml_builtin_system", relative_path)) or {}
    return DocsDefinitionDocument.model_validate(raw)


def _normalize_doc_ref(ref: str) -> str:
    normalized = str(ref).strip()
    return normalized.removeprefix("yaml/")


def _render_node_doc(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    doc_definition: DocsDefinitionDocument,
) -> str:
    node = load_node_operator_summary(session_factory, node_id=logical_node_id)
    summaries = list_summary_history(session_factory, logical_node_id=logical_node_id).summaries
    prompt_history = list_prompt_history(session_factory, logical_node_id=logical_node_id).prompts
    review_summary = load_review_summary_for_node(session_factory, logical_node_id=logical_node_id)
    testing_summary = load_testing_summary_for_node(session_factory, logical_node_id=logical_node_id)
    try:
        rationale = show_node_rationale(session_factory, logical_node_id=logical_node_id)
    except DaemonNotFoundError:
        rationale = None

    lines = [
        f"# {node.title}",
        "",
        f"- Scope: {doc_definition.scope}",
        f"- View: {doc_definition.outputs[0].view}",
        f"- Kind: {node.kind}",
        f"- Tier: {node.tier}",
        f"- Lifecycle: {node.lifecycle_state or 'unknown'}",
        "",
        "## Goal",
        node.prompt,
    ]
    if rationale is not None:
        lines.extend(["", "## Rationale", rationale.rationale_summary])
        if rationale.entity_history:
            lines.append("")
            lines.append("## Changed Entities")
            for entry in rationale.entity_history[:8]:
                lines.append(f"- `{entry.observed_canonical_name}`: {entry.change_type} ({entry.match_confidence})")
    if doc_definition.inputs.include_node_summaries:
        lines.extend(["", "## Summaries"])
        for item in summaries[-5:]:
            lines.append(f"- `{item.summary_type}` at `{item.summary_path or '<none>'}`")
    if doc_definition.inputs.include_prompt_history:
        lines.extend(["", "## Prompt History"])
        for item in prompt_history[-5:]:
            lines.append(f"- `{item.prompt_role}` from `{item.template_path or '<inline>'}`")
    if doc_definition.inputs.include_review_results:
        lines.extend(["", "## Review", f"- Status: {review_summary.status}", f"- Results: {len(review_summary.results)}"])
    if doc_definition.inputs.include_test_results:
        lines.extend(["", "## Testing", f"- Status: {testing_summary.status}", f"- Results: {len(testing_summary.results)}"])
    return "\n".join(lines) + "\n"


def _render_tree_doc(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    doc_definition: DocsDefinitionDocument,
) -> str:
    tree = load_tree_catalog(session_factory, root_node_id=logical_node_id)
    root = load_node_operator_summary(session_factory, node_id=logical_node_id)
    try:
        rationale = show_node_rationale(session_factory, logical_node_id=logical_node_id)
    except DaemonNotFoundError:
        rationale = None
    lines = [
        f"# {root.title} Tree Documentation",
        "",
        f"- Scope: {doc_definition.scope}",
        f"- View: {doc_definition.outputs[0].view}",
        "",
        "## Tree",
    ]
    for item in tree.nodes:
        indent = "  " * item.depth
        lines.append(f"{indent}- {item.title} [{item.kind}] ({item.lifecycle_state or 'unknown'})")
    if rationale is not None:
        lines.extend(["", "## Root Rationale", rationale.rationale_summary])
    if doc_definition.inputs.include_node_summaries:
        lines.extend(["", "## Root Summaries"])
        summaries = list_summary_history(session_factory, logical_node_id=logical_node_id).summaries
        for item in summaries[-5:]:
            lines.append(f"- `{item.summary_type}` at `{item.summary_path or '<none>'}`")
    return "\n".join(lines) + "\n"


def _persist_doc_output(
    session: Session,
    *,
    logical_node_id: UUID,
    node_version_id: UUID,
    document: DocsDefinitionDocument,
    content: str,
) -> DocumentationOutputSnapshot:
    output = document.outputs[0]
    row = DocumentationOutput(
        id=uuid4(),
        logical_node_id=logical_node_id,
        node_version_id=node_version_id,
        doc_definition_id=document.id,
        scope=document.scope,
        view_name=output.view,
        output_path=output.path,
        content=content,
        content_hash=sha256(content.encode("utf-8")).hexdigest(),
        metadata_json={
            "description": document.description,
            "inputs": document.inputs.model_dump(),
        },
    )
    session.add(row)
    session.flush()
    return _snapshot(row)


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _compiled_workflow(session: Session, version: NodeVersion) -> CompiledWorkflow:
    if version.compiled_workflow_id is None:
        raise DaemonConflictError("node has no compiled workflow for documentation build")
    workflow = session.get(CompiledWorkflow, version.compiled_workflow_id)
    if workflow is None:
        raise DaemonNotFoundError("compiled workflow not found")
    return workflow


def _snapshot(row: DocumentationOutput) -> DocumentationOutputSnapshot:
    return DocumentationOutputSnapshot(
        id=row.id,
        logical_node_id=row.logical_node_id,
        node_version_id=row.node_version_id,
        doc_definition_id=row.doc_definition_id,
        scope=row.scope,
        view_name=row.view_name,
        output_path=row.output_path,
        content=row.content,
        content_hash=row.content_hash,
        metadata_json=dict(row.metadata_json or {}),
        created_at=row.created_at.isoformat(),
    )
