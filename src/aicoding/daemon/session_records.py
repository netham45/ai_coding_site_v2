from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime, timezone
import hashlib
import time
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session as OrmSession, sessionmaker

from aicoding.daemon.admission import admit_node_run, check_node_dependency_readiness
from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.incremental_parent_merge import process_pending_incremental_parent_merges
from aicoding.daemon.lifecycle import transition_node_lifecycle
from aicoding.daemon.live_git import refresh_child_live_git_from_parent_head
from aicoding.daemon.session_manager import (
    build_primary_session_plan,
    build_recovery_primary_session_plan,
    codex_prompt_instruction,
    current_stage_prompt_cli_command,
)
from aicoding.daemon.session_harness import (
    SessionAdapter,
    SessionPoller,
    send_input_when_ready,
    try_send_input_when_ready,
    wait_for_codex_ready,
)
from aicoding.db.models import (
    CompiledSubtask,
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeLifecycleState,
    NodeRun,
    NodeRunState,
    NodeVersion,
    ParentChildAuthority,
    RebuildEvent,
    Session,
    SessionEvent,
    SubtaskAttempt,
    WorkflowEvent,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.errors import ConfigurationError
from aicoding.hierarchy import HierarchyRegistry
from aicoding.project_policies import resolve_effective_policy
from aicoding.resources import ResourceCatalog
from aicoding.rendering import build_render_context, render_text

ACTIVE_SESSION_STATUSES = {"BOUND", "ATTACHED", "RESUMED", "RUNNING"}
AUTO_RESTARTABLE_LIFECYCLE_STATES = {
    "READY",
    "RUNNING",
    "PAUSED_FOR_USER",
    "WAITING_ON_CHILDREN",
    "WAITING_ON_SIBLING_DEPENDENCY",
    "RECTIFYING_SELF",
    "RECTIFYING_UPSTREAM",
    "REVIEW_PENDING",
    "VALIDATION_PENDING",
    "TESTING_PENDING",
}
RECOVERABLE_SESSION_CLASSIFICATIONS = {
    "healthy",
    "detached",
    "stale_but_recoverable",
    "lost",
    "missing",
    "ambiguous",
    "non_resumable",
}
_ACTIVE_WORK_MARKERS = (
    "• Working (",
    "Working (",
    "Messages to be submitted after next tool call",
)
_RECENT_STAGE_PROMPT_GRACE_SECONDS = 30.0


def _initial_codex_instruction_target(
    *,
    prompt_log_path: str | None,
    prompt_cli_command: str | None,
) -> str | None:
    if isinstance(prompt_log_path, str) and prompt_log_path.strip():
        return prompt_log_path
    if isinstance(prompt_cli_command, str) and prompt_cli_command.strip():
        return prompt_cli_command
    return None


@dataclass(frozen=True, slots=True)
class DurableSessionSnapshot:
    session_id: UUID
    logical_node_id: UUID
    node_version_id: UUID
    node_run_id: UUID | None
    node_kind: str
    node_title: str
    run_status: str | None
    session_role: str
    provider: str
    provider_session_id: str | None
    tmux_session_name: str | None
    cwd: str | None
    status: str
    started_at: str
    last_heartbeat_at: str | None
    ended_at: str | None
    event_count: int
    latest_event_type: str | None
    backend: str
    pane_text: str | None
    idle_seconds: float | None
    in_alt_screen: bool | None
    tmux_session_exists: bool | None
    tmux_process_alive: bool | None
    tmux_exit_status: int | None
    attach_command: str | None
    screen_state: dict[str, object] | None = None
    recovery_classification: str | None = None
    recommended_action: str | None = None
    terminal_failure: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "session_id": str(self.session_id),
            "logical_node_id": str(self.logical_node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "node_kind": self.node_kind,
            "node_title": self.node_title,
            "run_status": self.run_status,
            "session_role": self.session_role,
            "provider": self.provider,
            "provider_session_id": self.provider_session_id,
            "tmux_session_name": self.tmux_session_name,
            "cwd": self.cwd,
            "status": self.status,
            "started_at": self.started_at,
            "last_heartbeat_at": self.last_heartbeat_at,
            "ended_at": self.ended_at,
            "event_count": self.event_count,
            "latest_event_type": self.latest_event_type,
            "backend": self.backend,
            "pane_text": self.pane_text,
            "idle_seconds": self.idle_seconds,
            "in_alt_screen": self.in_alt_screen,
            "tmux_session_exists": self.tmux_session_exists,
            "tmux_process_alive": self.tmux_process_alive,
            "tmux_exit_status": self.tmux_exit_status,
            "attach_command": self.attach_command,
            "screen_state": self.screen_state,
            "recovery_classification": self.recovery_classification,
            "recommended_action": self.recommended_action,
            "terminal_failure": self.terminal_failure,
        }


@dataclass(frozen=True, slots=True)
class SessionCatalogSnapshot:
    node_id: UUID
    sessions: list[DurableSessionSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {"node_id": str(self.node_id), "sessions": [item.to_payload() for item in self.sessions]}


@dataclass(frozen=True, slots=True)
class SessionEventSnapshot:
    id: UUID
    session_id: UUID
    event_type: str
    payload_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "session_id": str(self.session_id),
            "event_type": self.event_type,
            "payload_json": self.payload_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class RecoveryStatusSnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID
    session_id: UUID | None
    recovery_classification: str
    recommended_action: str
    reason: str | None
    is_resumable: bool
    pause_flag_name: str | None
    tmux_session_name: str | None
    tmux_session_exists: bool | None
    tmux_process_alive: bool | None
    tmux_exit_status: int | None
    provider: str | None
    provider_session_id_present: bool
    heartbeat_age_seconds: float | None
    duplicate_active_primary_sessions: int
    terminal_failure: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": str(self.node_run_id),
            "session_id": None if self.session_id is None else str(self.session_id),
            "recovery_classification": self.recovery_classification,
            "recommended_action": self.recommended_action,
            "reason": self.reason,
            "is_resumable": self.is_resumable,
            "pause_flag_name": self.pause_flag_name,
            "tmux_session_name": self.tmux_session_name,
            "tmux_session_exists": self.tmux_session_exists,
            "tmux_process_alive": self.tmux_process_alive,
            "tmux_exit_status": self.tmux_exit_status,
            "provider": self.provider,
            "provider_session_id_present": self.provider_session_id_present,
            "heartbeat_age_seconds": self.heartbeat_age_seconds,
            "duplicate_active_primary_sessions": self.duplicate_active_primary_sessions,
            "terminal_failure": self.terminal_failure,
        }


@dataclass(frozen=True, slots=True)
class RecoveryDecisionSnapshot:
    status: str
    recovery_status: RecoveryStatusSnapshot
    session: DurableSessionSnapshot | None

    def to_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "recovery_status": self.recovery_status.to_payload(),
            "session": None if self.session is None else self.session.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class ProviderRecoveryStatusSnapshot:
    node_id: UUID
    node_version_id: UUID
    node_run_id: UUID
    session_id: UUID | None
    provider: str | None
    provider_session_id: str | None
    provider_supported: bool
    provider_session_exists: bool | None
    tmux_session_name: str | None
    tmux_session_exists: bool | None
    tmux_process_alive: bool | None
    tmux_exit_status: int | None
    provider_rebind_possible: bool
    provider_recommended_action: str
    provider_reason: str | None
    recovery_status: RecoveryStatusSnapshot

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "node_run_id": str(self.node_run_id),
            "session_id": None if self.session_id is None else str(self.session_id),
            "provider": self.provider,
            "provider_session_id": self.provider_session_id,
            "provider_supported": self.provider_supported,
            "provider_session_exists": self.provider_session_exists,
            "tmux_session_name": self.tmux_session_name,
            "tmux_session_exists": self.tmux_session_exists,
            "tmux_process_alive": self.tmux_process_alive,
            "tmux_exit_status": self.tmux_exit_status,
            "provider_rebind_possible": self.provider_rebind_possible,
            "provider_recommended_action": self.provider_recommended_action,
            "provider_reason": self.provider_reason,
            "recovery_status": self.recovery_status.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class ProviderRecoveryDecisionSnapshot:
    status: str
    provider_recovery_status: ProviderRecoveryStatusSnapshot
    recovery_status: RecoveryStatusSnapshot
    session: DurableSessionSnapshot | None

    def to_payload(self) -> dict[str, object]:
        return {
            "status": self.status,
            "provider_recovery_status": self.provider_recovery_status.to_payload(),
            "recovery_status": self.recovery_status.to_payload(),
            "session": None if self.session is None else self.session.to_payload(),
        }


@dataclass(frozen=True, slots=True)
class SessionNudgeSnapshot:
    node_id: UUID
    session_id: UUID | None
    status: str
    action: str
    session_status: str | None
    idle_seconds: float | None
    in_alt_screen: bool | None
    nudge_count: int
    max_nudge_count: int
    prompt_relative_path: str | None
    pause_flag_name: str | None
    screen_state: dict[str, object] | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "session_id": None if self.session_id is None else str(self.session_id),
            "status": self.status,
            "action": self.action,
            "session_status": self.session_status,
            "idle_seconds": self.idle_seconds,
            "in_alt_screen": self.in_alt_screen,
            "nudge_count": self.nudge_count,
            "max_nudge_count": self.max_nudge_count,
            "prompt_relative_path": self.prompt_relative_path,
            "pause_flag_name": self.pause_flag_name,
            "screen_state": self.screen_state,
        }


@dataclass(frozen=True, slots=True)
class SessionScreenStateSnapshot:
    classification: str
    reason: str
    sampled_at: str
    idle_seconds: float
    in_alt_screen: bool
    pane_hash: str
    previous_pane_hash: str | None
    pane_changed: bool
    comparison_window_seconds: float | None

    def to_payload(self) -> dict[str, object]:
        return {
            "classification": self.classification,
            "reason": self.reason,
            "sampled_at": self.sampled_at,
            "idle_seconds": self.idle_seconds,
            "in_alt_screen": self.in_alt_screen,
            "pane_hash": self.pane_hash,
            "previous_pane_hash": self.previous_pane_hash,
            "pane_changed": self.pane_changed,
            "comparison_window_seconds": self.comparison_window_seconds,
        }


@dataclass(frozen=True, slots=True)
class AutoStartedChildSnapshot:
    parent_node_id: UUID
    child_node_id: UUID
    readiness_status: str
    admission_status: str
    session_id: UUID | None
    session_status: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "parent_node_id": str(self.parent_node_id),
            "child_node_id": str(self.child_node_id),
            "readiness_status": self.readiness_status,
            "admission_status": self.admission_status,
            "session_id": None if self.session_id is None else str(self.session_id),
            "session_status": self.session_status,
        }


@dataclass(frozen=True, slots=True)
class AutoAdvancedChildRuntimeSnapshot:
    processed_merge_count: int
    refreshed_child_node_ids: list[UUID]

    def to_payload(self) -> dict[str, object]:
        return {
            "processed_merge_count": self.processed_merge_count,
            "refreshed_child_node_ids": [str(item) for item in self.refreshed_child_node_ids],
        }


@dataclass(frozen=True, slots=True)
class SessionSupervisionSnapshot:
    node_id: UUID
    status: str
    action: str
    lifecycle_state: str | None
    run_status: str | None
    tracked_session_id: UUID | None
    resulting_session_id: UUID | None
    reason: str | None = None

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "status": self.status,
            "action": self.action,
            "lifecycle_state": self.lifecycle_state,
            "run_status": self.run_status,
            "tracked_session_id": None if self.tracked_session_id is None else str(self.tracked_session_id),
            "resulting_session_id": None if self.resulting_session_id is None else str(self.resulting_session_id),
            "reason": self.reason,
        }


def show_current_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot | None:
    with query_session_scope(session_factory) as session:
        current = session.execute(
            select(Session)
            .join(NodeRun, Session.node_run_id == NodeRun.id)
            .join(NodeVersion, Session.node_version_id == NodeVersion.id)
            .join(
                LogicalNodeCurrentVersion,
                LogicalNodeCurrentVersion.logical_node_id == NodeVersion.logical_node_id,
            )
            .where(
                Session.session_role == "primary",
                Session.status.in_(ACTIVE_SESSION_STATUSES),
                NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")),
                LogicalNodeCurrentVersion.authoritative_node_version_id == Session.node_version_id,
            )
            .order_by(Session.started_at.desc())
        ).scalars().first()
        if current is None:
            return None
        return _session_snapshot(session, current, adapter=adapter, poller=poller)


def bind_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _require_active_run(session, version.id)
        state = _require_run_state(session, run.id)
        current = _require_single_active_primary_session(session, run.id)
        if current is not None:
            current_snapshot = _tmux_session_snapshot(adapter, current.tmux_session_name)
            if current_snapshot is not None and current_snapshot.process_alive:
                _record_session_event(
                    session,
                    current.id,
                    "bind_reused",
                    {
                        "node_id": str(logical_node_id),
                        "tmux_session_name": current.tmux_session_name,
                    },
                )
                session.flush()
                return _session_snapshot(session, current, adapter=adapter, poller=poller)
            _invalidate_session(
                session,
                current,
                status="LOST",
                reason="tmux_session_missing" if current_snapshot is None else "tmux_process_exited",
            )
            _cleanup_tmux_session_record(
                session,
                current,
                adapter=adapter,
                cleanup_reason="bind_replacing_lost_primary_session",
            )

        durable_id = uuid4()
        launch_plan = build_primary_session_plan(
            node_version_id=version.id,
            logical_node_id=logical_node_id,
            node_run_id=run.id,
            run_number=run.run_number,
            session_id=durable_id,
            compiled_subtask_id=state.current_compiled_subtask_id,
        )
        adapter_snapshot = adapter.create_session(
            launch_plan.session_name,
            launch_plan.command,
            launch_plan.working_directory,
            environment=launch_plan.environment,
        )
        durable = Session(
            id=durable_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_role="primary",
            provider=adapter.backend_name,
            provider_session_id=adapter_snapshot.session_name,
            tmux_session_name=adapter_snapshot.session_name,
            cwd=adapter_snapshot.working_directory,
            status="BOUND",
            started_at=adapter_snapshot.created_at,
            last_heartbeat_at=adapter_snapshot.last_activity_at,
        )
        session.add(durable)
        session.flush()
        _record_session_event(
            session,
            durable.id,
            "bound",
            {
                "node_id": str(logical_node_id),
                "node_run_id": str(run.id),
                "tmux_session_name": launch_plan.session_name,
                "launch_command": launch_plan.command,
                "launch_mode": launch_plan.launch_mode,
                "cwd": launch_plan.working_directory,
                "attach_command": launch_plan.attach_command,
                "prompt_cli_command": launch_plan.prompt_cli_command,
                "prompt_log_path": launch_plan.prompt_log_path,
                "codex_home_path": launch_plan.codex_home_path,
                "trusted_workspace_paths": list(launch_plan.trusted_workspace_paths),
            },
        )
        session.flush()
        snapshot = _session_snapshot(session, durable, adapter=adapter, poller=poller)
        initial_instruction_target = _initial_codex_instruction_target(
            prompt_log_path=launch_plan.prompt_log_path,
            prompt_cli_command=launch_plan.prompt_cli_command,
        )
    try:
        ready_snapshot = wait_for_codex_ready(adapter, session_name=snapshot.tmux_session_name or "")
    except ConfigurationError as exc:
        session_name = snapshot.tmux_session_name or ""
        if (
            adapter.backend_name == "tmux"
            and getattr(exc, "code", None) == "codex_not_ready"
            and session_name
            and _tmux_session_exists(adapter, session_name) is True
            and _tmux_process_alive(adapter, session_name) is not False
        ):
            with session_scope(session_factory) as session:
                record = session.get(Session, snapshot.session_id)
                if record is not None:
                    _record_session_event(
                        session,
                        record.id,
                        "codex_ready_pending",
                        {
                            "node_id": str(logical_node_id),
                            "tmux_session_name": session_name,
                            "reason": str(exc),
                            "process_command_line": adapter.process_command_line(session_name),
                        },
                    )
                    session.flush()
            return snapshot
        raise
    with session_scope(session_factory) as session:
        record = session.get(Session, snapshot.session_id)
        if record is not None:
            record.last_heartbeat_at = ready_snapshot.last_activity_at
            _record_session_event(
                session,
                record.id,
                "codex_ready",
                {
                    "node_id": str(logical_node_id),
                    "tmux_session_name": ready_snapshot.session_name,
                },
            )
            session.flush()
    _prime_bound_primary_session(
        session_factory,
        logical_node_id=logical_node_id,
        session_id=snapshot.session_id,
        adapter=adapter,
        initial_instruction_target=initial_instruction_target,
    )
    return snapshot


def attach_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _require_active_run(session, version.id)
        current = _require_single_active_primary_session(session, run.id)
        if current is None:
            session.flush()
        else:
            current_snapshot = _tmux_session_snapshot(adapter, current.tmux_session_name)
            if current_snapshot is not None and current_snapshot.process_alive:
                current.status = "ATTACHED"
                current.last_heartbeat_at = datetime.now(timezone.utc)
                _record_session_event(
                    session,
                    current.id,
                    "attached",
                    {
                        "node_id": str(logical_node_id),
                        "reused": True,
                        "tmux_session_name": current.tmux_session_name,
                    },
                )
                session.flush()
                return _session_snapshot(session, current, adapter=adapter, poller=poller)
            _invalidate_session(
                session,
                current,
                status="LOST",
                reason="attach_missing_session" if current_snapshot is None else "attach_found_dead_tmux_process",
            )
            _cleanup_tmux_session_record(
                session,
                current,
                adapter=adapter,
                cleanup_reason="attach_replacing_lost_primary_session",
            )

    snapshot = bind_primary_session(session_factory, logical_node_id=logical_node_id, adapter=adapter, poller=poller)
    with session_scope(session_factory) as session:
        current = session.get(Session, snapshot.session_id)
        if current is None:
            raise DaemonNotFoundError("session not found")
        current.status = "ATTACHED"
        _record_session_event(session, current.id, "attached", {"node_id": str(logical_node_id), "reused": False})
        session.flush()
        return _session_snapshot(session, current, adapter=adapter, poller=poller)


def resume_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    decision = recover_primary_session(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        poller=poller,
    )
    if decision.session is None:
        raise DaemonConflictError("recovery did not produce a primary session")
    return decision.session


def load_recovery_status(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> RecoveryStatusSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            latest_failure = _latest_failed_supervision_context(session, node_version_id=version.id)
            if latest_failure is None:
                raise DaemonConflictError("active durable run not found")
            failed_session = latest_failure["session"]
            return RecoveryStatusSnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=latest_failure["run"].id,
                session_id=None if failed_session is None else failed_session.id,
                recovery_classification="non_resumable",
                recommended_action="inspect_failed_run",
                reason="latest_run_failed_after_supervision_recovery_failure",
                is_resumable=False,
                pause_flag_name=latest_failure["state"].pause_flag_name,
                tmux_session_name=None if failed_session is None else failed_session.tmux_session_name,
                tmux_session_exists=None if failed_session is None else _tmux_session_exists(adapter, failed_session.tmux_session_name),
                tmux_process_alive=None if failed_session is None else _tmux_process_alive(adapter, failed_session.tmux_session_name),
                tmux_exit_status=None if failed_session is None else _tmux_exit_status(adapter, failed_session.tmux_session_name),
                provider=None if failed_session is None else failed_session.provider,
                provider_session_id_present=False if failed_session is None else failed_session.provider_session_id is not None,
                heartbeat_age_seconds=_heartbeat_age_seconds(failed_session),
                duplicate_active_primary_sessions=0,
                terminal_failure=latest_failure["terminal_failure"],
            )
        state = _require_run_state(session, run.id)
        active_sessions = _active_primary_sessions(session, run.id)
        return _recovery_status_snapshot(
            session,
            logical_node_id=logical_node_id,
            version=version,
            run=run,
            state=state,
            active_sessions=active_sessions,
            adapter=adapter,
            poller=poller,
        )


def recover_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> RecoveryDecisionSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            latest_failure = _latest_failed_supervision_context(session, node_version_id=version.id)
            if latest_failure is None:
                raise DaemonConflictError("active durable run not found")
            failed_session = latest_failure["session"]
            recovery_status = RecoveryStatusSnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=latest_failure["run"].id,
                session_id=None if failed_session is None else failed_session.id,
                recovery_classification="non_resumable",
                recommended_action="inspect_failed_run",
                reason="latest_run_failed_after_supervision_recovery_failure",
                is_resumable=False,
                pause_flag_name=latest_failure["state"].pause_flag_name,
                tmux_session_name=None if failed_session is None else failed_session.tmux_session_name,
                tmux_session_exists=None if failed_session is None else _tmux_session_exists(adapter, failed_session.tmux_session_name),
                tmux_process_alive=None if failed_session is None else _tmux_process_alive(adapter, failed_session.tmux_session_name),
                tmux_exit_status=None if failed_session is None else _tmux_exit_status(adapter, failed_session.tmux_session_name),
                provider=None if failed_session is None else failed_session.provider,
                provider_session_id_present=False if failed_session is None else failed_session.provider_session_id is not None,
                heartbeat_age_seconds=_heartbeat_age_seconds(failed_session),
                duplicate_active_primary_sessions=0,
                terminal_failure=latest_failure["terminal_failure"],
            )
            snapshot = None
            if failed_session is not None:
                snapshot = _session_snapshot(
                    session,
                    failed_session,
                    adapter=adapter,
                    poller=poller,
                    recovery_classification="non_resumable",
                    recommended_action="inspect_failed_run",
                    terminal_failure=latest_failure["terminal_failure"],
                )
            return RecoveryDecisionSnapshot(status="recovery_rejected", recovery_status=recovery_status, session=snapshot)
        state = _require_run_state(session, run.id)
        active_sessions = _active_primary_sessions(session, run.id)
        status = _recovery_status_snapshot(
            session,
            logical_node_id=logical_node_id,
            version=version,
            run=run,
            state=state,
            active_sessions=active_sessions,
            adapter=adapter,
            poller=poller,
        )
        current = active_sessions[0] if active_sessions else None
        if current is not None:
            _record_session_event(
                session,
                current.id,
                "recovery_attempted",
                {
                    "node_id": str(logical_node_id),
                    "classification": status.recovery_classification,
                    "recommended_action": status.recommended_action,
                },
            )

        if status.recovery_classification == "non_resumable":
            if current is not None:
                _record_session_event(
                    session,
                    current.id,
                    "recovery_rejected",
                    {"node_id": str(logical_node_id), "reason": "non_resumable_run"},
                )
            session.flush()
            return RecoveryDecisionSnapshot(status="recovery_rejected", recovery_status=status, session=None)

        if status.recovery_classification == "ambiguous":
            if current is not None:
                _record_session_event(
                    session,
                    current.id,
                    "recovery_paused",
                    {"node_id": str(logical_node_id), "reason": "duplicate_primary_session"},
                )
            session.flush()
            from aicoding.daemon.run_orchestration import sync_paused_run

            sync_paused_run(session_factory, logical_node_id=logical_node_id, pause_flag_name="duplicate_primary_session")
            return RecoveryDecisionSnapshot(status="paused_for_user", recovery_status=status, session=None)

        if status.recovery_classification in {"healthy", "detached", "stale_but_recoverable"}:
            if current is None:
                raise DaemonNotFoundError("primary session not found")
            if current.tmux_session_name is None:
                raise DaemonConflictError("recoverable session is missing tmux identity")
            poll_result = poller.poll(current.tmux_session_name)
            current.status = "RESUMED"
            current.last_heartbeat_at = poll_result.snapshot.last_activity_at
            _record_session_event(
                session,
                current.id,
                "recovery_resumed_existing",
                {
                    "node_id": str(logical_node_id),
                    "classification": status.recovery_classification,
                    "idle_seconds": poll_result.idle_seconds,
                },
            )
            session.flush()
            from aicoding.daemon.run_orchestration import sync_resumed_run

            sync_resumed_run(session_factory, logical_node_id=logical_node_id, force=True)
            snapshot = _session_snapshot(
                session,
                current,
                adapter=adapter,
                poller=poller,
                recovery_classification=status.recovery_classification,
            )
            return RecoveryDecisionSnapshot(status="reused_existing_session", recovery_status=status, session=snapshot)

        for record in active_sessions:
            _invalidate_session(session, record, status="LOST", reason="provider_agnostic_recovery_replacement")
            _cleanup_tmux_session_record(
                session,
                record,
                adapter=adapter,
                cleanup_reason="provider_agnostic_recovery_replacement",
            )
        durable_id = uuid4()
        launch_plan = build_recovery_primary_session_plan(
            node_version_id=version.id,
            node_run_id=run.id,
            run_number=run.run_number,
            session_id=durable_id,
        )
        adapter_snapshot = adapter.create_session(
            launch_plan.session_name,
            launch_plan.command,
            launch_plan.working_directory,
            environment=launch_plan.environment,
        )
        durable = Session(
            id=durable_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_role="primary",
            provider=adapter.backend_name,
            provider_session_id=adapter_snapshot.session_name,
            tmux_session_name=adapter_snapshot.session_name,
            cwd=adapter_snapshot.working_directory,
            status="RESUMED",
            started_at=adapter_snapshot.created_at,
            last_heartbeat_at=adapter_snapshot.last_activity_at,
        )
        session.add(durable)
        session.flush()
        _record_session_event(
            session,
            durable.id,
            "recovery_replacement_created",
            {
                "node_id": str(logical_node_id),
                "classification": status.recovery_classification,
                "provider_session_id_present": status.provider_session_id_present,
                "tmux_session_name": launch_plan.session_name,
                "launch_command": launch_plan.command,
                "launch_mode": launch_plan.launch_mode,
                "cwd": launch_plan.working_directory,
                "attach_command": launch_plan.attach_command,
                "prompt_cli_command": launch_plan.prompt_cli_command,
                "prompt_log_path": launch_plan.prompt_log_path,
                "codex_home_path": launch_plan.codex_home_path,
                "trusted_workspace_paths": list(launch_plan.trusted_workspace_paths),
            },
        )
        session.flush()
        from aicoding.daemon.run_orchestration import sync_resumed_run

        sync_resumed_run(session_factory, logical_node_id=logical_node_id, force=True)
        snapshot = _session_snapshot(
            session,
            durable,
            adapter=adapter,
            poller=poller,
            recovery_classification=status.recovery_classification,
        )
        return RecoveryDecisionSnapshot(status="replacement_session_created", recovery_status=status, session=snapshot)


def load_provider_recovery_status(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> ProviderRecoveryStatusSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            latest_failure = _latest_failed_supervision_context(session, node_version_id=version.id)
            if latest_failure is None:
                raise DaemonConflictError("active durable run not found")
            failed_session = latest_failure["session"]
            recovery_status = RecoveryStatusSnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=latest_failure["run"].id,
                session_id=None if failed_session is None else failed_session.id,
                recovery_classification="non_resumable",
                recommended_action="inspect_failed_run",
                reason="latest_run_failed_after_supervision_recovery_failure",
                is_resumable=False,
                pause_flag_name=latest_failure["state"].pause_flag_name,
                tmux_session_name=None if failed_session is None else failed_session.tmux_session_name,
                tmux_session_exists=None if failed_session is None else _tmux_session_exists(adapter, failed_session.tmux_session_name),
                tmux_process_alive=None if failed_session is None else _tmux_process_alive(adapter, failed_session.tmux_session_name),
                tmux_exit_status=None if failed_session is None else _tmux_exit_status(adapter, failed_session.tmux_session_name),
                provider=None if failed_session is None else failed_session.provider,
                provider_session_id_present=False if failed_session is None else failed_session.provider_session_id is not None,
                heartbeat_age_seconds=_heartbeat_age_seconds(failed_session),
                duplicate_active_primary_sessions=0,
                terminal_failure=latest_failure["terminal_failure"],
            )
            return ProviderRecoveryStatusSnapshot(
                node_id=logical_node_id,
                node_version_id=version.id,
                node_run_id=latest_failure["run"].id,
                session_id=None if failed_session is None else failed_session.id,
                provider=None if failed_session is None else failed_session.provider,
                provider_session_id=None if failed_session is None else failed_session.provider_session_id,
                provider_supported=failed_session is not None,
                provider_session_exists=None if failed_session is None or failed_session.provider_session_id is None else adapter.session_exists(failed_session.provider_session_id),
                tmux_session_name=None if failed_session is None else failed_session.tmux_session_name,
                tmux_session_exists=None if failed_session is None else _tmux_session_exists(adapter, failed_session.tmux_session_name),
                tmux_process_alive=None if failed_session is None else _tmux_process_alive(adapter, failed_session.tmux_session_name),
                tmux_exit_status=None if failed_session is None else _tmux_exit_status(adapter, failed_session.tmux_session_name),
                provider_rebind_possible=False,
                provider_recommended_action="inspect_failed_run",
                provider_reason="latest_run_failed_after_supervision_recovery_failure",
                recovery_status=recovery_status,
            )
        state = _require_run_state(session, run.id)
        active_sessions = _active_primary_sessions(session, run.id)
        recovery_status = _recovery_status_snapshot(
            session,
            logical_node_id=logical_node_id,
            version=version,
            run=run,
            state=state,
            active_sessions=active_sessions,
            adapter=adapter,
            poller=poller,
        )
        current = active_sessions[0] if active_sessions else None
        return _provider_recovery_status_snapshot(
            current=current,
            recovery_status=recovery_status,
            adapter=adapter,
        )


def recover_primary_session_provider_specific(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> ProviderRecoveryDecisionSnapshot:
    provider_status = load_provider_recovery_status(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        poller=poller,
    )
    if provider_status.provider_rebind_possible and provider_status.session_id is not None and provider_status.provider_session_id is not None:
        with session_scope(session_factory) as session:
            current = session.get(Session, provider_status.session_id)
            if current is None:
                raise DaemonNotFoundError("primary session not found")
            _record_session_event(
                session,
                current.id,
                "provider_recovery_attempted",
                {
                    "node_id": str(logical_node_id),
                    "provider": current.provider,
                    "provider_session_id": provider_status.provider_session_id,
                    "provider_action": provider_status.provider_recommended_action,
                },
            )
            poll_result = poller.poll(provider_status.provider_session_id)
            current.tmux_session_name = provider_status.provider_session_id
            current.status = "RESUMED"
            current.last_heartbeat_at = poll_result.snapshot.last_activity_at
            _record_session_event(
                session,
                current.id,
                "provider_recovery_rebound",
                {
                    "node_id": str(logical_node_id),
                    "provider": current.provider,
                    "provider_session_id": provider_status.provider_session_id,
                    "idle_seconds": poll_result.idle_seconds,
                },
            )
            session.flush()
            from aicoding.daemon.run_orchestration import sync_resumed_run

            sync_resumed_run(session_factory, logical_node_id=logical_node_id, force=True)
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
            state = _require_run_state(session, run.id)
            recovery_status = _recovery_status_snapshot(
                session,
                logical_node_id=logical_node_id,
                version=version,
                run=run,
                state=state,
                active_sessions=[current],
                adapter=adapter,
                poller=poller,
            )
            rebound_provider_status = _provider_recovery_status_snapshot(
                current=current,
                recovery_status=recovery_status,
                adapter=adapter,
            )
            snapshot = _session_snapshot(
                session,
                current,
                adapter=adapter,
                poller=poller,
                recovery_classification=recovery_status.recovery_classification,
            )
            return ProviderRecoveryDecisionSnapshot(
                status="provider_session_rebound",
                provider_recovery_status=rebound_provider_status,
                recovery_status=recovery_status,
                session=snapshot,
            )

    decision = recover_primary_session(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        poller=poller,
    )
    provider_status = load_provider_recovery_status(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        poller=poller,
    )
    return ProviderRecoveryDecisionSnapshot(
        status=decision.status,
        provider_recovery_status=provider_status,
        recovery_status=decision.recovery_status,
        session=decision.session,
    )


def nudge_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
    max_nudge_count: int,
    idle_nudge_text: str,
    repeated_nudge_text: str,
) -> SessionNudgeSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _require_active_run(session, version.id)
        state = _require_run_state(session, run.id)
        current = _active_primary_session(session, run.id)
        if current is None:
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=None,
                status="missing_session",
                action="none",
                session_status=None,
                idle_seconds=None,
                in_alt_screen=None,
                nudge_count=0,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=None,
            )
        if run.run_status == "PAUSED":
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "run_paused",
                    "pause_flag_name": state.pause_flag_name,
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="run_paused",
                action="none",
                session_status=current.status,
                idle_seconds=None,
                in_alt_screen=None,
                nudge_count=_nudge_event_count(session, current.id),
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=None,
            )
        current_tmux_exists = _tmux_session_exists(adapter, current.tmux_session_name)
        current_process_alive = _tmux_process_alive(adapter, current.tmux_session_name)
        if current.tmux_session_name is None or current_tmux_exists is not True or current_process_alive is False:
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {"reason": "session_missing" if current_process_alive is not False else "session_process_exited"},
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="session_missing" if current_process_alive is not False else "session_not_running",
                action="none",
                session_status=current.status,
                idle_seconds=None,
                in_alt_screen=None,
                nudge_count=_nudge_event_count(session, current.id),
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=None,
            )
        screen_state = _classify_session_screen_state(session, current, adapter=adapter, poller=poller, persist=True)
        poll_result = poller.poll(current.tmux_session_name)
        latest_event_type = _latest_session_event_type(session, current.id)
        nudge_count = _nudge_event_count(session, current.id)
        if _current_subtask_has_registered_summary(session, run.id, state.current_compiled_subtask_id):
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "summary_already_registered",
                    "idle_seconds": poll_result.idle_seconds,
                    "screen_classification": screen_state.classification,
                    "screen_reason": screen_state.reason,
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="summary_registered",
                action="none",
                session_status=current.status,
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=_nudge_event_count(session, current.id),
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=screen_state.to_payload(),
            )
        current_subtask = _current_subtask_for_recovery(session, state.current_compiled_subtask_id)
        latest_codex_ready = _latest_session_event(
            session,
            current.id,
            event_types=("codex_ready",),
        )
        if latest_codex_ready is None:
            if _pane_shows_codex_ready_banner(adapter, current.tmux_session_name):
                current.last_heartbeat_at = datetime.now(timezone.utc)
                _record_session_event(
                    session,
                    current.id,
                    "codex_ready",
                    {
                        "node_id": str(logical_node_id),
                        "tmux_session_name": current.tmux_session_name,
                        "recovered_by": "idle_nudge",
                    },
                )
                session.flush()
                latest_codex_ready = _latest_session_event(
                    session,
                    current.id,
                    event_types=("codex_ready",),
                )
            else:
                _record_session_event(
                    session,
                    current.id,
                    "nudge_skipped",
                    {
                        "reason": "awaiting_codex_ready",
                        "idle_seconds": poll_result.idle_seconds,
                        "screen_classification": screen_state.classification,
                        "screen_reason": screen_state.reason,
                    },
                )
                session.flush()
                return SessionNudgeSnapshot(
                    node_id=logical_node_id,
                    session_id=current.id,
                    status="awaiting_codex_ready",
                    action="none",
                    session_status=current.status,
                    idle_seconds=poll_result.idle_seconds,
                    in_alt_screen=poll_result.snapshot.in_alt_screen,
                    nudge_count=nudge_count,
                    max_nudge_count=max_nudge_count,
                    prompt_relative_path=None,
                    pause_flag_name=state.pause_flag_name,
                    screen_state=screen_state.to_payload(),
                )
        if (
            screen_state.classification == "active"
            and screen_state.reason == "pane_changed"
            and poll_result.is_idle
            and latest_event_type == "nudged"
        ):
            screen_state = replace(
                screen_state,
                classification="idle",
                reason="daemon_nudge_only_change",
            )
        if screen_state.classification != "idle":
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "not_idle",
                    "idle_seconds": poll_result.idle_seconds,
                    "screen_classification": screen_state.classification,
                    "screen_reason": screen_state.reason,
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="not_idle",
                action="none",
                session_status=current.status,
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=nudge_count,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=screen_state.to_payload(),
            )
        missing_stage_prompt_seed = _seed_missing_stage_prompt_after_codex_ready(
            session_factory,
            logical_node_id=logical_node_id,
            adapter=adapter,
        )
        if missing_stage_prompt_seed != "skipped":
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "seeded_missing_stage_prompt",
                    "idle_seconds": poll_result.idle_seconds,
                    "seed_result": missing_stage_prompt_seed,
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="pending_stage_prompt" if missing_stage_prompt_seed == "queued" else "stage_prompt_seeded",
                action="none",
                session_status=current.status,
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=nudge_count,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=screen_state.to_payload(),
            )
        pending_stage_prompt = _latest_pending_stage_prompt_event(session, current.id)
        if pending_stage_prompt is not None:
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "pending_stage_prompt",
                    "idle_seconds": poll_result.idle_seconds,
                    "queued_event_id": str(pending_stage_prompt.id),
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="pending_stage_prompt",
                action="none",
                session_status=current.status,
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=nudge_count,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=screen_state.to_payload(),
            )
        recent_stage_event = _latest_session_event(
            session,
            current.id,
            event_types=("stage_prompt_pushed", "codex_ready"),
        )
        if (
            recent_stage_event is not None
            and poll_result.idle_seconds is not None
            and poll_result.idle_seconds < _RECENT_STAGE_PROMPT_GRACE_SECONDS
        ):
            _record_session_event(
                session,
                current.id,
                "nudge_skipped",
                {
                    "reason": "recent_stage_prompt_grace",
                    "idle_seconds": poll_result.idle_seconds,
                    "recent_event_type": recent_stage_event.event_type,
                    "recent_event_id": str(recent_stage_event.id),
                },
            )
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="recent_stage_prompt_grace",
                action="none",
                session_status=current.status,
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=nudge_count,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name=state.pause_flag_name,
                screen_state=screen_state.to_payload(),
            )
        if current_subtask is not None and current_subtask.subtask_type == "wait_for_children":
            active_children = _wait_stage_active_children(session, logical_node_id=logical_node_id)
            if active_children:
                _record_session_event(
                    session,
                    current.id,
                    "nudge_skipped",
                    {
                        "reason": "waiting_on_children",
                        "idle_seconds": poll_result.idle_seconds,
                        "active_children": active_children,
                    },
                )
                session.flush()
                return SessionNudgeSnapshot(
                    node_id=logical_node_id,
                    session_id=current.id,
                    status="waiting_on_children",
                    action="none",
                    session_status=current.status,
                    idle_seconds=poll_result.idle_seconds,
                    in_alt_screen=poll_result.snapshot.in_alt_screen,
                    nudge_count=nudge_count,
                    max_nudge_count=max_nudge_count,
                    prompt_relative_path=None,
                    pause_flag_name=state.pause_flag_name,
                    screen_state=screen_state.to_payload(),
                )
        if nudge_count >= max_nudge_count:
            current.status = "RUNNING"
            _record_session_event(
                session,
                current.id,
                "nudge_escalated",
                {"reason": "nudge_limit_exceeded", "idle_seconds": poll_result.idle_seconds, "nudge_count": nudge_count},
            )
            session.flush()
            from aicoding.daemon.run_orchestration import sync_paused_run

            sync_paused_run(session_factory, logical_node_id=logical_node_id, pause_flag_name="idle_nudge_limit_exceeded")
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="escalated_to_pause",
                action="pause_for_user",
                session_status="RUNNING",
                idle_seconds=poll_result.idle_seconds,
                in_alt_screen=poll_result.snapshot.in_alt_screen,
                nudge_count=nudge_count,
                max_nudge_count=max_nudge_count,
                prompt_relative_path=None,
                pause_flag_name="idle_nudge_limit_exceeded",
                screen_state=screen_state.to_payload(),
            )
        prompt_relative_path = "recovery/idle_nudge.md"
        prompt_text = _render_recovery_prompt(
            idle_nudge_text,
            session=session,
            logical_node_id=logical_node_id,
            current_subtask=current_subtask,
        )
        if nudge_count + 1 >= max_nudge_count:
            prompt_relative_path = "recovery/repeated_missed_step.md"
            prompt_text = _render_recovery_prompt(
                repeated_nudge_text,
                session=session,
                logical_node_id=logical_node_id,
                current_subtask=current_subtask,
            )
        send_input_when_ready(adapter, session_name=current.tmux_session_name, text=prompt_text, press_enter=True)
        current.last_heartbeat_at = datetime.now(timezone.utc)
        _record_session_event(
            session,
            current.id,
            "nudged",
            {
                "idle_seconds": poll_result.idle_seconds,
                "nudge_count": nudge_count + 1,
                "prompt_relative_path": prompt_relative_path,
                "screen_classification": screen_state.classification,
                "screen_reason": screen_state.reason,
            },
        )
        session.flush()
    return SessionNudgeSnapshot(
        node_id=logical_node_id,
        session_id=current.id,
        status="nudged",
            action="sent_prompt",
            session_status=current.status,
            idle_seconds=poll_result.idle_seconds,
            in_alt_screen=poll_result.snapshot.in_alt_screen,
            nudge_count=nudge_count + 1,
            max_nudge_count=max_nudge_count,
            prompt_relative_path=prompt_relative_path,
            pause_flag_name=state.pause_flag_name,
        screen_state=screen_state.to_payload(),
    )


def _pane_shows_codex_ready_banner(adapter: SessionAdapter, session_name: str | None) -> bool:
    if not isinstance(session_name, str) or not session_name.strip():
        return False
    if _tmux_session_exists(adapter, session_name) is not True:
        return False
    if _tmux_process_alive(adapter, session_name) is False:
        return False
    try:
        pane_text = adapter.capture_pane(session_name, include_alt_screen=True)
    except Exception:
        return False
    return "OpenAI Codex" in pane_text and ">_" in pane_text


def auto_nudge_idle_primary_sessions(
    session_factory: sessionmaker[OrmSession],
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
    max_nudge_count: int,
    idle_nudge_text: str,
    repeated_nudge_text: str,
) -> list[SessionNudgeSnapshot]:
    with query_session_scope(session_factory) as session:
        logical_node_ids = [
            row[0]
            for row in session.execute(
                select(NodeVersion.logical_node_id)
                .join(Session, Session.node_version_id == NodeVersion.id)
                .join(NodeRun, Session.node_run_id == NodeRun.id)
                .where(
                    Session.session_role == "primary",
                    Session.status.in_(tuple(ACTIVE_SESSION_STATUSES)),
                    NodeRun.run_status.in_(("PENDING", "RUNNING")),
                )
                .distinct()
            ).all()
        ]

    snapshots: list[SessionNudgeSnapshot] = []
    for logical_node_id in logical_node_ids:
        try:
            screen_state = inspect_primary_session_screen_state(
                session_factory,
                logical_node_id=logical_node_id,
                adapter=adapter,
                poller=poller,
                persist=True,
            )
        except (ConfigurationError, DaemonConflictError, DaemonNotFoundError) as exc:
            _record_auto_nudge_failure(
                session_factory,
                logical_node_id=logical_node_id,
                phase="inspect_primary_session_screen_state",
                exc=exc,
            )
            continue
        if screen_state.classification != "idle" or screen_state.reason != "unchanged_screen_past_idle_threshold":
            continue
        try:
            session_snapshot = get_session_for_node(
                session_factory,
                logical_node_id=logical_node_id,
                adapter=adapter,
                poller=poller,
            )
        except Exception as exc:
            _record_auto_nudge_failure(session_factory, logical_node_id=logical_node_id, phase="load_current_primary_session", exc=exc)
            continue
        if session_snapshot is None:
            continue
        reference = session_snapshot.last_heartbeat_at or session_snapshot.started_at
        try:
            reference_dt = _parse_iso8601(reference)
        except Exception:
            reference_dt = datetime.now(timezone.utc)
        bootstrap_age_seconds = max((datetime.now(timezone.utc) - reference_dt).total_seconds(), 0.0)
        bootstrap_grace_seconds = max(poller.idle_threshold_seconds * 2.0, 5.0)
        if bootstrap_age_seconds < bootstrap_grace_seconds:
            continue
        try:
            snapshot = nudge_primary_session(
                session_factory,
                logical_node_id=logical_node_id,
                adapter=adapter,
                poller=poller,
                max_nudge_count=max_nudge_count,
                idle_nudge_text=idle_nudge_text,
                repeated_nudge_text=repeated_nudge_text,
            )
        except (DaemonConflictError, DaemonNotFoundError):
            continue
        except Exception as exc:
            _record_auto_nudge_failure(session_factory, logical_node_id=logical_node_id, phase="nudge_primary_session", exc=exc)
            continue
        if snapshot.status in {"nudged", "escalated_to_pause"}:
            snapshots.append(snapshot)
    return snapshots


def auto_supervise_primary_sessions(
    session_factory: sessionmaker[OrmSession],
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> list[SessionSupervisionSnapshot]:
    with query_session_scope(session_factory) as session:
        logical_node_ids = [
            row[0]
            for row in session.execute(
                select(NodeVersion.logical_node_id)
                .join(NodeRun, NodeRun.node_version_id == NodeVersion.id)
                .join(Session, Session.node_run_id == NodeRun.id)
                .where(
                    Session.session_role == "primary",
                    NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")),
                )
                .distinct()
            ).all()
        ]

    snapshots: list[SessionSupervisionSnapshot] = []
    for logical_node_id in logical_node_ids:
        target = _load_session_supervision_target(session_factory, logical_node_id=logical_node_id, adapter=adapter)
        if target is None or target.tracked_session_id is None:
            continue
        codex_process_missing = (
            target.codex_ready_seen
            and target.tmux_session_exists
            and target.tmux_process_alive is not False
            and "codex" not in (target.tmux_process_command_line or "").lower()
        )
        if target.tmux_session_exists and target.tmux_process_alive is not False and not codex_process_missing:
            continue
        missing_reason = "tracked_tmux_session_missing"
        invalidation_reason = "supervision_detected_missing_tmux_session"
        if codex_process_missing:
            missing_reason = "tracked_codex_process_missing"
            invalidation_reason = "supervision_detected_non_codex_process"
        elif target.tmux_session_exists and target.tmux_process_alive is False:
            missing_reason = "tracked_tmux_process_exited"
            invalidation_reason = "supervision_detected_dead_tmux_process"
        if target.lifecycle_state not in AUTO_RESTARTABLE_LIFECYCLE_STATES:
            _record_supervision_failure_event(
                session_factory,
                logical_node_id=logical_node_id,
                session_id=target.tracked_session_id,
                reason="restart_not_allowed_for_lifecycle_state",
                details={
                    "lifecycle_state": target.lifecycle_state,
                    "run_status": target.run_status,
                    "tmux_session_exists": target.tmux_session_exists,
                    "tmux_process_alive": target.tmux_process_alive,
                    "tmux_exit_status": target.tmux_exit_status,
                    "tmux_process_command_line": target.tmux_process_command_line,
                },
                invalidate_active_session=True,
            )
            from aicoding.daemon.run_orchestration import sync_failed_run

            sync_failed_run(
                session_factory,
                logical_node_id=logical_node_id,
                failure_summary=(
                    f"Session supervision failed because the tracked tmux session was lost while the node "
                    f"lifecycle state '{target.lifecycle_state}' was not restartable."
                ),
                failure_reason="restart_not_allowed_for_lifecycle_state",
                adapter=adapter,
            )
            snapshots.append(
                SessionSupervisionSnapshot(
                    node_id=logical_node_id,
                    status="failed",
                    action="mark_run_failed",
                    lifecycle_state=target.lifecycle_state,
                    run_status="FAILED",
                    tracked_session_id=target.tracked_session_id,
                    resulting_session_id=None,
                    reason="restart_not_allowed_for_lifecycle_state",
                )
            )
            continue
        _record_supervision_event(
            session_factory,
            session_id=target.tracked_session_id,
            event_type="supervision_recovery_attempted",
            payload={
                "lifecycle_state": target.lifecycle_state,
                "run_status": target.run_status,
                "reason": missing_reason,
                "tmux_session_exists": target.tmux_session_exists,
                "tmux_process_alive": target.tmux_process_alive,
                "tmux_exit_status": target.tmux_exit_status,
                "tmux_process_command_line": target.tmux_process_command_line,
            },
            invalidate_active_session=True,
            invalidation_reason=invalidation_reason,
        )
        try:
            decision = recover_primary_session(
                session_factory,
                logical_node_id=logical_node_id,
                adapter=adapter,
                poller=poller,
            )
        except Exception as exc:
            _record_supervision_failure_event(
                session_factory,
                logical_node_id=logical_node_id,
                session_id=target.tracked_session_id,
                reason="restart_launch_failed",
                details={
                    "error_type": type(exc).__name__,
                    "message": str(exc),
                    "lifecycle_state": target.lifecycle_state,
                    "run_status": target.run_status,
                    "tmux_session_exists": target.tmux_session_exists,
                    "tmux_process_alive": target.tmux_process_alive,
                    "tmux_exit_status": target.tmux_exit_status,
                    "tmux_process_command_line": target.tmux_process_command_line,
                },
                invalidate_active_session=False,
            )
            from aicoding.daemon.run_orchestration import sync_failed_run

            sync_failed_run(
                session_factory,
                logical_node_id=logical_node_id,
                failure_summary=f"Session supervision failed because replacement launch raised {type(exc).__name__}: {exc}",
                failure_reason="restart_launch_failed",
                adapter=adapter,
            )
            snapshots.append(
                SessionSupervisionSnapshot(
                    node_id=logical_node_id,
                    status="failed",
                    action="mark_run_failed",
                    lifecycle_state=target.lifecycle_state,
                    run_status="FAILED",
                    tracked_session_id=target.tracked_session_id,
                    resulting_session_id=None,
                    reason="restart_launch_failed",
                )
            )
            continue
        if decision.session is None:
            _record_supervision_failure_event(
                session_factory,
                logical_node_id=logical_node_id,
                session_id=target.tracked_session_id,
                reason=decision.status,
                details={
                    "recovery_status": decision.recovery_status.to_payload(),
                },
                invalidate_active_session=False,
            )
            from aicoding.daemon.run_orchestration import sync_failed_run

            sync_failed_run(
                session_factory,
                logical_node_id=logical_node_id,
                failure_summary=(
                    "Session supervision failed because automatic recovery did not produce a replacement "
                    f"or reusable session (status={decision.status})."
                ),
                failure_reason=decision.status,
                adapter=adapter,
            )
            snapshots.append(
                SessionSupervisionSnapshot(
                    node_id=logical_node_id,
                    status="failed",
                    action="mark_run_failed",
                    lifecycle_state=target.lifecycle_state,
                    run_status="FAILED",
                    tracked_session_id=target.tracked_session_id,
                    resulting_session_id=None,
                    reason=decision.status,
                )
            )
            continue
        _record_supervision_event(
            session_factory,
            session_id=decision.session.session_id,
            event_type="supervision_recovery_succeeded",
            payload={
                "decision_status": decision.status,
                "recovery_classification": decision.recovery_status.recovery_classification,
                "tmux_session_name": decision.session.tmux_session_name,
            },
        )
        snapshots.append(
            SessionSupervisionSnapshot(
                node_id=logical_node_id,
                status="recovered",
                action="replacement_created" if decision.status == "replacement_session_created" else "session_reused",
                lifecycle_state=target.lifecycle_state,
                run_status=decision.session.run_status,
                tracked_session_id=target.tracked_session_id,
                resulting_session_id=decision.session.session_id,
                reason=decision.status,
            )
        )
    return snapshots


def auto_bind_ready_child_runs(
    session_factory: sessionmaker[OrmSession],
    *,
    hierarchy_registry: HierarchyRegistry,
    resources: ResourceCatalog,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> list[AutoStartedChildSnapshot]:
    candidate_pairs = _list_auto_run_child_candidate_pairs(
        session_factory,
        hierarchy_registry=hierarchy_registry,
        resources=resources,
    )

    snapshots: list[AutoStartedChildSnapshot] = []
    for parent_node_id, child_node_id in candidate_pairs:
        readiness = check_node_dependency_readiness(session_factory, node_id=child_node_id)
        if readiness.status != "ready":
            snapshots.append(
                AutoStartedChildSnapshot(
                    parent_node_id=parent_node_id,
                    child_node_id=child_node_id,
                    readiness_status=readiness.status,
                    admission_status="skipped",
                    session_id=None,
                    session_status=None,
                )
            )
            continue
        admission = admit_node_run(session_factory, node_id=child_node_id, trigger_reason="auto_run_child")
        if admission.status != "admitted":
            snapshots.append(
                AutoStartedChildSnapshot(
                    parent_node_id=parent_node_id,
                    child_node_id=child_node_id,
                    readiness_status=readiness.status,
                    admission_status=admission.status,
                    session_id=None,
                    session_status=None,
                )
            )
            continue
        session_snapshot = bind_primary_session(
            session_factory,
            logical_node_id=child_node_id,
            adapter=adapter,
            poller=poller,
        )
        with session_scope(session_factory) as session:
            _record_session_event(
                session,
                session_snapshot.session_id,
                "auto_child_bound",
                {
                    "parent_node_id": str(parent_node_id),
                    "child_node_id": str(child_node_id),
                    "trigger_reason": "auto_run_child",
                },
            )
            session.flush()
        snapshots.append(
            AutoStartedChildSnapshot(
                parent_node_id=parent_node_id,
                child_node_id=child_node_id,
                readiness_status=readiness.status,
                admission_status=admission.status,
                session_id=session_snapshot.session_id,
                session_status=session_snapshot.status,
            )
        )
    return snapshots


def _prime_bound_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    session_id: UUID,
    adapter: SessionAdapter,
    initial_instruction_target: str | None,
) -> None:
    from aicoding.daemon.run_orchestration import (
        load_current_run_progress,
        load_current_subtask_prompt,
        start_subtask_attempt,
    )

    progress = load_current_run_progress(session_factory, logical_node_id=logical_node_id)
    compiled_subtask_id = progress.state.current_compiled_subtask_id
    if compiled_subtask_id is None:
        return
    start_subtask_attempt(
        session_factory,
        logical_node_id=logical_node_id,
        compiled_subtask_id=compiled_subtask_id,
        adapter=adapter,
    )
    prompt_snapshot = load_current_subtask_prompt(session_factory, logical_node_id=logical_node_id)
    prompt_text = prompt_snapshot.prompt_text or prompt_snapshot.command_text
    instruction_text = None
    if (
        isinstance(initial_instruction_target, str)
        and initial_instruction_target.strip()
        and _should_use_stage_specific_prompt_message(prompt_snapshot)
    ):
        instruction_text = _initial_stage_prompt_instruction(
            logical_node_id=logical_node_id,
            prompt_snapshot=prompt_snapshot,
            prompt_target=initial_instruction_target,
        )
    elif isinstance(initial_instruction_target, str) and initial_instruction_target.strip():
        instruction_text = codex_prompt_instruction(
            prompt_target=initial_instruction_target,
            prompt_source="file",
        )
    elif isinstance(prompt_text, str) and prompt_text.strip():
        instruction_text = prompt_text
    if not isinstance(instruction_text, str) or not instruction_text.strip():
        return
    with session_scope(session_factory) as session:
        record = session.get(Session, session_id)
        if record is None or not record.tmux_session_name:
            return
    push_or_queue_primary_session_stage_prompt(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        prompt_text=instruction_text,
        compiled_subtask_id=prompt_snapshot.compiled_subtask_id,
        prompt_source=prompt_snapshot.subtask_type or "current_stage",
        source_subtask_key=prompt_snapshot.source_subtask_key,
        subtask_type=prompt_snapshot.subtask_type,
        initial_instruction_target=initial_instruction_target,
    )


def _should_use_stage_specific_prompt_message(prompt_snapshot) -> bool:
    source_subtask_key = (prompt_snapshot.source_subtask_key or "").strip()
    subtask_type = (prompt_snapshot.subtask_type or "").strip()
    return (
        source_subtask_key == "generate_child_layout.render_layout_prompt"
        or source_subtask_key == "wait_for_children.collect_child_summaries"
        or subtask_type in {"review", "spawn_child_node"}
    )


def _initial_stage_prompt_instruction(*, logical_node_id: UUID, prompt_snapshot, prompt_target: str) -> str:
    action_message = _stage_prompt_message(
        logical_node_id=logical_node_id,
        prompt_snapshot=prompt_snapshot,
    )
    return (
        f"Read the full current-stage prompt from `{prompt_target}` first and treat that file as authoritative for this turn. "
        "Do not start by re-fetching `subtask prompt`; only do that if the file is missing or unreadable and you must report that bounded failure. "
        "After reading the full prompt file, continue immediately with this concrete stage action guidance:\n\n"
        f"{action_message}"
    )


def push_or_queue_primary_session_stage_prompt(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    prompt_text: str,
    compiled_subtask_id: UUID,
    prompt_source: str,
    source_subtask_key: str | None,
    subtask_type: str | None,
    initial_instruction_target: str | None = None,
    queue_only: bool = False,
) -> str:
    with session_scope(session_factory) as session:
        try:
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
            current = _active_primary_session(session, run.id)
        except (DaemonConflictError, DaemonNotFoundError):
            return "skipped"
        if current is None or current.tmux_session_name is None:
            return "skipped"
        payload = {
            "node_id": str(logical_node_id),
            "compiled_subtask_id": str(compiled_subtask_id),
            "prompt_source": prompt_source,
            "source_subtask_key": source_subtask_key,
            "subtask_type": subtask_type,
            "prompt_text": prompt_text,
            "tmux_session_name": current.tmux_session_name,
            "initial_instruction_target": initial_instruction_target,
        }
        if not queue_only and try_send_input_when_ready(
            adapter,
            session_name=current.tmux_session_name,
            text=prompt_text,
            press_enter=True,
            timeout_seconds=1.0,
        ):
            current.last_heartbeat_at = datetime.now(timezone.utc)
            _record_session_event(session, current.id, "stage_prompt_pushed", payload)
            session.flush()
            return "pushed"
        _record_session_event(session, current.id, "stage_prompt_queued", payload)
        session.flush()
    return "queued"


def _stage_prompt_message(*, logical_node_id: UUID, prompt_snapshot) -> str:
    prompt_text = prompt_snapshot.prompt_text or prompt_snapshot.command_text
    message = (
        "The daemon routed you to the next workflow stage. Continue immediately with this current-stage prompt. "
        "When the prompt requires a shell command, your next response must be an `exec_command` tool call for that exact command rather than prose:\n\n"
        f"{(prompt_text or '').strip()}"
    )
    if prompt_snapshot.source_subtask_key == "generate_child_layout.render_layout_prompt":
        message = (
            "The daemon routed you to the layout-generation stage. Do not browse the repo or run broad discovery commands before completing it. "
            "Use the current prompt/context only unless a referenced file is missing. Your next actions are: "
            f"write `layouts/generated/{logical_node_id}.yaml`, run "
            f"`python3 -m aicoding.cli.main node register-layout --node {logical_node_id} --file layouts/generated/{logical_node_id}.yaml`, "
            "write `summaries/layout_generation.md`, then make your next response an `exec_command` tool call that runs exactly "
            f"`python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {prompt_snapshot.compiled_subtask_id} --summary-file summaries/layout_generation.md`. "
            "Do not answer with prose first."
        )
    elif prompt_snapshot.source_subtask_key == "wait_for_children.collect_child_summaries":
        message = (
            "The daemon routed you to the child-summary rollup stage. Do not wait and do not poll with `sleep`. "
            "If you need the final child states, inspect them once with "
            f"`python3 -m aicoding.cli.main tree show --node {logical_node_id} --full`, "
            "write `summaries/child_rollup.md`, then make your next response an `exec_command` tool call that runs exactly "
            f"`python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {prompt_snapshot.compiled_subtask_id} --summary-file summaries/child_rollup.md`. "
            "Do not answer with prose first."
        )
    elif prompt_snapshot.subtask_type == "spawn_child_node":
        command_text = prompt_snapshot.command_text or f"python3 -m aicoding.cli.main node materialize-children --node {logical_node_id}"
        message = (
            "The daemon routed you to the child-materialization stage. Do not wait. Your next response must be an `exec_command` tool call that runs exactly "
            f"`{command_text}`. That command records the materialization result and routes the workflow stage itself. Do not answer with prose first. Use foreground shell commands only."
        )
    return message


def flush_pending_primary_session_stage_prompts(
    session_factory: sessionmaker[OrmSession],
    *,
    adapter: SessionAdapter,
) -> int:
    with query_session_scope(session_factory) as session:
        active_sessions = session.execute(
            select(Session)
            .where(
                Session.session_role == "primary",
                Session.status.in_(("BOUND", "ATTACHED", "RUNNING", "RESUMED")),
                Session.tmux_session_name.is_not(None),
                Session.node_run_id.is_not(None),
            )
            .order_by(Session.started_at.asc())
        ).scalars().all()

    flushed = 0
    for record in active_sessions:
        with session_scope(session_factory) as session:
            current = session.get(Session, record.id)
            if current is None or current.tmux_session_name is None:
                continue
            if _tmux_session_exists(adapter, current.tmux_session_name) is not True:
                continue
            if _tmux_process_alive(adapter, current.tmux_session_name) is False:
                continue
            queued = _latest_pending_stage_prompt_event(session, current.id)
            if queued is None:
                continue
            payload = dict(queued.payload_json or {})
            prompt_text = payload.get("prompt_text")
            if not isinstance(prompt_text, str) or not prompt_text.strip():
                _record_session_event(
                    session,
                    current.id,
                    "stage_prompt_dropped",
                    {"reason": "missing_prompt_text", "queued_event_id": str(queued.id)},
                )
                session.flush()
                continue
            compiled_subtask_raw = payload.get("compiled_subtask_id")
            if not isinstance(compiled_subtask_raw, str):
                _record_session_event(
                    session,
                    current.id,
                    "stage_prompt_dropped",
                    {"reason": "missing_compiled_subtask_id", "queued_event_id": str(queued.id)},
                )
                session.flush()
                continue
            run = None if current.node_run_id is None else session.get(NodeRun, current.node_run_id)
            state = None if run is None else _require_run_state(session, run.id)
            if state is None or state.current_compiled_subtask_id is None:
                _record_session_event(
                    session,
                    current.id,
                    "stage_prompt_dropped",
                    {
                        "reason": "no_current_subtask",
                        "queued_event_id": str(queued.id),
                        "compiled_subtask_id": compiled_subtask_raw,
                    },
                )
                session.flush()
                continue
            if str(state.current_compiled_subtask_id) != compiled_subtask_raw:
                _record_session_event(
                    session,
                    current.id,
                    "stage_prompt_dropped",
                    {
                        "reason": "stale_compiled_subtask",
                        "queued_event_id": str(queued.id),
                        "queued_compiled_subtask_id": compiled_subtask_raw,
                        "current_compiled_subtask_id": str(state.current_compiled_subtask_id),
                    },
                )
                session.flush()
                continue
            if not try_send_input_when_ready(
                adapter,
                session_name=current.tmux_session_name,
                text=prompt_text,
                press_enter=True,
                timeout_seconds=1.0,
            ):
                continue
            current.last_heartbeat_at = datetime.now(timezone.utc)
            pushed_payload = dict(payload)
            pushed_payload["queued_event_id"] = str(queued.id)
            _record_session_event(session, current.id, "stage_prompt_pushed", pushed_payload)
            session.flush()
            flushed += 1
    return flushed


def auto_advance_incremental_parent_merge_and_refresh_children(
    session_factory: sessionmaker[OrmSession],
    *,
    hierarchy_registry: HierarchyRegistry,
    resources: ResourceCatalog,
) -> AutoAdvancedChildRuntimeSnapshot:
    merge_results = process_pending_incremental_parent_merges(session_factory)
    refreshed_child_node_ids: list[UUID] = []
    for _, child_node_id in _list_auto_run_child_candidate_pairs(
        session_factory,
        hierarchy_registry=hierarchy_registry,
        resources=resources,
    ):
        readiness = check_node_dependency_readiness(session_factory, node_id=child_node_id)
        if readiness.status != "blocked":
            continue
        if not any(item.blocker_kind == "blocked_on_parent_refresh" for item in readiness.blockers):
            continue
        try:
            refresh_child_live_git_from_parent_head(
                session_factory,
                child_version_id=readiness.node_version_id,
            )
        except DaemonConflictError:
            continue
        rematerialized = _maybe_rematerialize_dependency_invalidated_child(
            session_factory,
            logical_node_id=child_node_id,
            node_version_id=readiness.node_version_id,
            hierarchy_registry=hierarchy_registry,
            resources=resources,
        )
        post_refresh = check_node_dependency_readiness(session_factory, node_id=child_node_id)
        if _may_leave_sibling_dependency_wait(post_refresh):
            transition_node_lifecycle(
                session_factory,
                node_id=str(child_node_id),
                target_state="READY",
            )
            post_refresh = check_node_dependency_readiness(session_factory, node_id=child_node_id)
        if rematerialized or post_refresh.status in {"ready", "blocked"}:
            refreshed_child_node_ids.append(child_node_id)
    return AutoAdvancedChildRuntimeSnapshot(
        processed_merge_count=len(merge_results),
        refreshed_child_node_ids=refreshed_child_node_ids,
    )


def _maybe_rematerialize_dependency_invalidated_child(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    node_version_id: UUID,
    hierarchy_registry: HierarchyRegistry,
    resources: ResourceCatalog,
) -> bool:
    from aicoding.daemon.materialization import materialize_layout_children

    with query_session_scope(session_factory) as session:
        if not _is_dependency_invalidated_fresh_restart(session, node_version_id=node_version_id):
            return False
        version = session.get(NodeVersion, node_version_id)
        if version is None or version.supersedes_node_version_id is None:
            return False
        prior_child_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == version.supersedes_node_version_id)
        ).scalars().all()
        if not prior_child_edges:
            return False
        prior_authority = session.get(ParentChildAuthority, version.supersedes_node_version_id)
        if prior_authority is not None and prior_authority.authority_mode in {"manual", "hybrid"}:
            return False
    with session_scope(session_factory) as session:
        current_child_edges = session.execute(
            select(NodeChild).where(NodeChild.parent_node_version_id == node_version_id)
        ).scalars().all()
        for edge in current_child_edges:
            session.delete(edge)
        authority = session.get(ParentChildAuthority, node_version_id)
        if authority is None:
            authority = ParentChildAuthority(
                parent_node_version_id=node_version_id,
                authority_mode="layout_authoritative",
                authoritative_layout_hash=None,
            )
            session.add(authority)
        else:
            authority.authority_mode = "layout_authoritative"
            authority.authoritative_layout_hash = None
        session.flush()
    try:
        result = materialize_layout_children(
            session_factory,
            hierarchy_registry,
            resources,
            logical_node_id=logical_node_id,
        )
    except DaemonConflictError:
        return False
    return result.status in {"created", "already_materialized"}


def _is_dependency_invalidated_fresh_restart(session: OrmSession, *, node_version_id: UUID) -> bool:
    events = session.execute(
        select(RebuildEvent)
        .where(
            RebuildEvent.target_node_version_id == node_version_id,
            RebuildEvent.event_kind == "candidate_created",
        )
        .order_by(RebuildEvent.created_at.desc(), RebuildEvent.id.desc())
    ).scalars().all()
    for event in events:
        if bool((event.details_json or {}).get("fresh_dependency_restart")):
            return True
    return False


def _may_leave_sibling_dependency_wait(readiness) -> bool:
    blocker_kinds = {item.blocker_kind for item in readiness.blockers}
    return blocker_kinds in (set(), {"lifecycle_not_ready"})


def _list_auto_run_child_candidate_pairs(
    session_factory: sessionmaker[OrmSession],
    *,
    hierarchy_registry: HierarchyRegistry,
    resources: ResourceCatalog,
) -> list[tuple[UUID, UUID]]:
    effective_policy = resolve_effective_policy(resources, hierarchy_registry=hierarchy_registry)
    auto_run_children_default = bool(effective_policy.defaults.get("auto_run_children", True))
    candidate_pairs: list[tuple[UUID, UUID]] = []

    with query_session_scope(session_factory) as session:
        selectors = session.execute(select(LogicalNodeCurrentVersion)).scalars().all()
        authoritative_node_ids_by_version = {
            row.authoritative_node_version_id: row.logical_node_id for row in selectors
        }
        edges = session.execute(select(NodeChild).order_by(NodeChild.created_at)).scalars().all()
        seen_children: set[UUID] = set()
        for edge in edges:
            parent_node_id = authoritative_node_ids_by_version.get(edge.parent_node_version_id)
            child_node_id = authoritative_node_ids_by_version.get(edge.child_node_version_id)
            if parent_node_id is None or child_node_id is None or child_node_id in seen_children:
                continue
            parent = session.get(HierarchyNode, parent_node_id)
            if parent is None:
                continue
            parent_definition = hierarchy_registry.get(parent.kind)
            auto_run_children = auto_run_children_default and parent_definition.policies.auto_run_children
            if not auto_run_children:
                continue
            candidate_pairs.append((parent_node_id, child_node_id))
            seen_children.add(child_node_id)
    return candidate_pairs


def get_session_for_node(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _active_run_for_version(session, version.id)
        if run is None:
            latest_failure = _latest_failed_supervision_context(session, node_version_id=version.id)
            if latest_failure is None or latest_failure["session"] is None:
                raise DaemonNotFoundError("primary session not found")
            return _session_snapshot(
                session,
                latest_failure["session"],
                adapter=adapter,
                poller=poller,
                recovery_classification="non_resumable",
                recommended_action="inspect_failed_run",
                terminal_failure=latest_failure["terminal_failure"],
            )
        current = _active_primary_session(session, run.id)
        if current is None:
            raise DaemonNotFoundError("primary session not found")
        return _session_snapshot(session, current, adapter=adapter, poller=poller)


def get_session_by_id(
    session_factory: sessionmaker[OrmSession],
    *,
    session_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    with query_session_scope(session_factory) as session:
        current = session.get(Session, session_id)
        if current is None:
            raise DaemonNotFoundError("session not found")
        return _session_snapshot(session, current, adapter=adapter, poller=poller)


def list_sessions_for_node(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> SessionCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        rows = session.execute(
            select(Session).where(Session.node_version_id == version.id).order_by(Session.started_at)
        ).scalars().all()
        return SessionCatalogSnapshot(
            node_id=logical_node_id,
            sessions=[_session_snapshot(session, row, adapter=adapter, poller=poller) for row in rows],
        )


def list_session_events(
    session_factory: sessionmaker[OrmSession],
    *,
    session_id: UUID,
) -> list[SessionEventSnapshot]:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(SessionEvent).where(SessionEvent.session_id == session_id).order_by(SessionEvent.created_at)
        ).scalars().all()
        return [
            SessionEventSnapshot(
                id=row.id,
                session_id=row.session_id,
                event_type=row.event_type,
                payload_json=dict(row.payload_json),
                created_at=row.created_at.isoformat(),
            )
            for row in rows
        ]


def inspect_primary_session_screen_state(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
    persist: bool = False,
) -> SessionScreenStateSnapshot:
    with session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _require_active_run(session, version.id)
        current = _active_primary_session(session, run.id)
        if current is None:
            raise DaemonNotFoundError("primary session not found")
        snapshot = _classify_session_screen_state(session, current, adapter=adapter, poller=poller, persist=persist)
        session.flush()
        return snapshot


def _authoritative_version(session: OrmSession, logical_node_id: UUID) -> NodeVersion:
    from aicoding.db.models import LogicalNodeCurrentVersion

    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version


def _matched_lifecycle(session: OrmSession, *, logical_node_id: UUID, node_version_id: UUID) -> NodeLifecycleState | None:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None:
        return None
    if lifecycle.node_version_id not in {None, node_version_id}:
        return None
    return lifecycle


def _require_active_run(session: OrmSession, node_version_id: UUID):
    run = _active_run_for_version(session, node_version_id)
    if run is None:
        raise DaemonConflictError("active durable run not found")
    return run


def _active_run_for_version(session: OrmSession, node_version_id: UUID) -> NodeRun | None:
    run = session.execute(
        select(NodeRun).where(NodeRun.node_version_id == node_version_id, NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED"))).order_by(NodeRun.run_number.desc())
    ).scalars().first()
    return run


def _active_primary_session(session: OrmSession, node_run_id: UUID) -> Session | None:
    return session.execute(
        select(Session)
        .where(Session.node_run_id == node_run_id, Session.session_role == "primary", Session.status.in_(ACTIVE_SESSION_STATUSES))
        .order_by(Session.started_at.desc())
    ).scalars().first()


def _active_primary_sessions(session: OrmSession, node_run_id: UUID) -> list[Session]:
    return session.execute(
        select(Session)
        .where(Session.node_run_id == node_run_id, Session.session_role == "primary", Session.status.in_(ACTIVE_SESSION_STATUSES))
        .order_by(Session.started_at.desc())
    ).scalars().all()


def _latest_primary_session(session: OrmSession, node_run_id: UUID) -> Session | None:
    return session.execute(
        select(Session)
        .where(Session.node_run_id == node_run_id, Session.session_role == "primary")
        .order_by(Session.started_at.desc())
    ).scalars().first()


def _latest_failed_supervision_context(session: OrmSession, *, node_version_id: UUID) -> dict[str, object] | None:
    latest_run = session.execute(
        select(NodeRun).where(NodeRun.node_version_id == node_version_id).order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if latest_run is None or latest_run.run_status != "FAILED":
        return None
    state = session.get(NodeRunState, latest_run.id)
    if state is None:
        return None
    failure_row = session.execute(
        select(SessionEvent, Session)
        .join(Session, SessionEvent.session_id == Session.id)
        .where(
            Session.node_run_id == latest_run.id,
            Session.session_role == "primary",
            SessionEvent.event_type == "supervision_recovery_failed",
        )
        .order_by(SessionEvent.created_at.desc())
    ).first()
    if failure_row is None:
        return None
    failure_event, failed_session = failure_row
    payload = dict(failure_event.payload_json or {})
    terminal_failure = {
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
    }
    return {
        "run": latest_run,
        "state": state,
        "session": failed_session,
        "failure_event": failure_event,
        "terminal_failure": terminal_failure,
    }


def _require_single_active_primary_session(session: OrmSession, node_run_id: UUID) -> Session | None:
    active_sessions = _active_primary_sessions(session, node_run_id)
    if len(active_sessions) > 1:
        raise DaemonConflictError("duplicate active primary sessions detected")
    return active_sessions[0] if active_sessions else None


def _nudge_event_count(session: OrmSession, session_id: UUID) -> int:
    reset_at = session.execute(
        select(func.max(SessionEvent.created_at)).where(
            SessionEvent.session_id == session_id,
            SessionEvent.event_type == "stage_prompt_pushed",
        )
    ).scalar_one()
    nudged_events = session.execute(
        select(SessionEvent).where(
            SessionEvent.session_id == session_id,
            SessionEvent.event_type == "nudged",
            *(tuple() if reset_at is None else (SessionEvent.created_at >= reset_at,)),
        )
    ).scalars()
    return sum(1 for _ in nudged_events)


def _latest_pending_stage_prompt_event(session: OrmSession, session_id: UUID) -> SessionEvent | None:
    resolved_at = session.execute(
        select(func.max(SessionEvent.created_at)).where(
            SessionEvent.session_id == session_id,
            SessionEvent.event_type.in_(("stage_prompt_pushed", "stage_prompt_dropped")),
        )
    ).scalar_one()
    queued_query = select(SessionEvent).where(
        SessionEvent.session_id == session_id,
        SessionEvent.event_type == "stage_prompt_queued",
    )
    if resolved_at is not None:
        queued_query = queued_query.where(SessionEvent.created_at > resolved_at)
    return session.execute(queued_query.order_by(SessionEvent.created_at.desc())).scalars().first()


def _latest_session_event(
    session: OrmSession,
    session_id: UUID,
    *,
    event_types: tuple[str, ...],
) -> SessionEvent | None:
    return session.execute(
        select(SessionEvent)
        .where(
            SessionEvent.session_id == session_id,
            SessionEvent.event_type.in_(event_types),
        )
        .order_by(SessionEvent.created_at.desc())
    ).scalars().first()


def record_primary_session_stage_prompt(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    prompt_source: str,
    current_compiled_subtask_id: UUID | None = None,
) -> None:
    with session_scope(session_factory) as session:
        try:
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
            current = _active_primary_session(session, run.id)
        except (DaemonConflictError, DaemonNotFoundError):
            return
        if current is None:
            return
        current.last_heartbeat_at = datetime.now(timezone.utc)
        payload: dict[str, object] = {"prompt_source": prompt_source}
        if current_compiled_subtask_id is not None:
            payload["current_compiled_subtask_id"] = str(current_compiled_subtask_id)
        _record_session_event(
            session,
            current.id,
            "stage_prompt_pushed",
            payload,
        )
        session.flush()


def _seed_missing_stage_prompt_after_codex_ready(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
) -> str:
    with query_session_scope(session_factory) as session:
        try:
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
            state = _require_run_state(session, run.id)
            current = _active_primary_session(session, run.id)
        except (DaemonConflictError, DaemonNotFoundError):
            return "skipped"
        if current is None or current.tmux_session_name is None or state.current_compiled_subtask_id is None:
            return "skipped"
        latest_ready = _latest_session_event(session, current.id, event_types=("codex_ready",))
        if latest_ready is None:
            return "skipped"
        latest_stage_event = _latest_session_event(
            session,
            current.id,
            event_types=("stage_prompt_pushed", "stage_prompt_queued"),
        )
        if latest_stage_event is not None and latest_stage_event.created_at >= latest_ready.created_at:
            return "skipped"

    from aicoding.daemon.run_orchestration import load_current_subtask_prompt, start_subtask_attempt

    start_subtask_attempt(
        session_factory,
        logical_node_id=logical_node_id,
        compiled_subtask_id=state.current_compiled_subtask_id,
        adapter=adapter,
    )

    prompt_snapshot = load_current_subtask_prompt(session_factory, logical_node_id=logical_node_id)
    prompt_text = prompt_snapshot.prompt_text or prompt_snapshot.command_text
    if not isinstance(prompt_text, str) or not prompt_text.strip():
        return "skipped"
    return push_or_queue_primary_session_stage_prompt(
        session_factory,
        logical_node_id=logical_node_id,
        adapter=adapter,
        prompt_text=_stage_prompt_message(logical_node_id=logical_node_id, prompt_snapshot=prompt_snapshot),
        compiled_subtask_id=prompt_snapshot.compiled_subtask_id,
        prompt_source=prompt_snapshot.subtask_type or "current_stage",
        source_subtask_key=prompt_snapshot.source_subtask_key,
        subtask_type=prompt_snapshot.subtask_type,
    )


def _current_subtask_has_registered_summary(
    session: OrmSession,
    node_run_id: UUID,
    compiled_subtask_id: UUID | None,
) -> bool:
    if compiled_subtask_id is None:
        return False
    latest_attempt = session.execute(
        select(SubtaskAttempt)
        .where(
            SubtaskAttempt.node_run_id == node_run_id,
            SubtaskAttempt.compiled_subtask_id == compiled_subtask_id,
        )
        .order_by(SubtaskAttempt.attempt_number.desc())
    ).scalars().first()
    if latest_attempt is None:
        return False
    output_json = dict(latest_attempt.output_json or {})
    registrations = output_json.get("registered_summaries")
    return isinstance(registrations, list) and len(registrations) > 0


def _require_run_state(session: OrmSession, node_run_id: UUID) -> NodeRunState:
    state = session.get(NodeRunState, node_run_id)
    if state is None:
        raise DaemonNotFoundError("node run state not found")
    return state


def _invalidate_session(session: OrmSession, record: Session, *, status: str, reason: str) -> None:
    record.status = status
    record.ended_at = datetime.now(timezone.utc)
    _record_session_event(session, record.id, "invalidated", {"reason": reason, "status": status})


def _cleanup_tmux_session_record(
    session: OrmSession,
    record: Session,
    *,
    adapter: SessionAdapter,
    cleanup_reason: str,
    status: str | None = None,
) -> None:
    if status is not None:
        record.status = status
    if record.ended_at is None:
        record.ended_at = datetime.now(timezone.utc)
    session_name = record.tmux_session_name
    session_existed = False
    if session_name:
        session_existed = adapter.session_exists(session_name)
        adapter.kill_session(session_name)
    _record_session_event(
        session,
        record.id,
        "tmux_session_cleaned",
        {
            "cleanup_reason": cleanup_reason,
            "tmux_session_name": session_name,
            "tmux_session_existed": session_existed,
            "status": record.status,
        },
    )


def cleanup_session_by_id(
    session_factory: sessionmaker[OrmSession],
    *,
    session_id: UUID,
    adapter: SessionAdapter,
    cleanup_reason: str,
    status: str | None = None,
) -> None:
    with session_scope(session_factory) as session:
        record = session.get(Session, session_id)
        if record is None:
            return
        _cleanup_tmux_session_record(
            session,
            record,
            adapter=adapter,
            cleanup_reason=cleanup_reason,
            status=status,
        )
        session.flush()


def cleanup_sessions_for_run(
    session_factory: sessionmaker[OrmSession],
    *,
    node_run_id: UUID,
    adapter: SessionAdapter,
    cleanup_reason: str,
    status: str | None = None,
) -> None:
    with session_scope(session_factory) as session:
        rows = session.execute(select(Session).where(Session.node_run_id == node_run_id).order_by(Session.started_at)).scalars().all()
        for record in rows:
            _cleanup_tmux_session_record(
                session,
                record,
                adapter=adapter,
                cleanup_reason=cleanup_reason,
                status=status if record.session_role == "primary" else record.status,
            )
        session.flush()


def cleanup_sessions_for_node_version(
    session_factory: sessionmaker[OrmSession],
    *,
    node_version_id: UUID,
    adapter: SessionAdapter,
    cleanup_reason: str,
    status: str | None = None,
) -> None:
    with session_scope(session_factory) as session:
        rows = session.execute(select(Session).where(Session.node_version_id == node_version_id).order_by(Session.started_at)).scalars().all()
        for record in rows:
            _cleanup_tmux_session_record(
                session,
                record,
                adapter=adapter,
                cleanup_reason=cleanup_reason,
                status=status if record.session_role == "primary" else record.status,
            )
        session.flush()


def _record_session_event(session: OrmSession, session_id: UUID, event_type: str, payload: dict[str, object]) -> None:
    session.add(SessionEvent(id=uuid4(), session_id=session_id, event_type=event_type, payload_json=payload))


def _record_auto_nudge_failure(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    phase: str,
    exc: Exception,
) -> None:
    with session_scope(session_factory) as session:
        try:
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
            current = _active_primary_session(session, run.id)
        except (DaemonConflictError, DaemonNotFoundError):
            return
        if current is None:
            return
        _record_session_event(
            session,
            current.id,
            "auto_nudge_failed",
            {
                "phase": phase,
                "error_type": type(exc).__name__,
                "message": str(exc),
            },
        )


@dataclass(frozen=True, slots=True)
class _SessionSupervisionTarget:
    logical_node_id: UUID
    run_status: str
    lifecycle_state: str | None
    tracked_session_id: UUID | None
    current_session_id: UUID | None
    tmux_session_exists: bool
    tmux_process_alive: bool | None
    tmux_exit_status: int | None
    tmux_process_command_line: str | None
    codex_ready_seen: bool


def _load_session_supervision_target(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
) -> _SessionSupervisionTarget | None:
    with query_session_scope(session_factory) as session:
        try:
            version = _authoritative_version(session, logical_node_id)
            run = _require_active_run(session, version.id)
        except (DaemonConflictError, DaemonNotFoundError):
            return None
        latest = _latest_primary_session(session, run.id)
        if latest is None:
            return None
        current = _active_primary_session(session, run.id)
        lifecycle = _matched_lifecycle(session, logical_node_id=logical_node_id, node_version_id=version.id)
        tmux_session_name = None if current is None else current.tmux_session_name
        tmux_exists = _tmux_session_exists(adapter, tmux_session_name)
        tmux_process_alive = _tmux_process_alive(adapter, tmux_session_name)
        process_command_line = adapter.process_command_line(tmux_session_name) if tmux_session_name else None
        codex_ready_seen = False
        if latest is not None:
            codex_ready_seen = _session_event_exists(session, session_id=latest.id, event_type="codex_ready")
        return _SessionSupervisionTarget(
            logical_node_id=logical_node_id,
            run_status=run.run_status,
            lifecycle_state=None if lifecycle is None else lifecycle.lifecycle_state,
            tracked_session_id=latest.id,
            current_session_id=None if current is None else current.id,
            tmux_session_exists=bool(tmux_exists),
            tmux_process_alive=tmux_process_alive,
            tmux_exit_status=_tmux_exit_status(adapter, tmux_session_name),
            tmux_process_command_line=process_command_line,
            codex_ready_seen=codex_ready_seen,
        )


def _record_supervision_event(
    session_factory: sessionmaker[OrmSession],
    *,
    session_id: UUID,
    event_type: str,
    payload: dict[str, object],
    invalidate_active_session: bool = False,
    invalidation_reason: str = "supervision_detected_missing_tmux_session",
) -> None:
    with session_scope(session_factory) as session:
        record = session.get(Session, session_id)
        if record is None:
            return
        if invalidate_active_session and record.status in ACTIVE_SESSION_STATUSES:
            _invalidate_session(session, record, status="LOST", reason=invalidation_reason)
        _record_session_event(session, session_id, event_type, payload)
        session.flush()


def _record_supervision_failure_event(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    session_id: UUID,
    reason: str,
    details: dict[str, object],
    invalidate_active_session: bool,
) -> None:
    payload = {"reason": reason, **details}
    _record_supervision_event(
        session_factory,
        session_id=session_id,
        event_type="supervision_recovery_failed",
        payload=payload,
        invalidate_active_session=invalidate_active_session,
        invalidation_reason="supervision_detected_missing_tmux_session",
    )


def _pane_active_work_marker(pane_text: str) -> str | None:
    if "background terminal running" in pane_text or "Waited for background terminal" in pane_text:
        return None
    for marker in _ACTIVE_WORK_MARKERS:
        if marker in pane_text:
            return marker
    return None


def _current_subtask_for_recovery(session: OrmSession, compiled_subtask_id: UUID | None) -> CompiledSubtask | None:
    if compiled_subtask_id is None:
        return None
    return session.get(CompiledSubtask, compiled_subtask_id)


def _generated_layout_already_registered(session: OrmSession, *, logical_node_id: UUID) -> bool:
    row = (
        session.execute(
            select(WorkflowEvent.id)
            .where(
                WorkflowEvent.logical_node_id == logical_node_id,
                WorkflowEvent.event_scope == "child_layout",
                WorkflowEvent.event_type == "registered_generated_layout",
            )
            .limit(1)
        )
        .scalars()
        .first()
    )
    return row is not None


def _next_compiled_subtask_title(
    session: OrmSession,
    *,
    current_subtask: CompiledSubtask,
) -> str | None:
    row = (
        session.execute(
            select(CompiledSubtask.title, CompiledSubtask.source_subtask_key)
            .where(
                CompiledSubtask.compiled_workflow_id == current_subtask.compiled_workflow_id,
                CompiledSubtask.ordinal == current_subtask.ordinal + 1,
            )
            .limit(1)
        )
        .first()
    )
    if row is None:
        return None
    title, source_subtask_key = row
    for value in (title, source_subtask_key):
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _wait_stage_child_states(
    session: OrmSession,
    *,
    logical_node_id: UUID,
) -> list[dict[str, str | None]]:
    child_nodes = session.execute(
        select(HierarchyNode)
        .where(HierarchyNode.parent_node_id == logical_node_id)
        .order_by(HierarchyNode.created_at.asc(), HierarchyNode.node_id.asc())
    ).scalars().all()
    child_states: list[dict[str, str | None]] = []
    for child in child_nodes:
        lifecycle = session.get(NodeLifecycleState, str(child.node_id))
        child_states.append(
            {
                "node_id": str(child.node_id),
                "title": child.title,
                "kind": child.kind,
                "lifecycle_state": None if lifecycle is None else lifecycle.lifecycle_state,
                "run_status": None if lifecycle is None else lifecycle.run_status,
            }
        )
    return child_states


def _wait_stage_active_children(
    session: OrmSession,
    *,
    logical_node_id: UUID,
) -> list[dict[str, str | None]]:
    active_lifecycle_states = {
        "READY",
        "RUNNING",
        "WAITING_ON_CHILDREN",
        "WAITING_ON_SIBLING_DEPENDENCY",
        "RECTIFYING_SELF",
        "RECTIFYING_UPSTREAM",
        "REVIEW_PENDING",
        "VALIDATION_PENDING",
        "TESTING_PENDING",
    }
    return [
        child
        for child in _wait_stage_child_states(session, logical_node_id=logical_node_id)
        if child["lifecycle_state"] in active_lifecycle_states or child["run_status"] in {"PENDING", "RUNNING"}
    ]


def _recovery_stage_specific_guidance(
    *,
    session: OrmSession,
    logical_node_id: UUID,
    current_subtask: CompiledSubtask | None,
) -> str:
    if current_subtask is None:
        return ""
    next_stage_hint = _next_compiled_subtask_title(session, current_subtask=current_subtask)
    next_stage_line = ""
    if isinstance(next_stage_hint, str) and next_stage_hint.strip():
        next_stage_line = f"- after success, expect the daemon to route into `{next_stage_hint.strip()}`\n"
    if current_subtask.source_subtask_key == "generate_child_layout.render_layout_prompt":
        if _generated_layout_already_registered(session, logical_node_id=logical_node_id):
            return (
                "\nCurrent layout-generation action:\n"
                f"- `layouts/generated/{logical_node_id}.yaml` is already registered for this node\n"
                "- do not fetch the prompt again and do not explore unrelated files\n"
                "- write `summaries/layout_generation.md` now with a brief note that the generated layout was registered successfully\n"
                "- after writing that summary, your next response must be an `exec_command` tool call, not prose\n"
                f"{next_stage_line}"
                f"- run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/layout_generation.md` now\n"
            )
        return (
            "\nCurrent layout-generation action:\n"
            "- do not fetch `subtask prompt` again unless the generated prompt file is actually missing or unreadable\n"
            "- do not browse unrelated files or run broad discovery commands in this stage\n"
            "- do not combine daemon CLI commands with `&&`, `;`, `||`, pipes, or multi-command shell snippets; run each one as its own standalone `exec_command` tool call\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"- write `layouts/generated/{logical_node_id}.yaml` now\n"
            f"- immediately register it with `python3 -m aicoding.cli.main node register-layout --node {logical_node_id} --file layouts/generated/{logical_node_id}.yaml`\n"
            "- after registration, write `summaries/layout_generation.md`\n"
            f"{next_stage_line}"
            f"- then run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/layout_generation.md`\n"
        )
    if ".hook." in current_subtask.source_subtask_key and current_subtask.subtask_type == "run_prompt":
        return (
            "\nCurrent hook-stage action:\n"
            "- do not reload the bootstrap prompt again unless the active stage is genuinely unclear\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"- if needed, inspect `python3 -m aicoding.cli.main session show-current --node {logical_node_id}` once, then stop re-checking the same bootstrap state\n"
            "- write a brief durable bootstrap summary to `summaries/parent_subtask.md` now\n"
            f"{next_stage_line}"
            f"- after writing that summary, run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/parent_subtask.md` now\n"
        )
    if current_subtask.subtask_type == "review":
        review_prompt = (current_subtask.prompt_text or "").strip()
        if review_prompt:
            review_prompt = review_prompt.replace("CURRENT_COMPILED_SUBTASK_ID", str(current_subtask.id))
        compiled_prompt_block = ""
        if review_prompt:
            compiled_prompt_block = (
                "- follow the compiled review prompt below rather than reloading the prompt again unless the stage is genuinely unclear\n\n"
                f"{review_prompt}\n"
            )
        return (
            "\nCurrent review-stage action:\n"
            "- do not wait for another tool call or background terminal result\n"
            "- do not combine `subtask start`, `subtask context`, or `review run` with `&&`, `;`, `||`, pipes, or multi-command shell snippets; run each daemon CLI command as its own standalone `exec_command` tool call\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"{next_stage_line}"
            f"{compiled_prompt_block}"
            "- do not ask for `/review`\n"
        )
    if current_subtask.source_subtask_key == "wait_for_children.collect_child_summaries":
        return (
            "\nCurrent child-summary rollup action:\n"
            "- do not wait for another tool call, child-materialization event, or background terminal result\n"
            "- do not run `sleep` or a polling loop in this stage\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"- inspect `python3 -m aicoding.cli.main tree show --node {logical_node_id} --full` once if you still need the final child states or summary paths\n"
            "- gather the already-completed child summaries into `summaries/child_rollup.md` now\n"
            f"{next_stage_line}"
            f"- after writing that summary, run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/child_rollup.md` now\n"
        )
    if current_subtask.subtask_type == "build_context":
        return (
            "\nCurrent context-building action:\n"
            "- do not wait for another tool call or background terminal result\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"- if you need the latest stage data, run `python3 -m aicoding.cli.main subtask context --node {logical_node_id}` once, then stop reloading prompts\n"
            "- write a concise durable context summary to `summaries/context.md` now\n"
            f"{next_stage_line}"
            f"- after writing that summary, run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/context.md` now\n"
        )
    if current_subtask.subtask_type == "wait_for_children":
        return (
            "\nCurrent child-wait action:\n"
            "- do not mark this stage complete until every direct child is actually COMPLETE\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"- inspect `python3 -m aicoding.cli.main tree show --node {logical_node_id} --full` now\n"
            "- if any direct child is still READY, RUNNING, WAITING_ON_CHILDREN, WAITING_ON_SIBLING_DEPENDENCY, RECTIFYING_SELF, RECTIFYING_UPSTREAM, REVIEW_PENDING, VALIDATION_PENDING, or TESTING_PENDING, keep waiting and do not call `subtask succeed`\n"
            "- if any direct child is PAUSED_FOR_USER, FAILED, FAILED_TO_PARENT, CANCELLED, or otherwise terminal without being COMPLETE, write `summaries/parent_subtask_failure.md` and fail this stage instead of waiting forever\n"
            "- only after every direct child is COMPLETE, write `summaries/child_rollup.md` and prepare the success command\n"
            f"{next_stage_line}"
            f"- if a child has failed terminally, run `python3 -m aicoding.cli.main subtask fail --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/parent_subtask_failure.md` and stop; do not run `subtask succeed`\n"
            f"- only when every direct child is COMPLETE, run `python3 -m aicoding.cli.main subtask succeed --node {logical_node_id} --compiled-subtask {current_subtask.id} --summary-file summaries/child_rollup.md`\n"
        )
    if current_subtask.subtask_type == "spawn_child_node":
        return (
            "\nCurrent child-materialization action:\n"
            "- your next response must be an `exec_command` tool call, not prose\n"
            f"{next_stage_line}"
            f"- run `python3 -m aicoding.cli.main node materialize-children --node {logical_node_id}` now\n"
            "- that command records the materialization result and routes this workflow stage itself\n"
        )
    return ""


def _render_recovery_prompt(
    template_text: str,
    *,
    session: OrmSession,
    logical_node_id: UUID,
    current_subtask: CompiledSubtask | None = None,
) -> str:
    prompt_cli_command = current_stage_prompt_cli_command(logical_node_id=logical_node_id)
    context = build_render_context(
        scopes={
            "node": {"id": str(logical_node_id)},
            "prompt": {"cli_command": prompt_cli_command},
            "compat": {
                "node_id": str(logical_node_id),
                "prompt_cli_command": prompt_cli_command,
            },
        }
    )
    guidance = _recovery_stage_specific_guidance(
        session=session,
        logical_node_id=logical_node_id,
        current_subtask=current_subtask,
    ).rstrip()
    rendered = render_text(template_text, context=context, field_name="prompt").rendered_text.rstrip()
    if not guidance:
        return f"{rendered}\n"
    return f"{guidance}\n{rendered}\n"


def _classify_session_screen_state(
    session: OrmSession,
    record: Session,
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
    persist: bool,
) -> SessionScreenStateSnapshot:
    if record.tmux_session_name is None:
        raise DaemonConflictError("session is missing tmux identity")
    poll_result = poller.poll(record.tmux_session_name)
    pane_text = adapter.capture_pane(record.tmux_session_name, include_alt_screen=True)
    pane_hash = hashlib.sha256(pane_text.encode("utf-8")).hexdigest()
    previous = _latest_screen_poll_event(session, record.id)
    previous_pane_hash = None if previous is None else str(previous.get("pane_hash") or "")
    comparison_window = None
    if previous is not None:
        comparison_window = max((datetime.now(timezone.utc) - _parse_iso8601(previous.get("sampled_at"))).total_seconds(), 0.0)
    pane_changed = previous_pane_hash is None or previous_pane_hash != pane_hash
    active_work_marker = _pane_active_work_marker(pane_text)
    if active_work_marker is not None:
        classification = "active"
        reason = "active_work_indicator_present"
    elif pane_changed:
        if previous_pane_hash is None and poll_result.is_idle:
            classification = "idle"
            reason = "first_sample_idle_threshold_exceeded"
        else:
            classification = "active"
            reason = "first_sample" if previous_pane_hash is None else "pane_changed"
    elif poll_result.is_idle:
        classification = "idle"
        reason = "unchanged_screen_past_idle_threshold"
    else:
        classification = "quiet"
        reason = "unchanged_screen_within_threshold"
    snapshot = SessionScreenStateSnapshot(
        classification=classification,
        reason=reason,
        sampled_at=datetime.now(timezone.utc).isoformat(),
        idle_seconds=poll_result.idle_seconds,
        in_alt_screen=poll_result.snapshot.in_alt_screen,
        pane_hash=pane_hash,
        previous_pane_hash=previous_pane_hash,
        pane_changed=pane_changed,
        comparison_window_seconds=comparison_window,
    )
    if persist:
        payload = snapshot.to_payload()
        if active_work_marker is not None:
            payload["active_work_marker"] = active_work_marker
        _record_session_event(session, record.id, "screen_polled", payload)
    return snapshot


def _latest_screen_poll_event(session: OrmSession, session_id: UUID) -> dict[str, object] | None:
    row = session.execute(
        select(SessionEvent)
        .where(SessionEvent.session_id == session_id, SessionEvent.event_type == "screen_polled")
        .order_by(SessionEvent.created_at.desc())
    ).scalars().first()
    if row is None:
        return None
    return dict(row.payload_json)


def _session_event_exists(session: OrmSession, *, session_id: UUID, event_type: str) -> bool:
    row = session.execute(
        select(SessionEvent.id)
        .where(SessionEvent.session_id == session_id, SessionEvent.event_type == event_type)
        .limit(1)
    ).first()
    return row is not None


def _latest_session_event_type(session: OrmSession, session_id: UUID) -> str | None:
    row = session.execute(
        select(SessionEvent)
        .where(SessionEvent.session_id == session_id, SessionEvent.event_type != "screen_polled")
        .order_by(SessionEvent.created_at.desc())
    ).scalars().first()
    if row is None:
        return None
    return row.event_type


def _parse_iso8601(value: object) -> datetime:
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            pass
    return datetime.now(timezone.utc)


def _recovery_status_snapshot(
    session: OrmSession,
    *,
    logical_node_id: UUID,
    version: NodeVersion,
    run: NodeRun,
    state: NodeRunState,
    active_sessions: list[Session],
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> RecoveryStatusSnapshot:
    current = active_sessions[0] if active_sessions else None
    duplicate_count = len(active_sessions)
    if state.is_resumable is False:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=None if current is None else current.id,
            recovery_classification="non_resumable",
            recommended_action="reject_recovery",
            reason="run_marked_non_resumable",
            is_resumable=False,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=None if current is None else current.tmux_session_name,
            tmux_session_exists=None,
            tmux_process_alive=None,
            tmux_exit_status=None,
            provider=None if current is None else current.provider,
            provider_session_id_present=False if current is None else current.provider_session_id is not None,
            heartbeat_age_seconds=_heartbeat_age_seconds(current),
            duplicate_active_primary_sessions=duplicate_count,
            terminal_failure=None,
        )
    if duplicate_count > 1:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=None if current is None else current.id,
            recovery_classification="ambiguous",
            recommended_action="pause_for_user",
            reason="duplicate_primary_sessions_detected",
            is_resumable=state.is_resumable,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=None if current is None else current.tmux_session_name,
            tmux_session_exists=None if current is None else _tmux_session_exists(adapter, current.tmux_session_name),
            tmux_process_alive=None if current is None else _tmux_process_alive(adapter, current.tmux_session_name),
            tmux_exit_status=None if current is None else _tmux_exit_status(adapter, current.tmux_session_name),
            provider=None if current is None else current.provider,
            provider_session_id_present=False if current is None else current.provider_session_id is not None,
            heartbeat_age_seconds=_heartbeat_age_seconds(current),
            duplicate_active_primary_sessions=duplicate_count,
            terminal_failure=None,
        )
    if current is None:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=None,
            recovery_classification="missing",
            recommended_action="create_replacement_session",
            reason="no_active_primary_session",
            is_resumable=state.is_resumable,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=None,
            tmux_session_exists=False,
            tmux_process_alive=None,
            tmux_exit_status=None,
            provider=None,
            provider_session_id_present=False,
            heartbeat_age_seconds=None,
            duplicate_active_primary_sessions=0,
            terminal_failure=None,
        )
    tmux_exists = _tmux_session_exists(adapter, current.tmux_session_name) is True
    tmux_process_alive = _tmux_process_alive(adapter, current.tmux_session_name)
    tmux_exit_status = _tmux_exit_status(adapter, current.tmux_session_name)
    heartbeat_age = _heartbeat_age_seconds(current)
    if not tmux_exists:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=current.id,
            recovery_classification="lost",
            recommended_action="create_replacement_session",
            reason="tmux_session_missing",
            is_resumable=state.is_resumable,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=current.tmux_session_name,
            tmux_session_exists=False,
            tmux_process_alive=None,
            tmux_exit_status=None,
            provider=current.provider,
            provider_session_id_present=current.provider_session_id is not None,
            heartbeat_age_seconds=heartbeat_age,
            duplicate_active_primary_sessions=duplicate_count,
            terminal_failure=None,
        )
    if tmux_process_alive is False:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=current.id,
            recovery_classification="lost",
            recommended_action="create_replacement_session",
            reason="tmux_process_exited",
            is_resumable=state.is_resumable,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=current.tmux_session_name,
            tmux_session_exists=True,
            tmux_process_alive=False,
            tmux_exit_status=tmux_exit_status,
            provider=current.provider,
            provider_session_id_present=current.provider_session_id is not None,
            heartbeat_age_seconds=heartbeat_age,
            duplicate_active_primary_sessions=duplicate_count,
            terminal_failure=None,
        )
    poll_result = poller.poll(current.tmux_session_name)
    if poll_result.is_idle:
        return RecoveryStatusSnapshot(
            node_id=logical_node_id,
            node_version_id=version.id,
            node_run_id=run.id,
            session_id=current.id,
            recovery_classification="stale_but_recoverable",
            recommended_action="resume_existing_session",
            reason="session_idle_beyond_threshold",
            is_resumable=state.is_resumable,
            pause_flag_name=state.pause_flag_name,
            tmux_session_name=current.tmux_session_name,
            tmux_session_exists=True,
            tmux_process_alive=True,
            tmux_exit_status=tmux_exit_status,
            provider=current.provider,
            provider_session_id_present=current.provider_session_id is not None,
            heartbeat_age_seconds=heartbeat_age,
            duplicate_active_primary_sessions=duplicate_count,
            terminal_failure=None,
        )
    classification = "detached" if current.status == "BOUND" else "healthy"
    return RecoveryStatusSnapshot(
        node_id=logical_node_id,
        node_version_id=version.id,
        node_run_id=run.id,
        session_id=current.id,
        recovery_classification=classification,
        recommended_action="attach_existing_session" if classification == "detached" else "resume_existing_session",
        reason=None if current.provider_session_id is not None else "provider_identity_unavailable",
        is_resumable=state.is_resumable,
        pause_flag_name=state.pause_flag_name,
        tmux_session_name=current.tmux_session_name,
        tmux_session_exists=True,
        tmux_process_alive=True,
        tmux_exit_status=tmux_exit_status,
        provider=current.provider,
        provider_session_id_present=current.provider_session_id is not None,
        heartbeat_age_seconds=heartbeat_age,
        duplicate_active_primary_sessions=duplicate_count,
        terminal_failure=None,
    )


def _provider_recovery_status_snapshot(
    *,
    current: Session | None,
    recovery_status: RecoveryStatusSnapshot,
    adapter: SessionAdapter,
) -> ProviderRecoveryStatusSnapshot:
    provider = None if current is None else current.provider
    provider_session_id = None if current is None else current.provider_session_id
    tmux_session_name = None if current is None else current.tmux_session_name
    tmux_session_exists = _tmux_session_exists(adapter, tmux_session_name)
    tmux_process_alive = _tmux_process_alive(adapter, tmux_session_name)
    tmux_exit_status = _tmux_exit_status(adapter, tmux_session_name)
    provider_supported = current is not None and current.provider == adapter.backend_name and current.provider_session_id is not None
    provider_session_exists = None
    provider_rebind_possible = False
    provider_recommended_action = "fallback_to_provider_agnostic_recovery"
    provider_reason = None

    if current is None:
        provider_reason = "no_active_primary_session"
    elif current.provider != adapter.backend_name:
        provider_reason = "provider_backend_mismatch"
    elif current.provider_session_id is None:
        provider_reason = "provider_identity_unavailable"
    else:
        provider_session_exists = adapter.session_exists(current.provider_session_id)
        if provider_session_exists and (
            current.tmux_session_name != current.provider_session_id
            or tmux_session_exists is False
            or tmux_process_alive is False
        ):
            provider_rebind_possible = True
            provider_recommended_action = "rebind_provider_session"
            provider_reason = "provider_session_restorable"
        elif provider_session_exists:
            provider_recommended_action = "provider_recovery_not_needed"
            provider_reason = "provider_session_already_bound"
        else:
            provider_recommended_action = "fallback_to_provider_agnostic_recovery"
            provider_reason = "provider_session_missing"

    return ProviderRecoveryStatusSnapshot(
        node_id=recovery_status.node_id,
        node_version_id=recovery_status.node_version_id,
        node_run_id=recovery_status.node_run_id,
        session_id=recovery_status.session_id,
        provider=provider,
        provider_session_id=provider_session_id,
        provider_supported=provider_supported,
        provider_session_exists=provider_session_exists,
        tmux_session_name=tmux_session_name,
        tmux_session_exists=tmux_session_exists,
        tmux_process_alive=tmux_process_alive,
        tmux_exit_status=tmux_exit_status,
        provider_rebind_possible=provider_rebind_possible,
        provider_recommended_action=provider_recommended_action,
        provider_reason=provider_reason,
        recovery_status=recovery_status,
    )


def _heartbeat_age_seconds(record: Session | None) -> float | None:
    if record is None:
        return None
    reference = record.last_heartbeat_at or record.started_at
    return max((datetime.now(timezone.utc) - reference).total_seconds(), 0.0)


def _tmux_session_snapshot(adapter: SessionAdapter, session_name: str | None):
    if session_name is None:
        return None
    return adapter.describe(session_name)


def _tmux_session_exists(adapter: SessionAdapter, session_name: str | None) -> bool | None:
    if session_name is None:
        return None
    snapshot = _tmux_session_snapshot(adapter, session_name)
    if snapshot is not None:
        return True
    return adapter.session_exists(session_name)


def _tmux_process_alive(adapter: SessionAdapter, session_name: str | None) -> bool | None:
    snapshot = _tmux_session_snapshot(adapter, session_name)
    if snapshot is None:
        return None
    return snapshot.process_alive


def _tmux_exit_status(adapter: SessionAdapter, session_name: str | None) -> int | None:
    snapshot = _tmux_session_snapshot(adapter, session_name)
    if snapshot is None:
        return None
    return snapshot.exit_status


def _session_snapshot(
    session: OrmSession,
    record: Session,
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
    recovery_classification: str | None = None,
    recommended_action: str | None = None,
    terminal_failure: dict[str, object] | None = None,
) -> DurableSessionSnapshot:
    version = session.get(NodeVersion, record.node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    run = None if record.node_run_id is None else session.get(NodeRun, record.node_run_id)
    latest_event = session.execute(
        select(SessionEvent).where(SessionEvent.session_id == record.id).order_by(SessionEvent.created_at.desc())
    ).scalars().first()
    event_count = session.execute(select(func.count()).select_from(SessionEvent).where(SessionEvent.session_id == record.id)).scalar_one()
    adapter_snapshot = None if record.tmux_session_name is None else adapter.describe(record.tmux_session_name)
    idle_seconds = None
    tmux_session_exists = None
    tmux_process_alive = None
    tmux_exit_status = None
    screen_state = None
    if adapter_snapshot is not None:
        tmux_process_alive = adapter_snapshot.process_alive
        tmux_exit_status = adapter_snapshot.exit_status
        if adapter_snapshot.process_alive:
            idle_seconds = poller.poll(adapter_snapshot.session_name).idle_seconds
            screen_state = _classify_session_screen_state(session, record, adapter=adapter, poller=poller, persist=False).to_payload()
        tmux_session_exists = True
    elif record.tmux_session_name is not None:
        tmux_session_exists = adapter.session_exists(record.tmux_session_name)
    if recovery_classification is None and record.session_role == "primary" and record.node_run_id is not None and run is not None:
        state = _require_run_state(session, run.id)
        active_sessions = _active_primary_sessions(session, run.id)
        recovery_status = _recovery_status_snapshot(
            session,
            logical_node_id=version.logical_node_id,
            version=version,
            run=run,
            state=state,
            active_sessions=active_sessions,
            adapter=adapter,
            poller=poller,
        )
        recovery_classification = recovery_status.recovery_classification
        recommended_action = recovery_status.recommended_action
    return DurableSessionSnapshot(
        session_id=record.id,
        logical_node_id=version.logical_node_id,
        node_version_id=record.node_version_id,
        node_run_id=record.node_run_id,
        node_kind=version.node_kind,
        node_title=version.title,
        run_status=None if run is None else run.run_status,
        session_role=record.session_role,
        provider=record.provider,
        provider_session_id=record.provider_session_id,
        tmux_session_name=record.tmux_session_name,
        cwd=record.cwd,
        status=record.status,
        started_at=record.started_at.isoformat(),
        last_heartbeat_at=None if record.last_heartbeat_at is None else record.last_heartbeat_at.isoformat(),
        ended_at=None if record.ended_at is None else record.ended_at.isoformat(),
        event_count=int(event_count),
        latest_event_type=None if latest_event is None else latest_event.event_type,
        backend=adapter.backend_name,
        pane_text=None if adapter_snapshot is None else adapter.capture_pane(adapter_snapshot.session_name, include_alt_screen=True),
        idle_seconds=idle_seconds,
        in_alt_screen=None if adapter_snapshot is None else adapter_snapshot.in_alt_screen,
        tmux_session_exists=tmux_session_exists,
        tmux_process_alive=tmux_process_alive,
        tmux_exit_status=tmux_exit_status,
        attach_command=None if adapter.backend_name != "tmux" or record.tmux_session_name is None else f"tmux attach-session -t {record.tmux_session_name}",
        screen_state=screen_state,
        recovery_classification=recovery_classification,
        recommended_action=recommended_action,
        terminal_failure=terminal_failure,
    )
