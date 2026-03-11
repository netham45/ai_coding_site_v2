from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from uuid import NAMESPACE_URL, UUID, uuid4, uuid5

import yaml
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import (
    CompileFailure,
    CompiledSubtask,
    CompiledSubtaskDependency,
    CompiledTask,
    CompiledWorkflow,
    CompiledWorkflowSource,
    DaemonNodeState,
    LogicalNodeCurrentVersion,
    NodeRun,
    NodeRunState,
    NodeLifecycleState,
    NodeVersion,
    NodeVersionSourceDocument,
    RebuildEvent,
    SourceDocument,
    SubtaskAttempt,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import NodeDefinitionDocument, load_hierarchy_registry
from aicoding.overrides import (
    OverrideResolutionError,
    OverrideSourceSnapshot,
    SourceDocumentInput,
    build_base_document_index,
    resolve_overrides,
)
from aicoding.operational_library import ensure_builtin_operational_library
from aicoding.project_policies import policy_impact_for_node_kind, resolve_effective_policy
from aicoding.quality_library import ensure_builtin_quality_library
from aicoding.rendering import (
    RenderContext,
    TemplateRenderError,
    build_render_context,
    contains_template_syntax,
    render_text,
)
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.source_lineage import capture_node_version_source_lineage
from aicoding.structural_library import ensure_builtin_structural_library
from aicoding.daemon.environments import normalize_environment_relative_path
from aicoding.yaml_schemas import (
    EnvironmentPolicyDefinitionDocument,
    FAMILY_MODELS,
    HookDefinitionDocument,
    ProjectPolicyDefinitionDocument,
    RuntimePolicyDefinitionDocument,
    identify_yaml_family,
    unwrap_yaml_document_payload,
    wrap_yaml_document_payload,
)

BUILTIN_LIBRARY_VERSION = "builtin-system-v1"


@dataclass(frozen=True, slots=True)
class CompiledSubtaskSnapshot:
    id: UUID
    compiled_task_id: UUID
    source_subtask_key: str
    ordinal: int
    subtask_type: str
    title: str | None
    prompt_text: str | None
    command_text: str | None
    environment_policy_ref: str | None
    environment_request_json: dict[str, object] | None
    retry_policy_json: dict[str, object] | None
    block_on_user_flag: str | None
    pause_summary_prompt: str | None
    source_file_path: str | None
    source_hash: str | None
    inserted_by_hook: bool
    inserted_by_hook_id: UUID | None
    depends_on_compiled_subtask_ids: list[UUID]

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "compiled_task_id": str(self.compiled_task_id),
            "source_subtask_key": self.source_subtask_key,
            "ordinal": self.ordinal,
            "subtask_type": self.subtask_type,
            "title": self.title,
            "prompt_text": self.prompt_text,
            "command_text": self.command_text,
            "environment_policy_ref": self.environment_policy_ref,
            "environment_request_json": self.environment_request_json,
            "retry_policy_json": self.retry_policy_json,
            "block_on_user_flag": self.block_on_user_flag,
            "pause_summary_prompt": self.pause_summary_prompt,
            "source_file_path": self.source_file_path,
            "source_hash": self.source_hash,
            "inserted_by_hook": self.inserted_by_hook,
            "inserted_by_hook_id": None if self.inserted_by_hook_id is None else str(self.inserted_by_hook_id),
            "depends_on_compiled_subtask_ids": [str(item) for item in self.depends_on_compiled_subtask_ids],
        }


@dataclass(frozen=True, slots=True)
class CompiledTaskSnapshot:
    id: UUID
    task_key: str
    ordinal: int
    title: str | None
    description: str | None
    config_json: dict[str, object]
    subtasks: list[CompiledSubtaskSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "task_key": self.task_key,
            "ordinal": self.ordinal,
            "title": self.title,
            "description": self.description,
            "config_json": self.config_json,
            "subtasks": [item.to_payload() for item in self.subtasks],
        }


@dataclass(frozen=True, slots=True)
class CompiledWorkflowSnapshot:
    id: UUID
    node_version_id: UUID
    logical_node_id: UUID
    source_hash: str
    built_in_library_version: str
    created_at: str
    source_document_count: int
    task_count: int
    subtask_count: int
    compile_context: dict[str, object]
    resolved_yaml: dict[str, object]
    tasks: list[CompiledTaskSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "source_hash": self.source_hash,
            "built_in_library_version": self.built_in_library_version,
            "created_at": self.created_at,
            "source_document_count": self.source_document_count,
            "task_count": self.task_count,
            "subtask_count": self.subtask_count,
            "compile_context": self.compile_context,
            "resolved_yaml": self.resolved_yaml,
            "tasks": [item.to_payload() for item in self.tasks],
        }


@dataclass(frozen=True, slots=True)
class WorkflowChainEntrySnapshot:
    compiled_task_id: UUID
    compiled_subtask_id: UUID
    task_key: str
    task_ordinal: int
    subtask_ordinal: int
    subtask_type: str
    title: str | None
    depends_on_compiled_subtask_ids: list[UUID]
    derived_execution_state: str | None = None
    latest_attempt_number: int | None = None
    latest_attempt_status: str | None = None
    is_current: bool = False
    latest_summary: str | None = None
    pause_flag_name: str | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "compiled_task_id": str(self.compiled_task_id),
            "compiled_subtask_id": str(self.compiled_subtask_id),
            "task_key": self.task_key,
            "task_ordinal": self.task_ordinal,
            "subtask_ordinal": self.subtask_ordinal,
            "subtask_type": self.subtask_type,
            "title": self.title,
            "depends_on_compiled_subtask_ids": [str(item) for item in self.depends_on_compiled_subtask_ids],
            "derived_execution_state": self.derived_execution_state,
            "latest_attempt_number": self.latest_attempt_number,
            "latest_attempt_status": self.latest_attempt_status,
            "is_current": self.is_current,
            "latest_summary": self.latest_summary,
            "pause_flag_name": self.pause_flag_name,
        }


@dataclass(frozen=True, slots=True)
class WorkflowChainSnapshot:
    compiled_workflow_id: UUID
    node_version_id: UUID
    logical_node_id: UUID
    compile_context: dict[str, object]
    chain: list[WorkflowChainEntrySnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "compiled_workflow_id": str(self.compiled_workflow_id),
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "compile_context": self.compile_context,
            "chain": [item.to_payload() for item in self.chain],
        }


@dataclass(frozen=True, slots=True)
class CompileFailureSnapshot:
    id: UUID
    node_version_id: UUID
    logical_node_id: UUID
    failure_stage: str
    failure_class: str
    summary: str
    details_json: dict[str, object]
    source_hash: str | None
    target_family: str | None
    target_id: str | None
    compile_context: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "failure_stage": self.failure_stage,
            "failure_class": self.failure_class,
            "summary": self.summary,
            "details_json": self.details_json,
            "source_hash": self.source_hash,
            "target_family": self.target_family,
            "target_id": self.target_id,
            "compile_context": self.compile_context,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class WorkflowCompileAttemptSnapshot:
    status: str
    node_version_id: UUID
    logical_node_id: UUID
    compile_context: dict[str, object]
    compiled_workflow: CompiledWorkflowSnapshot | None = None
    compile_failure: CompileFailureSnapshot | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "compile_context": self.compile_context,
            "compiled_workflow": None if self.compiled_workflow is None else self.compiled_workflow.to_payload(),
            "compile_failure": None if self.compile_failure is None else self.compile_failure.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class ResolvedHookDocument:
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    applies_to: dict[str, object]
    run_steps: list[dict[str, object]]
    source_hash: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "hook_id": self.hook_id,
            "when": self.when,
            "relative_path": self.relative_path,
            "source_group": self.source_group,
            "applies_to": self.applies_to,
            "run_steps": self.run_steps,
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True, slots=True)
class HookExpansionStep:
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    insertion_phase: str
    task_key: str
    source_subtask_key: str
    subtask_type: str
    prompt_path: str | None
    command_text: str | None
    render_context: dict[str, object]
    checks: list[dict[str, object]]
    source_hash: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "hook_id": self.hook_id,
            "when": self.when,
            "relative_path": self.relative_path,
            "source_group": self.source_group,
            "insertion_phase": self.insertion_phase,
            "task_key": self.task_key,
            "source_subtask_key": self.source_subtask_key,
            "subtask_type": self.subtask_type,
            "prompt_path": self.prompt_path,
            "command_text": self.command_text,
            "render_context": self.render_context,
            "checks": self.checks,
            "source_hash": self.source_hash,
        }


@dataclass(frozen=True, slots=True)
class HookExpansionSkip:
    hook_id: str
    when: str
    relative_path: str
    source_group: str
    reason: str

    def to_payload(self) -> dict[str, object]:
        return {
            "hook_id": self.hook_id,
            "when": self.when,
            "relative_path": self.relative_path,
            "source_group": self.source_group,
            "reason": self.reason,
        }


class WorkflowCompileError(Exception):
    def __init__(
        self,
        *,
        failure_stage: str,
        failure_class: str,
        summary: str,
        details_json: dict[str, object] | None = None,
        target_family: str | None = None,
        target_id: str | None = None,
    ) -> None:
        super().__init__(summary)
        self.failure_stage = failure_stage
        self.failure_class = failure_class
        self.summary = summary
        self.details_json = details_json or {}
        self.target_family = target_family
        self.target_id = target_id


def compile_node_workflow(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> WorkflowCompileAttemptSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    version_id = _authoritative_version_id(session_factory, logical_node_id)
    return compile_node_version_workflow(
        session_factory,
        version_id=version_id,
        catalog=resource_catalog,
    )


def compile_node_version_workflow(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> WorkflowCompileAttemptSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    capture_node_version_source_lineage(session_factory, node_version_id=version_id, catalog=resource_catalog)

    with session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        compile_context = _compile_context(session, version)
        if version.status == "authoritative":
            _ensure_no_live_run(session, version.logical_node_id)

        try:
            with session.begin_nested():
                snapshot = _compile_version(session, version, resource_catalog)
            if version.status == "authoritative":
                _update_lifecycle_after_compile(session, version.logical_node_id, compiled=True)
            return WorkflowCompileAttemptSnapshot(
                status="compiled",
                node_version_id=version.id,
                logical_node_id=version.logical_node_id,
                compile_context=compile_context,
                compiled_workflow=snapshot,
            )
        except WorkflowCompileError as exc:
            version.compiled_workflow_id = None
            failure = _persist_compile_failure(session, version, exc, compile_context=compile_context)
            if version.status == "authoritative":
                _update_lifecycle_after_compile(session, version.logical_node_id, compiled=False)
            return WorkflowCompileAttemptSnapshot(
                status="failed",
                node_version_id=version.id,
                logical_node_id=version.logical_node_id,
                compile_context=compile_context,
                compile_failure=failure,
            )


def load_current_workflow(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> CompiledWorkflowSnapshot:
    with query_session_scope(session_factory) as session:
        selector = _require_selector(session, logical_node_id)
        version = session.get(NodeVersion, selector.authoritative_node_version_id)
        if version is None or version.compiled_workflow_id is None:
            raise DaemonNotFoundError("compiled workflow not found")
        return _workflow_snapshot(session, version.compiled_workflow_id)


def load_node_version_workflow(session_factory: sessionmaker[Session], *, version_id: UUID) -> CompiledWorkflowSnapshot:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None or version.compiled_workflow_id is None:
            raise DaemonNotFoundError("compiled workflow not found")
        return _workflow_snapshot(session, version.compiled_workflow_id)


def load_workflow(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> CompiledWorkflowSnapshot:
    with query_session_scope(session_factory) as session:
        return _workflow_snapshot(session, workflow_id)


def load_workflow_chain_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> WorkflowChainSnapshot:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_chain(session_factory, workflow_id=workflow.id)


def load_workflow_chain_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> WorkflowChainSnapshot:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_chain(session_factory, workflow_id=workflow.id)


def load_workflow_chain(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> WorkflowChainSnapshot:
    with query_session_scope(session_factory) as session:
        workflow = session.get(CompiledWorkflow, workflow_id)
        if workflow is None:
            raise DaemonNotFoundError("compiled workflow not found")
        version = session.get(NodeVersion, workflow.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        rows = session.execute(
            select(CompiledTask, CompiledSubtask)
            .join(CompiledSubtask, CompiledSubtask.compiled_task_id == CompiledTask.id)
            .where(CompiledTask.compiled_workflow_id == workflow_id)
            .order_by(CompiledTask.ordinal, CompiledSubtask.ordinal)
        ).all()
        deps = _dependency_map(session, workflow_id)
        active_run = session.execute(
            select(NodeRun)
            .where(
                NodeRun.compiled_workflow_id == workflow_id,
                NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")),
            )
            .order_by(NodeRun.run_number.desc())
        ).scalars().first()
        run_state = None if active_run is None else session.get(NodeRunState, active_run.id)
        attempts_by_subtask_id: dict[UUID, SubtaskAttempt] = {}
        if active_run is not None:
            attempts = session.execute(
                select(SubtaskAttempt)
                .where(SubtaskAttempt.node_run_id == active_run.id)
                .order_by(SubtaskAttempt.compiled_subtask_id, SubtaskAttempt.attempt_number.desc())
            ).scalars().all()
            for attempt in attempts:
                attempts_by_subtask_id.setdefault(attempt.compiled_subtask_id, attempt)
        completed_ids = set()
        if run_state is not None and run_state.last_completed_compiled_subtask_id is not None:
            seen_complete = False
            for _, subtask in rows:
                if not seen_complete:
                    completed_ids.add(subtask.id)
                if subtask.id == run_state.last_completed_compiled_subtask_id:
                    seen_complete = True
        return WorkflowChainSnapshot(
            compiled_workflow_id=workflow.id,
            node_version_id=workflow.node_version_id,
            logical_node_id=version.logical_node_id,
            compile_context=_compile_context(session, version),
            chain=[
                WorkflowChainEntrySnapshot(
                    compiled_task_id=task.id,
                    compiled_subtask_id=subtask.id,
                    task_key=task.task_key,
                    task_ordinal=task.ordinal,
                    subtask_ordinal=subtask.ordinal,
                    subtask_type=subtask.subtask_type,
                    title=subtask.title,
                    depends_on_compiled_subtask_ids=deps.get(subtask.id, []),
                    derived_execution_state=_derive_chain_state(
                        subtask_id=subtask.id,
                        active_run=active_run,
                        run_state=run_state,
                        completed_ids=completed_ids,
                        latest_attempt=attempts_by_subtask_id.get(subtask.id),
                    ),
                    latest_attempt_number=None if attempts_by_subtask_id.get(subtask.id) is None else attempts_by_subtask_id[subtask.id].attempt_number,
                    latest_attempt_status=None if attempts_by_subtask_id.get(subtask.id) is None else attempts_by_subtask_id[subtask.id].status,
                    is_current=bool(run_state is not None and run_state.current_compiled_subtask_id == subtask.id),
                    latest_summary=None if attempts_by_subtask_id.get(subtask.id) is None else attempts_by_subtask_id[subtask.id].summary,
                    pause_flag_name=None if run_state is None or run_state.current_compiled_subtask_id != subtask.id else run_state.pause_flag_name,
                )
                for task, subtask in rows
            ],
        )


def _derive_chain_state(
    *,
    subtask_id: UUID,
    active_run: NodeRun | None,
    run_state: NodeRunState | None,
    completed_ids: set[UUID],
    latest_attempt: SubtaskAttempt | None,
) -> str | None:
    if active_run is None or run_state is None:
        return None
    if active_run.run_status == "COMPLETE":
        return "complete"
    if subtask_id in completed_ids:
        return "complete"
    if run_state.current_compiled_subtask_id == subtask_id:
        if active_run.run_status == "PAUSED":
            return "paused"
        if latest_attempt is not None and latest_attempt.status == "FAILED":
            return "failed"
        return "current"
    if latest_attempt is not None and latest_attempt.status == "FAILED":
        return "failed"
    return "pending"


def load_workflow_sources_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_sources(session_factory, workflow_id=workflow.id)


def load_workflow_sources_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_sources(session_factory, workflow_id=workflow.id)


def load_workflow_source_discovery_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_source_discovery(session_factory, workflow_id=workflow.id)


def load_workflow_source_discovery_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_source_discovery(session_factory, workflow_id=workflow.id)


def load_workflow_source_discovery(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow_sources = load_workflow_sources(session_factory, workflow_id=workflow_id)
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    source_documents = workflow_sources["source_documents"]
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "source_hash": workflow.source_hash,
        "built_in_library_version": workflow.resolved_yaml.get("built_in_library_version", BUILTIN_LIBRARY_VERSION),
        "discovery_order": [
            {
                "ordinal": index,
                **item,
            }
            for index, item in enumerate(source_documents, start=1)
        ],
        "resolved_documents": workflow.resolved_yaml.get("resolved_documents", []),
    }


def load_workflow_schema_validation_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_schema_validation(session_factory, workflow_id=workflow.id)


def load_workflow_schema_validation_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_schema_validation(session_factory, workflow_id=workflow.id)


def load_workflow_schema_validation(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    source_discovery = load_workflow_source_discovery(session_factory, workflow_id=workflow_id)
    yaml_documents = [item for item in source_discovery["discovery_order"] if str(item["source_group"]).startswith("yaml_")]
    family_counts: dict[str, int] = {}
    for item in yaml_documents:
        family = str(item["doc_family"])
        family_counts[family] = family_counts.get(family, 0) + 1
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "validated_document_count": len(yaml_documents),
        "family_counts": family_counts,
        "validated_documents": yaml_documents,
    }


def load_workflow_sources(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    with query_session_scope(session_factory) as session:
        workflow = session.get(CompiledWorkflow, workflow_id)
        if workflow is None:
            raise DaemonNotFoundError("compiled workflow not found")
        version = session.get(NodeVersion, workflow.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        rows = session.execute(
            select(CompiledWorkflowSource, SourceDocument, NodeVersionSourceDocument)
            .join(SourceDocument, CompiledWorkflowSource.source_document_id == SourceDocument.id)
            .join(
                NodeVersionSourceDocument,
                (NodeVersionSourceDocument.source_document_id == SourceDocument.id)
                & (NodeVersionSourceDocument.node_version_id == workflow.node_version_id),
            )
            .where(CompiledWorkflowSource.compiled_workflow_id == workflow_id)
            .order_by(NodeVersionSourceDocument.resolution_order)
        ).all()
        return {
            "compiled_workflow_id": str(workflow.id),
            "node_version_id": str(workflow.node_version_id),
            "logical_node_id": str(version.logical_node_id),
            "compile_context": workflow.resolved_yaml.get("compile_context", {}),
            "source_documents": [
                {
                    "id": str(source.id),
                    "source_group": source.source_group,
                    "relative_path": source.relative_path,
                    "doc_family": source.doc_family,
                    "source_role": link.source_role,
                    "merge_mode": source.merge_mode,
                    "content_hash": source.content_hash,
                    "resolution_order": version_link.resolution_order,
                }
                for link, source, version_link in rows
            ],
        }


def load_override_chain_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_override_chain(session_factory, workflow_id=workflow.id)


def load_workflow_override_resolution_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_override_resolution(session_factory, workflow_id=workflow.id)


def load_workflow_override_resolution_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_override_resolution(session_factory, workflow_id=workflow.id)


def load_workflow_override_resolution(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    override_resolution = workflow.resolved_yaml.get("override_resolution", {})
    resolved_documents = workflow.resolved_yaml.get("resolved_documents", [])
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "applied_override_count": len(override_resolution.get("applied_overrides", [])),
        "warning_count": len(override_resolution.get("warnings", [])),
        "applied_overrides": override_resolution.get("applied_overrides", []),
        "warnings": override_resolution.get("warnings", []),
        "resolved_document_count": len(resolved_documents),
        "resolved_documents": resolved_documents,
    }


def load_override_chain(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    override_resolution = workflow.resolved_yaml.get("override_resolution", {})
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "applied_overrides": override_resolution.get("applied_overrides", []),
        "warnings": override_resolution.get("warnings", []),
    }


def load_workflow_hooks_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_hooks(session_factory, workflow_id=workflow.id)


def load_workflow_hooks_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_hooks(session_factory, workflow_id=workflow.id)


def load_workflow_hook_policy_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_hook_policy(session_factory, workflow_id=workflow.id)


def load_workflow_hook_policy_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_hook_policy(session_factory, workflow_id=workflow.id)


def load_workflow_hook_policy(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    hook_expansion = workflow.resolved_yaml.get("hook_expansion", {})
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "effective_policy": workflow.resolved_yaml.get("effective_policy", {}),
        "policy_impact": workflow.resolved_yaml.get("policy_impact", {}),
        "selected_hooks": hook_expansion.get("selected_hooks", []),
        "skipped_hooks": hook_expansion.get("skipped_hooks", []),
        "expanded_steps": hook_expansion.get("expanded_steps", []),
    }


def load_workflow_hooks(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    hook_expansion = workflow.resolved_yaml.get("hook_expansion", {})
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "selected_hooks": hook_expansion.get("selected_hooks", []),
        "skipped_hooks": hook_expansion.get("skipped_hooks", []),
        "expanded_steps": hook_expansion.get("expanded_steps", []),
    }


def load_workflow_rendering_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_workflow_rendering(session_factory, workflow_id=workflow.id)


def load_workflow_rendering_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_workflow_rendering(session_factory, workflow_id=workflow.id)


def load_workflow_rendering(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    rendering = workflow.resolved_yaml.get("rendering", {})
    compiled_subtasks = rendering.get("compiled_subtasks", [])
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "canonical_syntax": rendering.get("canonical_syntax"),
        "legacy_syntax_supported": rendering.get("legacy_syntax_supported", False),
        "compiled_subtask_count": len(compiled_subtasks),
        "compiled_subtasks": compiled_subtasks,
    }


def load_resolved_yaml_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    target_family: str | None = None,
    target_id: str | None = None,
) -> dict[str, object]:
    workflow = load_current_workflow(session_factory, logical_node_id=logical_node_id)
    return load_resolved_yaml(
        session_factory,
        workflow_id=workflow.id,
        target_family=target_family,
        target_id=target_id,
    )


def load_resolved_yaml_for_version(
    session_factory: sessionmaker[Session],
    *,
    version_id: UUID,
    target_family: str | None = None,
    target_id: str | None = None,
) -> dict[str, object]:
    workflow = load_node_version_workflow(session_factory, version_id=version_id)
    return load_resolved_yaml(
        session_factory,
        workflow_id=workflow.id,
        target_family=target_family,
        target_id=target_id,
    )


def load_resolved_yaml(
    session_factory: sessionmaker[Session],
    *,
    workflow_id: UUID,
    target_family: str | None = None,
    target_id: str | None = None,
) -> dict[str, object]:
    workflow = load_workflow(session_factory, workflow_id=workflow_id)
    documents = workflow.resolved_yaml.get("resolved_documents", [])
    if target_family is not None:
        documents = [item for item in documents if item.get("target_family") == target_family]
    if target_id is not None:
        documents = [item for item in documents if item.get("target_id") == target_id]
    return {
        "compiled_workflow_id": str(workflow.id),
        "node_version_id": str(workflow.node_version_id),
        "logical_node_id": str(workflow.logical_node_id),
        "compile_context": workflow.compile_context,
        "resolved_documents": documents,
        "warnings": workflow.resolved_yaml.get("override_resolution", {}).get("warnings", []),
    }


def list_compile_failures_for_node(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> list[CompileFailureSnapshot]:
    with query_session_scope(session_factory) as session:
        selector = _require_selector(session, logical_node_id)
        return _compile_failures_for_version(session, selector.authoritative_node_version_id)


def list_compile_failures_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> list[CompileFailureSnapshot]:
    with query_session_scope(session_factory) as session:
        return _compile_failures_for_version(session, version_id)


def list_compile_failures_for_workflow(session_factory: sessionmaker[Session], *, workflow_id: UUID) -> list[CompileFailureSnapshot]:
    with query_session_scope(session_factory) as session:
        workflow = session.get(CompiledWorkflow, workflow_id)
        if workflow is None:
            raise DaemonNotFoundError("compiled workflow not found")
        return _compile_failures_for_version(session, workflow.node_version_id)


def _compile_version(session: Session, version: NodeVersion, catalog: ResourceCatalog) -> CompiledWorkflowSnapshot:
    compile_context = _compile_context(session, version)
    try:
        ensure_builtin_structural_library(catalog)
    except ValueError as exc:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="invalid_structural_library",
            summary="Built-in structural YAML library is incomplete or invalid.",
            details_json={"message": str(exc)},
            target_family="structural_library",
            target_id="builtin_system",
        ) from exc
    try:
        ensure_builtin_quality_library(catalog)
    except ValueError as exc:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="invalid_quality_library",
            summary="Built-in quality YAML library is incomplete or invalid.",
            details_json={"message": str(exc)},
            target_family="quality_library",
            target_id="builtin_system",
        ) from exc
    try:
        ensure_builtin_operational_library(catalog)
    except ValueError as exc:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="invalid_operational_library",
            summary="Built-in runtime, hook, policy, or prompt library is incomplete or invalid.",
            details_json={"message": str(exc)},
            target_family="operational_library",
            target_id="builtin_system",
        ) from exc

    hierarchy_registry = load_hierarchy_registry(catalog)
    source_rows = _source_rows(session, version.id)
    bootstrap_resolution, parsed_by_path = _resolve_source_documents(
        version=version,
        source_rows=source_rows,
        allowed_targets={
            ("node_definition", version.node_kind),
            ("project_policy_definition", "default_project_policy"),
            ("runtime_policy_definition", "default_runtime_policy"),
            ("prompt_reference_definition", "default_prompt_refs"),
        },
    )

    bootstrap_node = bootstrap_resolution.document_for("node_definition", version.node_kind)
    if bootstrap_node is None:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary=f"Node definition for kind '{version.node_kind}' is missing.",
            details_json={"node_kind": version.node_kind},
            target_family="node_definition",
            target_id=version.node_kind,
        )
    bootstrap_project_policy_docs = _project_policy_documents_from_resolution(bootstrap_resolution)
    bootstrap_base_policy = _runtime_policy_document_from_resolution(bootstrap_resolution)
    bootstrap_effective_policy = resolve_effective_policy(
        catalog,
        hierarchy_registry=hierarchy_registry,
        base_policy_document=bootstrap_base_policy,
        project_policy_documents=bootstrap_project_policy_docs,
    )
    bootstrap_node_definition = NodeDefinitionDocument.model_validate(
        wrap_yaml_document_payload("node_definition", bootstrap_node.resolved_document)
    ).node_definition

    _ensure_compile_sources(
        session,
        version=version,
        catalog=catalog,
        node_definition=bootstrap_node_definition,
        prompt_pack=bootstrap_effective_policy.prompt_pack,
        effective_hook_refs=bootstrap_effective_policy.hook_refs,
        resolved_documents={
            (item.target_family, item.target_id): item for item in bootstrap_resolution.resolved_documents
        },
    )
    session.flush()

    source_rows = _source_rows(session, version.id)
    override_resolution, parsed_by_path = _resolve_source_documents(version=version, source_rows=source_rows)

    resolved_documents = {
        (item.target_family, item.target_id): item for item in override_resolution.resolved_documents
    }

    node_document = resolved_documents.get(("node_definition", version.node_kind))
    if node_document is None:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary=f"Node definition for kind '{version.node_kind}' is missing.",
            details_json={"node_kind": version.node_kind},
            target_family="node_definition",
            target_id=version.node_kind,
        )

    node_definition = NodeDefinitionDocument.model_validate(
        wrap_yaml_document_payload("node_definition", node_document.resolved_document)
    ).node_definition
    if not node_definition.available_tasks:
        raise WorkflowCompileError(
            failure_stage="workflow_compilation",
            failure_class="compiled_workflow_structure_failure",
            summary="Node definition resolved to an empty task list.",
            details_json={"node_kind": version.node_kind},
            target_family="node_definition",
            target_id=node_definition.kind,
        )

    base_policy_document = _runtime_policy_document_from_resolution(override_resolution)
    project_policy_documents = _project_policy_documents_from_resolution(override_resolution)
    effective_policy = resolve_effective_policy(
        catalog,
        hierarchy_registry=hierarchy_registry,
        base_policy_document=base_policy_document,
        project_policy_documents=project_policy_documents,
    )
    if _ensure_compile_sources(
        session,
        version=version,
        catalog=catalog,
        node_definition=node_definition,
        prompt_pack=effective_policy.prompt_pack,
        effective_hook_refs=effective_policy.hook_refs,
        resolved_documents=resolved_documents,
    ):
        session.flush()
        source_rows = _source_rows(session, version.id)
        override_resolution, parsed_by_path = _resolve_source_documents(version=version, source_rows=source_rows)
        resolved_documents = {
            (item.target_family, item.target_id): item for item in override_resolution.resolved_documents
        }
        node_document = resolved_documents.get(("node_definition", version.node_kind))
        if node_document is None:
            raise WorkflowCompileError(
                failure_stage="source_loading",
                failure_class="missing_source",
                summary=f"Node definition for kind '{version.node_kind}' is missing.",
                details_json={"node_kind": version.node_kind},
                target_family="node_definition",
                target_id=version.node_kind,
            )
        node_definition = NodeDefinitionDocument.model_validate(
            wrap_yaml_document_payload("node_definition", node_document.resolved_document)
        ).node_definition
        base_policy_document = _runtime_policy_document_from_resolution(override_resolution)
        project_policy_documents = _project_policy_documents_from_resolution(override_resolution)
        effective_policy = resolve_effective_policy(
            catalog,
            hierarchy_registry=hierarchy_registry,
            base_policy_document=base_policy_document,
            project_policy_documents=project_policy_documents,
        )
    policy_impact = policy_impact_for_node_kind(
        version.node_kind,
        catalog,
        hierarchy_registry=hierarchy_registry,
        base_policy_document=base_policy_document,
        project_policy_documents=project_policy_documents,
    )
    if not policy_impact.enabled_for_node_kind:
        raise WorkflowCompileError(
            failure_stage="policy_resolution",
            failure_class="policy_resolution_failure",
            summary=f"Project policy disables node kind '{version.node_kind}'.",
            details_json={"node_kind": version.node_kind, "enabled_node_kinds": effective_policy.enabled_node_kinds},
            target_family="project_policy_definition",
            target_id="enabled_node_kinds",
        )

    prompt_relative_path = node_definition.main_prompt.removeprefix("prompts/")
    prompt_group = "prompt_project" if effective_policy.prompt_pack == "project" else "prompt_pack_default"
    prompt_source = next(
        (
            source
            for _, source in source_rows
            if source.relative_path == prompt_relative_path and source.source_group == prompt_group
        ),
        None,
    )
    if prompt_source is None:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary=f"Prompt template '{prompt_relative_path}' is missing.",
            details_json={"prompt_path": prompt_relative_path, "prompt_group": prompt_group},
            target_family="prompt_template",
            target_id=prompt_relative_path,
        )

    selected_hooks, skipped_hooks = _resolve_selected_hooks(
        version=version,
        node_definition=node_definition,
        effective_hook_refs=effective_policy.hook_refs,
        resolved_documents=resolved_documents,
        source_rows=source_rows,
    )
    source_hash = _ordered_source_hash(source_rows)
    resolved_yaml = {
        "compiler_version": 1,
        "built_in_library_version": BUILTIN_LIBRARY_VERSION,
        "compile_context": compile_context,
        "node_version": {
            "id": str(version.id),
            "logical_node_id": str(version.logical_node_id),
            "node_kind": version.node_kind,
            "title": version.title,
            "prompt": version.prompt,
            "version_number": version.version_number,
        },
        "node_definition": node_definition.model_dump(),
        "effective_policy": effective_policy.to_payload(),
        "policy_impact": policy_impact.to_payload(),
        "override_resolution": override_resolution.to_payload(),
        "resolved_documents": [item.to_payload() for item in override_resolution.resolved_documents],
        "sources": [
            {
                "source_group": source.source_group,
                "relative_path": source.relative_path,
                "doc_family": source.doc_family,
                "source_role": link.source_role,
                "content_hash": source.content_hash,
            }
            for link, source in source_rows
        ],
    }

    try:
        workflow = CompiledWorkflow(
            id=uuid4(),
            node_version_id=version.id,
            source_hash=source_hash,
            resolved_yaml=resolved_yaml,
        )
        session.add(workflow)
        session.flush()

        for link, source in source_rows:
            session.add(
                CompiledWorkflowSource(
                    compiled_workflow_id=workflow.id,
                    source_document_id=source.id,
                    source_role=link.source_role,
                )
            )

        previous_subtask_id: UUID | None = None
        task_snapshots: list[CompiledTaskSnapshot] = []
        all_expanded_steps: list[HookExpansionStep] = []
        rendering_payloads: list[dict[str, object]] = []
        for task_ordinal, task_key in enumerate(node_definition.available_tasks, start=1):
            task_relative_path = f"tasks/{task_key}.yaml"
            task_source = next(
                (
                    source
                    for _, source in source_rows
                    if source.relative_path == task_relative_path and source.source_group == "yaml_builtin_system"
                ),
                None,
            )
            task_document = resolved_documents.get(("task_definition", task_key))
            if task_source is None or task_document is None:
                raise WorkflowCompileError(
                    failure_stage="source_loading",
                    failure_class="missing_source",
                    summary=f"Task definition '{task_key}' is missing.",
                    details_json={"task_key": task_key, "relative_path": task_relative_path},
                    target_family="task_definition",
                    target_id=task_key,
                )

            task_doc = task_document.resolved_document
            first_subtask_doc = dict(task_doc["subtasks"][0]) if task_doc.get("subtasks") else {
                "id": "main",
                "type": "run_prompt",
                "title": _humanize(task_key),
                "prompt": f"prompts/{prompt_relative_path}",
                "retry_policy": {"max_attempts": effective_policy.defaults.get("max_subtask_retries", node_definition.policies.max_subtask_retries)},
                "checks": [],
                "outputs": [],
            }
            task = CompiledTask(
                id=uuid4(),
                compiled_workflow_id=workflow.id,
                task_key=task_key,
                ordinal=task_ordinal,
                title=task_doc.get("name", _humanize(task_key)),
                description=task_doc.get("description", f"Compiled task for {task_key}."),
                config_json={
                    "task_definition": task_doc,
                    "entry_task": task_key == node_definition.entry_task,
                    "node_kind": node_definition.kind,
                    "effective_policy": effective_policy.to_payload(),
                },
            )
            session.add(task)
            session.flush()

            expanded_steps = _expand_hook_steps_for_task(
                selected_hooks=selected_hooks,
                version=version,
                node_definition=node_definition,
                task_key=task_key,
                task_doc=task_doc,
                base_subtask=first_subtask_doc,
                is_first_task=task_ordinal == 1,
                is_last_task=task_ordinal == len(node_definition.available_tasks),
            )
            all_expanded_steps.extend(expanded_steps)
            compiled_subtasks: list[CompiledSubtaskSnapshot] = []
            for subtask_ordinal, compiled_definition in enumerate(
                _materialize_task_subtask_definitions(
                    catalog=catalog,
                    version=version,
                    node_definition=node_definition,
                    task_key=task_key,
                    task_doc=task_doc,
                    task_source=task_source,
                    base_subtask=first_subtask_doc,
                    expanded_steps=expanded_steps,
                    prompt_pack=effective_policy.prompt_pack,
                    prompt_group=prompt_group,
                    default_retry_limit=int(
                        first_subtask_doc.get(
                            "retry_policy", {}
                        ).get(
                            "max_attempts",
                            effective_policy.defaults.get("max_subtask_retries", node_definition.policies.max_subtask_retries),
                        )
                    ),
                    resolved_documents=resolved_documents,
                    effective_policy=effective_policy,
                ),
                start=1,
            ):
                subtask = CompiledSubtask(
                    id=uuid4(),
                    compiled_workflow_id=workflow.id,
                    compiled_task_id=task.id,
                    source_subtask_key=compiled_definition["source_subtask_key"],
                    ordinal=subtask_ordinal,
                    subtask_type=compiled_definition["subtask_type"],
                    title=compiled_definition["title"],
                    prompt_text=compiled_definition["prompt_text"],
                    command_text=compiled_definition["command_text"],
                    environment_policy_ref=compiled_definition["environment_policy_ref"],
                    environment_request_json=compiled_definition["environment_request_json"],
                    retry_policy_json=compiled_definition["retry_policy_json"],
                    block_on_user_flag=compiled_definition["block_on_user_flag"],
                    pause_summary_prompt=compiled_definition["pause_summary_prompt"],
                    source_file_path=compiled_definition["source_file_path"],
                    source_hash=compiled_definition["source_hash"],
                    inserted_by_hook=compiled_definition["inserted_by_hook"],
                    inserted_by_hook_id=compiled_definition["inserted_by_hook_id"],
                )
                session.add(subtask)
                session.flush()
                depends_on_ids: list[UUID] = []
                if previous_subtask_id is not None:
                    session.add(
                        CompiledSubtaskDependency(
                            compiled_subtask_id=subtask.id,
                            depends_on_compiled_subtask_id=previous_subtask_id,
                        )
                    )
                    depends_on_ids.append(previous_subtask_id)
                previous_subtask_id = subtask.id
                rendering_payloads.append(compiled_definition["rendering"])
                compiled_subtasks.append(
                    CompiledSubtaskSnapshot(
                        id=subtask.id,
                        compiled_task_id=task.id,
                        source_subtask_key=subtask.source_subtask_key,
                        ordinal=subtask.ordinal,
                        subtask_type=subtask.subtask_type,
                        title=subtask.title,
                        prompt_text=subtask.prompt_text,
                        command_text=subtask.command_text,
                        environment_policy_ref=subtask.environment_policy_ref,
                        environment_request_json=subtask.environment_request_json,
                        retry_policy_json=subtask.retry_policy_json,
                        block_on_user_flag=subtask.block_on_user_flag,
                        pause_summary_prompt=subtask.pause_summary_prompt,
                        source_file_path=subtask.source_file_path,
                        source_hash=subtask.source_hash,
                        inserted_by_hook=subtask.inserted_by_hook,
                        inserted_by_hook_id=subtask.inserted_by_hook_id,
                        depends_on_compiled_subtask_ids=depends_on_ids,
                    )
                )
            task_snapshots.append(
                CompiledTaskSnapshot(
                    id=task.id,
                    task_key=task.task_key,
                    ordinal=task.ordinal,
                    title=task.title,
                    description=task.description,
                    config_json=task.config_json,
                    subtasks=compiled_subtasks,
                )
            )

        hook_expansion_payload = {
            "selected_hooks": [item.to_payload() for item in selected_hooks],
            "skipped_hooks": [item.to_payload() for item in skipped_hooks],
            "expanded_steps": [item.to_payload() for item in all_expanded_steps],
        }
        rendering = {
            "canonical_syntax": "{{variable}}",
            "legacy_compatibility_syntax": "<variable>",
            "renderable_fields": ["prompt", "command", "pause_summary_prompt"],
            "non_renderable_fields": ["args", "env", "checks", "outputs", "retry_policy"],
            "compiled_subtasks": rendering_payloads,
        }
        resolved_yaml = {**resolved_yaml, "hook_expansion": hook_expansion_payload, "rendering": rendering}
        workflow.resolved_yaml = resolved_yaml
        version.compiled_workflow_id = workflow.id
        session.flush()
        return _workflow_snapshot(session, workflow.id)
    except WorkflowCompileError:
        raise
    except Exception as exc:
        raise WorkflowCompileError(
            failure_stage="workflow_persistence",
            failure_class="workflow_persistence_failure",
            summary="Failed to persist compiled workflow artifacts.",
            details_json={
                "error_type": exc.__class__.__name__,
                "error": str(exc),
                "node_version_id": str(version.id),
            },
        ) from exc


def _workflow_snapshot(session: Session, workflow_id: UUID) -> CompiledWorkflowSnapshot:
    workflow = session.get(CompiledWorkflow, workflow_id)
    if workflow is None:
        raise DaemonNotFoundError("compiled workflow not found")
    version = session.get(NodeVersion, workflow.node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    task_rows = session.execute(
        select(CompiledTask).where(CompiledTask.compiled_workflow_id == workflow_id).order_by(CompiledTask.ordinal)
    ).scalars().all()
    subtask_rows = session.execute(
        select(CompiledSubtask).where(CompiledSubtask.compiled_workflow_id == workflow_id).order_by(CompiledSubtask.compiled_task_id, CompiledSubtask.ordinal)
    ).scalars().all()
    deps = _dependency_map(session, workflow_id)
    subtasks_by_task: dict[UUID, list[CompiledSubtaskSnapshot]] = {}
    for subtask in subtask_rows:
        subtasks_by_task.setdefault(subtask.compiled_task_id, []).append(
            CompiledSubtaskSnapshot(
                id=subtask.id,
                compiled_task_id=subtask.compiled_task_id,
                source_subtask_key=subtask.source_subtask_key,
                ordinal=subtask.ordinal,
                subtask_type=subtask.subtask_type,
                title=subtask.title,
                prompt_text=subtask.prompt_text,
                command_text=subtask.command_text,
                environment_policy_ref=subtask.environment_policy_ref,
                environment_request_json=subtask.environment_request_json,
                retry_policy_json=subtask.retry_policy_json,
                block_on_user_flag=subtask.block_on_user_flag,
                pause_summary_prompt=subtask.pause_summary_prompt,
                source_file_path=subtask.source_file_path,
                source_hash=subtask.source_hash,
                inserted_by_hook=subtask.inserted_by_hook,
                inserted_by_hook_id=subtask.inserted_by_hook_id,
                depends_on_compiled_subtask_ids=deps.get(subtask.id, []),
            )
        )
    tasks = [
        CompiledTaskSnapshot(
            id=task.id,
            task_key=task.task_key,
            ordinal=task.ordinal,
            title=task.title,
            description=task.description,
            config_json=task.config_json,
            subtasks=subtasks_by_task.get(task.id, []),
        )
        for task in task_rows
    ]
    source_count = session.execute(
        select(CompiledWorkflowSource).where(CompiledWorkflowSource.compiled_workflow_id == workflow_id)
    ).scalars().all()
    return CompiledWorkflowSnapshot(
        id=workflow.id,
        node_version_id=workflow.node_version_id,
        logical_node_id=version.logical_node_id,
        source_hash=workflow.source_hash,
        built_in_library_version=workflow.resolved_yaml.get("built_in_library_version", BUILTIN_LIBRARY_VERSION),
        created_at=workflow.created_at.isoformat(),
        source_document_count=len(source_count),
        task_count=len(tasks),
        subtask_count=sum(len(item.subtasks) for item in tasks),
        compile_context=workflow.resolved_yaml.get("compile_context", {}),
        resolved_yaml=workflow.resolved_yaml,
        tasks=tasks,
    )


def _compile_context(session: Session, version: NodeVersion) -> dict[str, object]:
    rebuild_event = session.execute(
        select(RebuildEvent)
        .where(RebuildEvent.target_node_version_id == version.id)
        .order_by(RebuildEvent.created_at.desc())
    ).scalars().first()
    compile_variant = "authoritative"
    rebuild_context: dict[str, object] | None = None
    if version.status == "candidate":
        if rebuild_event is None:
            compile_variant = "candidate"
        else:
            compile_variant = "rebuild_candidate"
            rebuild_context = {
                "rebuild_event_id": str(rebuild_event.id),
                "root_logical_node_id": str(rebuild_event.root_logical_node_id),
                "root_node_version_id": str(rebuild_event.root_node_version_id),
                "event_kind": rebuild_event.event_kind,
                "event_status": rebuild_event.event_status,
                "scope": rebuild_event.scope,
                "trigger_reason": rebuild_event.trigger_reason,
            }
    return {
        "compile_variant": compile_variant,
        "version_status": version.status,
        "version_number": version.version_number,
        "rebuild_context": rebuild_context,
    }


def _compile_failures_for_version(session: Session, node_version_id: UUID) -> list[CompileFailureSnapshot]:
    version = session.get(NodeVersion, node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    rows = session.execute(
        select(CompileFailure)
        .where(CompileFailure.node_version_id == node_version_id)
        .order_by(CompileFailure.created_at.desc())
    ).scalars().all()
    return [
        CompileFailureSnapshot(
            id=row.id,
            node_version_id=row.node_version_id,
            logical_node_id=version.logical_node_id,
            failure_stage=row.failure_stage,
            failure_class=row.failure_class,
            summary=row.summary,
            details_json=row.details_json,
            source_hash=row.source_hash,
            target_family=row.target_family,
            target_id=row.target_id,
            compile_context=row.details_json.get("compile_context", {}),
            created_at=row.created_at.isoformat(),
        )
        for row in rows
    ]


def _persist_compile_failure(
    session: Session,
    version: NodeVersion,
    exc: WorkflowCompileError,
    *,
    compile_context: dict[str, object],
) -> CompileFailureSnapshot:
    source_hash = _latest_source_hash(session, version.id)
    details_json = {**exc.details_json, "compile_context": compile_context}
    row = CompileFailure(
        id=uuid4(),
        node_version_id=version.id,
        failure_stage=exc.failure_stage,
        failure_class=exc.failure_class,
        summary=exc.summary,
        details_json=details_json,
        source_hash=source_hash,
        target_family=exc.target_family,
        target_id=exc.target_id,
    )
    session.add(row)
    session.flush()
    return CompileFailureSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        logical_node_id=version.logical_node_id,
        failure_stage=row.failure_stage,
        failure_class=row.failure_class,
        summary=row.summary,
        details_json=row.details_json,
        source_hash=row.source_hash,
        target_family=row.target_family,
        target_id=row.target_id,
        compile_context=compile_context,
        created_at=row.created_at.isoformat(),
    )


def _latest_source_hash(session: Session, node_version_id: UUID) -> str | None:
    rows = session.execute(
        select(NodeVersionSourceDocument, SourceDocument)
        .join(SourceDocument, NodeVersionSourceDocument.source_document_id == SourceDocument.id)
        .where(NodeVersionSourceDocument.node_version_id == node_version_id)
        .order_by(NodeVersionSourceDocument.resolution_order)
    ).all()
    if not rows:
        return None
    return _ordered_source_hash(rows)


def _ordered_source_hash(rows: list[tuple[NodeVersionSourceDocument, SourceDocument]]) -> str:
    digest = sha256()
    for link, source in rows:
        digest.update(f"{link.resolution_order}:{source.relative_path}:{source.content_hash}:{link.source_role}\n".encode("utf-8"))
    return digest.hexdigest()


def _json_safe_validation_errors(exc: ValidationError) -> list[dict[str, object]]:
    sanitized: list[dict[str, object]] = []
    for item in exc.errors():
        normalized: dict[str, object] = {}
        for key, value in item.items():
            if key == "ctx" and isinstance(value, dict):
                normalized[key] = {ctx_key: str(ctx_value) for ctx_key, ctx_value in value.items()}
            else:
                normalized[key] = value
        sanitized.append(normalized)
    return sanitized


def _source_rows(session: Session, node_version_id: UUID) -> list[tuple[NodeVersionSourceDocument, SourceDocument]]:
    return session.execute(
        select(NodeVersionSourceDocument, SourceDocument)
        .join(SourceDocument, NodeVersionSourceDocument.source_document_id == SourceDocument.id)
        .where(NodeVersionSourceDocument.node_version_id == node_version_id)
        .order_by(NodeVersionSourceDocument.resolution_order)
    ).all()


def _project_policy_documents_from_resolution(override_resolution) -> list[tuple[str, ProjectPolicyDefinitionDocument]]:
    documents: list[tuple[str, ProjectPolicyDefinitionDocument]] = []
    for item in override_resolution.resolved_documents:
        if item.target_family != "project_policy_definition":
            continue
        documents.append(
            (
                item.relative_path,
                ProjectPolicyDefinitionDocument.model_validate(item.resolved_document),
            )
        )
    return documents


def _runtime_policy_document_from_resolution(override_resolution) -> RuntimePolicyDefinitionDocument:
    item = override_resolution.document_for("runtime_policy_definition", "default_runtime_policy")
    if item is None:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary="Runtime policy 'default_runtime_policy' is missing.",
            details_json={"target_id": "default_runtime_policy"},
            target_family="runtime_policy_definition",
            target_id="default_runtime_policy",
        )
    return RuntimePolicyDefinitionDocument.model_validate(item.resolved_document)


def _override_documents_from_source_rows(
    source_rows: list[tuple[NodeVersionSourceDocument, SourceDocument]],
    *,
    logical_node_kind: str,
) -> list[OverrideSourceSnapshot]:
    documents: list[OverrideSourceSnapshot] = []
    for _, source in source_rows:
        if source.source_group != "yaml_overrides":
            continue
        raw = yaml.safe_load(source.content) or {}
        if raw.get("target_family") == "node_definition" and str(raw.get("target_id", "")).strip() != logical_node_kind:
            continue
        documents.append(
            OverrideSourceSnapshot(
                relative_path=source.relative_path,
                document=FAMILY_MODELS["override_definition"].model_validate(raw),
                content_hash=source.content_hash,
            )
        )
    return documents


def _ensure_compile_sources(
    session: Session,
    *,
    version: NodeVersion,
    catalog: ResourceCatalog,
    node_definition,
    prompt_pack: str,
    effective_hook_refs: list[str],
    resolved_documents: dict[tuple[str, str], object],
) -> bool:
    added_sources = False
    source_rows = _source_rows(session, version.id)
    captured_keys = {
        (source.source_group, source.relative_path, link.source_role)
        for link, source in source_rows
    }
    next_order = max((link.resolution_order for link, _ in source_rows), default=0) + 10
    prompt_group = "prompt_project" if prompt_pack == "project" else "prompt_pack_default"
    prompt_relative_path = node_definition.main_prompt.removeprefix("prompts/")
    next_order, did_add = _ensure_source_document_link(
        session,
        node_version_id=version.id,
        catalog=catalog,
        source_group=prompt_group,
        relative_path=prompt_relative_path,
        source_role="prompt_template",
        resolution_order=next_order,
        captured_keys=captured_keys,
    )
    added_sources = added_sources or did_add
    for task_key in node_definition.available_tasks:
        task_relative_path = f"tasks/{task_key}.yaml"
        next_order, did_add = _ensure_source_document_link(
            session,
            node_version_id=version.id,
            catalog=catalog,
            source_group="yaml_builtin_system",
            relative_path=task_relative_path,
            source_role="base_definition",
            resolution_order=next_order,
            captured_keys=captured_keys,
        )
        added_sources = added_sources or did_add
        task_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", task_relative_path)) or {}
        for subtask in task_doc.get("subtasks", []):
            environment_ref = str(subtask.get("environment_policy_ref", "")).strip()
            if not environment_ref:
                continue
            environment_relative_path = normalize_environment_relative_path(environment_ref)
            environment_source_group = "yaml_project" if (catalog.yaml_project_dir / environment_relative_path).exists() else "yaml_builtin_system"
            next_order, did_add = _ensure_source_document_link(
                session,
                node_version_id=version.id,
                catalog=catalog,
                source_group=environment_source_group,
                relative_path=environment_relative_path,
                source_role="policy_definition",
                resolution_order=next_order,
                captured_keys=captured_keys,
            )
            added_sources = added_sources or did_add
        for review_ref in task_doc.get("uses_reviews", []):
            review_relative_path = _normalize_review_relative_path(str(review_ref))
            next_order, did_add = _ensure_source_document_link(
                session,
                node_version_id=version.id,
                catalog=catalog,
                source_group="yaml_builtin_system",
                relative_path=review_relative_path,
                source_role="base_definition",
                resolution_order=next_order,
                captured_keys=captured_keys,
            )
            added_sources = added_sources or did_add
            review_doc = yaml.safe_load(catalog.read_text("yaml_builtin_system", review_relative_path)) or {}
            review_prompt = str(review_doc.get("prompt", "")).strip()
            if review_prompt:
                next_order, did_add = _ensure_source_document_link(
                    session,
                    node_version_id=version.id,
                    catalog=catalog,
                    source_group=prompt_group,
                    relative_path=review_prompt.removeprefix("prompts/"),
                    source_role="prompt_template",
                    resolution_order=next_order,
                    captured_keys=captured_keys,
                )
                added_sources = added_sources or did_add
        for testing_ref in task_doc.get("uses_testing", []):
            testing_source_group, testing_relative_path = _resolve_testing_source(str(testing_ref), catalog)
            next_order, did_add = _ensure_source_document_link(
                session,
                node_version_id=version.id,
                catalog=catalog,
                source_group=testing_source_group,
                relative_path=testing_relative_path,
                source_role="base_definition",
                resolution_order=next_order,
                captured_keys=captured_keys,
            )
            added_sources = added_sources or did_add
    for hook_ref in _normalize_hook_refs([*effective_hook_refs, *list(node_definition.hooks)]):
        resolved_hook = next(
            (
                item
                for item in resolved_documents.values()
                if item.target_family == "hook_definition" and item.relative_path == hook_ref
            ),
            None,
        )
        hook_source_group = (
            resolved_hook.source_group
            if resolved_hook is not None
            else ("yaml_project" if (catalog.yaml_project_dir / hook_ref).exists() else "yaml_builtin_system")
        )
        next_order, did_add = _ensure_source_document_link(
            session,
            node_version_id=version.id,
            catalog=catalog,
            source_group=hook_source_group,
            relative_path=hook_ref,
            source_role="base_definition",
            resolution_order=next_order,
            captured_keys=captured_keys,
        )
        added_sources = added_sources or did_add
        hook_payload = (
            resolved_hook.resolved_document
            if resolved_hook is not None
            else yaml.safe_load(catalog.read_text(hook_source_group, hook_ref)) or {}
        )
        hook_document = HookDefinitionDocument.model_validate(hook_payload)
        for step in hook_document.run:
            if not step.prompt:
                continue
            next_order, did_add = _ensure_source_document_link(
                session,
                node_version_id=version.id,
                catalog=catalog,
                source_group=prompt_group,
                relative_path=step.prompt.removeprefix("prompts/"),
                source_role="prompt_template",
                resolution_order=next_order,
                captured_keys=captured_keys,
            )
            added_sources = added_sources or did_add
    layout_relative_path = _default_layout_for_kind(version.node_kind)
    if layout_relative_path is not None:
        _, did_add = _ensure_source_document_link(
            session,
            node_version_id=version.id,
            catalog=catalog,
            source_group="yaml_builtin_system",
            relative_path=layout_relative_path,
            source_role="base_definition",
            resolution_order=next_order,
            captured_keys=captured_keys,
        )
        added_sources = added_sources or did_add
    return added_sources


def _ensure_source_document_link(
    session: Session,
    *,
    node_version_id: UUID,
    catalog: ResourceCatalog,
    source_group: str,
    relative_path: str,
    source_role: str,
    resolution_order: int,
    captured_keys: set[tuple[str, str, str]],
) -> tuple[int, bool]:
    key = (source_group, relative_path, source_role)
    if key in captured_keys:
        return resolution_order, False
    existing_link = session.execute(
        select(NodeVersionSourceDocument, SourceDocument)
        .join(SourceDocument, NodeVersionSourceDocument.source_document_id == SourceDocument.id)
        .where(NodeVersionSourceDocument.node_version_id == node_version_id)
        .where(NodeVersionSourceDocument.source_role == source_role)
        .where(SourceDocument.source_group == source_group)
        .where(SourceDocument.relative_path == relative_path)
    ).first()
    if existing_link is not None:
        captured_keys.add(key)
        return resolution_order, False
    next_order, did_add = _persist_missing_source_document(
        session,
        node_version_id=node_version_id,
        catalog=catalog,
        source_group=source_group,
        relative_path=relative_path,
        source_role=source_role,
        resolution_order=resolution_order,
    )
    if did_add:
        captured_keys.add(key)
    return next_order, did_add


def _persist_missing_source_document(
    session: Session,
    *,
    node_version_id: UUID,
    catalog: ResourceCatalog,
    source_group: str,
    relative_path: str,
    source_role: str,
    resolution_order: int,
) -> tuple[int, bool]:
    try:
        content = catalog.read_text(source_group, relative_path)
    except FileNotFoundError as exc:
        target_family = "prompt_template" if source_group.startswith("prompt_") else identify_yaml_family(relative_path, source_group)
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary=f"Required source '{relative_path}' is missing.",
            details_json={"source_group": source_group, "relative_path": relative_path},
            target_family=target_family,
            target_id=relative_path,
        ) from exc
    content_hash = sha256(content.encode("utf-8")).hexdigest()
    doc_family = "prompt_template" if source_group.startswith("prompt_") else identify_yaml_family(relative_path, source_group)
    source_document = (
        session.execute(
            select(SourceDocument).where(
                SourceDocument.source_group == source_group,
                SourceDocument.relative_path == relative_path,
                SourceDocument.content_hash == content_hash,
            )
        )
        .scalars()
        .first()
    )
    if source_document is None:
        source_document = SourceDocument(
            id=uuid4(),
            source_group=source_group,
            relative_path=relative_path,
            doc_family=doc_family,
            source_role=source_role,
            merge_mode="direct",
            content=content,
            content_hash=content_hash,
        )
        session.add(source_document)
        session.flush()
    session.add(
        NodeVersionSourceDocument(
            id=uuid4(),
            node_version_id=node_version_id,
            source_document_id=source_document.id,
            source_role=source_role,
            resolution_order=resolution_order,
            is_resolved_input=True,
        )
    )
    return resolution_order + 10, True


def _resolve_source_documents(
    *,
    version: NodeVersion,
    source_rows: list[tuple[NodeVersionSourceDocument, SourceDocument]],
    allowed_targets: set[tuple[str, str]] | None = None,
) -> tuple[object, dict[str, dict[str, object]]]:
    if not source_rows:
        raise WorkflowCompileError(
            failure_stage="source_discovery",
            failure_class="missing_source",
            summary="No source documents were captured for the selected node version.",
        )
    parsed_by_path: dict[str, dict[str, object]] = {}
    for _, source in source_rows:
        if not source.source_group.startswith("yaml_"):
            continue
        family = identify_yaml_family(source.relative_path, source.source_group)
        raw = yaml.safe_load(source.content) or {}
        validation_payload = unwrap_yaml_document_payload(family, raw) if family == "project_policy_definition" else raw
        try:
            FAMILY_MODELS[family].model_validate(validation_payload)
        except ValidationError as exc:
            raise WorkflowCompileError(
                failure_stage="schema_validation",
                failure_class="schema_validation_failure",
                summary=f"Schema validation failed for {source.relative_path}.",
                details_json={"errors": _json_safe_validation_errors(exc), "relative_path": source.relative_path},
                target_family=family,
                target_id=source.relative_path,
            ) from exc
        if source.source_group != "yaml_overrides":
            parsed_by_path[source.relative_path] = unwrap_yaml_document_payload(family, raw)
    try:
        source_inputs = [
            SourceDocumentInput(
                source_group=source.source_group,
                relative_path=source.relative_path,
                source_role=link.source_role,
                content=source.content,
                content_hash=source.content_hash,
            )
            for link, source in source_rows
        ]
        resolution = resolve_overrides(
            build_base_document_index(source_inputs),
            _override_documents_from_source_rows(source_rows, logical_node_kind=version.node_kind),
            built_in_library_version=BUILTIN_LIBRARY_VERSION,
            allowed_targets=allowed_targets,
        )
    except OverrideResolutionError as exc:
        raise WorkflowCompileError(
            failure_stage="override_resolution",
            failure_class=exc.failure_class,
            summary=exc.summary,
            details_json=exc.details_json,
            target_family=exc.target_family,
            target_id=exc.target_id,
        ) from exc
    return resolution, parsed_by_path


def _resolve_selected_hooks(
    *,
    version: NodeVersion,
    node_definition,
    effective_hook_refs: list[str],
    resolved_documents: dict[tuple[str, str], object],
    source_rows: list[tuple[NodeVersionSourceDocument, SourceDocument]],
) -> tuple[list[ResolvedHookDocument], list[HookExpansionSkip]]:
    source_hashes = {
        (source.source_group, source.relative_path): source.content_hash
        for _, source in source_rows
    }
    selected: list[ResolvedHookDocument] = []
    skipped: list[HookExpansionSkip] = []
    seen: set[tuple[str, str]] = set()
    for hook_ref in _normalize_hook_refs([*effective_hook_refs, *list(node_definition.hooks)]):
        resolved_hook = next(
            (
                item
                for item in resolved_documents.values()
                if item.target_family == "hook_definition" and item.relative_path == hook_ref
            ),
            None,
        )
        if resolved_hook is None:
            raise WorkflowCompileError(
                failure_stage="source_loading",
                failure_class="missing_source",
                summary=f"Hook definition '{hook_ref}' is missing.",
                details_json={"relative_path": hook_ref},
                target_family="hook_definition",
                target_id=hook_ref,
            )
        hook_document = HookDefinitionDocument.model_validate(resolved_hook.resolved_document)
        dedupe_key = (resolved_hook.source_group, resolved_hook.relative_path)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)
        if hook_document.if_.changed_entity_types or hook_document.if_.paths_match:
            skipped.append(
                HookExpansionSkip(
                    hook_id=hook_document.id,
                    when=hook_document.when,
                    relative_path=resolved_hook.relative_path,
                    source_group=resolved_hook.source_group,
                    reason="conditional_if_not_supported_at_compile_time",
                )
            )
            continue
        if hook_document.when in {"on_node_created", "on_merge_conflict"}:
            skipped.append(
                HookExpansionSkip(
                    hook_id=hook_document.id,
                    when=hook_document.when,
                    relative_path=resolved_hook.relative_path,
                    source_group=resolved_hook.source_group,
                    reason="runtime_only_trigger_not_materialized_during_compile",
                )
            )
            continue
        if not _hook_matches_node_scope(hook_document, node_kind=version.node_kind, tier=node_definition.tier):
            skipped.append(
                HookExpansionSkip(
                    hook_id=hook_document.id,
                    when=hook_document.when,
                    relative_path=resolved_hook.relative_path,
                    source_group=resolved_hook.source_group,
                    reason="hook_does_not_apply_to_resolved_node_scope",
                )
            )
            continue
        selected.append(
            ResolvedHookDocument(
                hook_id=hook_document.id,
                when=hook_document.when,
                relative_path=resolved_hook.relative_path,
                source_group=resolved_hook.source_group,
                applies_to=hook_document.applies_to.model_dump(),
                run_steps=[item.model_dump(by_alias=True) for item in hook_document.run],
                source_hash=source_hashes.get((resolved_hook.source_group, resolved_hook.relative_path)),
            )
        )
    selected.sort(
        key=lambda item: (
            _hook_phase_sort_key(item.when),
            _source_group_priority(item.source_group),
            item.relative_path,
            item.hook_id,
        )
    )
    skipped.sort(key=lambda item: (_source_group_priority(item.source_group), item.relative_path, item.hook_id))
    return selected, skipped


def _materialize_task_subtask_definitions(
    *,
    catalog: ResourceCatalog,
    version: NodeVersion,
    node_definition,
    task_key: str,
    task_doc: dict[str, object],
    task_source: SourceDocument,
    base_subtask: dict[str, object],
    expanded_steps: list[HookExpansionStep],
    prompt_pack: str,
    prompt_group: str,
    default_retry_limit: int,
    resolved_documents: dict[tuple[str, str], object],
    effective_policy,
) -> list[dict[str, object]]:
    before_steps = [item for item in expanded_steps if item.insertion_phase.startswith("before")]
    after_steps = [item for item in expanded_steps if item.insertion_phase.startswith("after")]
    materialized = [
        _compiled_subtask_definition_from_hook(
            catalog=catalog,
            version=version,
            node_definition=node_definition,
            task_key=task_key,
            task_doc=task_doc,
            step=step,
            prompt_pack=prompt_pack,
            prompt_group=prompt_group,
        )
        for step in before_steps
    ]
    materialized.append(
        _compiled_subtask_definition_from_base(
            catalog=catalog,
            version=version,
            node_definition=node_definition,
            task_key=task_key,
            task_doc=task_doc,
            task_source=task_source,
            base_subtask=base_subtask,
            prompt_pack=prompt_pack,
            prompt_group=prompt_group,
            default_retry_limit=default_retry_limit,
            resolved_documents=resolved_documents,
            effective_policy=effective_policy,
        )
    )
    materialized.extend(
        _compiled_subtask_definition_from_hook(
            catalog=catalog,
            version=version,
            node_definition=node_definition,
            task_key=task_key,
            task_doc=task_doc,
            step=step,
            prompt_pack=prompt_pack,
            prompt_group=prompt_group,
        )
        for step in after_steps
    )
    return materialized


def _compiled_subtask_definition_from_base(
    *,
    catalog: ResourceCatalog,
    version: NodeVersion,
    node_definition,
    task_key: str,
    task_doc: dict[str, object],
    task_source: SourceDocument,
    base_subtask: dict[str, object],
    prompt_pack: str,
    prompt_group: str,
    default_retry_limit: int,
    resolved_documents: dict[tuple[str, str], object],
    effective_policy,
) -> dict[str, object]:
    _ensure_no_illegal_render_targets(
        subtask_definition=base_subtask,
        task_key=task_key,
        source_subtask_key=str(base_subtask.get("id", "main")),
    )
    prompt_value = _effective_subtask_prompt_value(
        version=version,
        node_definition=node_definition,
        task_key=task_key,
        source_subtask_key=str(base_subtask.get("id", "main")),
        prompt_value=base_subtask.get("prompt"),
    )
    render_context = _build_subtask_render_context(
        version=version,
        task_key=task_key,
        task_doc=task_doc,
        source_subtask_key=str(base_subtask.get("id", "main")),
        prompt_pack=prompt_pack,
        prompt_relative_path=None if prompt_value is None else _render_source_relative_path(
            prompt_value=prompt_value,
            task_key=task_key,
            source_subtask_key=str(base_subtask.get("id", "main")),
        ),
        command_relative_path=f"{task_source.relative_path}#subtasks.{base_subtask.get('id', 'main')}.command",
        extra_context=base_subtask.get("render_context"),
    )
    prompt_info = _resolve_prompt_payload(
        catalog=catalog,
        version=version,
        node_definition=node_definition,
        task_key=task_key,
        source_subtask_key=str(base_subtask.get("id", "main")),
        prompt_value=prompt_value,
        task_doc=task_doc,
        prompt_pack=prompt_pack,
        prompt_group=prompt_group,
        render_context=render_context,
    )
    environment_request = _resolve_environment_request(
        base_subtask=base_subtask,
        resolved_documents=resolved_documents,
        catalog=catalog,
        effective_policy=effective_policy,
    )
    command_render = _render_optional_text(
        value=base_subtask.get("command"),
        context=render_context,
        field_name=f"{task_key}.{base_subtask.get('id', 'main')}.command",
    )
    pause_render = _render_optional_text(
        value=base_subtask.get("pause_summary_prompt"),
        context=render_context,
        field_name=f"{task_key}.{base_subtask.get('id', 'main')}.pause_summary_prompt",
    )
    prompt_text = prompt_info["prompt_text"]
    command_text = None if command_render is None else command_render.rendered_text
    if version.node_kind in {"epic", "phase", "plan"}:
        prompt_text = _wrap_parent_workflow_subtask_prompt(
            version=version,
            task_key=task_key,
            source_subtask_key=f"{task_key}.{base_subtask.get('id', 'main')}",
            title=str(base_subtask.get("title", _humanize(task_key))),
            subtask_type=str(base_subtask.get("type", "run_prompt")),
            prompt_text=prompt_text,
            command_text=command_text,
        )
    return {
        "source_subtask_key": f"{task_key}.{base_subtask.get('id', 'main')}",
        "subtask_type": str(base_subtask.get("type", "run_prompt")),
        "title": base_subtask.get("title", _humanize(task_key)),
        "prompt_text": prompt_text,
        "command_text": command_text,
        "environment_policy_ref": None if environment_request is None else environment_request["policy_ref"],
        "environment_request_json": environment_request,
        "retry_policy_json": {
            "max_retries": int(base_subtask.get("retry_policy", {}).get("max_attempts", default_retry_limit)),
            "checks": list(base_subtask.get("checks", [])),
            "outputs": list(base_subtask.get("outputs", [])),
            "on_failure": base_subtask.get("on_failure"),
        },
        "block_on_user_flag": None if base_subtask.get("block_on_user_flag") is None else str(base_subtask.get("block_on_user_flag")),
        "pause_summary_prompt": None if pause_render is None else pause_render.rendered_text,
        "source_file_path": task_source.relative_path,
        "source_hash": task_source.content_hash,
        "inserted_by_hook": False,
        "inserted_by_hook_id": None,
        "rendering": _rendering_payload(
            source_subtask_key=f"{task_key}.{base_subtask.get('id', 'main')}",
            prompt_result=prompt_info["render_result"],
            command_result=command_render,
            pause_result=pause_render,
            render_context=render_context,
        ),
    }


def _compiled_subtask_definition_from_hook(
    *,
    catalog: ResourceCatalog,
    version: NodeVersion,
    node_definition,
    task_key: str,
    task_doc: dict[str, object],
    step: HookExpansionStep,
    prompt_pack: str,
    prompt_group: str,
) -> dict[str, object]:
    _ensure_no_illegal_render_targets(
        subtask_definition={
            "args": None,
            "env": None,
            "checks": step.checks,
            "outputs": [],
            "retry_policy": None,
        },
        task_key=task_key,
        source_subtask_key=step.source_subtask_key,
    )
    render_context = _build_subtask_render_context(
        version=version,
        task_key=task_key,
        task_doc=task_doc,
        source_subtask_key=step.source_subtask_key,
        prompt_pack=prompt_pack,
        prompt_relative_path=None if step.prompt_path is None else _render_source_relative_path(
            prompt_value=step.prompt_path,
            task_key=task_key,
            source_subtask_key=step.source_subtask_key,
        ),
        command_relative_path=f"{step.relative_path}#run.{step.source_subtask_key}.command",
        hook_step=step,
        extra_context=step.render_context,
    )
    prompt_info = _resolve_prompt_payload(
        catalog=catalog,
        version=version,
        node_definition=node_definition,
        task_key=task_key,
        source_subtask_key=step.source_subtask_key,
        prompt_value=step.prompt_path,
        task_doc=task_doc,
        prompt_pack=prompt_pack,
        prompt_group=prompt_group,
        hook_step=step,
        render_context=render_context,
    )
    command_render = _render_optional_text(
        value=step.command_text,
        context=render_context,
        field_name=f"{step.source_subtask_key}.command",
    )
    prompt_text = prompt_info["prompt_text"]
    command_text = None if command_render is None else command_render.rendered_text
    if version.node_kind in {"epic", "phase", "plan"}:
        prompt_text = _wrap_parent_workflow_subtask_prompt(
            version=version,
            task_key=task_key,
            source_subtask_key=step.source_subtask_key,
            title=_humanize(step.source_subtask_key.split(".")[-1]),
            subtask_type=step.subtask_type,
            prompt_text=prompt_text,
            command_text=command_text,
        )
    return {
        "source_subtask_key": step.source_subtask_key,
        "subtask_type": step.subtask_type,
        "title": _humanize(step.source_subtask_key.split(".")[-1]),
        "prompt_text": prompt_text,
        "command_text": command_text,
        "environment_policy_ref": None,
        "environment_request_json": None,
        "retry_policy_json": {
            "max_retries": 0,
            "checks": step.checks,
            "outputs": [],
            "on_failure": None,
        },
        "block_on_user_flag": None,
        "pause_summary_prompt": None,
        "source_file_path": step.relative_path,
        "source_hash": step.source_hash,
        "inserted_by_hook": True,
        "inserted_by_hook_id": uuid5(NAMESPACE_URL, f"hook:{step.relative_path}:{step.source_subtask_key}"),
        "rendering": _rendering_payload(
            source_subtask_key=step.source_subtask_key,
            prompt_result=prompt_info["render_result"],
            command_result=command_render,
            pause_result=None,
            render_context=render_context,
        ),
    }


def _resolve_prompt_payload(
    *,
    catalog: ResourceCatalog,
    version: NodeVersion,
    node_definition,
    task_key: str,
    source_subtask_key: str,
    prompt_value: object,
    task_doc: dict[str, object],
    prompt_pack: str,
    prompt_group: str,
    render_context: RenderContext,
    hook_step: HookExpansionStep | None = None,
) -> dict[str, object]:
    if not isinstance(prompt_value, str) or not prompt_value:
        return {"prompt_text": None, "render_result": None}
    if prompt_value.startswith("prompts/") or prompt_value.endswith(".md"):
        prompt_relative_path = prompt_value.removeprefix("prompts/")
        if hook_step is None:
            prompt_text = catalog.read_text(prompt_group, prompt_relative_path)
            render_result = _render_prompt_body(
                template_text=prompt_text,
                context=render_context,
                field_name=f"{task_key}.{source_subtask_key}.prompt",
            )
            return {
                "prompt_text": _render_prompt(
                    render_result=render_result,
                    version=version,
                    task_key=task_key,
                    task_doc=task_doc,
                    prompt_relative_path=prompt_relative_path,
                    prompt_pack=prompt_pack,
                ),
                "render_result": render_result,
            }
        prompt_text = catalog.read_text(prompt_group, prompt_relative_path)
        render_result = _render_prompt_body(
            template_text=prompt_text,
            context=render_context,
            field_name=f"{task_key}.{source_subtask_key}.prompt",
        )
        return {
            "prompt_text": _render_hook_prompt(
                render_result=render_result,
                version=version,
                task_key=task_key,
                task_doc=task_doc,
                prompt_relative_path=prompt_relative_path,
                prompt_pack=prompt_pack,
                hook_step=hook_step,
            ),
            "render_result": render_result,
        }
    render_result = _render_prompt_body(
        template_text=prompt_value,
        context=render_context,
        field_name=f"{task_key}.{source_subtask_key}.prompt",
    )
    if hook_step is None:
        return {
            "prompt_text": _render_prompt(
                render_result=render_result,
                version=version,
                task_key=task_key,
                task_doc=task_doc,
                prompt_relative_path=f"inline/{task_key}/{source_subtask_key}",
                prompt_pack=prompt_pack,
            ),
            "render_result": render_result,
        }
    return {
        "prompt_text": _render_hook_prompt(
            render_result=render_result,
            version=version,
            task_key=task_key,
            task_doc=task_doc,
            prompt_relative_path=f"inline/{task_key}/{source_subtask_key}",
            prompt_pack=prompt_pack,
            hook_step=hook_step,
        ),
        "render_result": render_result,
    }


def _effective_subtask_prompt_value(
    *,
    version: NodeVersion,
    node_definition,
    task_key: str,
    source_subtask_key: str,
    prompt_value: object,
) -> object:
    if (
        task_key == "generate_child_layout"
        and source_subtask_key.endswith("render_layout_prompt")
        and version.node_kind in {"epic", "phase", "plan"}
    ):
        return str(node_definition.main_prompt)
    return prompt_value


def _resolve_environment_request(
    *,
    base_subtask: dict[str, object],
    resolved_documents: dict[tuple[str, str], object],
    catalog: ResourceCatalog,
    effective_policy,
) -> dict[str, object] | None:
    raw_ref = base_subtask.get("environment_policy_ref")
    if raw_ref is None:
        return None
    relative_path = normalize_environment_relative_path(str(raw_ref))
    resolved_environment = next(
        (
            item
            for item in resolved_documents.values()
            if item.target_family == "environment_policy_definition"
            and (
                item.relative_path == relative_path
                or item.target_id == str(raw_ref)
                or item.target_id == relative_path.rsplit("/", 1)[-1].removesuffix(".yaml")
            )
        ),
        None,
    )
    if resolved_environment is None:
        raise WorkflowCompileError(
            failure_stage="source_loading",
            failure_class="missing_source",
            summary=f"Environment policy '{raw_ref}' is missing.",
            details_json={"environment_policy_ref": str(raw_ref), "relative_path": relative_path},
            target_family="environment_policy_definition",
            target_id=str(raw_ref),
        )
    environment_document = EnvironmentPolicyDefinitionDocument.model_validate(resolved_environment.resolved_document)
    if (
        environment_document.isolation_mode == "custom_profile"
        and environment_document.runtime_profile not in effective_policy.environment_profiles
    ):
        raise WorkflowCompileError(
            failure_stage="environment_resolution",
            failure_class="environment_profile_undeclared",
            summary=f"Environment profile '{environment_document.runtime_profile}' is not enabled by project policy.",
            details_json={
                "environment_policy_ref": str(raw_ref),
                "runtime_profile": environment_document.runtime_profile,
                "declared_profiles": list(effective_policy.environment_profiles),
            },
            target_family="environment_policy_definition",
            target_id=environment_document.id,
        )
    return {
        "policy_ref": relative_path,
        "policy_id": environment_document.id,
        "source_group": resolved_environment.source_group,
        "relative_path": resolved_environment.relative_path,
        "isolation_mode": environment_document.isolation_mode,
        "allow_network": environment_document.allow_network,
        "runtime_profile": environment_document.runtime_profile,
        "mandatory": environment_document.mandatory,
        "profile_declared": (
            True
            if environment_document.runtime_profile is None
            else environment_document.runtime_profile in effective_policy.environment_profiles
        ),
        "supported_by_launcher": environment_document.isolation_mode in {"none", "custom_profile"},
    }


def _expand_hook_steps_for_task(
    *,
    selected_hooks: list[ResolvedHookDocument],
    version: NodeVersion,
    node_definition,
    task_key: str,
    task_doc: dict[str, object],
    base_subtask: dict[str, object],
    is_first_task: bool,
    is_last_task: bool,
) -> list[HookExpansionStep]:
    base_subtask_type = str(base_subtask.get("type", "run_prompt"))
    expanded: list[HookExpansionStep] = []
    for hook in selected_hooks:
        insertion_phase = _hook_insertion_phase(
            when=hook.when,
            task_key=task_key,
            is_first_task=is_first_task,
            is_last_task=is_last_task,
        )
        if insertion_phase is None:
            continue
        if not _resolved_hook_matches_task_scope(
            hook,
            node_kind=version.node_kind,
            tier=node_definition.tier,
            task_key=task_key,
            subtask_type=base_subtask_type,
        ):
            continue
        for step_index, run_step in enumerate(hook.run_steps, start=1):
            expanded.append(
                HookExpansionStep(
                    hook_id=hook.hook_id,
                    when=hook.when,
                    relative_path=hook.relative_path,
                    source_group=hook.source_group,
                    insertion_phase=insertion_phase,
                    task_key=task_key,
                    source_subtask_key=f"{task_key}.hook.{hook.hook_id}.{step_index}",
                    subtask_type=str(run_step.get("type", "run_prompt")),
                    prompt_path=None if run_step.get("prompt") is None else str(run_step.get("prompt")),
                    command_text=None if run_step.get("command") is None else str(run_step.get("command")),
                    render_context=dict(run_step.get("render_context") or {}),
                    checks=list(run_step.get("checks", [])),
                    source_hash=hook.source_hash,
                )
            )
    expanded.sort(
        key=lambda item: (
            0 if item.insertion_phase.startswith("before") else 1,
            _source_group_priority(item.source_group),
            item.relative_path,
            item.hook_id,
            item.source_subtask_key,
        )
    )
    return expanded


def _hook_matches_node_scope(hook_document: HookDefinitionDocument, *, node_kind: str, tier: int | str) -> bool:
    tiers = [str(item) for item in hook_document.applies_to.tiers]
    if tiers and str(tier) not in tiers:
        return False
    return not hook_document.applies_to.node_kinds or node_kind in hook_document.applies_to.node_kinds


def _resolved_hook_matches_task_scope(
    hook: ResolvedHookDocument,
    *,
    node_kind: str,
    tier: int | str,
    task_key: str,
    subtask_type: str,
) -> bool:
    applies_to = hook.applies_to
    tiers = [str(item) for item in applies_to.get("tiers", [])]
    if tiers and str(tier) not in tiers:
        return False
    node_kinds = [str(item) for item in applies_to.get("node_kinds", [])]
    if node_kinds and node_kind not in node_kinds:
        return False
    task_ids = [str(item) for item in applies_to.get("task_ids", [])]
    if task_ids and task_key not in task_ids:
        return False
    subtask_types = [str(item) for item in applies_to.get("subtask_types", [])]
    if subtask_types and subtask_type not in subtask_types:
        return False
    return True


def _hook_insertion_phase(*, when: str, task_key: str, is_first_task: bool, is_last_task: bool) -> str | None:
    if when == "before_node_run":
        return "before_task" if is_first_task else None
    if when == "before_node_complete":
        return "before_task" if is_last_task else None
    if when == "after_node_complete":
        return "after_task" if is_last_task else None
    if when.startswith("before_"):
        return "before_subtask" if when == "before_subtask" else "before_task"
    if when.startswith("after_"):
        return "after_subtask" if when == "after_subtask" else "after_task"
    return None


def _hook_phase_sort_key(when: str) -> tuple[int, str]:
    if when.startswith("before_") or when == "before_node_run":
        return (0, when)
    if when.startswith("after_"):
        return (1, when)
    return (2, when)


def _source_group_priority(source_group: str) -> int:
    return {"yaml_builtin_system": 0, "yaml_project": 1, "yaml_overrides": 2}.get(source_group, 99)


def _normalize_hook_refs(hook_refs: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for ref in hook_refs:
        relative_path = str(ref).removeprefix("hooks/")
        if not relative_path.endswith(".yaml"):
            relative_path = f"{relative_path}.yaml"
        normalized_ref = f"hooks/{relative_path}"
        if normalized_ref in seen:
            continue
        seen.add(normalized_ref)
        normalized.append(normalized_ref)
    return normalized


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


def _normalize_testing_relative_path(reference: str) -> str:
    relative_path = reference.removeprefix("testing/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    return f"testing/{relative_path}"


def _resolve_testing_source(reference: str, catalog: ResourceCatalog) -> tuple[str, str]:
    relative_path = _normalize_testing_relative_path(reference)
    if (catalog.yaml_project_dir / relative_path).exists():
        return "yaml_project", relative_path
    return "yaml_builtin_system", relative_path


def _dependency_map(session: Session, workflow_id: UUID) -> dict[UUID, list[UUID]]:
    rows = session.execute(
        select(CompiledSubtaskDependency)
        .join(CompiledSubtask, CompiledSubtaskDependency.compiled_subtask_id == CompiledSubtask.id)
        .where(CompiledSubtask.compiled_workflow_id == workflow_id)
    ).scalars().all()
    mapping: dict[UUID, list[UUID]] = {}
    for row in rows:
        mapping.setdefault(row.compiled_subtask_id, []).append(row.depends_on_compiled_subtask_id)
    return mapping


def _authoritative_version_id(session_factory: sessionmaker[Session], logical_node_id: UUID) -> UUID:
    with query_session_scope(session_factory) as session:
        selector = _require_selector(session, logical_node_id)
        return selector.authoritative_node_version_id


def _require_selector(session: Session, logical_node_id: UUID) -> LogicalNodeCurrentVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    return selector


def _ensure_no_live_run(session: Session, logical_node_id: UUID) -> None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    daemon_state = session.get(DaemonNodeState, str(logical_node_id))
    if lifecycle is not None and lifecycle.current_run_id is not None:
        raise DaemonConflictError("cannot compile a node with an active lifecycle run")
    if daemon_state is not None and daemon_state.current_run_id is not None:
        raise DaemonConflictError("cannot compile a node with an active daemon run")


def _update_lifecycle_after_compile(session: Session, logical_node_id: UUID, *, compiled: bool) -> None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None:
        return
    lifecycle.lifecycle_state = "COMPILED" if compiled else "COMPILE_FAILED"
    lifecycle.run_status = None
    lifecycle.current_run_id = None
    lifecycle.current_task_id = None
    lifecycle.current_subtask_id = None
    lifecycle.current_subtask_attempt = None
    lifecycle.last_completed_subtask_id = None
    lifecycle.execution_cursor_json = {}
    lifecycle.is_resumable = False
    lifecycle.pause_flag_name = None


def _humanize(value: str) -> str:
    return value.replace("_", " ").strip().title()


def _render_prompt(
    *,
    render_result,
    version: NodeVersion,
    task_key: str,
    task_doc: dict[str, object],
    prompt_relative_path: str,
    prompt_pack: str,
) -> str:
    return (
        f"Template Path: prompts/{prompt_relative_path}\n"
        f"Prompt Pack: {prompt_pack}\n\n"
        f"{render_result.rendered_text.strip()}\n\n"
        f"Node Title: {version.title}\n"
        f"Node Kind: {version.node_kind}\n"
        f"Node Version: {version.version_number}\n"
        f"Task Key: {task_key}\n\n"
        f"Node Prompt:\n{version.prompt.strip()}\n\n"
        f"Task Definition:\n{yaml.safe_dump(task_doc, sort_keys=False).strip()}\n"
    )


def _wrap_parent_workflow_subtask_prompt(
    *,
    version: NodeVersion,
    task_key: str,
    source_subtask_key: str,
    title: str,
    subtask_type: str,
    prompt_text: str | None,
    command_text: str | None,
) -> str:
    body = "" if prompt_text is None else prompt_text.strip()
    if command_text is not None:
        command_block = (
            "Execute this command for the current subtask after starting the attempt and inspecting context:\n"
            f"`{command_text}`"
        )
        body = f"{body}\n\n{command_block}".strip() if body else command_block
    success_block = (
        "5. On success:\n"
        "   - write a concise summary to `summaries/parent_subtask.md`\n"
        f"   - record success and let the daemon route the workflow with `python3 -m aicoding.cli.main subtask succeed --node {version.logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file $(pwd)/summaries/parent_subtask.md`\n"
    )
    continuation_block = (
        "7. After a successful completion, do not stop while the parent node still has pending workflow stages.\n"
        "   - follow the routed daemon outcome instead of manually chaining low-level commands\n"
        f"   - if the routed outcome is `next_stage`, fetch the next prompt with `python3 -m aicoding.cli.main subtask prompt --node {version.logical_node_id}` and continue in the same session\n"
        "   - if the routed outcome is `completed`, stop and do not probe the closed run with additional low-level workflow commands\n\n"
    )
    if command_text is not None:
        success_block = (
            "5. On command completion:\n"
            "   - write `summaries/command_result.json` containing at least the real exit code\n"
            "   - if the command failed, write a bounded failure summary to `summaries/parent_subtask_failure.md`\n"
            f"   - report the command result and let the daemon route the workflow with `python3 -m aicoding.cli.main subtask report-command --node {version.logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --result-file $(pwd)/summaries/command_result.json --failure-summary-file $(pwd)/summaries/parent_subtask_failure.md`\n"
        )
        continuation_block = (
            "7. After reporting the command result, do not stop while the parent node still has pending workflow stages.\n"
            "   - follow the routed daemon outcome instead of manually chaining low-level commands\n"
            f"   - if the routed outcome is `next_stage`, fetch the next prompt with `python3 -m aicoding.cli.main subtask prompt --node {version.logical_node_id}` and continue in the same session\n"
            "   - if the routed outcome is `completed`, stop and do not probe the closed run with additional low-level workflow commands\n\n"
        )
    if subtask_type == "review":
        success_block = (
            "5. On success:\n"
            "   - decide whether the layout passes, needs revision, or fails\n"
            "   - optionally write structured findings to `reviews/findings.json`\n"
            "   - optionally write structured criteria results to `reviews/criteria.json`\n"
            f"   - submit the review with `python3 -m aicoding.cli.main review run --node {version.logical_node_id} --status pass --summary \"Approved the parent layout review.\"`\n"
            "   - if the review should revise or fail, change `--status pass` to `--status revise` or `--status fail` and use a bounded summary instead\n"
            "   - do not call `subtask complete` or `workflow advance` after `review run`; that command records and routes the review outcome itself\n"
        )
        continuation_block = (
            "7. After a successful review submission, do not stop while the parent node still has pending workflow stages.\n"
            f"   - run `python3 -m aicoding.cli.main subtask current --node {version.logical_node_id}`\n"
            f"   - if the node still has a current compiled subtask, fetch the next prompt with `python3 -m aicoding.cli.main subtask prompt --node {version.logical_node_id}` and continue in the same session\n"
            f"   - repeat until `python3 -m aicoding.cli.main node child-materialization --node {version.logical_node_id}` shows created or materialized children, or the node run is no longer active\n\n"
        )
    return (
        f"You are executing parent workflow node `{version.logical_node_id}`.\n"
        f"Current task key: `{task_key}`\n"
        f"Current subtask key: `{source_subtask_key}`\n"
        f"Current subtask title: `{title}`\n"
        f"Current subtask type: `{subtask_type}`\n\n"
        "Required CLI workflow:\n"
        f"1. Resolve the live compiled subtask UUID with `python3 -m aicoding.cli.main subtask current --node {version.logical_node_id}`.\n"
        f"2. Start the attempt with `python3 -m aicoding.cli.main subtask start --node {version.logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID`.\n"
        f"3. Inspect the current context with `python3 -m aicoding.cli.main subtask context --node {version.logical_node_id}`.\n"
        "4. Execute the current subtask instructions below.\n"
        f"{success_block}"
        "6. If blocked:\n"
        "   - write the blocker summary to `summaries/parent_subtask_failure.md`\n"
        f"   - fail the current subtask with `python3 -m aicoding.cli.main subtask fail --node {version.logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --summary-file $(pwd)/summaries/parent_subtask_failure.md`\n"
        f"{continuation_block}"
        f"Current subtask instructions:\n{body}\n"
    )


def _render_hook_prompt(
    *,
    render_result,
    version: NodeVersion,
    task_key: str,
    task_doc: dict[str, object],
    prompt_relative_path: str,
    prompt_pack: str,
    hook_step: HookExpansionStep,
) -> str:
    return (
        f"Template Path: prompts/{prompt_relative_path}\n"
        f"Prompt Pack: {prompt_pack}\n"
        f"Hook Id: {hook_step.hook_id}\n"
        f"Hook Trigger: {hook_step.when}\n"
        f"Hook Source: {hook_step.relative_path}\n"
        f"Insertion Phase: {hook_step.insertion_phase}\n\n"
        f"{render_result.rendered_text.strip()}\n\n"
        f"Node Title: {version.title}\n"
        f"Node Kind: {version.node_kind}\n"
        f"Node Version: {version.version_number}\n"
        f"Task Key: {task_key}\n"
        f"Hook Subtask Key: {hook_step.source_subtask_key}\n\n"
        f"Node Prompt:\n{version.prompt.strip()}\n\n"
        f"Task Definition:\n{yaml.safe_dump(task_doc, sort_keys=False).strip()}\n"
    )


def _render_prompt_body(*, template_text: str, context: RenderContext, field_name: str):
    try:
        return render_text(template_text, context=context, field_name=field_name)
    except TemplateRenderError as exc:
        raise WorkflowCompileError(
            failure_stage="rendering",
            failure_class="missing_render_variable",
            summary=str(exc),
            details_json={"field_name": field_name},
            target_family="prompt_template",
            target_id=field_name,
        ) from exc


def _render_optional_text(*, value: object, context: RenderContext, field_name: str):
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    try:
        return render_text(value, context=context, field_name=field_name)
    except TemplateRenderError as exc:
        raise WorkflowCompileError(
            failure_stage="rendering",
            failure_class="missing_render_variable",
            summary=str(exc),
            details_json={"field_name": field_name},
            target_family="subtask_definition",
            target_id=field_name,
        ) from exc


def _build_subtask_render_context(
    *,
    version: NodeVersion,
    task_key: str,
    task_doc: dict[str, object],
    source_subtask_key: str,
    prompt_pack: str,
    prompt_relative_path: str | None,
    command_relative_path: str | None,
    extra_context: object,
    hook_step: HookExpansionStep | None = None,
) -> RenderContext:
    task_yaml = yaml.safe_dump(task_doc, sort_keys=False).strip()
    scopes: dict[str, dict[str, object]] = {
        "node": {
            "id": str(version.logical_node_id),
            "logical_node_id": str(version.logical_node_id),
            "version_id": str(version.id),
            "kind": version.node_kind,
            "tier": version.tier,
            "title": version.title,
            "prompt": version.prompt.strip(),
            "version_number": version.version_number,
        },
        "task": {
            "key": task_key,
            "name": str(task_doc.get("name", _humanize(task_key))),
            "description": str(task_doc.get("description", "")),
            "definition_yaml": task_yaml,
        },
        "subtask": {
            "key": source_subtask_key,
            "id": source_subtask_key,
        },
        "prompt": {
            "pack": prompt_pack,
            "template_path": "" if prompt_relative_path is None else prompt_relative_path,
        },
        "command": {
            "template_path": "" if command_relative_path is None else command_relative_path,
        },
        "compat": {
            "node_id": str(version.logical_node_id),
            "logical_node_id": str(version.logical_node_id),
            "node_version_id": str(version.id),
            "node_kind": version.node_kind,
            "node_tier": version.tier,
            "node_title": version.title,
            "node_prompt": version.prompt.strip(),
            "user_request": version.prompt.strip(),
            "acceptance_criteria": "" if version.description is None else version.description.strip(),
            "node_version": version.version_number,
            "task_key": task_key,
            "task_name": str(task_doc.get("name", _humanize(task_key))),
            "task_description": str(task_doc.get("description", "")),
            "compiled_subtask_id": source_subtask_key,
            "source_subtask_key": source_subtask_key,
            "prompt_pack": prompt_pack,
            "template_path": "" if prompt_relative_path is None else prompt_relative_path,
            "command_template_path": "" if command_relative_path is None else command_relative_path,
        },
        "invoker": {},
    }
    if hook_step is not None:
        scopes["hook"] = {
            "id": hook_step.hook_id,
            "trigger": hook_step.when,
            "source_path": hook_step.relative_path,
            "insertion_phase": hook_step.insertion_phase,
            "subtask_key": hook_step.source_subtask_key,
        }
        scopes["compat"].update(
            {
                "hook_id": hook_step.hook_id,
                "hook_trigger": hook_step.when,
                "hook_source": hook_step.relative_path,
                "hook_subtask_key": hook_step.source_subtask_key,
            }
        )
    render_context = build_render_context(scopes=scopes)
    if isinstance(extra_context, dict):
        if bool(extra_context.get("inherits", True)) is False:
            base_scopes = {key: value for key, value in render_context.scopes.items() if key == "invoker"}
            render_context = build_render_context(scopes=base_scopes)
        explicit_values = extra_context.get("variables", {})
        if isinstance(explicit_values, dict):
            explicit_context = build_render_context(scopes={"invoker": explicit_values})
            merged_scopes = dict(render_context.scopes)
            merged_scopes["invoker"] = explicit_context.scopes.get("invoker", {})
            render_context = build_render_context(scopes=merged_scopes)
    return render_context


def _rendering_payload(
    *,
    source_subtask_key: str,
    prompt_result,
    command_result,
    pause_result,
    render_context: RenderContext,
) -> dict[str, object]:
    rendered_fields: list[dict[str, object]] = []
    if prompt_result is not None:
        rendered_fields.append(
            {
                "field": "prompt",
                "variables_used": prompt_result.variables_used,
                "source_syntaxes": prompt_result.source_syntaxes,
                "source_text": prompt_result.source_text,
                "rendered_text": prompt_result.rendered_text,
            }
        )
    if command_result is not None:
        rendered_fields.append(
            {
                "field": "command",
                "variables_used": command_result.variables_used,
                "source_syntaxes": command_result.source_syntaxes,
                "source_text": command_result.source_text,
                "rendered_text": command_result.rendered_text,
            }
        )
    if pause_result is not None:
        rendered_fields.append(
            {
                "field": "pause_summary_prompt",
                "variables_used": pause_result.variables_used,
                "source_syntaxes": pause_result.source_syntaxes,
                "source_text": pause_result.source_text,
                "rendered_text": pause_result.rendered_text,
            }
        )
    return {
        "source_subtask_key": source_subtask_key,
        "rendered_fields": rendered_fields,
        "available_scope_keys": {scope: sorted(values) for scope, values in render_context.scopes.items()},
    }


def _render_source_relative_path(*, prompt_value: object, task_key: str, source_subtask_key: str) -> str:
    if not isinstance(prompt_value, str) or not prompt_value:
        return ""
    if prompt_value.startswith("prompts/") or prompt_value.endswith(".md"):
        return prompt_value.removeprefix("prompts/")
    return f"inline/{task_key}/{source_subtask_key}"


def _ensure_no_illegal_render_targets(
    *,
    subtask_definition: dict[str, object],
    task_key: str,
    source_subtask_key: str,
) -> None:
    illegal_fields = {
        "args": subtask_definition.get("args"),
        "env": subtask_definition.get("env"),
        "checks": subtask_definition.get("checks"),
        "outputs": subtask_definition.get("outputs"),
        "retry_policy": subtask_definition.get("retry_policy"),
    }
    for field_name, value in illegal_fields.items():
        if contains_template_syntax(value):
            raise WorkflowCompileError(
                failure_stage="rendering",
                failure_class="illegal_render_target",
                summary=(
                    f"render variables are not supported in {task_key}.{source_subtask_key}.{field_name}; "
                    "only prompt, command, and pause_summary_prompt are renderable in this phase"
                ),
                details_json={
                    "task_key": task_key,
                    "source_subtask_key": source_subtask_key,
                    "field_name": field_name,
                },
                target_family="subtask_definition",
                target_id=f"{task_key}.{source_subtask_key}.{field_name}",
            )
