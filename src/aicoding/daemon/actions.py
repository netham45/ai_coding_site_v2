from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.materialization import inspect_child_reconciliation
from aicoding.daemon.operator_views import load_node_operator_summary, load_pause_state
from aicoding.daemon.rebuild_coordination import inspect_rebuild_coordination
from aicoding.daemon.session_harness import SessionAdapter, SessionPoller
from aicoding.daemon.session_records import load_provider_recovery_status, load_recovery_status
from aicoding.resources import ResourceCatalog


@dataclass(frozen=True, slots=True)
class NodeActionSnapshot:
    action_id: str
    label: str
    group: str
    legal: bool
    blocked_reason: str | None
    confirmation_mode: str
    confirmation_label: str
    target_scope: str
    details_json: dict[str, object]

    def to_payload(self) -> dict[str, object]:
        return {
            "action_id": self.action_id,
            "label": self.label,
            "group": self.group,
            "legal": self.legal,
            "blocked_reason": self.blocked_reason,
            "confirmation_mode": self.confirmation_mode,
            "confirmation_label": self.confirmation_label,
            "target_scope": self.target_scope,
            "details_json": self.details_json,
        }


@dataclass(frozen=True, slots=True)
class NodeActionCatalogSnapshot:
    node_id: UUID
    node_version_id: UUID | None
    actions: list[NodeActionSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_version_id": None if self.node_version_id is None else str(self.node_version_id),
            "actions": [item.to_payload() for item in self.actions],
        }


def list_node_actions(
    session_factory: sessionmaker[Session],
    resources: ResourceCatalog,
    *,
    logical_node_id: UUID,
    adapter: SessionAdapter | None = None,
    poller: SessionPoller | None = None,
) -> NodeActionCatalogSnapshot:
    summary = load_node_operator_summary(session_factory, node_id=logical_node_id)
    pause_state = load_pause_state(session_factory, node_id=logical_node_id)
    recovery_status = None
    provider_status = None
    if adapter is not None and poller is not None:
        try:
            recovery_status = load_recovery_status(session_factory, logical_node_id=logical_node_id, adapter=adapter, poller=poller)
        except (DaemonConflictError, DaemonNotFoundError):
            recovery_status = None
        try:
            provider_status = load_provider_recovery_status(session_factory, logical_node_id=logical_node_id, adapter=adapter, poller=poller)
        except (DaemonConflictError, DaemonNotFoundError):
            provider_status = None

    actions: list[NodeActionSnapshot] = []

    can_start = summary.run_status not in {"RUNNING"}
    actions.append(
        NodeActionSnapshot(
            action_id="start_run",
            label="Start Run",
            group="execution",
            legal=can_start,
            blocked_reason=None if can_start else "node already has a running run",
            confirmation_mode="inline",
            confirmation_label="start run",
            target_scope="selected_node",
            details_json={"run_status": summary.run_status},
        )
    )

    can_pause = summary.run_status == "RUNNING"
    actions.append(
        NodeActionSnapshot(
            action_id="pause_run",
            label="Pause Run",
            group="execution",
            legal=can_pause,
            blocked_reason=None if can_pause else "node is not currently running",
            confirmation_mode="inline",
            confirmation_label="pause run",
            target_scope="selected_node",
            details_json={"run_status": summary.run_status},
        )
    )

    can_resume = bool(summary.is_resumable)
    actions.append(
        NodeActionSnapshot(
            action_id="resume_run",
            label="Resume Run",
            group="execution",
            legal=can_resume,
            blocked_reason=None if can_resume else "node does not currently expose a resumable pause state",
            confirmation_mode="inline",
            confirmation_label="resume run",
            target_scope="selected_node",
            details_json=pause_state.to_payload(),
        )
    )

    attach_recommended = recovery_status is not None and recovery_status.recommended_action == "attach_existing_session"
    actions.append(
        NodeActionSnapshot(
            action_id="session_attach",
            label="Attach Session",
            group="sessions",
            legal=attach_recommended,
            blocked_reason=None if attach_recommended else "session attach is not the current daemon-recommended recovery action",
            confirmation_mode="inline",
            confirmation_label="attach session",
            target_scope="selected_node",
            details_json={} if recovery_status is None else recovery_status.to_payload(),
        )
    )

    resume_recommended = recovery_status is not None and recovery_status.recommended_action == "resume_existing_session"
    actions.append(
        NodeActionSnapshot(
            action_id="session_resume",
            label="Resume Session",
            group="sessions",
            legal=resume_recommended,
            blocked_reason=None if resume_recommended else "session resume is not the current daemon-recommended recovery action",
            confirmation_mode="inline",
            confirmation_label="resume session",
            target_scope="selected_node",
            details_json={} if recovery_status is None else recovery_status.to_payload(),
        )
    )

    provider_resume_recommended = (
        provider_status is not None and provider_status.provider_recommended_action == "rebind_provider_session"
    )
    actions.append(
        NodeActionSnapshot(
            action_id="session_provider_resume",
            label="Resume Provider Session",
            group="sessions",
            legal=provider_resume_recommended,
            blocked_reason=None if provider_resume_recommended else "provider-specific resume is not currently recommended",
            confirmation_mode="inline",
            confirmation_label="resume provider session",
            target_scope="selected_node",
            details_json={} if provider_status is None else provider_status.to_payload(),
        )
    )

    try:
        reconciliation = inspect_child_reconciliation(session_factory, resources, logical_node_id=logical_node_id)
    except (DaemonConflictError, DaemonNotFoundError):
        reconciliation = None
    if reconciliation is not None and reconciliation.available_decisions:
        for decision in reconciliation.available_decisions:
            legal = reconciliation.materialization_status == "reconciliation_required"
            actions.append(
                NodeActionSnapshot(
                    action_id=f"reconcile_children:{decision}",
                    label=f"Reconcile Children: {decision.replace('_', ' ')}",
                    group="hierarchy",
                    legal=legal,
                    blocked_reason=None if legal else "child reconciliation is not currently required",
                    confirmation_mode="inline",
                    confirmation_label=decision.replace("_", " "),
                    target_scope="selected_node",
                    details_json=reconciliation.to_payload(),
                )
            )
    else:
        actions.append(
            NodeActionSnapshot(
                action_id="reconcile_children:noop",
                label="Reconcile Children",
                group="hierarchy",
                legal=False,
                blocked_reason="child reconciliation is not currently required",
                confirmation_mode="inline",
                confirmation_label="reconcile children",
                target_scope="selected_node",
                details_json={},
            )
        )

    coordination = inspect_rebuild_coordination(session_factory, logical_node_id=logical_node_id, scope="subtree")
    can_regenerate = coordination.status == "clear"
    actions.append(
        NodeActionSnapshot(
            action_id="regenerate_node",
            label="Regenerate Node",
            group="execution",
            legal=can_regenerate,
            blocked_reason=None if can_regenerate else "live runtime state blocks subtree rebuild; inspect rebuild coordination",
            confirmation_mode="inline",
            confirmation_label="regenerate node",
            target_scope="selected_node",
            details_json=coordination.to_payload(),
        )
    )

    return NodeActionCatalogSnapshot(
        node_id=logical_node_id,
        node_version_id=summary.authoritative_node_version_id,
        actions=actions,
    )
