from __future__ import annotations

from dataclasses import dataclass
from typing import cast
from uuid import UUID, uuid4

import yaml
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import (
    CompiledSubtask,
    CompiledTask,
    LogicalNodeCurrentVersion,
    NodeRun,
    NodeRunState,
    NodeVersion,
    SubtaskAttempt,
    TestResult,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.yaml_schemas import TestingDefinitionDocument

TEST_RESULT_STATUSES = {"passed", "failed"}


@dataclass(frozen=True, slots=True)
class TestResultSnapshot:
    id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    testing_definition_id: str | None
    suite_name: str | None
    status: str
    attempt_number: int | None
    results_json: dict[str, object] | list[dict[str, object]] | None
    summary: str | None
    action: str | None
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "testing_definition_id": self.testing_definition_id,
            "suite_name": self.suite_name,
            "status": self.status,
            "attempt_number": self.attempt_number,
            "results_json": self.results_json,
            "summary": self.summary,
            "action": self.action,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class TestingSummarySnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    status: str
    action: str | None
    passed_count: int
    failed_count: int
    retry_allowed: bool
    retry_pending: bool
    attempt_number: int | None
    max_attempts: int | None
    rerun_failed_only: bool
    results: list[TestResultSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "status": self.status,
            "action": self.action,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "retry_allowed": self.retry_allowed,
            "retry_pending": self.retry_pending,
            "attempt_number": self.attempt_number,
            "max_attempts": self.max_attempts,
            "rerun_failed_only": self.rerun_failed_only,
            "results": [item.to_payload() for item in self.results],
        }


def evaluate_testing_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> TestingSummarySnapshot:
    resource_catalog = catalog or load_resource_catalog()
    with session_scope(session_factory) as session:
        run, version = _load_active_run_and_version(session, logical_node_id)
        subtask = _current_testing_subtask(session, run.id)
        attempt = _latest_attempt(session, run.id, subtask.id)
        if attempt is None or attempt.status != "COMPLETE":
            raise DaemonConflictError("testing subtask is not complete")
        testing_documents = _testing_documents_for_subtask(session, run.id, subtask, catalog=resource_catalog)
        if not testing_documents:
            raise DaemonConflictError("testing subtask has no resolved testing definitions")

        result_pairs = [
            _persist_result(
                session,
                version=version,
                run=run,
                subtask=subtask,
                attempt=attempt,
                testing_document=testing_document,
            )
            for testing_document in testing_documents
        ]
        summary = _summary_for(
            version.logical_node_id,
            version.id,
            run.id,
            subtask.id,
            attempt_number=attempt.attempt_number,
            results=[snapshot for snapshot, _ in result_pairs],
            max_attempts=max((document.retry_policy.max_attempts for document in testing_documents), default=None),
            rerun_failed_only=any(document.retry_policy.rerun_failed_only for document in testing_documents),
        )
        attempt.testing_json = summary.to_payload()
        session.flush()
        return summary


def load_testing_summary_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> TestingSummarySnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = session.execute(
            select(NodeRun).where(NodeRun.node_version_id == version.id).order_by(NodeRun.run_number.desc())
        ).scalars().first()
        if run is None:
            return TestingSummarySnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=None,
                compiled_subtask_id=None,
                status="not_run",
                action=None,
                passed_count=0,
                failed_count=0,
                retry_allowed=False,
                retry_pending=False,
                attempt_number=None,
                max_attempts=None,
                rerun_failed_only=False,
                results=[],
            )
        return _load_summary_for_run(session, node_id=logical_node_id, node_run_id=run.id)


def load_testing_summary_for_run(
    session_factory: sessionmaker[Session],
    *,
    node_run_id: UUID,
) -> TestingSummarySnapshot:
    with query_session_scope(session_factory) as session:
        run = session.get(NodeRun, node_run_id)
        if run is None:
            raise DaemonNotFoundError("node run not found")
        version = session.get(NodeVersion, run.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        return _load_summary_for_run(session, node_id=version.logical_node_id, node_run_id=node_run_id)


def list_test_results_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> list[TestResultSnapshot]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(TestResult).where(TestResult.node_version_id == version.id).order_by(TestResult.created_at, TestResult.id)
        ).scalars().all()
        return [_snapshot(row) for row in rows]


def _load_summary_for_run(session: Session, *, node_id: UUID, node_run_id: UUID) -> TestingSummarySnapshot:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    rows = session.execute(
        select(TestResult).where(TestResult.node_run_id == node_run_id).order_by(TestResult.created_at, TestResult.id)
    ).scalars().all()
    summary = _summary_for(
        node_id,
        run.node_version_id,
        node_run_id,
        None if not rows else rows[-1].compiled_subtask_id,
        attempt_number=None if not rows else rows[-1].attempt_number,
        results=[_snapshot(row) for row in rows],
        max_attempts=None,
        rerun_failed_only=False,
    )
    latest_attempt = session.execute(
        select(SubtaskAttempt)
        .where(SubtaskAttempt.node_run_id == node_run_id, SubtaskAttempt.testing_json.is_not(None))
        .order_by(SubtaskAttempt.ended_at.desc(), SubtaskAttempt.created_at.desc())
    ).scalars().first()
    if latest_attempt is not None and latest_attempt.testing_json is not None:
        payload = dict(latest_attempt.testing_json)
        return TestingSummarySnapshot(
            node_id=summary.node_id,
            node_version_id=summary.node_version_id,
            node_run_id=summary.node_run_id,
            compiled_subtask_id=summary.compiled_subtask_id,
            status=str(payload.get("status", summary.status)),
            action=cast(str | None, payload.get("action")),
            passed_count=summary.passed_count,
            failed_count=summary.failed_count,
            retry_allowed=bool(payload.get("retry_allowed", False)),
            retry_pending=bool(payload.get("retry_pending", False)),
            attempt_number=cast(int | None, payload.get("attempt_number")),
            max_attempts=cast(int | None, payload.get("max_attempts")),
            rerun_failed_only=bool(payload.get("rerun_failed_only", False)),
            results=summary.results,
        )
    return summary


def _summary_for(
    node_id: UUID,
    node_version_id: UUID,
    node_run_id: UUID | None,
    compiled_subtask_id: UUID | None,
    *,
    attempt_number: int | None,
    results: list[TestResultSnapshot],
    max_attempts: int | None,
    rerun_failed_only: bool,
) -> TestingSummarySnapshot:
    failed_results = [item for item in results if item.status == "failed"]
    failed_count = len(failed_results)
    passed_count = sum(1 for item in results if item.status == "passed")
    retry_allowed = bool(failed_count and attempt_number is not None and max_attempts is not None and attempt_number < max_attempts)
    retry_pending = bool(failed_count and retry_allowed)
    status = "retry_pending" if retry_pending else ("failed" if failed_count else ("passed" if results else "not_run"))
    action = "retry_subtask" if retry_pending else (failed_results[0].action if failed_results else "continue")
    return TestingSummarySnapshot(
        node_id=node_id,
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        compiled_subtask_id=compiled_subtask_id,
        status=status,
        action=action,
        passed_count=passed_count,
        failed_count=failed_count,
        retry_allowed=retry_allowed,
        retry_pending=retry_pending,
        attempt_number=attempt_number,
        max_attempts=max_attempts,
        rerun_failed_only=rerun_failed_only,
        results=results,
    )


def _persist_result(
    session: Session,
    *,
    version: NodeVersion,
    run: NodeRun,
    subtask: CompiledSubtask,
    attempt: SubtaskAttempt,
    testing_document: TestingDefinitionDocument,
) -> tuple[TestResultSnapshot, str | None]:
    status, payload, summary = _evaluate_testing_document(testing_document, attempt=attempt)
    action = testing_document.on_result.pass_action if status == "passed" else testing_document.on_result.fail_action
    record = TestResult(
        id=uuid4(),
        node_version_id=version.id,
        node_run_id=run.id,
        compiled_subtask_id=subtask.id,
        testing_definition_id=testing_document.id,
        suite_name=testing_document.name,
        status=status,
        attempt_number=attempt.attempt_number,
        results_json=payload,
        summary=summary,
    )
    session.add(record)
    session.flush()
    return _snapshot(record, action=action), action


def _evaluate_testing_document(
    testing_document: TestingDefinitionDocument,
    *,
    attempt: SubtaskAttempt,
) -> tuple[str, dict[str, object], str]:
    output_json = dict(attempt.output_json or {})
    payload = _resolve_test_payload(testing_document, output_json=output_json)
    actual_exit_code = payload.get("exit_code", output_json.get("exit_code"))
    actual_failed_tests = payload.get("failed_tests", output_json.get("failed_tests", 0))
    if actual_failed_tests is None:
        actual_failed_tests = 0
    try:
        failed_tests = int(actual_failed_tests)
    except (TypeError, ValueError):
        failed_tests = 0
    status = "passed"
    has_exit_code = "exit_code" in payload or "exit_code" in output_json
    if testing_document.pass_rules.require_exit_code_zero and actual_exit_code not in {0, "0"}:
        status = "failed"
    if failed_tests > testing_document.pass_rules.max_failed_tests:
        status = "failed"
    if testing_document.pass_rules.require_exit_code_zero and (not has_exit_code or actual_exit_code in {None, ""}):
        status = "failed"
    summary = str(payload.get("summary") or output_json.get("summary") or attempt.summary or "").strip()
    if not summary:
        summary = f"{testing_document.name} {status}"
    result_payload = {
        "testing_definition_id": testing_document.id,
        "suite_name": testing_document.name,
        "scope": testing_document.scope,
        "exit_code": actual_exit_code,
        "failed_tests": failed_tests,
        "max_failed_tests": testing_document.pass_rules.max_failed_tests,
        "require_exit_code_zero": testing_document.pass_rules.require_exit_code_zero,
        "rerun_failed_only": testing_document.retry_policy.rerun_failed_only,
        "command_results": payload.get("command_results"),
        "raw_output": payload.get("raw_output"),
    }
    return status, result_payload, summary


def _resolve_test_payload(testing_document: TestingDefinitionDocument, *, output_json: dict[str, object]) -> dict[str, object]:
    suites = output_json.get("test_suites", [])
    if isinstance(suites, list):
        for item in suites:
            if not isinstance(item, dict):
                continue
            suite_id = str(item.get("testing_definition_id") or "").strip()
            suite_name = str(item.get("suite_name") or "").strip()
            if suite_id == testing_document.id or suite_name == testing_document.name:
                return dict(item)
    return output_json


def _testing_documents_for_subtask(
    session: Session,
    node_run_id: UUID,
    subtask: CompiledSubtask,
    *,
    catalog: ResourceCatalog,
) -> list[TestingDefinitionDocument]:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    task = session.get(CompiledTask, subtask.compiled_task_id)
    if task is None:
        raise DaemonNotFoundError("compiled task not found")
    task_definition = dict(task.config_json or {}).get("task_definition", {})
    effective_policy = dict(task.config_json or {}).get("effective_policy", {})
    refs = [
        *[str(item) for item in task_definition.get("uses_testing", [])],
        *[str(item) for item in effective_policy.get("testing_refs", [])],
    ]
    documents: list[TestingDefinitionDocument] = []
    seen: set[tuple[str, str]] = set()
    for reference in refs:
        group, relative_path = _resolve_testing_reference(reference, catalog)
        key = (group, relative_path)
        if key in seen:
            continue
        seen.add(key)
        raw = yaml.safe_load(catalog.read_text(group, relative_path)) or {}
        payload = raw.get("testing_definition", raw)
        documents.append(TestingDefinitionDocument.model_validate(payload))
    return documents


def _resolve_testing_reference(reference: str, catalog: ResourceCatalog) -> tuple[str, str]:
    relative_path = reference.removeprefix("testing/")
    if not relative_path.endswith(".yaml"):
        relative_path = f"{relative_path}.yaml"
    normalized = f"testing/{relative_path}"
    if (catalog.yaml_project_dir / normalized).exists():
        return "yaml_project", normalized
    return "yaml_builtin_system", normalized


def _current_testing_subtask(session: Session, node_run_id: UUID) -> CompiledSubtask:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    state = session.get(NodeRunState, node_run_id)
    if state is None or state.current_compiled_subtask_id is None:
        raise DaemonConflictError("current testing subtask not found")
    subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
    if subtask is None:
        raise DaemonNotFoundError("compiled subtask not found")
    if subtask.subtask_type != "run_tests":
        raise DaemonConflictError("current subtask is not a testing subtask")
    return subtask


def _latest_attempt(session: Session, node_run_id: UUID, compiled_subtask_id: UUID) -> SubtaskAttempt | None:
    return session.execute(
        select(SubtaskAttempt)
        .where(SubtaskAttempt.node_run_id == node_run_id, SubtaskAttempt.compiled_subtask_id == compiled_subtask_id)
        .order_by(SubtaskAttempt.attempt_number.desc())
    ).scalars().first()


def _load_active_run_and_version(session: Session, logical_node_id: UUID) -> tuple[NodeRun, NodeVersion]:
    version = _authoritative_version(session, logical_node_id)
    run = session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == version.id, NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")))
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if run is None:
        raise DaemonNotFoundError("active node run not found")
    return run, version


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    version = session.execute(
        select(NodeVersion)
        .join(
            LogicalNodeCurrentVersion,
            LogicalNodeCurrentVersion.authoritative_node_version_id == NodeVersion.id,
        )
        .where(LogicalNodeCurrentVersion.logical_node_id == logical_node_id)
    ).scalars().first()
    if version is None:
        raise DaemonNotFoundError("authoritative node version not found")
    return version


def _snapshot(row: TestResult, *, action: str | None = None) -> TestResultSnapshot:
    return TestResultSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        testing_definition_id=row.testing_definition_id,
        suite_name=row.suite_name,
        status=row.status,
        attempt_number=row.attempt_number,
        results_json=row.results_json,
        summary=row.summary,
        action=action,
        created_at=row.created_at.isoformat(),
    )
