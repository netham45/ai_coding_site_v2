from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session as OrmSession, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.session_manager import build_child_session_plan
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.db.models import ChildSessionResult, NodeRunState, Session, SessionEvent
from aicoding.db.session import query_session_scope, session_scope


@dataclass(frozen=True, slots=True)
class ChildSessionSnapshot:
    session_id: UUID
    parent_session_id: UUID
    node_run_id: UUID
    node_version_id: UUID
    parent_compiled_subtask_id: UUID
    reason: str
    status: str
    tmux_session_name: str | None
    provider: str
    delegated_prompt_path: str
    pane_text: str | None
    idle_seconds: float | None
    in_alt_screen: bool | None
    started_at: str
    ended_at: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "session_id": str(self.session_id),
            "parent_session_id": str(self.parent_session_id),
            "node_run_id": str(self.node_run_id),
            "node_version_id": str(self.node_version_id),
            "parent_compiled_subtask_id": str(self.parent_compiled_subtask_id),
            "reason": self.reason,
            "status": self.status,
            "tmux_session_name": self.tmux_session_name,
            "provider": self.provider,
            "delegated_prompt_path": self.delegated_prompt_path,
            "pane_text": self.pane_text,
            "idle_seconds": self.idle_seconds,
            "in_alt_screen": self.in_alt_screen,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
        }


@dataclass(frozen=True, slots=True)
class ChildSessionResultSnapshot:
    child_session_id: UUID
    parent_compiled_subtask_id: UUID
    status: str
    summary: str
    findings: list[str]
    artifacts: list[dict[str, object]]
    suggested_next_actions: list[str]
    recorded_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "child_session_id": str(self.child_session_id),
            "parent_compiled_subtask_id": str(self.parent_compiled_subtask_id),
            "status": self.status,
            "summary": self.summary,
            "findings": self.findings,
            "artifacts": self.artifacts,
            "suggested_next_actions": self.suggested_next_actions,
            "recorded_at": self.recorded_at,
        }


def push_child_session(
    session_factory: sessionmaker[OrmSession],
    *,
    logical_node_id: UUID,
    reason: str,
    adapter: SessionAdapter,
    poller: SessionPoller,
    delegated_prompt_text: str,
    delegated_prompt_path: str,
) -> ChildSessionSnapshot:
    with session_scope(session_factory) as session:
        parent = _require_active_primary_session_bundle(session, logical_node_id)
        existing = session.execute(
            select(Session)
            .where(
                Session.parent_session_id == parent.id,
                Session.session_role == "pushed_child",
                Session.status.in_(("BOUND", "ATTACHED", "RUNNING", "RESUMED")),
            )
            .order_by(Session.started_at.desc())
        ).scalars().first()
        parent_state = _require_parent_state(session, parent.node_run_id)
        if parent_state.current_compiled_subtask_id is None:
            raise DaemonConflictError("parent compiled subtask not found")
        if existing is not None:
            event_payload = _child_push_event_payload(session, existing.id)
            return _child_session_snapshot(
                existing,
                reason=str(event_payload.get("reason", reason)),
                delegated_prompt_path=str(event_payload.get("delegated_prompt_path", delegated_prompt_path)),
                parent_compiled_subtask_id=UUID(str(event_payload.get("parent_compiled_subtask_id", parent_state.current_compiled_subtask_id))),
                adapter=adapter,
                poller=poller,
            )

        record_id = uuid4()
        launch_plan = build_child_session_plan(parent_session_id=parent.id, session_id=record_id)
        snapshot = adapter.create_session(
            launch_plan.session_name,
            launch_plan.command,
            launch_plan.working_directory,
            environment=launch_plan.environment,
        )
        adapter.send_input(launch_plan.session_name, delegated_prompt_text, press_enter=True)
        record = Session(
            id=record_id,
            node_version_id=parent.node_version_id,
            node_run_id=parent.node_run_id,
            session_role="pushed_child",
            parent_session_id=parent.id,
            provider=adapter.backend_name,
            provider_session_id=snapshot.session_name,
            tmux_session_name=snapshot.session_name,
            cwd=snapshot.working_directory,
            status="BOUND",
            started_at=snapshot.created_at,
            last_heartbeat_at=snapshot.last_activity_at,
        )
        session.add(record)
        session.flush()
        _record_session_event(
            session,
            record.id,
            "child_pushed",
            {
                "reason": reason,
                "parent_session_id": str(parent.id),
                "parent_compiled_subtask_id": str(parent_state.current_compiled_subtask_id),
                "delegated_prompt_path": delegated_prompt_path,
                "tmux_session_name": launch_plan.session_name,
                "launch_command": launch_plan.command,
                "cwd": launch_plan.working_directory,
                "attach_command": launch_plan.attach_command,
            },
        )
        session.flush()
        return _child_session_snapshot(
            record,
            reason=reason,
            delegated_prompt_path=delegated_prompt_path,
            parent_compiled_subtask_id=parent_state.current_compiled_subtask_id,
            adapter=adapter,
            poller=poller,
        )


def pop_child_session(
    session_factory: sessionmaker[OrmSession],
    *,
    child_session_id: UUID,
    result_payload: dict[str, object],
) -> ChildSessionResultSnapshot:
    with session_scope(session_factory) as session:
        child = session.get(Session, child_session_id)
        if child is None or child.session_role != "pushed_child":
            raise DaemonNotFoundError("child session not found")
        if child.parent_session_id is None or child.node_run_id is None:
            raise DaemonConflictError("child session is missing parent linkage")
        status = str(result_payload.get("status", "")).strip().lower()
        summary = str(result_payload.get("summary", "")).strip()
        if status not in {"success", "partial", "failed"}:
            raise DaemonConflictError("child session result status is invalid")
        if not summary:
            raise DaemonConflictError("child session summary is required")
        findings = _normalize_string_list(result_payload.get("findings"))
        suggested_next_actions = _normalize_string_list(result_payload.get("suggested_next_actions"))
        artifacts = _normalize_artifacts(result_payload.get("artifacts"))
        parent_state = _require_parent_state(session, child.node_run_id)
        if parent_state.current_compiled_subtask_id is None:
            raise DaemonConflictError("parent compiled subtask not found")

        durable = ChildSessionResult(
            id=uuid4(),
            child_session_id=child.id,
            parent_compiled_subtask_id=parent_state.current_compiled_subtask_id,
            status=status,
            result_json={
                "summary": summary,
                "findings": findings,
                "artifacts": artifacts,
                "suggested_next_actions": suggested_next_actions,
            },
        )
        session.add(durable)
        child.status = "COMPLETE"
        child.ended_at = datetime.now(timezone.utc)
        _record_session_event(
            session,
            child.id,
            "child_popped",
            {
                "status": status,
                "parent_compiled_subtask_id": str(parent_state.current_compiled_subtask_id),
            },
        )
        _attach_result_to_parent_context(
            session,
            node_run_id=child.node_run_id,
            parent_compiled_subtask_id=parent_state.current_compiled_subtask_id,
            payload={
                "child_session_id": str(child.id),
                "status": status,
                "summary": summary,
                "findings": findings,
                "artifacts": artifacts,
                "suggested_next_actions": suggested_next_actions,
            },
        )
        session.flush()
        return ChildSessionResultSnapshot(
            child_session_id=child.id,
            parent_compiled_subtask_id=parent_state.current_compiled_subtask_id,
            status=status,
            summary=summary,
            findings=findings,
            artifacts=artifacts,
            suggested_next_actions=suggested_next_actions,
            recorded_at=durable.created_at.isoformat(),
        )


def load_child_session_result(
    session_factory: sessionmaker[OrmSession],
    *,
    child_session_id: UUID,
) -> ChildSessionResultSnapshot:
    with query_session_scope(session_factory) as session:
        row = session.execute(
            select(ChildSessionResult).where(ChildSessionResult.child_session_id == child_session_id).order_by(ChildSessionResult.created_at.desc())
        ).scalars().first()
        if row is None:
            raise DaemonNotFoundError("child session result not found")
        payload = dict(row.result_json)
        return ChildSessionResultSnapshot(
            child_session_id=row.child_session_id,
            parent_compiled_subtask_id=row.parent_compiled_subtask_id,
            status=row.status,
            summary=str(payload.get("summary", "")),
            findings=_normalize_string_list(payload.get("findings")),
            artifacts=_normalize_artifacts(payload.get("artifacts")),
            suggested_next_actions=_normalize_string_list(payload.get("suggested_next_actions")),
            recorded_at=row.created_at.isoformat(),
        )


def _require_active_primary_session_bundle(session: OrmSession, logical_node_id: UUID) -> Session:
    from aicoding.db.models import LogicalNodeCurrentVersion, NodeVersion

    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    current = session.execute(
        select(Session)
        .where(
            Session.node_version_id == version.id,
            Session.session_role == "primary",
            Session.status.in_(("BOUND", "ATTACHED", "RESUMED", "RUNNING")),
        )
        .order_by(Session.started_at.desc())
    ).scalars().first()
    if current is None or current.node_run_id is None:
        raise DaemonConflictError("active primary session not found")
    return current


def _require_parent_state(session: OrmSession, node_run_id: UUID) -> NodeRunState:
    state = session.get(NodeRunState, node_run_id)
    if state is None:
        raise DaemonNotFoundError("parent run state not found")
    return state


def _attach_result_to_parent_context(
    session: OrmSession,
    *,
    node_run_id: UUID,
    parent_compiled_subtask_id: UUID,
    payload: dict[str, object],
) -> None:
    from aicoding.db.models import SubtaskAttempt

    latest_attempt = session.execute(
        select(SubtaskAttempt)
        .where(SubtaskAttempt.node_run_id == node_run_id, SubtaskAttempt.compiled_subtask_id == parent_compiled_subtask_id)
        .order_by(SubtaskAttempt.attempt_number.desc())
    ).scalars().first()
    state = _require_parent_state(session, node_run_id)
    if latest_attempt is not None:
        input_context = dict(latest_attempt.input_context_json or {})
        child_results = list(input_context.get("child_session_results", []))
        child_results.append(payload)
        input_context["child_session_results"] = child_results
        latest_attempt.input_context_json = input_context
    cursor = dict(state.execution_cursor_json or {})
    child_results = list(cursor.get("child_session_results", []))
    child_results.append(payload)
    cursor["child_session_results"] = child_results
    state.execution_cursor_json = cursor


def _record_session_event(session: OrmSession, session_id: UUID, event_type: str, payload: dict[str, object]) -> None:
    session.add(SessionEvent(id=uuid4(), session_id=session_id, event_type=event_type, payload_json=payload))


def _child_push_event_payload(session: OrmSession, session_id: UUID) -> dict[str, object]:
    row = session.execute(
        select(SessionEvent).where(SessionEvent.session_id == session_id, SessionEvent.event_type == "child_pushed").order_by(SessionEvent.created_at.desc())
    ).scalars().first()
    if row is None:
        return {}
    return dict(row.payload_json)


def _child_session_snapshot(
    record: Session,
    *,
    reason: str,
    delegated_prompt_path: str,
    parent_compiled_subtask_id: UUID,
    adapter: SessionAdapter,
    poller: SessionPoller,
) -> ChildSessionSnapshot:
    adapter_snapshot = None if record.tmux_session_name is None else adapter.describe(record.tmux_session_name)
    idle_seconds = None if adapter_snapshot is None else poller.poll(adapter_snapshot.session_name).idle_seconds
    if record.parent_session_id is None or record.node_run_id is None:
        raise DaemonConflictError("child session is missing parent linkage")
    return ChildSessionSnapshot(
        session_id=record.id,
        parent_session_id=record.parent_session_id,
        node_run_id=record.node_run_id,
        node_version_id=record.node_version_id,
        parent_compiled_subtask_id=parent_compiled_subtask_id,
        reason=reason,
        status=record.status,
        tmux_session_name=record.tmux_session_name,
        provider=record.provider,
        delegated_prompt_path=delegated_prompt_path,
        pane_text=None if adapter_snapshot is None else adapter.capture_pane(adapter_snapshot.session_name, include_alt_screen=True),
        idle_seconds=idle_seconds,
        in_alt_screen=None if adapter_snapshot is None else adapter_snapshot.in_alt_screen,
        started_at=record.started_at.isoformat(),
        ended_at=None if record.ended_at is None else record.ended_at.isoformat(),
    )


def _normalize_string_list(value: object | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DaemonConflictError("child session result list field is invalid")
    normalized = [str(item).strip() for item in value if str(item).strip()]
    return normalized


def _normalize_artifacts(value: object | None) -> list[dict[str, object]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise DaemonConflictError("child session artifacts field is invalid")
    artifacts: list[dict[str, object]] = []
    for item in value:
        if not isinstance(item, dict):
            raise DaemonConflictError("child session artifact entry is invalid")
        path = str(item.get("path", "")).strip()
        artifact_type = str(item.get("type", "")).strip()
        if not path or not artifact_type:
            raise DaemonConflictError("child session artifact entry is incomplete")
        artifacts.append({"path": path, "type": artifact_type})
    return artifacts
