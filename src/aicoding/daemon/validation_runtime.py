from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.history import has_registered_summary
from aicoding.db.models import CompiledSubtask, NodeRun, NodeRunState, NodeVersion, SubtaskAttempt, ValidationResult
from aicoding.db.session import query_session_scope, session_scope

VALIDATION_STATUSES = {"passed", "failed"}


@dataclass(frozen=True, slots=True)
class ValidationResultSnapshot:
    id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    check_type: str
    status: str
    evidence_json: dict[str, object] | None
    summary: str | None
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "check_type": self.check_type,
            "status": self.status,
            "evidence_json": self.evidence_json,
            "summary": self.summary,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class ValidationSummarySnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    status: str
    passed_count: int
    failed_count: int
    results: list[ValidationResultSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "status": self.status,
            "passed_count": self.passed_count,
            "failed_count": self.failed_count,
            "results": [item.to_payload() for item in self.results],
        }


def evaluate_validation_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> ValidationSummarySnapshot:
    with session_scope(session_factory) as session:
        run, version = _load_active_run_and_version(session, logical_node_id)
        subtask = _current_validation_subtask(session, run.id)
        attempt = _latest_attempt(session, run.id, subtask.id)
        if attempt is None or attempt.status != "COMPLETE":
            raise DaemonConflictError("validation subtask is not complete")
        checks = _compiled_checks(subtask)
        if not checks:
            raise DaemonConflictError("validation subtask has no compiled checks")

        results = [_persist_result(session, version, run, subtask, attempt, check) for check in checks]
        summary = _summary_for(version.logical_node_id, version.id, run.id, subtask.id, results)
        attempt.validation_json = summary.to_payload()
        session.flush()
        return summary


def load_validation_summary_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> ValidationSummarySnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = session.execute(
            select(NodeRun)
            .where(NodeRun.node_version_id == version.id)
            .order_by(NodeRun.run_number.desc())
        ).scalars().first()
        if run is None:
            return ValidationSummarySnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=None,
                compiled_subtask_id=None,
                status="not_run",
                passed_count=0,
                failed_count=0,
                results=[],
            )
        return _load_summary_for_run(session, node_id=logical_node_id, node_run_id=run.id)


def load_validation_summary_for_run(
    session_factory: sessionmaker[Session],
    *,
    node_run_id: UUID,
) -> ValidationSummarySnapshot:
    with query_session_scope(session_factory) as session:
        run = session.get(NodeRun, node_run_id)
        if run is None:
            raise DaemonNotFoundError("node run not found")
        version = session.get(NodeVersion, run.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        return _load_summary_for_run(session, node_id=version.logical_node_id, node_run_id=node_run_id)


def list_validation_results_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> list[ValidationResultSnapshot]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(ValidationResult)
            .where(ValidationResult.node_version_id == version.id)
            .order_by(ValidationResult.created_at, ValidationResult.id)
        ).scalars().all()
        return [_snapshot(row) for row in rows]


def _load_summary_for_run(session: Session, *, node_id: UUID, node_run_id: UUID) -> ValidationSummarySnapshot:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    rows = session.execute(
        select(ValidationResult)
        .where(ValidationResult.node_run_id == node_run_id)
        .order_by(ValidationResult.created_at, ValidationResult.id)
    ).scalars().all()
    return _summary_for(node_id, run.node_version_id, node_run_id, None if not rows else rows[-1].compiled_subtask_id, [_snapshot(row) for row in rows])


def _summary_for(
    node_id: UUID,
    node_version_id: UUID,
    node_run_id: UUID | None,
    compiled_subtask_id: UUID | None,
    results: list[ValidationResultSnapshot],
) -> ValidationSummarySnapshot:
    failed_count = sum(1 for item in results if item.status == "failed")
    passed_count = sum(1 for item in results if item.status == "passed")
    status = "failed" if failed_count else ("passed" if results else "not_run")
    return ValidationSummarySnapshot(
        node_id=node_id,
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        compiled_subtask_id=compiled_subtask_id,
        status=status,
        passed_count=passed_count,
        failed_count=failed_count,
        results=results,
    )


def _persist_result(
    session: Session,
    version: NodeVersion,
    run: NodeRun,
    subtask: CompiledSubtask,
    attempt: SubtaskAttempt,
    check: dict[str, object],
) -> ValidationResultSnapshot:
    check_type = str(check.get("type", "")).strip()
    status, evidence, summary = _evaluate_check(session, check_type, check=check, attempt=attempt)
    record = ValidationResult(
        id=uuid4(),
        node_version_id=version.id,
        node_run_id=run.id,
        compiled_subtask_id=subtask.id,
        check_type=check_type,
        status=status,
        evidence_json=evidence,
        summary=summary,
    )
    session.add(record)
    session.flush()
    return _snapshot(record)


def _evaluate_check(
    session: Session,
    check_type: str,
    *,
    check: dict[str, object],
    attempt: SubtaskAttempt,
) -> tuple[str, dict[str, object], str]:
    output_json = dict(attempt.output_json or {})
    registered_summaries = list(output_json.get("registered_summaries", []))
    if check_type == "command_exit_code":
        expected = int(check.get("exit_code", 0))
        actual = output_json.get("exit_code")
        status = "passed" if actual == expected else "failed"
        return status, {"expected_exit_code": expected, "actual_exit_code": actual}, f"exit code expected {expected}, got {actual}"
    if check_type == "summary_written":
        path = str(check.get("path", "")).strip()
        found = (
            attempt.summary is not None
            or any(str(item.get("summary_path")) == path for item in registered_summaries)
            or has_registered_summary(
                session,
                node_run_id=attempt.node_run_id,
                compiled_subtask_id=attempt.compiled_subtask_id,
                summary_path=path,
            )
        )
        status = "passed" if found else "failed"
        return status, {"path": path, "summary_present": found}, f"summary path {path or '<any>'} {'present' if found else 'missing'}"
    if check_type in {"file_exists", "file_updated", "docs_built", "provenance_updated"}:
        path = str(check.get("path", "")).strip()
        exists = Path(path).exists() if path else False
        status = "passed" if exists else "failed"
        return status, {"path": path, "exists": exists}, f"path {path} {'exists' if exists else 'missing'}"
    if check_type == "file_contains":
        path = str(check.get("path", "")).strip()
        pattern = str(check.get("pattern", ""))
        exists = Path(path).exists() if path else False
        content = Path(path).read_text(encoding="utf-8") if exists else ""
        matched = exists and pattern in content
        status = "passed" if matched else "failed"
        return status, {"path": path, "pattern": pattern, "matched": matched}, f"path {path} {'contains' if matched else 'does not contain'} pattern"
    raise DaemonConflictError(f"unsupported validation check type '{check_type}'")


def _current_validation_subtask(session: Session, node_run_id: UUID) -> CompiledSubtask:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    state = session.get(NodeRunState, node_run_id)
    if state is None or state.current_compiled_subtask_id is None:
        raise DaemonConflictError("current validation subtask not found")
    subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
    if subtask is None:
        raise DaemonNotFoundError("compiled subtask not found")
    if subtask.subtask_type != "validate":
        raise DaemonConflictError("current subtask is not a validation subtask")
    return subtask


def _compiled_checks(subtask: CompiledSubtask) -> list[dict[str, object]]:
    payload = dict(subtask.retry_policy_json or {})
    checks = payload.get("checks", [])
    return [dict(item) for item in checks if isinstance(item, dict)]


def _latest_attempt(session: Session, node_run_id: UUID, compiled_subtask_id: UUID) -> SubtaskAttempt | None:
    return session.execute(
        select(SubtaskAttempt)
        .where(
            SubtaskAttempt.node_run_id == node_run_id,
            SubtaskAttempt.compiled_subtask_id == compiled_subtask_id,
        )
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
    from aicoding.db.models import LogicalNodeCurrentVersion

    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _snapshot(row: ValidationResult) -> ValidationResultSnapshot:
    return ValidationResultSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        check_type=row.check_type,
        status=row.status,
        evidence_json=None if row.evidence_json is None else dict(row.evidence_json),
        summary=row.summary,
        created_at=row.created_at.isoformat(),
    )
