from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.incremental_parent_merge import record_completed_child_for_incremental_merge_in_session
from aicoding.daemon.history import record_prompt_delivery, record_summary_history
from aicoding.daemon.environments import build_execution_environment
from aicoding.daemon.review_runtime import evaluate_review_subtask
from aicoding.daemon.session_manager import current_stage_prompt_cli_command
from aicoding.daemon.testing_runtime import evaluate_testing_subtask
from aicoding.daemon.validation_runtime import evaluate_validation_subtask
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.db.models import (
    CompiledSubtask,
    CompiledTask,
    CompiledWorkflow,
    LogicalNodeCurrentVersion,
    NodeDependency,
    NodeDependencyBlocker,
    NodeLifecycleState,
    NodeRun,
    NodeRunState,
    NodeVersion,
    PromptRecord,
    Session as DurableSession,
    SessionEvent,
    SummaryRecord,
    SubtaskAttempt,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog

ACTIVE_RUN_STATUSES = {"PENDING", "RUNNING", "PAUSED"}
APPROVED_PAUSE_FLAGS_KEY = "approved_pause_flags"
PAUSE_CONTEXT_KEY = "pause_context"


@dataclass(frozen=True, slots=True)
class NodeRunSnapshot:
    id: UUID
    node_version_id: UUID
    logical_node_id: UUID
    run_number: int
    trigger_reason: str
    run_status: str
    compiled_workflow_id: UUID
    started_at: str | None
    ended_at: str | None
    summary: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_version_id": str(self.node_version_id),
            "logical_node_id": str(self.logical_node_id),
            "run_number": self.run_number,
            "trigger_reason": self.trigger_reason,
            "run_status": self.run_status,
            "compiled_workflow_id": str(self.compiled_workflow_id),
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "summary": self.summary,
        }


@dataclass(frozen=True, slots=True)
class NodeRunStateSnapshot:
    node_run_id: UUID
    lifecycle_state: str
    current_task_id: UUID | None
    current_compiled_subtask_id: UUID | None
    current_subtask_attempt: int | None
    last_completed_compiled_subtask_id: UUID | None
    execution_cursor_json: dict[str, object]
    failure_count_from_children: int
    failure_count_consecutive: int
    defer_to_user_threshold: int | None
    pause_flag_name: str | None
    is_resumable: bool
    working_tree_state: str | None
    updated_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "node_run_id": str(self.node_run_id),
            "lifecycle_state": self.lifecycle_state,
            "current_task_id": None if self.current_task_id is None else str(self.current_task_id),
            "current_compiled_subtask_id": None if self.current_compiled_subtask_id is None else str(self.current_compiled_subtask_id),
            "current_subtask_attempt": self.current_subtask_attempt,
            "last_completed_compiled_subtask_id": None if self.last_completed_compiled_subtask_id is None else str(self.last_completed_compiled_subtask_id),
            "execution_cursor_json": self.execution_cursor_json,
            "failure_count_from_children": self.failure_count_from_children,
            "failure_count_consecutive": self.failure_count_consecutive,
            "defer_to_user_threshold": self.defer_to_user_threshold,
            "pause_flag_name": self.pause_flag_name,
            "is_resumable": self.is_resumable,
            "working_tree_state": self.working_tree_state,
            "updated_at": self.updated_at,
        }


@dataclass(frozen=True, slots=True)
class SubtaskAttemptSnapshot:
    id: UUID
    node_run_id: UUID
    compiled_subtask_id: UUID
    attempt_number: int
    status: str
    input_context_json: dict[str, object] | None
    output_json: dict[str, object] | None
    execution_result_json: dict[str, object] | None
    execution_environment_json: dict[str, object] | None
    validation_json: dict[str, object] | None
    review_json: dict[str, object] | None
    testing_json: dict[str, object] | None
    summary: str | None
    started_at: str | None
    ended_at: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_run_id": str(self.node_run_id),
            "compiled_subtask_id": str(self.compiled_subtask_id),
            "attempt_number": self.attempt_number,
            "status": self.status,
            "input_context_json": self.input_context_json,
            "output_json": self.output_json,
            "execution_result_json": self.execution_result_json,
            "execution_environment_json": self.execution_environment_json,
            "validation_json": self.validation_json,
            "review_json": self.review_json,
            "testing_json": self.testing_json,
            "summary": self.summary,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


@dataclass(frozen=True, slots=True)
class RunProgressSnapshot:
    run: NodeRunSnapshot
    state: NodeRunStateSnapshot
    current_subtask: dict[str, object] | None
    latest_attempt: SubtaskAttemptSnapshot | None
    terminal_failure: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "run": self.run.to_payload(),
            "state": self.state.to_payload(),
            "current_subtask": self.current_subtask,
            "latest_attempt": None if self.latest_attempt is None else self.latest_attempt.to_payload(),
            "terminal_failure": self.terminal_failure,
        }


@dataclass(frozen=True, slots=True)
class SubtaskPromptSnapshot:
    node_id: UUID
    node_run_id: UUID
    compiled_subtask_id: UUID
    prompt_id: UUID
    source_subtask_key: str
    title: str | None
    subtask_type: str
    prompt_text: str | None
    command_text: str | None
    environment_request_json: dict[str, object] | None
    stage_context_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_run_id": str(self.node_run_id),
            "compiled_subtask_id": str(self.compiled_subtask_id),
            "prompt_id": str(self.prompt_id),
            "source_subtask_key": self.source_subtask_key,
            "title": self.title,
            "subtask_type": self.subtask_type,
            "prompt_text": self.prompt_text,
            "command_text": self.command_text,
            "environment_request_json": self.environment_request_json,
            "stage_context_json": self.stage_context_json,
        }


@dataclass(frozen=True, slots=True)
class SubtaskContextSnapshot:
    node_id: UUID
    node_run_id: UUID
    compiled_subtask_id: UUID
    attempt_number: int | None
    input_context_json: dict[str, object]
    latest_summary: str | None
    stage_context_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_run_id": str(self.node_run_id),
            "compiled_subtask_id": str(self.compiled_subtask_id),
            "attempt_number": self.attempt_number,
            "input_context_json": self.input_context_json,
            "latest_summary": self.latest_summary,
            "stage_context_json": self.stage_context_json,
        }


@dataclass(frozen=True, slots=True)
class SummaryRegistrationSnapshot:
    summary_id: UUID
    node_id: UUID
    node_run_id: UUID
    compiled_subtask_id: UUID
    attempt_number: int
    summary_type: str
    summary_path: str
    content_hash: str
    content_length: int
    registered_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "summary_id": str(self.summary_id),
            "node_id": str(self.node_id),
            "node_run_id": str(self.node_run_id),
            "compiled_subtask_id": str(self.compiled_subtask_id),
            "attempt_number": self.attempt_number,
            "summary_type": self.summary_type,
            "summary_path": self.summary_path,
            "content_hash": self.content_hash,
            "content_length": self.content_length,
            "registered_at": self.registered_at,
        }


@dataclass(frozen=True, slots=True)
class CompositeStageOutcomeSnapshot:
    node_id: UUID
    node_run_id: UUID
    accepted_compiled_subtask_id: UUID
    accepted_subtask_type: str
    recorded_summary_id: UUID
    recorded_summary_path: str
    outcome: str
    progress: RunProgressSnapshot

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_run_id": str(self.node_run_id),
            "accepted_compiled_subtask_id": str(self.accepted_compiled_subtask_id),
            "accepted_subtask_type": self.accepted_subtask_type,
            "recorded_summary_id": str(self.recorded_summary_id),
            "recorded_summary_path": self.recorded_summary_path,
            "outcome": self.outcome,
            "progress": self.progress.to_payload(),
        }


def ensure_node_run_started(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    run_id: UUID,
    trigger_reason: str = "manual_start",
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        if version.compiled_workflow_id is None:
            raise DaemonConflictError("compiled workflow not found")
        existing = _active_run_for_version(session, version.id)
        if existing is None:
            run_number = _next_run_number(session, version.id)
            first_subtask = _first_subtask(session, version.compiled_workflow_id)
            state = NodeRunState(
                node_run_id=run_id,
                lifecycle_state="RUNNING",
                current_task_id=None if first_subtask is None else first_subtask.compiled_task_id,
                current_compiled_subtask_id=None if first_subtask is None else first_subtask.id,
                current_subtask_attempt=None,
                execution_cursor_json={"position": 0},
                is_resumable=True,
            )
            run = NodeRun(
                id=run_id,
                node_version_id=version.id,
                run_number=run_number,
                trigger_reason=trigger_reason,
                run_status="RUNNING",
                compiled_workflow_id=version.compiled_workflow_id,
                started_at=datetime.now(timezone.utc),
            )
            session.add(run)
            session.add(state)
            _sync_lifecycle_with_run(
                session,
                logical_node_id=logical_node_id,
                run=run,
                state=state,
            )
            session.flush()
            return _progress_snapshot(session, run.id)

        if existing.id != run_id:
            raise DaemonConflictError("node already has an active durable run")
        return _progress_snapshot(session, existing.id)


def load_current_run_progress(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> RunProgressSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            latest_failure = _latest_failed_supervision_context(session, version.id)
            if latest_failure is None:
                raise DaemonNotFoundError("active node run not found")
            return _progress_snapshot_with_failure(session, latest_failure["run"].id, terminal_failure=latest_failure["terminal_failure"])
        return _progress_snapshot(session, run.id)


def list_node_runs(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> list[NodeRunSnapshot]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(NodeRun).where(NodeRun.node_version_id == version.id).order_by(NodeRun.run_number)
        ).scalars().all()
        return [_run_snapshot(row, version.logical_node_id) for row in rows]


def start_subtask_attempt(session_factory: sessionmaker[Session], *, logical_node_id: UUID, compiled_subtask_id: UUID) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        existing = _latest_attempt(session, run.id, compiled_subtask_id)
        if existing is not None and existing.status == "RUNNING":
            return _progress_snapshot(session, run.id)
        compiled_subtask = session.get(CompiledSubtask, compiled_subtask_id)
        if compiled_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        attempt_number = 1 if existing is None else existing.attempt_number + 1
        input_context_json = _subtask_input_snapshot(session, run.compiled_workflow_id, compiled_subtask_id)
        attempt = SubtaskAttempt(
            id=uuid4(),
            node_run_id=run.id,
            compiled_subtask_id=compiled_subtask_id,
            attempt_number=attempt_number,
            status="RUNNING",
            input_context_json=input_context_json,
            started_at=datetime.now(timezone.utc),
        )
        execution_environment = build_execution_environment(
            compiled_subtask.environment_request_json,
            attempt_id=attempt.id,
        )
        attempt.execution_environment_json = execution_environment.to_payload()
        attempt.input_context_json = {
            **dict(input_context_json or {}),
            "execution_environment": execution_environment.to_payload(),
        }
        session.add(attempt)
        state.current_subtask_attempt = attempt_number
        if execution_environment.launch_status == "launch_failed":
            attempt.status = "FAILED"
            attempt.summary = execution_environment.summary
            attempt.output_json = {
                "failure_class": execution_environment.failure_class,
                "execution_environment": execution_environment.to_payload(),
            }
            attempt.ended_at = datetime.now(timezone.utc)
            run.run_status = "FAILED"
            run.ended_at = datetime.now(timezone.utc)
            run.summary = execution_environment.summary
            state.lifecycle_state = "FAILED_TO_PARENT"
            state.is_resumable = False
            state.failure_count_consecutive += 1
        elif execution_environment.launch_status == "fallback_local":
            attempt.output_json = {"execution_environment": execution_environment.to_payload()}
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def heartbeat_current_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        attempt = _require_running_attempt(session, run.id, compiled_subtask_id)
        heartbeat_at = datetime.now(timezone.utc).isoformat()
        output_json = dict(attempt.output_json or {})
        output_json["last_heartbeat_at"] = heartbeat_at
        attempt.output_json = output_json
        execution_cursor = dict(state.execution_cursor_json or {})
        execution_cursor["last_heartbeat_at"] = heartbeat_at
        state.execution_cursor_json = execution_cursor
        session.flush()
        return _progress_snapshot(session, run.id)


def complete_current_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    output_json: dict[str, object] | None = None,
    execution_result_json: dict[str, object] | None = None,
    summary: str | None = None,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        attempt = _require_running_attempt(session, run.id, compiled_subtask_id)
        attempt.status = "COMPLETE"
        if output_json is None:
            attempt.output_json = dict(attempt.output_json or {}) or None
        else:
            merged_output = dict(attempt.output_json or {})
            merged_output.update(output_json)
            attempt.output_json = merged_output
        if execution_result_json is None:
            attempt.execution_result_json = dict(attempt.execution_result_json or {}) or None
        else:
            merged_result = dict(attempt.execution_result_json or {})
            merged_result.update(execution_result_json)
            attempt.execution_result_json = merged_result
            compatibility_output = dict(attempt.output_json or {})
            compatibility_output.update(execution_result_json)
            attempt.output_json = compatibility_output
        attempt.summary = summary
        attempt.ended_at = datetime.now(timezone.utc)
        state.last_completed_compiled_subtask_id = compiled_subtask_id
        state.failure_count_consecutive = 0
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def load_current_subtask_prompt(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> SubtaskPromptSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id is None:
            raise DaemonNotFoundError("current compiled subtask not found")
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        if subtask is None:
            raise DaemonNotFoundError("current compiled subtask not found")
        stage_context_json = _assemble_stage_context(session, run=run, state=state, version=version, subtask=subtask)
        prompt_text = subtask.prompt_text
        command_text = subtask.command_text
        if prompt_text is None and command_text:
            prompt_text = _synthesized_command_subtask_prompt(logical_node_id=logical_node_id, subtask=subtask)
        content = prompt_text or command_text or ""
        prompt_record = record_prompt_delivery(
            session,
            node_version_id=version.id,
            node_run_id=run.id,
            compiled_subtask=subtask,
            content=content,
            payload_json={
                "prompt_text": prompt_text,
                "command_text": command_text,
                "source_subtask_key": subtask.source_subtask_key,
                "template_path": subtask.source_file_path,
                "template_hash": subtask.source_hash,
                "environment_request_json": dict(subtask.environment_request_json or {}),
                "stage_context_json": stage_context_json,
            },
        )
        return SubtaskPromptSnapshot(
            node_id=version.logical_node_id,
            node_run_id=run.id,
            compiled_subtask_id=subtask.id,
            prompt_id=prompt_record.id,
            source_subtask_key=subtask.source_subtask_key,
            title=subtask.title,
            subtask_type=subtask.subtask_type,
            prompt_text=prompt_text,
            command_text=command_text,
            environment_request_json=dict(subtask.environment_request_json or {}) or None,
            stage_context_json=stage_context_json,
        )


def _synthesized_command_subtask_prompt(*, logical_node_id: UUID, subtask: CompiledSubtask) -> str:
    prompt_command = current_stage_prompt_cli_command(logical_node_id=logical_node_id)
    result_path = "summaries/command_result.json"
    failure_path = "summaries/command_failure.md"
    output_instructions = [
        f"Current subtask key: `{subtask.source_subtask_key}`",
        f"Current subtask title: `{subtask.title or subtask.source_subtask_key}`",
        f"Current subtask type: `{subtask.subtask_type}`",
        "",
        "Required CLI workflow:",
        f"1. Resolve the live compiled subtask UUID with `python3 -m aicoding.cli.main subtask current --node {logical_node_id}`.",
        f"2. Start the attempt with `python3 -m aicoding.cli.main subtask start --node {logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID`.",
        f"3. Inspect the current context with `python3 -m aicoding.cli.main subtask context --node {logical_node_id}`.",
        "4. Run the current command exactly once and capture its real exit code:",
        f"   - `{subtask.command_text}`",
        "5. Write `summaries/command_result.json` containing at least:",
        '   - `{"exit_code": REAL_EXIT_CODE}`',
    ]
    if subtask.subtask_type in {"validate", "run_tests"}:
        output_instructions.extend(
            [
                "6. Report the command result even when the exit code is non-zero, because the daemon-owned validation/testing gate decides pass or fail:",
                f"   - `python3 -m aicoding.cli.main subtask report-command --node {logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --result-file {result_path}`",
                "7. If the returned outcome still leaves a current compiled subtask, fetch the next prompt with:",
                f"   - `{prompt_command}`",
                "8. Do not stop while a later workflow stage is available in the same session.",
            ]
        )
    else:
        output_instructions.extend(
            [
                "6. If the exit code is non-zero, write a bounded failure summary to `summaries/command_failure.md`.",
                "7. Report the command result and let the daemon route the workflow:",
                f"   - `python3 -m aicoding.cli.main subtask report-command --node {logical_node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --result-file {result_path} --failure-summary-file {failure_path}`",
                "8. If the returned outcome is `next_stage`, fetch the next prompt with:",
                f"   - `{prompt_command}`",
                "9. Do not stop while a later workflow stage is available in the same session.",
            ]
        )
    return "\n".join(output_instructions)


def load_current_subtask_context(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> SubtaskContextSnapshot:
    with query_session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id is None:
            raise DaemonNotFoundError("current compiled subtask not found")
        latest_attempt = _latest_attempt(session, run.id, state.current_compiled_subtask_id)
        if latest_attempt is not None and latest_attempt.input_context_json is not None:
            input_context_json = dict(latest_attempt.input_context_json)
            attempt_number = latest_attempt.attempt_number
            latest_summary = latest_attempt.summary
        else:
            input_context_json = _subtask_input_snapshot(session, run.compiled_workflow_id, state.current_compiled_subtask_id)
            attempt_number = None
            latest_summary = None
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        if subtask is None:
            raise DaemonNotFoundError("current compiled subtask not found")
        cursor_child_results = list((state.execution_cursor_json or {}).get("child_session_results", []))
        if cursor_child_results:
            merged_child_results = list(input_context_json.get("child_session_results", []))
            merged_child_results.extend(item for item in cursor_child_results if item not in merged_child_results)
            input_context_json["child_session_results"] = merged_child_results
        parent_reconcile_context = dict((state.execution_cursor_json or {}).get("parent_reconcile_context", {}))
        if parent_reconcile_context:
            input_context_json["parent_reconcile_context"] = parent_reconcile_context
        stage_context_json = _assemble_stage_context(session, run=run, state=state, version=version, subtask=subtask)
        input_context_json["stage_context_json"] = stage_context_json
        return SubtaskContextSnapshot(
            node_id=version.logical_node_id,
            node_run_id=run.id,
            compiled_subtask_id=state.current_compiled_subtask_id,
            attempt_number=attempt_number,
            input_context_json=input_context_json,
            latest_summary=latest_summary,
            stage_context_json=stage_context_json,
        )


def register_summary(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    summary_type: str,
    summary_path: str,
    content: str,
) -> SummaryRegistrationSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id is None:
            raise DaemonConflictError("current compiled subtask not found")
        attempt = _require_running_attempt(session, run.id, state.current_compiled_subtask_id)
        registered_at = datetime.now(timezone.utc).isoformat()
        content_hash = sha256(content.encode("utf-8")).hexdigest()
        output_json = dict(attempt.output_json or {})
        registrations = list(output_json.get("registered_summaries", []))
        registrations.append(
            {
                "summary_type": summary_type,
                "summary_path": summary_path,
                "content": content,
                "content_hash": content_hash,
                "content_length": len(content),
                "registered_at": registered_at,
            }
        )
        output_json["registered_summaries"] = registrations
        attempt.output_json = output_json
        attempt.summary = content if summary_type in {"subtask", "failure"} else attempt.summary
        summary_record = record_summary_history(
            session,
            node_version_id=version.id,
            node_run_id=run.id,
            compiled_subtask_id=attempt.compiled_subtask_id,
            attempt_number=attempt.attempt_number,
            summary_type=summary_type,
            summary_scope="subtask_attempt",
            summary_path=summary_path,
            content=content,
            metadata_json={
                "summary_type": summary_type,
                "summary_path": summary_path,
                "content_length": len(content),
                "registered_at": registered_at,
            },
        )
        session.flush()
        return SummaryRegistrationSnapshot(
            summary_id=summary_record.id,
            node_id=version.logical_node_id,
            node_run_id=run.id,
            compiled_subtask_id=attempt.compiled_subtask_id,
            attempt_number=attempt.attempt_number,
            summary_type=summary_type,
            summary_path=summary_path,
            content_hash=content_hash,
            content_length=len(content),
            registered_at=registered_at,
        )


def succeed_current_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    summary_path: str,
    content: str,
    catalog: ResourceCatalog | None = None,
) -> CompositeStageOutcomeSnapshot:
    with query_session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        current_subtask = session.get(CompiledSubtask, compiled_subtask_id)
        if current_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        if current_subtask.command_text:
            raise DaemonConflictError("subtask succeed only supports non-command stages")
        if current_subtask.subtask_type in {"review", "validate", "run_tests", "build_docs"}:
            raise DaemonConflictError("subtask succeed does not support this stage type")
        accepted_subtask_type = current_subtask.subtask_type
        node_run_id = run.id
        node_id = version.logical_node_id

    registration = register_summary(
        session_factory,
        logical_node_id=logical_node_id,
        summary_type="subtask",
        summary_path=summary_path,
        content=content,
    )
    complete_current_subtask(
        session_factory,
        logical_node_id=logical_node_id,
        compiled_subtask_id=compiled_subtask_id,
        summary=_summary_preview(content),
    )
    progressed = advance_workflow(session_factory, logical_node_id=logical_node_id, catalog=catalog)
    return CompositeStageOutcomeSnapshot(
        node_id=node_id,
        node_run_id=node_run_id,
        accepted_compiled_subtask_id=compiled_subtask_id,
        accepted_subtask_type=accepted_subtask_type,
        recorded_summary_id=registration.summary_id,
        recorded_summary_path=summary_path,
        outcome=_route_outcome(progressed),
        progress=progressed,
    )


def report_command_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    execution_result_json: dict[str, object],
    failure_summary: str | None = None,
    catalog: ResourceCatalog | None = None,
) -> CompositeStageOutcomeSnapshot:
    with query_session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        current_subtask = session.get(CompiledSubtask, compiled_subtask_id)
        if current_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        if not current_subtask.command_text:
            raise DaemonConflictError("subtask report-command only supports command stages")
        node_run_id = run.id
        node_id = version.logical_node_id
        accepted_subtask_type = current_subtask.subtask_type

    exit_code = execution_result_json.get("exit_code")
    if not isinstance(exit_code, int):
        raise DaemonConflictError("command result payload must include integer exit_code")

    if accepted_subtask_type in {"validate", "run_tests"}:
        complete_current_subtask(
            session_factory,
            logical_node_id=logical_node_id,
            compiled_subtask_id=compiled_subtask_id,
            execution_result_json=execution_result_json,
            summary=f"Recorded command result for {accepted_subtask_type}.",
        )
        progressed = advance_workflow(session_factory, logical_node_id=logical_node_id, catalog=catalog)
        return CompositeStageOutcomeSnapshot(
            node_id=node_id,
            node_run_id=node_run_id,
            accepted_compiled_subtask_id=compiled_subtask_id,
            accepted_subtask_type=accepted_subtask_type,
            recorded_summary_id=UUID(int=0),
            recorded_summary_path="summaries/command_result.json",
            outcome=_route_outcome(progressed),
            progress=progressed,
        )

    if exit_code == 0:
        complete_current_subtask(
            session_factory,
            logical_node_id=logical_node_id,
            compiled_subtask_id=compiled_subtask_id,
            execution_result_json=execution_result_json,
            summary="Completed command subtask.",
        )
        progressed = advance_workflow(session_factory, logical_node_id=logical_node_id, catalog=catalog)
        return CompositeStageOutcomeSnapshot(
            node_id=node_id,
            node_run_id=node_run_id,
            accepted_compiled_subtask_id=compiled_subtask_id,
            accepted_subtask_type=accepted_subtask_type,
            recorded_summary_id=UUID(int=0),
            recorded_summary_path="summaries/command_result.json",
            outcome=_route_outcome(progressed),
            progress=progressed,
        )

    failed = fail_current_subtask(
        session_factory,
        logical_node_id=logical_node_id,
        compiled_subtask_id=compiled_subtask_id,
        summary=(failure_summary or f"Command subtask failed with exit code {exit_code}."),
        execution_result_json=execution_result_json,
    )
    return CompositeStageOutcomeSnapshot(
        node_id=node_id,
        node_run_id=node_run_id,
        accepted_compiled_subtask_id=compiled_subtask_id,
        accepted_subtask_type=accepted_subtask_type,
        recorded_summary_id=UUID(int=0),
        recorded_summary_path="summaries/command_result.json",
        outcome=_route_outcome(failed),
        progress=failed,
    )


def fail_current_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    compiled_subtask_id: UUID,
    summary: str,
    execution_result_json: dict[str, object] | None = None,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if state.current_compiled_subtask_id != compiled_subtask_id:
            raise DaemonConflictError("compiled subtask is not the current run cursor")
        attempt = _require_running_attempt(session, run.id, compiled_subtask_id)
        attempt.status = "FAILED"
        if execution_result_json is not None:
            attempt.execution_result_json = dict(execution_result_json)
            compatibility_output = dict(attempt.output_json or {})
            compatibility_output.update(execution_result_json)
            attempt.output_json = compatibility_output
        attempt.summary = summary
        attempt.ended_at = datetime.now(timezone.utc)
        run.run_status = "FAILED"
        run.ended_at = datetime.now(timezone.utc)
        run.summary = summary
        state.lifecycle_state = "FAILED_TO_PARENT"
        state.is_resumable = False
        state.failure_count_consecutive += 1
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def advance_workflow(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    catalog: ResourceCatalog | None = None,
) -> RunProgressSnapshot:
    current_subtask_id: UUID | None = None
    current_subtask_type: str | None = None
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        current_subtask_id = state.current_compiled_subtask_id
        if current_subtask_id is None:
            raise DaemonConflictError("run has no current compiled subtask")
        attempt = _latest_attempt(session, run.id, current_subtask_id)
        if attempt is None or attempt.status != "COMPLETE":
            raise DaemonConflictError("current compiled subtask is not complete")
        current_subtask = session.get(CompiledSubtask, current_subtask_id)
        if current_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        current_subtask_type = current_subtask.subtask_type
    if current_subtask_type == "validate":
        summary = evaluate_validation_subtask(session_factory, logical_node_id=logical_node_id)
        if summary.status != "passed":
            with session_scope(session_factory) as session:
                run, state, _ = _load_active_run_bundle(session, logical_node_id)
                attempt = _latest_attempt(session, run.id, current_subtask_id)
                if attempt is not None:
                    attempt.validation_json = summary.to_payload()
                    attempt.summary = "validation failed"
                run.run_status = "FAILED"
                run.ended_at = datetime.now(timezone.utc)
                run.summary = "validation failed"
                state.lifecycle_state = "FAILED_TO_PARENT"
                state.is_resumable = False
                _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
                session.flush()
                return _progress_snapshot(session, run.id)
        with session_scope(session_factory) as session:
            run, _, _ = _load_active_run_bundle(session, logical_node_id)
            attempt = _latest_attempt(session, run.id, current_subtask_id)
            if attempt is not None:
                attempt.validation_json = summary.to_payload()
            session.flush()
    if current_subtask_type == "review":
        summary = evaluate_review_subtask(session_factory, logical_node_id=logical_node_id)
        if summary.status == "failed":
            return _apply_review_failure_route(
                session_factory,
                logical_node_id=logical_node_id,
                current_subtask_id=current_subtask_id,
                summary=summary,
            )
        if summary.status == "revise":
            return _apply_review_revise_route(
                session_factory,
                logical_node_id=logical_node_id,
                current_subtask_id=current_subtask_id,
                summary=summary,
            )
        with session_scope(session_factory) as session:
            run, _, _ = _load_active_run_bundle(session, logical_node_id)
            attempt = _latest_attempt(session, run.id, current_subtask_id)
            if attempt is not None:
                attempt.review_json = summary.to_payload()
            session.flush()
    if current_subtask_type == "run_tests":
        summary = evaluate_testing_subtask(session_factory, logical_node_id=logical_node_id, catalog=catalog)
        if summary.retry_pending:
            return _apply_testing_retry_route(
                session_factory,
                logical_node_id=logical_node_id,
                current_subtask_id=current_subtask_id,
                summary=summary,
            )
        if summary.status == "failed":
            return _apply_testing_failure_route(
                session_factory,
                logical_node_id=logical_node_id,
                current_subtask_id=current_subtask_id,
                summary=summary,
            )
        with session_scope(session_factory) as session:
            run, state, _ = _load_active_run_bundle(session, logical_node_id)
            attempt = _latest_attempt(session, run.id, current_subtask_id)
            if attempt is not None:
                attempt.testing_json = summary.to_payload()
            execution_cursor = dict(state.execution_cursor_json or {})
            execution_cursor.pop("testing_retry_pending", None)
            execution_cursor.pop("testing_rerun_failed_only", None)
            state.execution_cursor_json = execution_cursor
            session.flush()
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        assert current_subtask_id is not None
        next_subtask = _next_subtask(session, run.compiled_workflow_id, current_subtask_id)
        if next_subtask is None:
            run.run_status = "COMPLETE"
            run.ended_at = datetime.now(timezone.utc)
            state.lifecycle_state = "COMPLETE"
            state.current_task_id = None
            state.current_compiled_subtask_id = None
            state.current_subtask_attempt = None
            state.is_resumable = False
            record_completed_child_for_incremental_merge_in_session(session, child_node_version_id=version.id)
            _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
            session.flush()
            return _progress_snapshot(session, run.id)
        state.lifecycle_state = "RUNNING"
        state.current_task_id = next_subtask.compiled_task_id
        state.current_compiled_subtask_id = next_subtask.id
        state.current_subtask_attempt = None
        state.execution_cursor_json = {"position": next_subtask.ordinal}
        if next_subtask.block_on_user_flag:
            _pause_run(
                session,
                logical_node_id=logical_node_id,
                run=run,
                state=state,
                node_version_id=version.id,
                pause_flag_name=next_subtask.block_on_user_flag,
                pause_summary=f"Paused before gated subtask '{next_subtask.title or next_subtask.source_subtask_key}'.",
                approval_required=True,
                current_subtask=next_subtask,
                pause_summary_prompt=next_subtask.pause_summary_prompt,
            )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def sync_paused_run(session_factory: sessionmaker[Session], *, logical_node_id: UUID, pause_flag_name: str | None) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        _pause_run(
            session,
            logical_node_id=logical_node_id,
            run=run,
            state=state,
            node_version_id=version.id,
            pause_flag_name=pause_flag_name or "manual_pause",
            pause_summary="Run paused manually by operator request.",
            approval_required=False,
            event_type="pause_entered",
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def approve_paused_run(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    pause_flag_name: str | None = None,
    approval_summary: str | None = None,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        if run.run_status != "PAUSED" or state.lifecycle_state != "PAUSED_FOR_USER":
            raise DaemonConflictError("node run is not currently paused for user approval")
        active_flag = state.pause_flag_name
        if active_flag is None:
            raise DaemonConflictError("paused run does not have an active pause flag")
        if pause_flag_name is not None and pause_flag_name != active_flag:
            raise DaemonConflictError(f"pause flag mismatch: expected '{active_flag}'")
        cursor = dict(state.execution_cursor_json or {})
        approved_flags = [str(item) for item in cursor.get(APPROVED_PAUSE_FLAGS_KEY, [])]
        if active_flag not in approved_flags:
            approved_flags.append(active_flag)
        cursor[APPROVED_PAUSE_FLAGS_KEY] = approved_flags
        pause_context = dict(cursor.get(PAUSE_CONTEXT_KEY, {}))
        pause_context["approved"] = True
        pause_context["approval_summary"] = approval_summary
        cursor[PAUSE_CONTEXT_KEY] = pause_context
        state.execution_cursor_json = cursor
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            event_scope="pause",
            event_type="pause_cleared",
            payload_json={
                "pause_flag_name": active_flag,
                "approval_summary": approval_summary,
            },
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def sync_resumed_run(session_factory: sessionmaker[Session], *, logical_node_id: UUID, force: bool = False) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        active_flag = state.pause_flag_name
        if active_flag is not None and active_flag != "manual_pause" and not force:
            cursor = dict(state.execution_cursor_json or {})
            approved_flags = {str(item) for item in cursor.get(APPROVED_PAUSE_FLAGS_KEY, [])}
            if active_flag not in approved_flags:
                raise DaemonConflictError(f"pause flag '{active_flag}' requires explicit approval before resume")
        run.run_status = "RUNNING"
        state.lifecycle_state = "RUNNING"
        cursor = dict(state.execution_cursor_json or {})
        pause_context = dict(cursor.get(PAUSE_CONTEXT_KEY, {}))
        pause_context["resumed"] = True
        cursor[PAUSE_CONTEXT_KEY] = pause_context
        cursor.pop(APPROVED_PAUSE_FLAGS_KEY, None)
        state.execution_cursor_json = cursor
        state.pause_flag_name = None
        state.is_resumable = True
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            event_scope="pause",
            event_type="pause_resumed",
            payload_json={
                "pause_flag_name": active_flag,
                "resumed_via": "force" if force else "approved_resume",
            },
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def sync_failed_run(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    failure_summary: str,
    failure_reason: str,
) -> RunProgressSnapshot:
    failed_at = datetime.now(timezone.utc)
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        failed_attempt_id: UUID | None = None
        if state.current_compiled_subtask_id is not None:
            latest_attempt = _latest_attempt(session, run.id, state.current_compiled_subtask_id)
            if latest_attempt is not None and latest_attempt.status == "RUNNING":
                latest_attempt.status = "FAILED"
                latest_attempt.summary = failure_summary
                latest_attempt.ended_at = failed_at
                output_json = dict(latest_attempt.output_json or {})
                output_json["session_failure_reason"] = failure_reason
                output_json["session_failure_summary"] = failure_summary
                latest_attempt.output_json = output_json
                failed_attempt_id = latest_attempt.id
        run.run_status = "FAILED"
        run.ended_at = failed_at
        run.summary = failure_summary
        state.lifecycle_state = "FAILED_TO_PARENT"
        state.pause_flag_name = None
        state.is_resumable = False
        state.failure_count_consecutive += 1
        cursor = dict(state.execution_cursor_json or {})
        cursor.pop(APPROVED_PAUSE_FLAGS_KEY, None)
        cursor.pop(PAUSE_CONTEXT_KEY, None)
        cursor["session_failure"] = {
            "failed_at": failed_at.isoformat(),
            "reason": failure_reason,
            "summary": failure_summary,
            "failed_attempt_id": None if failed_attempt_id is None else str(failed_attempt_id),
        }
        state.execution_cursor_json = cursor
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            event_scope="run",
            event_type="run_failed",
            payload_json=dict(cursor["session_failure"]),
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def cancel_active_run(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    summary: str | None = None,
) -> RunProgressSnapshot:
    cancelled_at = datetime.now(timezone.utc)
    cancellation_summary = summary or "Run cancelled by operator request."
    with session_scope(session_factory) as session:
        run, state, version = _load_active_run_bundle(session, logical_node_id)
        cancelled_attempt_id: UUID | None = None
        if state.current_compiled_subtask_id is not None:
            latest_attempt = _latest_attempt(session, run.id, state.current_compiled_subtask_id)
            if latest_attempt is not None and latest_attempt.status == "RUNNING":
                latest_attempt.status = "CANCELLED"
                latest_attempt.summary = cancellation_summary
                latest_attempt.ended_at = cancelled_at
                cancelled_attempt_id = latest_attempt.id
        run.run_status = "CANCELLED"
        run.ended_at = cancelled_at
        run.summary = cancellation_summary
        state.lifecycle_state = "CANCELLED"
        state.current_task_id = None
        state.current_compiled_subtask_id = None
        state.current_subtask_attempt = None
        state.pause_flag_name = None
        state.is_resumable = False
        cursor = dict(state.execution_cursor_json or {})
        cursor.pop(APPROVED_PAUSE_FLAGS_KEY, None)
        cursor.pop(PAUSE_CONTEXT_KEY, None)
        cursor["cancellation"] = {
            "cancelled_at": cancelled_at.isoformat(),
            "summary": cancellation_summary,
            "cancelled_attempt_id": None if cancelled_attempt_id is None else str(cancelled_attempt_id),
        }
        state.execution_cursor_json = cursor
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            event_scope="run_control",
            event_type="run_cancelled",
            payload_json=dict(cursor["cancellation"]),
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def retry_current_subtask(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID | None = None,
    attempt_id: UUID | None = None,
) -> RunProgressSnapshot:
    if logical_node_id is None and attempt_id is None:
        raise DaemonConflictError("retry requires a node id or attempt id")
    with session_scope(session_factory) as session:
        run, state, version, latest_attempt = _load_retryable_bundle(
            session,
            logical_node_id=logical_node_id,
            attempt_id=attempt_id,
        )
        compiled_subtask = session.get(CompiledSubtask, latest_attempt.compiled_subtask_id)
        if compiled_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        if latest_attempt.status == "RUNNING":
            raise DaemonConflictError("current compiled subtask already has a running attempt")
        cursor = dict(state.execution_cursor_json or {})
        retry_reason: str | None = None
        if latest_attempt.status == "FAILED":
            retry_reason = "failed_attempt"
        elif bool(cursor.get("testing_retry_pending")) and latest_attempt.status == "COMPLETE":
            retry_reason = "testing_retry_pending"
        elif run.run_status == "PAUSED" and state.pause_flag_name in {
            "review_failed",
            "review_revision_requested",
            "testing_failed",
            "testing_override_required",
        }:
            retry_reason = f"pause_flag:{state.pause_flag_name}"
        if retry_reason is None:
            raise DaemonConflictError("current subtask is not in a retryable state")
        retried_at = datetime.now(timezone.utc)
        next_attempt_number = latest_attempt.attempt_number + 1
        run.run_status = "RUNNING"
        run.ended_at = None
        run.summary = None
        state.lifecycle_state = "RUNNING"
        state.current_task_id = compiled_subtask.compiled_task_id
        state.current_compiled_subtask_id = latest_attempt.compiled_subtask_id
        state.current_subtask_attempt = next_attempt_number
        state.pause_flag_name = None
        state.is_resumable = True
        cursor.pop(APPROVED_PAUSE_FLAGS_KEY, None)
        cursor.pop(PAUSE_CONTEXT_KEY, None)
        cursor.pop("testing_retry_pending", None)
        cursor.pop("testing_rerun_failed_only", None)
        state.execution_cursor_json = cursor
        attempt = SubtaskAttempt(
            id=uuid4(),
            node_run_id=run.id,
            compiled_subtask_id=latest_attempt.compiled_subtask_id,
            attempt_number=next_attempt_number,
            status="RUNNING",
            input_context_json=_subtask_input_snapshot(session, run.compiled_workflow_id, latest_attempt.compiled_subtask_id),
            started_at=retried_at,
        )
        session.add(attempt)
        record_workflow_event(
            session,
            logical_node_id=version.logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            event_scope="subtask",
            event_type="subtask_retry_started",
            payload_json={
                "compiled_subtask_id": str(latest_attempt.compiled_subtask_id),
                "retry_reason": retry_reason,
                "previous_attempt_id": str(latest_attempt.id),
                "new_attempt_id": str(attempt.id),
                "new_attempt_number": next_attempt_number,
            },
        )
        _sync_lifecycle_with_run(session, logical_node_id=version.logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def _progress_snapshot(session: Session, run_id: UUID) -> RunProgressSnapshot:
    return _progress_snapshot_with_failure(session, run_id, terminal_failure=None)


def _progress_snapshot_with_failure(session: Session, run_id: UUID, *, terminal_failure: dict[str, object] | None) -> RunProgressSnapshot:
    run = session.get(NodeRun, run_id)
    if run is None:
        raise DaemonNotFoundError("node run not found")
    version = session.get(NodeVersion, run.node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    state = session.get(NodeRunState, run.id)
    if state is None:
        raise DaemonNotFoundError("node run state not found")
    latest_attempt = None
    if state.current_compiled_subtask_id is not None:
        latest_attempt = _latest_attempt(session, run.id, state.current_compiled_subtask_id)
    return RunProgressSnapshot(
        run=_run_snapshot(run, version.logical_node_id),
        state=_state_snapshot(state),
        current_subtask=_current_subtask_payload(session, state.current_compiled_subtask_id),
        latest_attempt=None if latest_attempt is None else _attempt_snapshot(latest_attempt),
        terminal_failure=terminal_failure,
    )


def _run_snapshot(run: NodeRun, logical_node_id: UUID) -> NodeRunSnapshot:
    return NodeRunSnapshot(
        id=run.id,
        node_version_id=run.node_version_id,
        logical_node_id=logical_node_id,
        run_number=run.run_number,
        trigger_reason=run.trigger_reason,
        run_status=run.run_status,
        compiled_workflow_id=run.compiled_workflow_id,
        started_at=None if run.started_at is None else run.started_at.isoformat(),
        ended_at=None if run.ended_at is None else run.ended_at.isoformat(),
        summary=run.summary,
    )


def _state_snapshot(state: NodeRunState) -> NodeRunStateSnapshot:
    return NodeRunStateSnapshot(
        node_run_id=state.node_run_id,
        lifecycle_state=state.lifecycle_state,
        current_task_id=state.current_task_id,
        current_compiled_subtask_id=state.current_compiled_subtask_id,
        current_subtask_attempt=state.current_subtask_attempt,
        last_completed_compiled_subtask_id=state.last_completed_compiled_subtask_id,
        execution_cursor_json=dict(state.execution_cursor_json),
        failure_count_from_children=state.failure_count_from_children,
        failure_count_consecutive=state.failure_count_consecutive,
        defer_to_user_threshold=state.defer_to_user_threshold,
        pause_flag_name=state.pause_flag_name,
        is_resumable=state.is_resumable,
        working_tree_state=state.working_tree_state,
        updated_at=state.updated_at.isoformat(),
    )


def _attempt_snapshot(attempt: SubtaskAttempt) -> SubtaskAttemptSnapshot:
    return SubtaskAttemptSnapshot(
        id=attempt.id,
        node_run_id=attempt.node_run_id,
        compiled_subtask_id=attempt.compiled_subtask_id,
        attempt_number=attempt.attempt_number,
        status=attempt.status,
        input_context_json=attempt.input_context_json,
        output_json=attempt.output_json,
        execution_result_json=attempt.execution_result_json,
        execution_environment_json=attempt.execution_environment_json,
        validation_json=attempt.validation_json,
        review_json=attempt.review_json,
        testing_json=attempt.testing_json,
        summary=attempt.summary,
        started_at=None if attempt.started_at is None else attempt.started_at.isoformat(),
        ended_at=None if attempt.ended_at is None else attempt.ended_at.isoformat(),
    )


def load_subtask_attempt(session_factory: sessionmaker[Session], *, attempt_id: UUID) -> SubtaskAttemptSnapshot:
    with query_session_scope(session_factory) as session:
        attempt = session.get(SubtaskAttempt, attempt_id)
        if attempt is None:
            raise DaemonNotFoundError("subtask attempt not found")
        return _attempt_snapshot(attempt)


def list_subtask_attempts_for_node(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
) -> tuple[UUID, list[SubtaskAttemptSnapshot]]:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            raise DaemonNotFoundError("active node run not found")
        attempts = session.execute(
            select(SubtaskAttempt)
            .where(SubtaskAttempt.node_run_id == run.id)
            .order_by(SubtaskAttempt.created_at, SubtaskAttempt.attempt_number, SubtaskAttempt.id)
        ).scalars().all()
        return run.id, [_attempt_snapshot(item) for item in attempts]


def _current_subtask_payload(session: Session, compiled_subtask_id: UUID | None) -> dict[str, object] | None:
    if compiled_subtask_id is None:
        return None
    subtask = session.get(CompiledSubtask, compiled_subtask_id)
    if subtask is None:
        return None
    return {
        "id": str(subtask.id),
        "compiled_task_id": str(subtask.compiled_task_id),
        "source_subtask_key": subtask.source_subtask_key,
        "ordinal": subtask.ordinal,
        "subtask_type": subtask.subtask_type,
        "title": subtask.title,
        "prompt_text": subtask.prompt_text,
        "command_text": subtask.command_text,
        "environment_policy_ref": subtask.environment_policy_ref,
        "environment_request_json": dict(subtask.environment_request_json or {}),
        "block_on_user_flag": subtask.block_on_user_flag,
        "pause_summary_prompt": subtask.pause_summary_prompt,
    }


def _summary_preview(content: str) -> str:
    for raw_line in content.splitlines():
        line = raw_line.strip().strip("#*-` ").strip()
        if line:
            return line[:160]
    return "subtask succeeded"


def _route_outcome(progress: RunProgressSnapshot) -> str:
    if progress.run.run_status == "COMPLETE":
        return "completed"
    if progress.run.run_status == "FAILED":
        return "failed"
    if progress.run.run_status == "PAUSED" or progress.state.lifecycle_state == "PAUSED":
        return "paused"
    return "next_stage"


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _active_run_for_version(session: Session, node_version_id: UUID) -> NodeRun | None:
    return session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == node_version_id, NodeRun.run_status.in_(ACTIVE_RUN_STATUSES))
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()


def _next_run_number(session: Session, node_version_id: UUID) -> int:
    current = session.execute(
        select(func.max(NodeRun.run_number)).where(NodeRun.node_version_id == node_version_id)
    ).scalar_one()
    return 1 if current is None else int(current) + 1


def _first_subtask(session: Session, workflow_id: UUID) -> CompiledSubtask | None:
    return session.execute(
        select(CompiledSubtask)
        .join(CompiledTask, CompiledSubtask.compiled_task_id == CompiledTask.id)
        .where(CompiledTask.compiled_workflow_id == workflow_id)
        .order_by(CompiledTask.ordinal, CompiledSubtask.ordinal)
    ).scalars().first()


def _first_subtask_for_task(session: Session, compiled_task_id: UUID) -> CompiledSubtask:
    subtask = session.execute(
        select(CompiledSubtask)
        .where(CompiledSubtask.compiled_task_id == compiled_task_id)
        .order_by(CompiledSubtask.ordinal)
    ).scalars().first()
    if subtask is None:
        raise DaemonNotFoundError("compiled task entry subtask not found")
    return subtask


def _review_retry_subtask(session: Session, workflow_id: UUID, current_subtask_id: UUID) -> CompiledSubtask:
    ordered = session.execute(
        select(CompiledSubtask)
        .join(CompiledTask, CompiledSubtask.compiled_task_id == CompiledTask.id)
        .where(CompiledTask.compiled_workflow_id == workflow_id)
        .order_by(CompiledTask.ordinal, CompiledSubtask.ordinal)
    ).scalars().all()
    gate_types = {"validate", "review", "run_tests", "build_docs"}
    prior: list[CompiledSubtask] = []
    for subtask in ordered:
        if subtask.id == current_subtask_id:
            break
        prior.append(subtask)
    for subtask in reversed(prior):
        if subtask.subtask_type not in gate_types:
            return _first_subtask_for_task(session, subtask.compiled_task_id)
    if prior:
        return _first_subtask_for_task(session, prior[-1].compiled_task_id)
    raise DaemonConflictError("review revision route could not determine a retry subtask")


def _next_subtask(session: Session, workflow_id: UUID, current_subtask_id: UUID) -> CompiledSubtask | None:
    ordered = session.execute(
        select(CompiledSubtask)
        .join(CompiledTask, CompiledSubtask.compiled_task_id == CompiledTask.id)
        .where(CompiledTask.compiled_workflow_id == workflow_id)
        .order_by(CompiledTask.ordinal, CompiledSubtask.ordinal)
    ).scalars().all()
    for index, subtask in enumerate(ordered):
        if subtask.id == current_subtask_id:
            return None if index + 1 >= len(ordered) else ordered[index + 1]
    raise DaemonConflictError("current compiled subtask is not part of the run workflow")


def _pause_run(
    session: Session,
    *,
    logical_node_id: UUID,
    run: NodeRun,
    state: NodeRunState,
    node_version_id: UUID,
    pause_flag_name: str,
    pause_summary: str,
    approval_required: bool,
    event_type: str = "pause_entered",
    current_subtask: CompiledSubtask | None = None,
    pause_summary_prompt: str | None = None,
) -> None:
    run.run_status = "PAUSED"
    state.lifecycle_state = "PAUSED_FOR_USER"
    state.pause_flag_name = pause_flag_name
    state.is_resumable = True
    cursor = dict(state.execution_cursor_json or {})
    cursor.pop(APPROVED_PAUSE_FLAGS_KEY, None)
    cursor[PAUSE_CONTEXT_KEY] = {
        "pause_flag_name": pause_flag_name,
        "pause_summary": pause_summary,
        "approval_required": approval_required,
        "compiled_subtask_id": None if current_subtask is None else str(current_subtask.id),
        "source_subtask_key": None if current_subtask is None else current_subtask.source_subtask_key,
        "pause_summary_prompt": pause_summary_prompt,
        "approved": False,
        "resumed": False,
    }
    state.execution_cursor_json = cursor
    record_workflow_event(
        session,
        logical_node_id=logical_node_id,
        node_version_id=node_version_id,
        node_run_id=run.id,
        event_scope="pause",
        event_type=event_type,
        payload_json=dict(cursor[PAUSE_CONTEXT_KEY]),
    )


def _apply_review_failure_route(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    current_subtask_id: UUID,
    summary,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, _ = _load_active_run_bundle(session, logical_node_id)
        attempt = _latest_attempt(session, run.id, current_subtask_id)
        if attempt is not None:
            attempt.review_json = summary.to_payload()
            attempt.summary = "review failed"
        action = summary.action or "fail_to_parent"
        if action == "pause_for_user":
            current_subtask = session.get(CompiledSubtask, current_subtask_id)
            pause_summary = next((item.summary for item in summary.results if item.summary), None)
            _pause_run(
                session,
                logical_node_id=logical_node_id,
                run=run,
                state=state,
                node_version_id=run.node_version_id,
                pause_flag_name="review_failed",
                pause_summary=pause_summary or "Review failed and requires user intervention.",
                approval_required=True,
                current_subtask=current_subtask,
            )
        else:
            run.run_status = "FAILED"
            run.ended_at = datetime.now(timezone.utc)
            run.summary = "review failed"
            state.lifecycle_state = "FAILED_TO_PARENT"
            state.is_resumable = False
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def _apply_review_revise_route(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    current_subtask_id: UUID,
    summary,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, _ = _load_active_run_bundle(session, logical_node_id)
        attempt = _latest_attempt(session, run.id, current_subtask_id)
        if attempt is not None:
            attempt.review_json = summary.to_payload()
            attempt.summary = "review requested revision"
        action = summary.action or "rerun_task"
        if action == "pause_for_user":
            current_subtask = session.get(CompiledSubtask, current_subtask_id)
            _pause_run(
                session,
                logical_node_id=logical_node_id,
                run=run,
                state=state,
                node_version_id=run.node_version_id,
                pause_flag_name="review_revision_requested",
                pause_summary=summary.summary or "Review requested a revision and requires explicit approval to continue.",
                approval_required=True,
                current_subtask=current_subtask,
            )
        else:
            current_subtask = session.get(CompiledSubtask, current_subtask_id)
            if current_subtask is None:
                raise DaemonNotFoundError("compiled subtask not found")
            retry_subtask = _review_retry_subtask(session, run.compiled_workflow_id, current_subtask_id)
            run.run_status = "RUNNING"
            state.lifecycle_state = "RUNNING"
            state.current_task_id = retry_subtask.compiled_task_id
            state.current_compiled_subtask_id = retry_subtask.id
            state.current_subtask_attempt = None
            state.pause_flag_name = None
            state.is_resumable = True
            state.execution_cursor_json = {"position": retry_subtask.ordinal}
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def _apply_testing_failure_route(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    current_subtask_id: UUID,
    summary,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, _ = _load_active_run_bundle(session, logical_node_id)
        attempt = _latest_attempt(session, run.id, current_subtask_id)
        if attempt is not None:
            attempt.testing_json = summary.to_payload()
            attempt.summary = "testing failed"
        action = summary.action or "fail_to_parent"
        if action in {"pause_for_user", "allow_override"}:
            current_subtask = session.get(CompiledSubtask, current_subtask_id)
            pause_summary = next((item.summary for item in summary.results if item.summary), None)
            _pause_run(
                session,
                logical_node_id=logical_node_id,
                run=run,
                state=state,
                node_version_id=run.node_version_id,
                pause_flag_name="testing_failed" if action == "pause_for_user" else "testing_override_required",
                pause_summary=pause_summary or "Testing failed and requires explicit user approval.",
                approval_required=True,
                current_subtask=current_subtask,
            )
        else:
            run.run_status = "FAILED"
            run.ended_at = datetime.now(timezone.utc)
            run.summary = "testing failed"
            state.lifecycle_state = "FAILED_TO_PARENT"
            state.is_resumable = False
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def _apply_testing_retry_route(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    current_subtask_id: UUID,
    summary,
) -> RunProgressSnapshot:
    with session_scope(session_factory) as session:
        run, state, _ = _load_active_run_bundle(session, logical_node_id)
        attempt = _latest_attempt(session, run.id, current_subtask_id)
        if attempt is not None:
            attempt.testing_json = summary.to_payload()
            attempt.summary = "testing retry required"
        current_subtask = session.get(CompiledSubtask, current_subtask_id)
        if current_subtask is None:
            raise DaemonNotFoundError("compiled subtask not found")
        run.run_status = "RUNNING"
        state.lifecycle_state = "RUNNING"
        state.current_task_id = current_subtask.compiled_task_id
        state.current_compiled_subtask_id = current_subtask.id
        state.current_subtask_attempt = None
        state.pause_flag_name = None
        state.is_resumable = True
        state.execution_cursor_json = {
            "position": current_subtask.ordinal,
            "testing_retry_pending": True,
            "testing_rerun_failed_only": summary.rerun_failed_only,
        }
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=run, state=state)
        session.flush()
        return _progress_snapshot(session, run.id)


def _latest_attempt(session: Session, node_run_id: UUID, compiled_subtask_id: UUID) -> SubtaskAttempt | None:
    return session.execute(
        select(SubtaskAttempt)
        .where(
            SubtaskAttempt.node_run_id == node_run_id,
            SubtaskAttempt.compiled_subtask_id == compiled_subtask_id,
        )
        .order_by(SubtaskAttempt.attempt_number.desc())
    ).scalars().first()


def _require_running_attempt(session: Session, node_run_id: UUID, compiled_subtask_id: UUID) -> SubtaskAttempt:
    attempt = _latest_attempt(session, node_run_id, compiled_subtask_id)
    if attempt is None or attempt.status != "RUNNING":
        raise DaemonConflictError("current compiled subtask has no running attempt")
    return attempt


def _assemble_stage_context(
    session: Session,
    *,
    run: NodeRun,
    state: NodeRunState,
    version: NodeVersion,
    subtask: CompiledSubtask,
) -> dict[str, object]:
    compiled_task = session.get(CompiledTask, subtask.compiled_task_id)
    prompt_rows = session.execute(
        select(PromptRecord)
        .where(PromptRecord.node_run_id == run.id)
        .order_by(PromptRecord.delivered_at.desc(), PromptRecord.id.desc())
        .limit(5)
    ).scalars().all()
    summary_rows = session.execute(
        select(SummaryRecord)
        .where(SummaryRecord.node_run_id == run.id)
        .order_by(SummaryRecord.created_at.desc(), SummaryRecord.id.desc())
        .limit(5)
    ).scalars().all()
    dependency_rows = session.execute(
        select(NodeDependency)
        .where(NodeDependency.node_version_id == version.id)
        .order_by(NodeDependency.created_at, NodeDependency.id)
    ).scalars().all()
    blocker_rows = session.execute(
        select(NodeDependencyBlocker)
        .where(NodeDependencyBlocker.node_version_id == version.id)
        .order_by(NodeDependencyBlocker.created_at, NodeDependencyBlocker.id)
    ).scalars().all()
    cursor = dict(state.execution_cursor_json or {})
    return {
        "startup": {
            "node_id": str(version.logical_node_id),
            "node_version_id": str(version.id),
            "node_title": version.title,
            "node_kind": version.node_kind,
            "node_prompt": version.prompt,
            "run_id": str(run.id),
            "run_number": run.run_number,
            "trigger_reason": run.trigger_reason,
            "compiled_workflow_id": str(run.compiled_workflow_id),
        },
        "stage": {
            "compiled_task_id": str(subtask.compiled_task_id),
            "task_key": None if compiled_task is None else compiled_task.task_key,
            "compiled_subtask_id": str(subtask.id),
            "source_subtask_key": subtask.source_subtask_key,
            "subtask_type": subtask.subtask_type,
            "title": subtask.title,
            "environment_policy_ref": subtask.environment_policy_ref,
            "environment_request_json": dict(subtask.environment_request_json or {}),
        },
        "dependencies": {
            "dependencies": [
                {
                    "dependency_id": str(item.id),
                    "depends_on_node_version_id": str(item.depends_on_node_version_id),
                    "dependency_type": item.dependency_type,
                    "required_state": item.required_state,
                }
                for item in dependency_rows
            ],
            "blockers": [
                {
                    "blocker_kind": item.blocker_kind,
                    "dependency_id": None if item.dependency_id is None else str(item.dependency_id),
                    "target_node_version_id": None if item.target_node_version_id is None else str(item.target_node_version_id),
                    "details_json": dict(item.details_json or {}),
                }
                for item in blocker_rows
            ],
        },
        "history": {
            "recent_prompts": [
                {
                    "id": str(item.id),
                    "prompt_role": item.prompt_role,
                    "source_subtask_key": item.source_subtask_key,
                    "delivered_at": item.delivered_at.isoformat(),
                }
                for item in prompt_rows
            ],
            "recent_summaries": [
                {
                    "id": str(item.id),
                    "summary_type": item.summary_type,
                    "summary_scope": item.summary_scope,
                    "summary_path": item.summary_path,
                    "content": item.content,
                    "created_at": item.created_at.isoformat(),
                }
                for item in summary_rows
            ],
        },
        "cursor": {
            "current_subtask_attempt": state.current_subtask_attempt,
            "last_completed_compiled_subtask_id": None
            if state.last_completed_compiled_subtask_id is None
            else str(state.last_completed_compiled_subtask_id),
            "pause_context": dict(cursor.get(PAUSE_CONTEXT_KEY, {})),
            "parent_reconcile_context": dict(cursor.get("parent_reconcile_context", {})),
            "child_session_results": list(cursor.get("child_session_results", [])),
        },
    }


def _subtask_input_snapshot(session: Session, workflow_id: UUID, compiled_subtask_id: UUID) -> dict[str, object]:
    subtask = session.get(CompiledSubtask, compiled_subtask_id)
    if subtask is None:
        raise DaemonNotFoundError("compiled subtask not found")
    run = session.execute(select(NodeRun).where(NodeRun.compiled_workflow_id == workflow_id).order_by(NodeRun.run_number.desc())).scalars().first()
    version = None if run is None else session.get(NodeVersion, run.node_version_id)
    state = None if run is None else session.get(NodeRunState, run.id)
    stage_context_json = (
        {}
        if run is None or version is None or state is None
        else _assemble_stage_context(session, run=run, state=state, version=version, subtask=subtask)
    )
    return {
        "compiled_workflow_id": str(workflow_id),
        "compiled_subtask_id": str(subtask.id),
        "source_subtask_key": subtask.source_subtask_key,
        "subtask_type": subtask.subtask_type,
        "title": subtask.title,
        "stage_context_json": stage_context_json,
    }


def _load_active_run_bundle(session: Session, logical_node_id: UUID) -> tuple[NodeRun, NodeRunState, NodeVersion]:
    version = _authoritative_version(session, logical_node_id)
    run = _active_run_for_version(session, version.id)
    if run is None:
        latest_failure = _latest_failed_supervision_context(session, version.id)
        if latest_failure is not None:
            raise DaemonConflictError(
                "latest run failed after session supervision recovery failure; inspect node run show, session show, or node recovery-status instead of probing the closed run"
            )
        raise DaemonNotFoundError("active node run not found")
    state = session.get(NodeRunState, run.id)
    if state is None:
        raise DaemonNotFoundError("node run state not found")
    return run, state, version


def _load_retryable_bundle(
    session: Session,
    *,
    logical_node_id: UUID | None,
    attempt_id: UUID | None,
) -> tuple[NodeRun, NodeRunState, NodeVersion, SubtaskAttempt]:
    if logical_node_id is not None:
        version = _authoritative_version(session, logical_node_id)
        run = _latest_retryable_run_for_version(session, version.id)
        if run is None:
            raise DaemonNotFoundError("retryable node run not found")
    else:
        attempt = session.get(SubtaskAttempt, attempt_id)
        if attempt is None:
            raise DaemonNotFoundError("subtask attempt not found")
        run = session.get(NodeRun, attempt.node_run_id)
        if run is None:
            raise DaemonNotFoundError("node run not found")
        version = session.get(NodeVersion, run.node_version_id)
        if version is None:
            raise DaemonNotFoundError("node version not found")
        selector = session.get(LogicalNodeCurrentVersion, version.logical_node_id)
        if selector is None or selector.authoritative_node_version_id != version.id:
            raise DaemonConflictError("subtask attempt does not belong to the authoritative node version")
    state = session.get(NodeRunState, run.id)
    if state is None:
        raise DaemonNotFoundError("node run state not found")
    if state.current_compiled_subtask_id is None:
        raise DaemonConflictError("node run does not have a current compiled subtask")
    latest_attempt = _latest_attempt(session, run.id, state.current_compiled_subtask_id)
    if latest_attempt is None:
        raise DaemonConflictError("current compiled subtask has no prior attempt to retry")
    if attempt_id is not None and latest_attempt.id != attempt_id:
        raise DaemonConflictError("only the latest attempt for the current subtask may be retried")
    return run, state, version, latest_attempt


def _latest_retryable_run_for_version(session: Session, node_version_id: UUID) -> NodeRun | None:
    return session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == node_version_id, NodeRun.run_status.in_(ACTIVE_RUN_STATUSES | {"FAILED"}))
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()


def _latest_failed_supervision_context(session: Session, node_version_id: UUID) -> dict[str, object] | None:
    latest_run = session.execute(
        select(NodeRun).where(NodeRun.node_version_id == node_version_id).order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if latest_run is None or latest_run.run_status != "FAILED":
        return None
    state = session.get(NodeRunState, latest_run.id)
    if state is None:
        return None
    failure_row = session.execute(
        select(SessionEvent, DurableSession)
        .join(DurableSession, SessionEvent.session_id == DurableSession.id)
        .where(
            DurableSession.node_run_id == latest_run.id,
            DurableSession.session_role == "primary",
            SessionEvent.event_type == "supervision_recovery_failed",
        )
        .order_by(SessionEvent.created_at.desc())
    ).first()
    if failure_row is None:
        return None
    failure_event, failed_session = failure_row
    payload = dict(failure_event.payload_json or {})
    return {
        "run": latest_run,
        "state": state,
        "session": failed_session,
        "terminal_failure": {
            "failure_origin": "session_supervision",
            "failure_event_type": failure_event.event_type,
            "failure_reason": payload.get("reason"),
            "failure_summary": payload.get("failure_summary") or latest_run.summary,
            "error_type": payload.get("error_type"),
            "failed_run_id": str(latest_run.id),
            "failed_session_id": str(failed_session.id),
            "run_status": latest_run.run_status,
            "lifecycle_state": state.lifecycle_state,
            "session_status": failed_session.status,
            "recommended_action": "inspect_failed_run",
        },
    }


def _sync_lifecycle_with_run(session: Session, *, logical_node_id: UUID, run: NodeRun, state: NodeRunState) -> None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None:
        raise DaemonNotFoundError("node lifecycle record not found")
    lifecycle.node_version_id = run.node_version_id
    lifecycle.current_run_id = run.id
    lifecycle.lifecycle_state = state.lifecycle_state
    lifecycle.run_status = run.run_status
    lifecycle.current_task_id = None if state.current_task_id is None else str(state.current_task_id)
    lifecycle.current_subtask_id = None if state.current_compiled_subtask_id is None else str(state.current_compiled_subtask_id)
    lifecycle.current_subtask_attempt = state.current_subtask_attempt
    lifecycle.last_completed_subtask_id = (
        None if state.last_completed_compiled_subtask_id is None else str(state.last_completed_compiled_subtask_id)
    )
    lifecycle.execution_cursor_json = dict(state.execution_cursor_json)
    lifecycle.failure_count_from_children = 0 if state.failure_count_from_children is None else state.failure_count_from_children
    lifecycle.failure_count_consecutive = 0 if state.failure_count_consecutive is None else state.failure_count_consecutive
    lifecycle.defer_to_user_threshold = 0 if state.defer_to_user_threshold is None else state.defer_to_user_threshold
    lifecycle.pause_flag_name = state.pause_flag_name
    lifecycle.is_resumable = state.is_resumable
    lifecycle.working_tree_state = state.working_tree_state
