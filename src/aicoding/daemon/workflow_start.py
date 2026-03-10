from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.admission import NodeRunAdmissionSnapshot, admit_node_run
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.lifecycle import load_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.manual_tree import ManualNodeCreationSnapshot, create_manual_node
from aicoding.daemon.run_orchestration import RunProgressSnapshot, load_current_run_progress
from aicoding.daemon.workflows import WorkflowCompileAttemptSnapshot, compile_node_workflow
from aicoding.hierarchy import HierarchyRegistry
from aicoding.resources import ResourceCatalog
from aicoding.source_lineage import capture_node_version_source_lineage


@dataclass(frozen=True, slots=True)
class WorkflowStartSnapshot:
    status: str
    requested_start_run: bool
    resolved_title: str
    node: dict[str, object]
    node_version_id: UUID
    compile: WorkflowCompileAttemptSnapshot
    lifecycle: dict[str, object]
    run_admission: dict[str, object] | None
    run_progress: dict[str, object] | None

    def to_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "requested_start_run": self.requested_start_run,
            "resolved_title": self.resolved_title,
            "node": self.node,
            "node_version_id": str(self.node_version_id),
            "compile": self.compile.to_payload(),
            "lifecycle": self.lifecycle,
            "run_admission": self.run_admission,
            "run_progress": self.run_progress,
        }


def start_top_level_workflow(
    session_factory: sessionmaker[Session],
    *,
    hierarchy_registry: HierarchyRegistry,
    resource_catalog: ResourceCatalog,
    kind: str,
    prompt: str,
    title: str | None = None,
    start_run: bool = True,
) -> WorkflowStartSnapshot:
    definition = hierarchy_registry.get(kind)
    if not definition.parent_constraints.allow_parentless:
        raise DaemonConflictError(f"node kind '{kind}' is not a top-level kind")

    resolved_title = _resolve_title(title=title, prompt=prompt)
    creation = create_manual_node(
        session_factory,
        hierarchy_registry,
        kind=kind,
        title=resolved_title,
        prompt=prompt,
        parent_node_id=None,
    )
    capture_node_version_source_lineage(
        session_factory,
        node_version_id=creation.node_version_id,
        catalog=resource_catalog,
    )
    compile_attempt = compile_node_workflow(
        session_factory,
        logical_node_id=creation.node.node_id,
        catalog=resource_catalog,
    )
    lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
    run_admission: NodeRunAdmissionSnapshot | None = None
    run_progress: RunProgressSnapshot | None = None
    status = "compile_failed"

    if compile_attempt.status == "compiled":
        lifecycle = transition_node_lifecycle(
            session_factory,
            node_id=str(creation.node.node_id),
            target_state="READY",
        )
        status = "compiled"
        if start_run:
            run_admission = admit_node_run(
                session_factory,
                node_id=creation.node.node_id,
                trigger_reason="workflow_start",
            )
            if run_admission.status == "admitted":
                run_progress = load_current_run_progress(session_factory, logical_node_id=creation.node.node_id)
                lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
                status = "started"
            else:
                lifecycle = load_node_lifecycle(session_factory, str(creation.node.node_id))
                status = "start_blocked"

    return WorkflowStartSnapshot(
        status=status,
        requested_start_run=start_run,
        resolved_title=resolved_title,
        node=creation.node.to_payload(),
        node_version_id=creation.node_version_id,
        compile=compile_attempt,
        lifecycle=lifecycle.to_payload(),
        run_admission=None if run_admission is None else run_admission.to_payload(),
        run_progress=None if run_progress is None else run_progress.to_payload(),
    )


def _resolve_title(*, title: str | None, prompt: str) -> str:
    if title is not None and title.strip():
        return title.strip()
    normalized = " ".join(prompt.strip().split())
    if not normalized:
        raise DaemonConflictError("prompt must not be blank")
    truncated = normalized[:72].rstrip()
    return truncated if truncated else "Untitled workflow"
