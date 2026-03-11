from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.docs_runtime import list_docs_for_node
from aicoding.daemon.errors import DaemonNotFoundError
from aicoding.daemon.git_conflicts import list_merge_conflicts_for_node, list_merge_events_for_node
from aicoding.daemon.history import list_prompt_history, list_summary_history
from aicoding.daemon.operator_views import load_node_operator_summary
from aicoding.daemon.regeneration import list_rebuild_events_for_node
from aicoding.daemon.review_runtime import list_review_results_for_node
from aicoding.daemon.run_orchestration import NodeRunSnapshot, NodeRunStateSnapshot, SubtaskAttemptSnapshot
from aicoding.daemon.session_records import DurableSessionSnapshot, SessionEventSnapshot
from aicoding.daemon.testing_runtime import list_test_results_for_node
from aicoding.daemon.validation_runtime import list_validation_results_for_node
from aicoding.daemon.versioning import load_node_lineage
from aicoding.daemon.workflow_events import WorkflowEventSnapshot, list_workflow_events_for_node
from aicoding.daemon.workflows import (
    CompileFailureSnapshot,
    CompiledWorkflowSnapshot,
    WorkflowChainSnapshot,
    load_current_workflow,
    load_workflow_chain_for_node,
)
from aicoding.db.models import (
    CompileFailure,
    LogicalNodeCurrentVersion,
    NodeRun,
    NodeRunState,
    NodeVersion,
    PromptRecord,
    Session,
    SessionEvent,
    SubtaskAttempt,
    SummaryRecord,
    TestResult,
    ReviewResult,
    ValidationResult,
)
from aicoding.db.session import query_session_scope
from aicoding.source_lineage import load_node_version_source_lineage


@dataclass(frozen=True, slots=True)
class SessionAuditSnapshot:
    session: DurableSessionSnapshot
    events: list[SessionEventSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "session": self.session.to_payload(),
            "events": [item.to_payload() for item in self.events],
        }


@dataclass(frozen=True, slots=True)
class NodeAuditSnapshot:
    node_id: UUID
    node_summary: dict[str, object]
    lineage: dict[str, object]
    authoritative_version_id: UUID
    current_workflow: dict[str, object] | None
    workflow_chain: dict[str, object] | None
    source_lineage: dict[str, object]
    compile_failures: list[dict[str, object]]
    workflow_events: list[dict[str, object]]
    prompt_history: dict[str, object]
    summary_history: dict[str, object]
    validation_results: list[dict[str, object]]
    review_results: list[dict[str, object]]
    test_results: list[dict[str, object]]
    sessions: list[dict[str, object]]
    rebuild_history: list[dict[str, object]]
    merge_events: list[dict[str, object]]
    merge_conflicts: list[dict[str, object]]
    documentation_outputs: list[dict[str, object]]
    run_count: int

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_summary": self.node_summary,
            "lineage": self.lineage,
            "authoritative_version_id": str(self.authoritative_version_id),
            "current_workflow": self.current_workflow,
            "workflow_chain": self.workflow_chain,
            "source_lineage": self.source_lineage,
            "compile_failures": self.compile_failures,
            "workflow_events": self.workflow_events,
            "prompt_history": self.prompt_history,
            "summary_history": self.summary_history,
            "validation_results": self.validation_results,
            "review_results": self.review_results,
            "test_results": self.test_results,
            "sessions": self.sessions,
            "rebuild_history": self.rebuild_history,
            "merge_events": self.merge_events,
            "merge_conflicts": self.merge_conflicts,
            "documentation_outputs": self.documentation_outputs,
            "run_count": self.run_count,
        }


@dataclass(frozen=True, slots=True)
class RunAuditSnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID
    run: dict[str, object]
    state: dict[str, object]
    workflow: dict[str, object] | None
    source_lineage: dict[str, object]
    attempts: list[dict[str, object]]
    workflow_events: list[dict[str, object]]
    prompts: list[dict[str, object]]
    summaries: list[dict[str, object]]
    validation_results: list[dict[str, object]]
    review_results: list[dict[str, object]]
    test_results: list[dict[str, object]]
    sessions: list[dict[str, object]]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": str(self.node_run_id),
            "run": self.run,
            "state": self.state,
            "workflow": self.workflow,
            "source_lineage": self.source_lineage,
            "attempts": self.attempts,
            "workflow_events": self.workflow_events,
            "prompts": self.prompts,
            "summaries": self.summaries,
            "validation_results": self.validation_results,
            "review_results": self.review_results,
            "test_results": self.test_results,
            "sessions": self.sessions,
        }


def load_node_audit_snapshot(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> NodeAuditSnapshot:
    lineage = load_node_lineage(session_factory, logical_node_id)
    authoritative_version_id = lineage.authoritative_node_version_id
    current_workflow = _maybe_current_workflow(session_factory, logical_node_id=logical_node_id)
    workflow_chain = _maybe_workflow_chain(session_factory, logical_node_id=logical_node_id)
    sessions = _list_sessions_with_events_for_version(session_factory, node_version_id=authoritative_version_id)
    return NodeAuditSnapshot(
        node_id=logical_node_id,
        node_summary=load_node_operator_summary(session_factory, node_id=logical_node_id).to_payload(),
        lineage=lineage.to_payload(),
        authoritative_version_id=authoritative_version_id,
        current_workflow=None if current_workflow is None else current_workflow.to_payload(),
        workflow_chain=None if workflow_chain is None else workflow_chain.to_payload(),
        source_lineage=load_node_version_source_lineage(session_factory, node_version_id=authoritative_version_id).to_payload(),
        compile_failures=[item.to_payload() for item in _list_compile_failures_for_version(session_factory, node_version_id=authoritative_version_id)],
        workflow_events=[item.to_payload() for item in list_workflow_events_for_node(session_factory, logical_node_id=logical_node_id)],
        prompt_history=list_prompt_history(session_factory, logical_node_id=logical_node_id).to_payload(),
        summary_history=list_summary_history(session_factory, logical_node_id=logical_node_id).to_payload(),
        validation_results=[item.to_payload() for item in list_validation_results_for_node(session_factory, logical_node_id=logical_node_id)],
        review_results=[item.to_payload() for item in list_review_results_for_node(session_factory, logical_node_id=logical_node_id)],
        test_results=[item.to_payload() for item in list_test_results_for_node(session_factory, logical_node_id=logical_node_id)],
        sessions=[item.to_payload() for item in sessions],
        rebuild_history=[item.to_payload() for item in list_rebuild_events_for_node(session_factory, logical_node_id=logical_node_id).events],
        merge_events=[item.to_payload() for item in list_merge_events_for_node(session_factory, logical_node_id=logical_node_id)],
        merge_conflicts=[item.to_payload() for item in list_merge_conflicts_for_node(session_factory, logical_node_id=logical_node_id)],
        documentation_outputs=[item.to_payload() for item in list_docs_for_node(session_factory, logical_node_id=logical_node_id).documents],
        run_count=_count_runs_for_version(session_factory, node_version_id=authoritative_version_id),
    )


def load_run_audit_snapshot(
    session_factory: sessionmaker[Session],
    *,
    node_run_id: UUID | None = None,
    logical_node_id: UUID | None = None,
) -> RunAuditSnapshot:
    with query_session_scope(session_factory) as session:
        run = _require_run(session, node_run_id=node_run_id, logical_node_id=logical_node_id)
        version = session.get(NodeVersion, run.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        state = session.get(NodeRunState, run.id)
        if state is None:
            raise DaemonNotFoundError("node run state not found")
        workflow = _maybe_workflow_for_version(session_factory, version_id=version.id)
        source_lineage = load_node_version_source_lineage(session_factory, node_version_id=version.id).to_payload()
        attempts = session.execute(
            select(SubtaskAttempt)
            .where(SubtaskAttempt.node_run_id == run.id)
            .order_by(SubtaskAttempt.attempt_number, SubtaskAttempt.created_at, SubtaskAttempt.id)
        ).scalars().all()
        sessions = _list_sessions_with_events_for_run(session_factory, node_run_id=run.id)
        return RunAuditSnapshot(
            node_id=version.logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            run=_run_snapshot(run, version.logical_node_id).to_payload(),
            state=_run_state_snapshot(state).to_payload(),
            workflow=None if workflow is None else workflow.to_payload(),
            source_lineage=source_lineage,
            attempts=[_attempt_snapshot(item).to_payload() for item in attempts],
            workflow_events=[item.to_payload() for item in _list_workflow_events_for_run(session_factory, node_run_id=run.id)],
            prompts=[item for item in _prompt_history_for_run(session_factory, node_run_id=run.id)],
            summaries=[item for item in _summary_history_for_run(session_factory, node_run_id=run.id)],
            validation_results=[item for item in _validation_results_for_run(session_factory, node_run_id=run.id)],
            review_results=[item for item in _review_results_for_run(session_factory, node_run_id=run.id)],
            test_results=[item for item in _test_results_for_run(session_factory, node_run_id=run.id)],
            sessions=[item.to_payload() for item in sessions],
        )


def _maybe_current_workflow(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> CompiledWorkflowSnapshot | None:
    try:
        return load_current_workflow(session_factory, logical_node_id=logical_node_id)
    except DaemonNotFoundError:
        return None


def _maybe_workflow_chain(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> WorkflowChainSnapshot | None:
    try:
        return load_workflow_chain_for_node(session_factory, logical_node_id=logical_node_id)
    except DaemonNotFoundError:
        return None


def _maybe_workflow_for_version(session_factory: sessionmaker[Session], *, version_id: UUID) -> CompiledWorkflowSnapshot | None:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None or version.compiled_workflow_id is None:
            return None
    try:
        return _maybe_current_workflow_for_version_id(session_factory, version_id=version_id)
    except DaemonNotFoundError:
        return None


def _maybe_current_workflow_for_version_id(session_factory: sessionmaker[Session], *, version_id: UUID) -> CompiledWorkflowSnapshot:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, version_id)
        if version is None or version.compiled_workflow_id is None:
            raise DaemonNotFoundError("compiled workflow not found")
    from aicoding.daemon.workflows import load_workflow

    return load_workflow(session_factory, workflow_id=version.compiled_workflow_id)


def _require_run(session: Session, *, node_run_id: UUID | None, logical_node_id: UUID | None) -> NodeRun:
    if node_run_id is not None:
        run = session.get(NodeRun, node_run_id)
        if run is None:
            raise DaemonNotFoundError("node run not found")
        return run
    if logical_node_id is None:
        raise DaemonNotFoundError("node run not found")
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    run = session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == selector.authoritative_node_version_id)
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if run is None:
        raise DaemonNotFoundError("node run not found")
    return run


def _run_snapshot(row: NodeRun, logical_node_id: UUID) -> NodeRunSnapshot:
    return NodeRunSnapshot(
        id=row.id,
        node_version_id=row.node_version_id,
        logical_node_id=logical_node_id,
        run_number=row.run_number,
        trigger_reason=row.trigger_reason,
        run_status=row.run_status,
        compiled_workflow_id=row.compiled_workflow_id,
        started_at=None if row.started_at is None else row.started_at.isoformat(),
        ended_at=None if row.ended_at is None else row.ended_at.isoformat(),
        summary=row.summary,
    )


def _run_state_snapshot(row: NodeRunState) -> NodeRunStateSnapshot:
    return NodeRunStateSnapshot(
        node_run_id=row.node_run_id,
        lifecycle_state=row.lifecycle_state,
        current_task_id=row.current_task_id,
        current_compiled_subtask_id=row.current_compiled_subtask_id,
        current_subtask_attempt=row.current_subtask_attempt,
        last_completed_compiled_subtask_id=row.last_completed_compiled_subtask_id,
        execution_cursor_json=dict(row.execution_cursor_json or {}),
        failure_count_from_children=row.failure_count_from_children,
        failure_count_consecutive=row.failure_count_consecutive,
        defer_to_user_threshold=row.defer_to_user_threshold,
        pause_flag_name=row.pause_flag_name,
        is_resumable=row.is_resumable,
        working_tree_state=row.working_tree_state,
        updated_at=row.updated_at.isoformat(),
    )


def _attempt_snapshot(row: SubtaskAttempt) -> SubtaskAttemptSnapshot:
    return SubtaskAttemptSnapshot(
        id=row.id,
        node_run_id=row.node_run_id,
        compiled_subtask_id=row.compiled_subtask_id,
        attempt_number=row.attempt_number,
        status=row.status,
        input_context_json=None if row.input_context_json is None else dict(row.input_context_json),
        output_json=None if row.output_json is None else dict(row.output_json),
        execution_result_json=None if row.execution_result_json is None else dict(row.execution_result_json),
        execution_environment_json=None if row.execution_environment_json is None else dict(row.execution_environment_json),
        validation_json=None if row.validation_json is None else dict(row.validation_json),
        review_json=None if row.review_json is None else dict(row.review_json),
        testing_json=None if row.testing_json is None else dict(row.testing_json),
        summary=row.summary,
        started_at=None if row.started_at is None else row.started_at.isoformat(),
        ended_at=None if row.ended_at is None else row.ended_at.isoformat(),
    )


def _count_runs_for_version(session_factory: sessionmaker[Session], *, node_version_id: UUID) -> int:
    with query_session_scope(session_factory) as session:
        return len(session.execute(select(NodeRun.id).where(NodeRun.node_version_id == node_version_id)).all())


def _list_compile_failures_for_version(session_factory: sessionmaker[Session], *, node_version_id: UUID) -> list[CompileFailureSnapshot]:
    with query_session_scope(session_factory) as session:
        version = session.get(NodeVersion, node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        rows = session.execute(
            select(CompileFailure)
            .where(CompileFailure.node_version_id == node_version_id)
            .order_by(CompileFailure.created_at, CompileFailure.id)
        ).scalars().all()
        return [
            CompileFailureSnapshot(
                id=row.id,
                node_version_id=row.node_version_id,
                logical_node_id=version.logical_node_id,
                failure_stage=row.failure_stage,
                failure_class=row.failure_class,
                summary=row.summary,
                details_json=dict(row.details_json or {}),
                source_hash=row.source_hash,
                target_family=row.target_family,
                target_id=row.target_id,
                compile_context=dict(row.details_json or {}).get("compile_context", {}),
                created_at=row.created_at.isoformat(),
            )
            for row in rows
        ]


def _list_sessions_with_events_for_version(session_factory: sessionmaker[Session], *, node_version_id: UUID) -> list[SessionAuditSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(Session)
            .where(Session.node_version_id == node_version_id)
            .order_by(Session.started_at, Session.id)
        ).scalars().all()
        return [_session_audit_snapshot(session, row) for row in rows]


def _list_sessions_with_events_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[SessionAuditSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(Session)
            .where(Session.node_run_id == node_run_id)
            .order_by(Session.started_at, Session.id)
        ).scalars().all()
        return [_session_audit_snapshot(session, row) for row in rows]


def _session_audit_snapshot(session: Session, row: Session) -> SessionAuditSnapshot:
    version = session.get(NodeVersion, row.node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    run = session.get(NodeRun, row.node_run_id) if row.node_run_id is not None else None
    events = session.execute(
        select(SessionEvent).where(SessionEvent.session_id == row.id).order_by(SessionEvent.created_at, SessionEvent.id)
    ).scalars().all()
    event_snapshots = [
        SessionEventSnapshot(
            id=item.id,
            session_id=item.session_id,
            event_type=item.event_type,
            payload_json=dict(item.payload_json or {}),
            created_at=item.created_at.isoformat(),
        )
        for item in events
    ]
    latest_event = event_snapshots[-1].event_type if event_snapshots else None
    return SessionAuditSnapshot(
        session=DurableSessionSnapshot(
            session_id=row.id,
            logical_node_id=version.logical_node_id,
            node_version_id=row.node_version_id,
            node_run_id=row.node_run_id,
            node_kind=version.node_kind,
            node_title=version.title,
            run_status=None if run is None else run.run_status,
            session_role=row.session_role,
            provider=row.provider,
            provider_session_id=row.provider_session_id,
            tmux_session_name=row.tmux_session_name,
            cwd=row.cwd,
            status=row.status,
            started_at=row.started_at.isoformat(),
            last_heartbeat_at=None if row.last_heartbeat_at is None else row.last_heartbeat_at.isoformat(),
            ended_at=None if row.ended_at is None else row.ended_at.isoformat(),
            event_count=len(event_snapshots),
            latest_event_type=latest_event,
            backend="durable_history",
            pane_text=None,
            idle_seconds=None,
            in_alt_screen=None,
            tmux_session_exists=None,
            attach_command=None,
            recovery_classification=None,
        ),
        events=event_snapshots,
    )


def _list_workflow_events_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[WorkflowEventSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(NodeRun, NodeVersion).join(NodeVersion, NodeVersion.id == NodeRun.node_version_id).where(NodeRun.id == node_run_id)
        ).first()
        if rows is None:
            raise DaemonNotFoundError("node run not found")
        run, version = rows
    return [
        item
        for item in list_workflow_events_for_node(session_factory, logical_node_id=version.logical_node_id)
        if str(item.node_run_id) == str(node_run_id)
    ]


def _prompt_history_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[dict[str, object]]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(PromptRecord).where(PromptRecord.node_run_id == node_run_id).order_by(PromptRecord.delivered_at, PromptRecord.id)
        ).scalars().all()
        return [
            {
                "id": str(row.id),
                "node_version_id": str(row.node_version_id),
                "node_run_id": str(row.node_run_id),
                "compiled_subtask_id": None if row.compiled_subtask_id is None else str(row.compiled_subtask_id),
                "prompt_role": row.prompt_role,
                "source_subtask_key": row.source_subtask_key,
                "template_path": row.template_path,
                "template_hash": row.template_hash,
                "content": row.content,
                "content_hash": row.content_hash,
                "payload_json": dict(row.payload_json or {}),
                "delivered_at": row.delivered_at.isoformat(),
            }
            for row in rows
        ]


def _summary_history_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[dict[str, object]]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(SummaryRecord).where(SummaryRecord.node_run_id == node_run_id).order_by(SummaryRecord.created_at, SummaryRecord.id)
        ).scalars().all()
        return [
            {
                "id": str(row.id),
                "node_version_id": str(row.node_version_id),
                "node_run_id": None if row.node_run_id is None else str(row.node_run_id),
                "compiled_subtask_id": None if row.compiled_subtask_id is None else str(row.compiled_subtask_id),
                "attempt_number": row.attempt_number,
                "summary_type": row.summary_type,
                "summary_scope": row.summary_scope,
                "summary_path": row.summary_path,
                "content": row.content,
                "content_hash": row.content_hash,
                "metadata_json": dict(row.metadata_json or {}),
                "created_at": row.created_at.isoformat(),
            }
            for row in rows
        ]


def _validation_results_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[dict[str, object]]:
    return _result_rows_for_run(session_factory, node_run_id=node_run_id, model=ValidationResult)


def _review_results_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[dict[str, object]]:
    return _result_rows_for_run(session_factory, node_run_id=node_run_id, model=ReviewResult)


def _test_results_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID) -> list[dict[str, object]]:
    return _result_rows_for_run(session_factory, node_run_id=node_run_id, model=TestResult)


def _result_rows_for_run(session_factory: sessionmaker[Session], *, node_run_id: UUID, model) -> list[dict[str, object]]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(select(model).where(model.node_run_id == node_run_id).order_by(model.created_at, model.id)).scalars().all()
        payloads: list[dict[str, object]] = []
        for row in rows:
            payload: dict[str, object] = {
                "id": str(row.id),
                "node_version_id": str(row.node_version_id),
                "node_run_id": None if row.node_run_id is None else str(row.node_run_id),
                "compiled_subtask_id": None if row.compiled_subtask_id is None else str(row.compiled_subtask_id),
                "created_at": row.created_at.isoformat(),
                "status": row.status,
                "summary": row.summary,
            }
            if hasattr(row, "check_type"):
                payload["check_type"] = row.check_type
                payload["evidence_json"] = None if row.evidence_json is None else dict(row.evidence_json)
            if hasattr(row, "review_definition_id"):
                payload["review_definition_id"] = row.review_definition_id
                payload["scope"] = row.scope
                payload["criteria_json"] = row.criteria_json
                payload["findings_json"] = row.findings_json
            if hasattr(row, "testing_definition_id"):
                payload["testing_definition_id"] = row.testing_definition_id
                payload["suite_name"] = row.suite_name
                payload["attempt_number"] = row.attempt_number
                payload["results_json"] = row.results_json
            payloads.append(payload)
        return payloads
