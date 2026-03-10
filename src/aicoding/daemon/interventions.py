from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.git_conflicts import list_merge_conflicts_for_node, resolve_merge_conflict
from aicoding.daemon.live_git import abort_live_merge
from aicoding.daemon.materialization import inspect_child_reconciliation, reconcile_child_authority
from aicoding.daemon.operator_views import load_pause_state
from aicoding.daemon.rebuild_coordination import inspect_cutover_readiness
from aicoding.daemon.run_orchestration import approve_paused_run
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.daemon.session_records import load_recovery_status, recover_primary_session
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.db.models import LogicalNodeCurrentVersion, NodeLifecycleState, NodeVersion
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog


@dataclass(frozen=True, slots=True)
class InterventionOptionSnapshot:
    action: str
    requires_summary: bool
    label: str

    def to_payload(self) -> dict[str, object]:
        return {
            "action": self.action,
            "requires_summary": self.requires_summary,
            "label": self.label,
        }


@dataclass(frozen=True, slots=True)
class InterventionSnapshot:
    kind: str
    status: str
    subject_key: str
    title: str
    summary: str | None
    recommended_action: str | None
    available_actions: list[InterventionOptionSnapshot]
    details_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "status": self.status,
            "subject_key": self.subject_key,
            "title": self.title,
            "summary": self.summary,
            "recommended_action": self.recommended_action,
            "available_actions": [item.to_payload() for item in self.available_actions],
            "details_json": self.details_json,
        }


@dataclass(frozen=True, slots=True)
class InterventionCatalogSnapshot:
    node_id: UUID
    node_version_id: UUID
    pending_count: int
    interventions: list[InterventionSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "pending_count": self.pending_count,
            "interventions": [item.to_payload() for item in self.interventions],
        }


@dataclass(frozen=True, slots=True)
class InterventionActionSnapshot:
    node_id: UUID
    node_version_id: UUID
    intervention_kind: str
    action: str
    status: str
    result_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": str(self.node_version_id),
            "intervention_kind": self.intervention_kind,
            "action": self.action,
            "status": self.status,
            "result_json": self.result_json,
        }


def list_node_interventions(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter | None = None,
    poller: SessionPoller | None = None,
) -> InterventionCatalogSnapshot:
    version = _authoritative_version(session_factory, logical_node_id=logical_node_id)
    interventions: list[InterventionSnapshot] = []

    pause_state = load_pause_state(session_factory, node_id=logical_node_id)
    if pause_state.approval_required and not pause_state.approved and pause_state.pause_flag_name is not None:
        interventions.append(
            InterventionSnapshot(
                kind="pause_approval",
                status="pending",
                subject_key=f"pause:{pause_state.pause_flag_name}",
                title=f"Pause approval required for '{pause_state.pause_flag_name}'",
                summary=pause_state.pause_summary,
                recommended_action="approve_pause",
                available_actions=[
                    InterventionOptionSnapshot("approve_pause", requires_summary=False, label="Approve pause gate"),
                ],
                details_json=pause_state.to_payload(),
            )
        )

    try:
        reconciliation = inspect_child_reconciliation(session_factory, resources, logical_node_id=logical_node_id)
    except (DaemonConflictError, DaemonNotFoundError):
        reconciliation = None
    if reconciliation is not None and reconciliation.materialization_status == "reconciliation_required" and reconciliation.available_decisions:
        interventions.append(
            InterventionSnapshot(
                kind="child_reconciliation",
                status="pending",
                subject_key=f"reconciliation:{reconciliation.parent_node_version_id}",
                title="Child authority reconciliation required",
                summary=f"{reconciliation.authority_mode} child authority requires an explicit operator decision.",
                recommended_action=reconciliation.available_decisions[0],
                available_actions=[
                    InterventionOptionSnapshot(action, requires_summary=False, label=action.replace("_", " "))
                    for action in reconciliation.available_decisions
                ],
                details_json=reconciliation.to_payload(),
            )
        )

    for conflict in list_merge_conflicts_for_node(session_factory, logical_node_id=logical_node_id):
        if conflict.resolution_status != "unresolved":
            continue
        interventions.append(
            InterventionSnapshot(
                kind="merge_conflict",
                status="pending",
                subject_key=f"merge-conflict:{conflict.id}",
                title="Live merge conflict requires intervention",
                summary=f"Conflicted files: {', '.join(conflict.files_json)}",
                recommended_action="abort_merge",
                available_actions=[
                    InterventionOptionSnapshot("abort_merge", requires_summary=False, label="Abort live merge"),
                    InterventionOptionSnapshot("resolve_conflict", requires_summary=True, label="Mark conflict resolved"),
                ],
                details_json=conflict.to_payload(),
            )
        )

    if adapter is not None and poller is not None:
        try:
            recovery_status = load_recovery_status(session_factory, logical_node_id=logical_node_id, adapter=adapter, poller=poller)
        except (DaemonConflictError, DaemonNotFoundError):
            recovery_status = None
        if recovery_status is not None and recovery_status.recommended_action != "none":
            available_actions: list[InterventionOptionSnapshot] = []
            if recovery_status.recommended_action in {"attach_existing_session", "resume_existing_session"}:
                available_actions.append(
                    InterventionOptionSnapshot("resume_session", requires_summary=False, label="Resume or attach session")
                )
            interventions.append(
                InterventionSnapshot(
                    kind="session_recovery",
                    status="pending" if available_actions else "attention_required",
                    subject_key=f"recovery:{recovery_status.node_run_id}",
                    title="Session recovery requires operator attention",
                    summary=recovery_status.reason,
                    recommended_action="resume_session" if available_actions else None,
                    available_actions=available_actions,
                    details_json=recovery_status.to_payload(),
                )
            )

    latest_created_candidate_id = _latest_created_candidate_version_id(session_factory, logical_node_id=logical_node_id)
    if latest_created_candidate_id is not None:
        cutover = inspect_cutover_readiness(session_factory, version_id=latest_created_candidate_id)
        if cutover.status == "blocked":
            interventions.append(
                InterventionSnapshot(
                    kind="cutover_review",
                    status="attention_required",
                    subject_key=f"cutover:{cutover.node_version_id}",
                    title="Candidate cutover is blocked",
                    summary="Candidate version is not yet ready for cutover.",
                    recommended_action=None,
                    available_actions=[],
                    details_json=cutover.to_payload(),
                )
            )

    return InterventionCatalogSnapshot(
        node_id=logical_node_id,
        node_version_id=version.id,
        pending_count=sum(1 for item in interventions if item.status == "pending"),
        interventions=interventions,
    )


def apply_node_intervention(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
    intervention_kind: str,
    action: str,
    summary: str | None = None,
    conflict_id: UUID | None = None,
    pause_flag_name: str | None = None,
    adapter: SessionAdapter | None = None,
    poller: SessionPoller | None = None,
) -> InterventionActionSnapshot:
    version = _authoritative_version(session_factory, logical_node_id=logical_node_id)
    if intervention_kind == "pause_approval":
        if action != "approve_pause":
            raise DaemonConflictError(f"unsupported pause intervention action '{action}'")
        approve_paused_run(
            session_factory,
            logical_node_id=logical_node_id,
            pause_flag_name=pause_flag_name,
            approval_summary=summary,
        )
        result_json = load_pause_state(session_factory, node_id=logical_node_id).to_payload()
    elif intervention_kind == "child_reconciliation":
        result_json = reconcile_child_authority(
            session_factory,
            resources,
            logical_node_id=logical_node_id,
            decision=action,
        ).to_payload()
    elif intervention_kind == "merge_conflict":
        if action == "abort_merge":
            result_json = abort_live_merge(session_factory, logical_node_id=logical_node_id).to_payload()
        elif action == "resolve_conflict":
            if conflict_id is None:
                raise DaemonConflictError("resolve_conflict requires a conflict id")
            if not summary:
                raise DaemonConflictError("resolve_conflict requires a resolution summary")
            result_json = resolve_merge_conflict(
                session_factory,
                conflict_id=conflict_id,
                resolution_summary=summary,
            ).to_payload()
        else:
            raise DaemonConflictError(f"unsupported merge conflict action '{action}'")
    elif intervention_kind == "session_recovery":
        if action != "resume_session":
            raise DaemonConflictError(f"unsupported session recovery action '{action}'")
        if adapter is None or poller is None:
            raise DaemonConflictError("session recovery intervention requires a session adapter and poller")
        result_json = recover_primary_session(
            session_factory,
            logical_node_id=logical_node_id,
            adapter=adapter,
            poller=poller,
        ).to_payload()
    else:
        raise DaemonConflictError(f"unsupported intervention kind '{intervention_kind}'")

    _record_intervention_event(
        session_factory,
        logical_node_id=logical_node_id,
        intervention_kind=intervention_kind,
        action=action,
        summary=summary,
        conflict_id=conflict_id,
    )
    return InterventionActionSnapshot(
        node_id=logical_node_id,
        node_version_id=version.id,
        intervention_kind=intervention_kind,
        action=action,
        status="accepted",
        result_json=result_json,
    )


def _record_intervention_event(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    intervention_kind: str,
    action: str,
    summary: str | None,
    conflict_id: UUID | None,
) -> None:
    with session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=selector.authoritative_node_version_id,
            node_run_id=None if lifecycle is None else lifecycle.current_run_id,
            event_scope="intervention",
            event_type="intervention_applied",
            payload_json={
                "intervention_kind": intervention_kind,
                "action": action,
                "summary": summary,
                "conflict_id": None if conflict_id is None else str(conflict_id),
            },
        )
        session.flush()


def _authoritative_version(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> NodeVersion:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        version = session.get(NodeVersion, selector.authoritative_node_version_id)
        if version is None:
            raise DaemonNotFoundError("authoritative node version not found")
        return version


def _latest_created_candidate_version_id(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> UUID | None:
    with query_session_scope(session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
        if selector is None:
            raise DaemonNotFoundError("logical node version selector not found")
        latest = session.get(NodeVersion, selector.latest_created_node_version_id)
        if latest is None or latest.status != "candidate":
            return None
        if latest.id == selector.authoritative_node_version_id:
            return None
        return latest.id
