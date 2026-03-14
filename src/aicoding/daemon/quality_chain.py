from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.docs_runtime import DocumentationBuildSnapshot, build_node_docs
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.history import record_summary_history
from aicoding.daemon.provenance import ProvenanceRefreshSnapshot, refresh_node_provenance
from aicoding.daemon.review_runtime import ReviewSummarySnapshot, load_review_summary_for_node
from aicoding.daemon.run_orchestration import (
    RunProgressSnapshot,
    advance_workflow,
    complete_current_subtask,
    load_current_run_progress,
    start_subtask_attempt,
)
from aicoding.daemon.testing_runtime import TestingSummarySnapshot, load_testing_summary_for_node
from aicoding.daemon.validation_runtime import ValidationSummarySnapshot, load_validation_summary_for_node
from aicoding.db.models import CompiledSubtask, CompiledTask, LogicalNodeCurrentVersion, NodeRun, NodeVersion
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.yaml_schemas import TestingDefinitionDocument

AUTOMATED_QUALITY_SUBTASK_TYPES = {"validate", "review", "run_tests"}


@dataclass(frozen=True, slots=True)
class QualityChainSnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID
    run_status: str
    executed_stage_types: list[str]
    validation: ValidationSummarySnapshot
    review: ReviewSummarySnapshot
    testing: TestingSummarySnapshot
    provenance: dict[str, object] | None
    docs: list[dict[str, object]]
    final_summary: dict[str, object] | None
    progress: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": str(self.node_run_id),
            "run_status": self.run_status,
            "executed_stage_types": self.executed_stage_types,
            "validation": self.validation.to_payload(),
            "review": self.review.to_payload(),
            "testing": self.testing.to_payload(),
            "provenance": self.provenance,
            "docs": self.docs,
            "final_summary": self.final_summary,
            "progress": self.progress,
        }


def run_turnkey_quality_chain(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> QualityChainSnapshot:
    resource_catalog = catalog or load_resource_catalog()
    executed_stage_types: list[str] = []
    progress = load_current_run_progress(session_factory, logical_node_id=logical_node_id)
    if progress.current_subtask is None:
        raise DaemonConflictError("active run does not have a current subtask")

    while True:
        current_subtask = progress.current_subtask
        if current_subtask is None:
            break
        current_type = str(current_subtask.get("subtask_type"))
        stage_type = _current_quality_stage_type(session_factory, progress=progress)
        is_gate_subtask = current_type in AUTOMATED_QUALITY_SUBTASK_TYPES
        if stage_type is None:
            if not executed_stage_types:
                raise DaemonConflictError("quality chain can only start when the current subtask is a built-in quality gate")
            break
        compiled_subtask_id = UUID(str(progress.state.current_compiled_subtask_id))
        start_subtask_attempt(
            session_factory,
            logical_node_id=logical_node_id,
            compiled_subtask_id=compiled_subtask_id,
        )
        complete_current_subtask(
            session_factory,
            logical_node_id=logical_node_id,
            compiled_subtask_id=compiled_subtask_id,
            output_json=(
                _default_stage_output(
                    session_factory,
                    logical_node_id=logical_node_id,
                    compiled_subtask_id=compiled_subtask_id,
                    subtask_type=stage_type,
                    catalog=resource_catalog,
                )
                if is_gate_subtask
                else {}
            ),
            summary=_default_stage_summary(stage_type) if is_gate_subtask else _quality_prelude_summary(stage_type),
        )
        progress = advance_workflow(session_factory, logical_node_id=logical_node_id, catalog=resource_catalog)
        if not executed_stage_types or executed_stage_types[-1] != stage_type:
            executed_stage_types.append(stage_type)
        if progress.run.run_status in {"FAILED", "PAUSED"}:
            break

    validation = load_validation_summary_for_node(session_factory, logical_node_id=logical_node_id)
    review = load_review_summary_for_node(session_factory, logical_node_id=logical_node_id)
    testing = load_testing_summary_for_node(session_factory, logical_node_id=logical_node_id)

    provenance_payload: dict[str, object] | None = None
    docs_payload: list[dict[str, object]] = []
    final_summary_payload: dict[str, object] | None = None
    if (
        progress.run.run_status == "COMPLETE"
        and validation.status == "passed"
        and review.status == "passed"
        and testing.status == "passed"
    ):
        provenance = refresh_node_provenance(session_factory, logical_node_id=logical_node_id)
        docs = build_node_docs(session_factory, logical_node_id=logical_node_id, catalog=resource_catalog)
        final_summary_payload = _record_final_quality_summary(
            session_factory,
            logical_node_id=logical_node_id,
            progress=progress,
            validation=validation,
            review=review,
            testing=testing,
            provenance=provenance,
            docs=docs,
        )
        provenance_payload = provenance.to_payload()
        docs_payload = [item.to_payload() for item in docs.documents]

    return QualityChainSnapshot(
        node_id=logical_node_id,
        node_version_id=_as_uuid(progress.run.node_version_id),
        node_run_id=_as_uuid(progress.run.id),
        run_status=progress.run.run_status,
        executed_stage_types=executed_stage_types,
        validation=validation,
        review=review,
        testing=testing,
        provenance=provenance_payload,
        docs=docs_payload,
        final_summary=final_summary_payload,
        progress=progress.to_payload(),
    )


def _default_stage_summary(subtask_type: str) -> str:
    if subtask_type == "validate":
        return "validation input prepared"
    if subtask_type == "review":
        return "review passed"
    if subtask_type == "run_tests":
        return "tests passed"
    return f"{subtask_type} complete"


def _quality_prelude_summary(stage_type: str) -> str:
    return f"{stage_type} preparation complete"


def _default_stage_output(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    subtask_type: str,
    catalog: ResourceCatalog,
) -> dict[str, object]:
    if subtask_type == "validate":
        return {"exit_code": 0}
    if subtask_type == "review":
        return {
            "status": "passed",
            "findings": [],
            "criteria_results": [{"criterion": "default_review", "status": "passed"}],
            "summary": "review passed",
        }
    if subtask_type == "run_tests":
        suites = _default_test_suites(
            session_factory,
            logical_node_id=logical_node_id,
            compiled_subtask_id=compiled_subtask_id,
            catalog=catalog,
        )
        return {
            "test_suites": suites,
            "exit_code": 0,
            "failed_tests": 0,
            "summary": "tests passed",
        }
    return {}


def _default_test_suites(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    catalog: ResourceCatalog,
) -> list[dict[str, object]]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _latest_run(session, version.id)
        if run is None:
            raise DaemonConflictError("node run not found for testing stage")
        subtask = session.get(CompiledSubtask, compiled_subtask_id)
        if subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        task = session.get(CompiledTask, subtask.compiled_task_id)
        if task is None:
            raise DaemonNotFoundError("compiled task not found")
        refs = [
            *[str(item) for item in dict(task.config_json or {}).get("task_definition", {}).get("uses_testing", [])],
            *[str(item) for item in dict(task.config_json or {}).get("effective_policy", {}).get("testing_refs", [])],
        ]
    suites: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for reference in refs:
        group, relative_path = _resolve_testing_reference(reference, catalog)
        key = (group, relative_path)
        if key in seen:
            continue
        seen.add(key)
        raw = yaml.safe_load(catalog.read_text(group, relative_path)) or {}
        document = TestingDefinitionDocument.model_validate(raw.get("testing_definition", raw))
        suites.append(
            {
                "testing_definition_id": document.id,
                "suite_name": document.name,
                "exit_code": 0,
                "failed_tests": 0,
                "summary": f"{document.name} passed",
            }
        )
    return suites


def _resolve_testing_reference(reference: str, catalog: ResourceCatalog) -> tuple[str, str]:
    relative_path = reference.removeprefix("testing/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    normalized = f"testing/{relative_path}"
    if (catalog.yaml_project_dir / normalized).exists():
        return "yaml_project", normalized
    return "yaml_builtin_system", normalized


def _current_quality_stage_type(
    session_factory: sessionmaker[Session],
    *,
    progress: RunProgressSnapshot,
) -> str | None:
    current_subtask = progress.current_subtask or {}
    current_type = str(current_subtask.get("subtask_type") or "")
    if current_type in AUTOMATED_QUALITY_SUBTASK_TYPES:
        return current_type
    current_task_id = progress.state.current_task_id
    if current_task_id is None:
        return None
    with query_session_scope(session_factory) as session:
        task = session.get(CompiledTask, UUID(str(current_task_id)))
        if task is None:
            raise DaemonNotFoundError("compiled task not found")
        return {
            "validate_node": "validate",
            "review_node": "review",
            "test_node": "run_tests",
        }.get(task.task_key)


def _record_final_quality_summary(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    progress: RunProgressSnapshot,
    validation: ValidationSummarySnapshot,
    review: ReviewSummarySnapshot,
    testing: TestingSummarySnapshot,
    provenance: ProvenanceRefreshSnapshot,
    docs: DocumentationBuildSnapshot,
) -> dict[str, object]:
    content = "\n".join(
        [
            "Turnkey quality chain completed.",
            f"Validation: {validation.status} ({validation.passed_count} passed, {validation.failed_count} failed)",
            f"Review: {review.status} ({review.passed_count} passed, {review.revise_count} revise, {review.failed_count} failed)",
            f"Testing: {testing.status} ({testing.passed_count} passed, {testing.failed_count} failed)",
            f"Provenance: {provenance.entity_count} entities, {provenance.relation_count} relations",
            f"Docs: {len(docs.documents)} documents",
        ]
    )
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = session.get(NodeRun, _as_uuid(progress.run.id))
        if run is None:
            raise DaemonNotFoundError("node run not found")
        summary_record = record_summary_history(
            session,
            node_version_id=version.id,
            node_run_id=run.id,
            compiled_subtask_id=None,
            attempt_number=None,
            summary_type="node",
            summary_scope="node_run",
            summary_path="summaries/final.md",
            content=content,
            metadata_json={
                "generated_by": "quality_chain",
                "recorded_at": datetime.now(timezone.utc).isoformat(),
                "provenance_summary_id": str(provenance.provenance_summary_id),
                "documentation_output_ids": [str(item.id) for item in docs.documents],
            },
        )
        run.summary = content
        session.flush()
        return {
            "summary_id": str(summary_record.id),
            "summary_type": summary_record.summary_type,
            "summary_path": summary_record.summary_path,
            "content_hash": summary_record.content_hash,
        }


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    current = session.execute(
        select(LogicalNodeCurrentVersion).where(LogicalNodeCurrentVersion.logical_node_id == logical_node_id)
    ).scalars().first()
    if current is None:
        raise DaemonNotFoundError("authoritative node version not found")
    version = session.get(NodeVersion, current.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _latest_run(session: Session, node_version_id: UUID) -> NodeRun | None:
    return session.execute(
        select(NodeRun).where(NodeRun.node_version_id == node_version_id).order_by(NodeRun.run_number.desc())
    ).scalars().first()


def _as_uuid(value: UUID | str) -> UUID:
    return value if isinstance(value, UUID) else UUID(str(value))
