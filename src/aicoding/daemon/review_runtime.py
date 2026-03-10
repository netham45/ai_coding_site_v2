from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.db.models import CompiledSubtask, CompiledTask, CompiledWorkflow, NodeRun, NodeRunState, NodeVersion, ReviewResult, SubtaskAttempt
from aicoding.db.session import query_session_scope, session_scope

REVIEW_RESULT_STATUSES = {"passed", "revise", "failed"}


@dataclass(frozen=True, slots=True)
class ReviewResultSnapshot:
    id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    review_definition_id: str | None
    scope: str
    status: str
    criteria_json: list[dict[str, object]] | dict[str, object] | None
    findings_json: list[dict[str, object]] | None
    summary: str | None
    action: str | None
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "review_definition_id": self.review_definition_id,
            "scope": self.scope,
            "status": self.status,
            "criteria_json": self.criteria_json,
            "findings_json": self.findings_json,
            "summary": self.summary,
            "action": self.action,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class ReviewSummarySnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    compiled_subtask_id: UUID | None
    status: str
    action: str | None
    passed_count: int
    revise_count: int
    failed_count: int
    results: list[ReviewResultSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "compiled_subtask_id": None if self.compiled_subtask_id is None else str(self.compiled_subtask_id),
            "status": self.status,
            "action": self.action,
            "passed_count": self.passed_count,
            "revise_count": self.revise_count,
            "failed_count": self.failed_count,
            "results": [item.to_payload() for item in self.results],
        }


def evaluate_review_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> ReviewSummarySnapshot:
    with session_scope(session_factory) as session:
        run, version = _load_active_run_and_version(session, logical_node_id)
        subtask = _current_review_subtask(session, run.id)
        attempt = _latest_attempt(session, run.id, subtask.id)
        if attempt is None or attempt.status != "COMPLETE":
            raise DaemonConflictError("review subtask is not complete")
        review_documents = _review_documents_for_subtask(session, run.id, subtask)
        if not review_documents:
            raise DaemonConflictError("review subtask has no resolved review definitions")

        result_pairs = [
            _persist_result(
                session,
                version=version,
                run=run,
                subtask=subtask,
                attempt=attempt,
                review_document=review_document,
            )
            for review_document in review_documents
        ]
        summary = _summary_for(
            version.logical_node_id,
            version.id,
            run.id,
            subtask.id,
            [snapshot for snapshot, _ in result_pairs],
        )
        attempt.review_json = summary.to_payload()
        session.flush()
        return summary


def load_review_summary_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> ReviewSummarySnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = session.execute(
            select(NodeRun)
            .where(NodeRun.node_version_id == version.id)
            .order_by(NodeRun.run_number.desc())
        ).scalars().first()
        if run is None:
            return ReviewSummarySnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=None,
                compiled_subtask_id=None,
                status="not_run",
                action=None,
                passed_count=0,
                revise_count=0,
                failed_count=0,
                results=[],
            )
        return _load_summary_for_run(session, node_id=logical_node_id, node_run_id=run.id)


def load_review_summary_for_run(
    session_factory: sessionmaker[Session],
    *,
    node_run_id: UUID,
) -> ReviewSummarySnapshot:
    with query_session_scope(session_factory) as session:
        run = session.get(NodeRun, node_run_id)
        if run is None:
            raise DaemonNotFoundError("node run not found")
        version = session.get(NodeVersion, run.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        return _load_summary_for_run(session, node_id=version.logical_node_id, node_run_id=node_run_id)


def list_review_results_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> list[ReviewResultSnapshot]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(ReviewResult)
            .where(ReviewResult.node_version_id == version.id)
            .order_by(ReviewResult.created_at, ReviewResult.id)
        ).scalars().all()
        return [_snapshot(row) for row in rows]


def _load_summary_for_run(session: Session, *, node_id: UUID, node_run_id: UUID) -> ReviewSummarySnapshot:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    rows = session.execute(
        select(ReviewResult)
        .where(ReviewResult.node_run_id == node_run_id)
        .order_by(ReviewResult.created_at, ReviewResult.id)
    ).scalars().all()
    summary = _summary_for(
        node_id,
        run.node_version_id,
        node_run_id,
        None if not rows else rows[-1].compiled_subtask_id,
        [_snapshot(row) for row in rows],
    )
    latest_attempt = session.execute(
        select(SubtaskAttempt)
        .where(SubtaskAttempt.node_run_id == node_run_id, SubtaskAttempt.review_json.is_not(None))
        .order_by(SubtaskAttempt.ended_at.desc(), SubtaskAttempt.created_at.desc())
    ).scalars().first()
    if latest_attempt is not None and latest_attempt.review_json is not None:
        summary_payload = dict(latest_attempt.review_json)
        return ReviewSummarySnapshot(
            node_id=summary.node_id,
            node_version_id=summary.node_version_id,
            node_run_id=summary.node_run_id,
            compiled_subtask_id=summary.compiled_subtask_id,
            status=summary.status,
            action=summary_payload.get("action"),
            passed_count=summary.passed_count,
            revise_count=summary.revise_count,
            failed_count=summary.failed_count,
            results=summary.results,
        )
    return summary


def _persist_result(
    session: Session,
    *,
    version: NodeVersion,
    run: NodeRun,
    subtask: CompiledSubtask,
    attempt: SubtaskAttempt,
    review_document: dict[str, object],
) -> tuple[ReviewResultSnapshot, str | None]:
    review_id = str(review_document.get("id", "")).strip() or None
    scope = str(review_document.get("scope", "custom")).strip() or "custom"
    status, criteria, findings, summary = _evaluate_review_document(review_document, attempt=attempt)
    action = _action_for_review_document(review_document, status)
    record = ReviewResult(
        id=uuid4(),
        node_version_id=version.id,
        node_run_id=run.id,
        compiled_subtask_id=subtask.id,
        review_definition_id=review_id,
        scope=scope,
        status=status,
        criteria_json=criteria,
        findings_json=findings,
        summary=summary,
    )
    session.add(record)
    session.flush()
    return _snapshot(record, action=action), action


def _evaluate_review_document(
    review_document: dict[str, object],
    *,
    attempt: SubtaskAttempt,
) -> tuple[str, list[dict[str, object]] | dict[str, object] | None, list[dict[str, object]] | None, str]:
    output_json = dict(attempt.output_json or {})
    review_payload = _resolve_review_payload(
        review_document_id=str(review_document.get("id", "")).strip() or None,
        output_json=output_json,
    )
    normalized_status = _normalize_status(review_payload.get("status") or output_json.get("status") or output_json.get("review_status"))
    criteria = _normalize_criteria(review_payload.get("criteria_results") or output_json.get("criteria_results"))
    findings = _normalize_findings(review_payload.get("findings") or output_json.get("findings"))
    summary = str(review_payload.get("summary") or output_json.get("summary") or attempt.summary or "").strip()
    if not summary:
        summary = f"review {normalized_status}"
    return normalized_status, criteria, findings, summary


def _resolve_review_payload(review_document_id: str | None, *, output_json: dict[str, object]) -> dict[str, object]:
    reviews = output_json.get("reviews", [])
    if isinstance(reviews, list):
        for item in reviews:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("review_definition_id", "")).strip() or None
            if review_document_id is not None and item_id == review_document_id:
                return dict(item)
    return output_json


def _normalize_status(raw_status: object) -> str:
    normalized = str(raw_status or "").strip().lower()
    if normalized == "pass":
        normalized = "passed"
    elif normalized == "fail":
        normalized = "failed"
    if normalized not in REVIEW_RESULT_STATUSES:
        raise DaemonConflictError(f"unsupported review status '{raw_status}'")
    return normalized


def _normalize_criteria(raw_criteria: object) -> list[dict[str, object]] | dict[str, object] | None:
    if raw_criteria is None:
        return None
    if isinstance(raw_criteria, dict):
        return dict(raw_criteria)
    if isinstance(raw_criteria, list):
        return [dict(item) if isinstance(item, dict) else {"value": item} for item in raw_criteria]
    raise DaemonConflictError("review criteria results must be an object or list")


def _normalize_findings(raw_findings: object) -> list[dict[str, object]] | None:
    if raw_findings is None:
        return None
    if not isinstance(raw_findings, list):
        raise DaemonConflictError("review findings must be a list")
    normalized: list[dict[str, object]] = []
    for item in raw_findings:
        if isinstance(item, dict):
            normalized.append(dict(item))
        else:
            normalized.append({"message": str(item)})
    return normalized


def _review_documents_for_subtask(session: Session, node_run_id: UUID, subtask: CompiledSubtask) -> list[dict[str, object]]:
    run = session.get(NodeRun, node_run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    task = session.get(CompiledTask, subtask.compiled_task_id)
    if task is None:
        raise DaemonNotFoundError("compiled task not found")
    task_definition = dict(task.config_json.get("task_definition", {}))
    review_refs = list(task_definition.get("uses_reviews", []))
    if not review_refs:
        return []
    version = session.get(NodeVersion, run.node_version_id)
    if version is None or version.compiled_workflow_id is None:
        raise DaemonNotFoundError("compiled workflow not found")
    workflow = session.get(CompiledWorkflow, version.compiled_workflow_id)
    if workflow is None:
        raise DaemonNotFoundError("compiled workflow not found")
    resolved_documents = list(workflow.resolved_yaml.get("resolved_documents", []))
    documents: list[dict[str, object]] = []
    for reference in review_refs:
        reference_id = str(reference).strip()
        reference_path = reference_id.removeprefix("reviews/")
        if not reference_path.endswith(".yaml"):
            reference_path = f"{reference_path}.yaml"
        reference_path = f"reviews/{reference_path}" if not reference_path.startswith("reviews/") else reference_path
        matched = next(
            (
                item
                for item in resolved_documents
                if item.get("target_family") == "review_definition"
                and (
                    item.get("relative_path") == reference_path
                    or item.get("target_id") == reference_id
                    or item.get("target_id") == reference_id.removeprefix("reviews/").removesuffix(".yaml")
                )
            ),
            None,
        )
        if matched is None:
            raise DaemonConflictError(f"review definition '{reference}' was not resolved into the compiled workflow")
        documents.append(dict(matched.get("resolved_document", {})))
    return documents


def _current_review_subtask(session: Session, node_run_id: UUID) -> CompiledSubtask:
    state = session.get(NodeRunState, node_run_id)
    if state is None or state.current_compiled_subtask_id is None:
        raise DaemonConflictError("current review subtask not found")
    subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
    if subtask is None:
        raise DaemonNotFoundError("compiled subtask not found")
    if subtask.subtask_type != "review":
        raise DaemonConflictError("current subtask is not a review subtask")
    return subtask


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


def _summary_for(
    node_id: UUID,
    node_version_id: UUID,
    node_run_id: UUID | None,
    compiled_subtask_id: UUID | None,
    results: list[ReviewResultSnapshot],
) -> ReviewSummarySnapshot:
    failed_count = sum(1 for item in results if item.status == "failed")
    revise_count = sum(1 for item in results if item.status == "revise")
    passed_count = sum(1 for item in results if item.status == "passed")
    if failed_count:
        status = "failed"
    elif revise_count:
        status = "revise"
    else:
        status = "passed" if results else "not_run"
    action = _action_for_status(status, results)
    return ReviewSummarySnapshot(
        node_id=node_id,
        node_version_id=node_version_id,
        node_run_id=node_run_id,
        compiled_subtask_id=compiled_subtask_id,
        status=status,
        action=action,
        passed_count=passed_count,
        revise_count=revise_count,
        failed_count=failed_count,
        results=results,
    )


def _action_for_status(status: str, results: list[ReviewResultSnapshot]) -> str | None:
    if not results:
        return None
    if status == "passed":
        for result in results:
            if result.status == "passed":
                return result.action
        return "continue"
    target_status = "failed" if status == "failed" else "revise"
    for result in results:
        if result.status != target_status:
            continue
        return result.action
    return None


def _action_for_review_document(review_document: dict[str, object], status: str) -> str | None:
    on_result = dict(review_document.get("on_result", {}))
    if status == "passed":
        return str(on_result.get("pass_action", "continue"))
    if status == "revise":
        return str(on_result.get("revise_action", "rerun_task"))
    return str(on_result.get("fail_action", "fail_to_parent"))


def _snapshot(row: ReviewResult, *, action: str | None = None) -> ReviewResultSnapshot:
    findings = None if row.findings_json is None else [dict(item) for item in row.findings_json]
    criteria = row.criteria_json
    if isinstance(criteria, list):
        criteria = [dict(item) if isinstance(item, dict) else {"value": item} for item in criteria]
    elif isinstance(criteria, dict):
        criteria = dict(criteria)
    return ReviewResultSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        review_definition_id=row.review_definition_id,
        scope=row.scope,
        status=row.status,
        criteria_json=criteria,
        findings_json=findings,
        summary=row.summary,
        action=action,
        created_at=row.created_at.isoformat(),
    )
