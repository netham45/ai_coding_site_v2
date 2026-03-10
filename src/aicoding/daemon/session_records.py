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
from aicoding.daemon.session_manager import build_primary_session_plan, build_recovery_primary_session_plan
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.db.models import HierarchyNode, LogicalNodeCurrentVersion, NodeChild, NodeRun, NodeRunState, NodeVersion, Session, SessionEvent, SubtaskAttempt
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import HierarchyRegistry
from aicoding.project_policies import resolve_effective_policy
from aicoding.resources import ResourceCatalog
from aicoding.rendering import build_render_context, render_text

ACTIVE_SESSION_STATUSES = {"BOUND", "ATTACHED", "RESUMED", "RUNNING"}
RECOVERABLE_SESSION_CLASSIFICATIONS = {
    "healthy",
    "detached",
    "stale_but_recoverable",
    "lost",
    "missing",
    "ambiguous",
    "non_resumable",
}
CODEX_WORKSPACE_TRUST_PROMPT = "Do you trust the contents of this directory?"
CODEX_WORKSPACE_TRUST_ACCEPT_MARKER = "1. Yes, continue"
_ACTIVE_WORK_MARKERS = (
    "• Working (",
    "Working (",
    "Messages to be submitted after next tool call",
)


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
    attach_command: str | None
    screen_state: dict[str, object] | None = None
    recovery_classification: str | None = None
    recommended_action: str | None = None

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
            "attach_command": self.attach_command,
            "screen_state": self.screen_state,
            "recovery_classification": self.recovery_classification,
            "recommended_action": self.recommended_action,
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
    provider: str | None
    provider_session_id_present: bool
    heartbeat_age_seconds: float | None
    duplicate_active_primary_sessions: int

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
            "provider": self.provider,
            "provider_session_id_present": self.provider_session_id_present,
            "heartbeat_age_seconds": self.heartbeat_age_seconds,
            "duplicate_active_primary_sessions": self.duplicate_active_primary_sessions,
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


def show_current_primary_session(
    session_factory: sessionmaker[OrmSession],
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot | None:
    with query_session_scope(session_factory) as session:
        current = session.execute(
            select(Session)
            .where(Session.session_role == "primary", Session.status.in_(ACTIVE_SESSION_STATUSES))
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
            if current.tmux_session_name and adapter.session_exists(current.tmux_session_name):
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
            _invalidate_session(session, current, status="LOST", reason="tmux_session_missing")

        durable_id = uuid4()
        launch_plan = build_primary_session_plan(
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
            },
        )
        _accept_codex_workspace_trust_prompt(
            session,
            durable_id=durable.id,
            adapter=adapter,
            session_name=launch_plan.session_name,
        )
        session.flush()
        return _session_snapshot(session, durable, adapter=adapter, poller=poller)


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
            if current.tmux_session_name and adapter.session_exists(current.tmux_session_name):
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
            _invalidate_session(session, current, status="LOST", reason="attach_missing_session")

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
        run = _require_active_run(session, version.id)
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
        run = _require_active_run(session, version.id)
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
        durable_id = uuid4()
        launch_plan = build_recovery_primary_session_plan(
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
            },
        )
        _accept_codex_workspace_trust_prompt(
            session,
            durable_id=durable.id,
            adapter=adapter,
            session_name=launch_plan.session_name,
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
        run = _require_active_run(session, version.id)
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
        if current.tmux_session_name is None or not adapter.session_exists(current.tmux_session_name):
            _record_session_event(session, current.id, "nudge_skipped", {"reason": "session_missing"})
            session.flush()
            return SessionNudgeSnapshot(
                node_id=logical_node_id,
                session_id=current.id,
                status="session_missing",
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
        nudge_count = _nudge_event_count(session, current.id)
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
        prompt_text = _render_recovery_prompt(idle_nudge_text, logical_node_id=logical_node_id)
        if nudge_count + 1 >= max_nudge_count:
            prompt_relative_path = "recovery/repeated_missed_step.md"
            prompt_text = _render_recovery_prompt(repeated_nudge_text, logical_node_id=logical_node_id)
        adapter.send_input(current.tmux_session_name, prompt_text, press_enter=True)
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
                    NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED")),
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
        except (DaemonConflictError, DaemonNotFoundError):
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


def auto_bind_ready_child_runs(
    session_factory: sessionmaker[OrmSession],
    *,
    hierarchy_registry: HierarchyRegistry,
    resources: ResourceCatalog,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> list[AutoStartedChildSnapshot]:
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


def get_session_for_node(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> DurableSessionSnapshot:
    with query_session_scope(session_factory) as session:
        version = _authoritative_version(session, logical_node_id)
        run = _require_active_run(session, version.id)
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


def _require_active_run(session: OrmSession, node_version_id: UUID):
    run = session.execute(
        select(NodeRun).where(NodeRun.node_version_id == node_version_id, NodeRun.run_status.in_(("PENDING", "RUNNING", "PAUSED"))).order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if run is None:
        raise DaemonConflictError("active durable run not found")
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


def _require_single_active_primary_session(session: OrmSession, node_run_id: UUID) -> Session | None:
    active_sessions = _active_primary_sessions(session, node_run_id)
    if len(active_sessions) > 1:
        raise DaemonConflictError("duplicate active primary sessions detected")
    return active_sessions[0] if active_sessions else None


def _nudge_event_count(session: OrmSession, session_id: UUID) -> int:
    count = session.execute(
        select(func.count()).select_from(SessionEvent).where(SessionEvent.session_id == session_id, SessionEvent.event_type == "nudged")
    ).scalar_one()
    return int(count)


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


def _accept_codex_workspace_trust_prompt(
    session: OrmSession,
    *,
    durable_id: UUID,
    adapter: SessionAdapter,
    session_name: str,
) -> None:
    if adapter.backend_name != "tmux" or not adapter.session_exists(session_name):
        return
    deadline = time.time() + 12.0
    while time.time() < deadline:
        pane_text = adapter.capture_pane(session_name, include_alt_screen=True)
        if CODEX_WORKSPACE_TRUST_PROMPT not in pane_text or CODEX_WORKSPACE_TRUST_ACCEPT_MARKER not in pane_text:
            time.sleep(0.25)
            continue
        adapter.send_input(session_name, "1", press_enter=True)
        _record_session_event(
            session,
            durable_id,
            "workspace_trust_prompt_accepted",
            {
                "tmux_session_name": session_name,
                "prompt_text": CODEX_WORKSPACE_TRUST_PROMPT,
            },
        )
        return


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
        session.flush()


def _pane_active_work_marker(pane_text: str) -> str | None:
    for marker in _ACTIVE_WORK_MARKERS:
        if marker in pane_text:
            return marker
    return None


def _render_recovery_prompt(template_text: str, *, logical_node_id: UUID) -> str:
    context = build_render_context(
        scopes={
            "node": {"id": str(logical_node_id)},
            "compat": {"node_id": str(logical_node_id)},
        }
    )
    return render_text(template_text, context=context, field_name="prompt").rendered_text


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
            provider=None if current is None else current.provider,
            provider_session_id_present=False if current is None else current.provider_session_id is not None,
            heartbeat_age_seconds=_heartbeat_age_seconds(current),
            duplicate_active_primary_sessions=duplicate_count,
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
            tmux_session_exists=None if current is None or current.tmux_session_name is None else adapter.session_exists(current.tmux_session_name),
            provider=None if current is None else current.provider,
            provider_session_id_present=False if current is None else current.provider_session_id is not None,
            heartbeat_age_seconds=_heartbeat_age_seconds(current),
            duplicate_active_primary_sessions=duplicate_count,
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
            provider=None,
            provider_session_id_present=False,
            heartbeat_age_seconds=None,
            duplicate_active_primary_sessions=0,
        )
    tmux_exists = current.tmux_session_name is not None and adapter.session_exists(current.tmux_session_name)
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
            provider=current.provider,
            provider_session_id_present=current.provider_session_id is not None,
            heartbeat_age_seconds=heartbeat_age,
            duplicate_active_primary_sessions=duplicate_count,
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
            provider=current.provider,
            provider_session_id_present=current.provider_session_id is not None,
            heartbeat_age_seconds=heartbeat_age,
            duplicate_active_primary_sessions=duplicate_count,
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
        provider=current.provider,
        provider_session_id_present=current.provider_session_id is not None,
        heartbeat_age_seconds=heartbeat_age,
        duplicate_active_primary_sessions=duplicate_count,
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
    tmux_session_exists = None if tmux_session_name is None else adapter.session_exists(tmux_session_name)
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
        if provider_session_exists and (current.tmux_session_name != current.provider_session_id or tmux_session_exists is False):
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


def _session_snapshot(
    session: OrmSession,
    record: Session,
    *,
    adapter: SessionAdapter,
    poller: SessionPoller,
    recovery_classification: str | None = None,
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
    screen_state = None
    recommended_action = None
    if adapter_snapshot is not None:
        idle_seconds = poller.poll(adapter_snapshot.session_name).idle_seconds
        tmux_session_exists = True
        screen_state = _classify_session_screen_state(session, record, adapter=adapter, poller=poller, persist=False).to_payload()
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
        attach_command=None if adapter.backend_name != "tmux" or record.tmux_session_name is None else f"tmux attach-session -t {record.tmux_session_name}",
        screen_state=screen_state,
        recovery_classification=recovery_classification,
        recommended_action=recommended_action,
    )
