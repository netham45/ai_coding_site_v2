from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, text
from sqlalchemy.orm import Session, sessionmaker

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.regeneration import regenerate_node_and_descendants
from aicoding.daemon.run_orchestration import _pause_run, _sync_lifecycle_with_run
from aicoding.daemon.workflow_events import record_workflow_event
from aicoding.db.models import (
    CompiledWorkflow,
    DaemonMutationEvent,
    DaemonNodeState,
    HierarchyNode,
    LogicalNodeCurrentVersion,
    NodeChild,
    NodeLifecycleState,
    NodeRun,
    NodeRunChildFailureCounter,
    NodeRunState,
    NodeVersion,
    SubtaskAttempt,
    WorkflowEvent,
)
from aicoding.db.session import query_session_scope, session_scope
from aicoding.resources import ResourceCatalog

PARENT_DECISION_TYPES = {
    "retry_child": "parent_retry_child",
    "regenerate_child": "parent_regenerate_child",
    "replan_parent": "parent_replan",
    "pause_for_user": "parent_pause_for_user",
}


@dataclass(frozen=True, slots=True)
class ParentFailurePolicySnapshot:
    total_threshold: int
    consecutive_threshold: int
    per_child_threshold: int

    def to_payload(self) -> dict[str, int]:
        return {
            "total_threshold": self.total_threshold,
            "consecutive_threshold": self.consecutive_threshold,
            "per_child_threshold": self.per_child_threshold,
        }


@dataclass(frozen=True, slots=True)
class ChildFailureContext:
    child_node_id: UUID
    child_node_version_id: UUID
    child_run_id: UUID
    child_title: str
    child_kind: str
    classification: str
    classification_reason: str
    failure_origin: str
    summary: str
    source_subtask_key: str | None
    failed_attempt_number: int | None


@dataclass(frozen=True, slots=True)
class ChildFailureCounterSnapshot:
    child_node_id: UUID
    child_node_version_id: UUID
    child_title: str
    child_kind: str
    failure_count: int
    last_failure_at: str | None
    last_failure_class: str | None
    last_failure_summary: str | None
    last_failure_subtask_key: str | None
    last_failed_node_run_id: UUID | None
    last_decision_type: str | None
    last_decision_at: str | None

    def to_payload(self) -> dict[str, object]:
        return {
            "child_node_id": str(self.child_node_id),
            "child_node_version_id": str(self.child_node_version_id),
            "child_title": self.child_title,
            "child_kind": self.child_kind,
            "failure_count": self.failure_count,
            "last_failure_at": self.last_failure_at,
            "last_failure_class": self.last_failure_class,
            "last_failure_summary": self.last_failure_summary,
            "last_failure_subtask_key": self.last_failure_subtask_key,
            "last_failed_node_run_id": None if self.last_failed_node_run_id is None else str(self.last_failed_node_run_id),
            "last_decision_type": self.last_decision_type,
            "last_decision_at": self.last_decision_at,
        }


@dataclass(frozen=True, slots=True)
class ChildFailureCatalogSnapshot:
    node_id: UUID
    node_run_id: UUID | None
    failure_count_from_children: int
    failure_count_consecutive: int
    counters: list[ChildFailureCounterSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "failure_count_from_children": self.failure_count_from_children,
            "failure_count_consecutive": self.failure_count_consecutive,
            "counters": [item.to_payload() for item in self.counters],
        }


@dataclass(frozen=True, slots=True)
class ParentDecisionSnapshot:
    id: UUID
    node_id: UUID
    node_version_id: UUID | None
    node_run_id: UUID | None
    child_node_id: UUID | None
    child_node_version_id: UUID | None
    child_node_run_id: UUID | None
    failure_class: str | None
    failure_origin: str | None
    decision_type: str
    decision_source: str | None
    decision_reason: str | None
    options_considered: list[str]
    threshold_triggered: bool
    threshold_reason: str | None
    summary: str | None
    payload_json: dict[str, object]
    created_at: str

    def to_payload(self) -> dict[str, object]:
        return {
            "id": str(self.id),
            "node_id": str(self.node_id),
            "node_version_id": None if self.node_version_id is None else str(self.node_version_id),
            "node_run_id": None if self.node_run_id is None else str(self.node_run_id),
            "child_node_id": None if self.child_node_id is None else str(self.child_node_id),
            "child_node_version_id": None if self.child_node_version_id is None else str(self.child_node_version_id),
            "child_node_run_id": None if self.child_node_run_id is None else str(self.child_node_run_id),
            "failure_class": self.failure_class,
            "failure_origin": self.failure_origin,
            "decision_type": self.decision_type,
            "decision_source": self.decision_source,
            "decision_reason": self.decision_reason,
            "options_considered": self.options_considered,
            "threshold_triggered": self.threshold_triggered,
            "threshold_reason": self.threshold_reason,
            "summary": self.summary,
            "payload_json": self.payload_json,
            "created_at": self.created_at,
        }


@dataclass(frozen=True, slots=True)
class ParentDecisionCatalogSnapshot:
    node_id: UUID
    decisions: list[ParentDecisionSnapshot]

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "decisions": [item.to_payload() for item in self.decisions],
        }


@dataclass(frozen=True, slots=True)
class ParentFailureDecisionResult:
    node_id: UUID
    node_run_id: UUID
    child_node_id: UUID
    child_node_version_id: UUID
    child_node_run_id: UUID
    failure_class: str
    failure_origin: str
    decision_type: str
    decision_source: str
    decision_reason: str
    options_considered: list[str]
    threshold_triggered: bool
    threshold_reason: str | None
    policy_snapshot: ParentFailurePolicySnapshot
    summary: str
    parent_lifecycle_state: str
    parent_run_status: str
    child_lifecycle_state: str
    post_action_status: str | None
    counters: ChildFailureCatalogSnapshot

    def to_payload(self) -> dict[str, object]:
        return {
            "node_id": str(self.node_id),
            "node_run_id": str(self.node_run_id),
            "child_node_id": str(self.child_node_id),
            "child_node_version_id": str(self.child_node_version_id),
            "child_node_run_id": str(self.child_node_run_id),
            "failure_class": self.failure_class,
            "failure_origin": self.failure_origin,
            "decision_type": self.decision_type,
            "decision_source": self.decision_source,
            "decision_reason": self.decision_reason,
            "options_considered": self.options_considered,
            "threshold_triggered": self.threshold_triggered,
            "threshold_reason": self.threshold_reason,
            "policy_snapshot": self.policy_snapshot.to_payload(),
            "summary": self.summary,
            "parent_lifecycle_state": self.parent_lifecycle_state,
            "parent_run_status": self.parent_run_status,
            "child_lifecycle_state": self.child_lifecycle_state,
            "post_action_status": self.post_action_status,
            "counters": self.counters.to_payload(),
        }


def list_child_failure_counters(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> ChildFailureCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        return _child_failure_catalog_from_session(session, logical_node_id=logical_node_id)


def list_parent_decision_history(session_factory: sessionmaker[Session], *, logical_node_id: UUID) -> ParentDecisionCatalogSnapshot:
    with query_session_scope(session_factory) as session:
        rows = session.execute(
            select(WorkflowEvent)
            .where(
                WorkflowEvent.logical_node_id == logical_node_id,
                WorkflowEvent.event_scope == "parent_decision",
            )
            .order_by(WorkflowEvent.created_at, WorkflowEvent.id)
        ).scalars().all()
        return ParentDecisionCatalogSnapshot(
            node_id=logical_node_id,
            decisions=[_decision_snapshot(row) for row in rows],
        )


def handle_child_failure_at_parent(
    session_factory: sessionmaker[Session],
    *,
    logical_node_id: UUID,
    child_node_id: UUID,
    requested_action: str | None = None,
    catalog: ResourceCatalog | None = None,
) -> ParentFailureDecisionResult:
    post_action_status: str | None = None
    if requested_action is not None and requested_action not in PARENT_DECISION_TYPES:
        raise DaemonConflictError(f"unsupported parent decision action '{requested_action}'")
    with session_scope(session_factory) as session:
        parent_version = _authoritative_version(session, logical_node_id)
        parent_run, parent_state = _active_parent_run(session, logical_node_id, parent_version.id)
        child_failure = _load_child_failure_context(session, parent_node_version_id=parent_version.id, child_node_id=child_node_id)
        counter_row = _increment_child_failure_counter(
            session,
            node_run_id=parent_run.id,
            child_failure=child_failure,
        )
        parent_state.failure_count_from_children += 1
        parent_state.failure_count_consecutive += 1
        policy = _parent_failure_policy(session, parent_version)
        decision_source = "override" if requested_action is not None else "auto"
        evaluation = _evaluate_parent_decision(
            child_failure=child_failure,
            counter_row=counter_row,
            parent_state=parent_state,
            policy=policy,
            requested_action=requested_action,
        )
        decision_type = str(evaluation["decision_type"])
        summary = _build_parent_decision_summary(
            parent_node_id=logical_node_id,
            child_failure=child_failure,
            evaluation=evaluation,
            counter_row=counter_row,
            parent_state=parent_state,
            policy=policy,
        )
        payload = {
            "child_node_id": str(child_failure.child_node_id),
            "child_node_version_id": str(child_failure.child_node_version_id),
            "child_node_run_id": str(child_failure.child_run_id),
            "failure_class": child_failure.classification,
            "failure_origin": child_failure.failure_origin,
            "classification_reason": child_failure.classification_reason,
            "failure_summary": child_failure.summary,
            "failure_count_for_child": counter_row.failure_count,
            "failure_count_total": parent_state.failure_count_from_children,
            "failure_count_consecutive": parent_state.failure_count_consecutive,
            "decision_type": decision_type,
            "decision_source": decision_source,
            "decision_reason": evaluation["decision_reason"],
            "options_considered": evaluation["options_considered"],
            "threshold_triggered": evaluation["threshold_triggered"],
            "threshold_reason": evaluation["threshold_reason"],
            "policy_snapshot": policy.to_payload(),
            "summary": summary,
        }
        if decision_type in {"replan_parent", "pause_for_user"}:
            _pause_run(
                session,
                logical_node_id=logical_node_id,
                run=parent_run,
                state=parent_state,
                node_version_id=parent_version.id,
                pause_flag_name="parent_replan_required" if decision_type == "replan_parent" else "parent_child_failure_pause",
                pause_summary=summary,
                approval_required=True,
                pause_summary_prompt=(
                    "runtime/parent_local_replan.md" if decision_type == "replan_parent" else "runtime/parent_pause_for_user.md"
                ),
            )
            post_action_status = "parent_paused"
        elif decision_type == "retry_child":
            _reset_child_after_failure(session, child_node_id=child_node_id)
            post_action_status = "child_ready_for_retry"
        counter_row.last_decision_type = decision_type
        counter_row.last_decision_at = datetime.now(timezone.utc)
        record_workflow_event(
            session,
            logical_node_id=logical_node_id,
            node_version_id=parent_version.id,
            node_run_id=parent_run.id,
            event_scope="parent_decision",
            event_type=PARENT_DECISION_TYPES[decision_type],
            payload_json=payload,
        )
        _sync_lifecycle_with_run(session, logical_node_id=logical_node_id, run=parent_run, state=parent_state)
        session.flush()
        child_lifecycle = session.get(NodeLifecycleState, str(child_node_id))
        parent_lifecycle_state = parent_state.lifecycle_state
        parent_run_status = parent_run.run_status
        child_lifecycle_state = "UNKNOWN" if child_lifecycle is None else child_lifecycle.lifecycle_state
        counters = _child_failure_catalog_from_session(session, logical_node_id=logical_node_id)
    if requested_action == "regenerate_child" or (
        requested_action is None and decision_type == "regenerate_child"
    ):
        regenerate_node_and_descendants(
            session_factory,
            logical_node_id=child_node_id,
            catalog=catalog,
        )
        post_action_status = "child_regeneration_requested"
    return ParentFailureDecisionResult(
        node_id=logical_node_id,
        node_run_id=parent_run.id,
        child_node_id=child_failure.child_node_id,
        child_node_version_id=child_failure.child_node_version_id,
        child_node_run_id=child_failure.child_run_id,
        failure_class=child_failure.classification,
        failure_origin=child_failure.failure_origin,
        decision_type=decision_type,
        decision_source=decision_source,
        decision_reason=str(evaluation["decision_reason"]),
        options_considered=list(evaluation["options_considered"]),
        threshold_triggered=bool(evaluation["threshold_triggered"]),
        threshold_reason=None if evaluation["threshold_reason"] is None else str(evaluation["threshold_reason"]),
        policy_snapshot=policy,
        summary=summary,
        parent_lifecycle_state=parent_lifecycle_state,
        parent_run_status=parent_run_status,
        child_lifecycle_state=child_lifecycle_state,
        post_action_status=post_action_status,
        counters=counters,
    )


def _active_parent_run(session: Session, logical_node_id: UUID, node_version_id: UUID) -> tuple[NodeRun, NodeRunState]:
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if lifecycle is None or lifecycle.current_run_id is None:
        raise DaemonConflictError("parent node has no active durable run for child-failure handling")
    run = session.get(NodeRun, lifecycle.current_run_id)
    if run is None or run.node_version_id != node_version_id:
        raise DaemonConflictError("parent active run does not match the authoritative node version")
    state = session.get(NodeRunState, run.id)
    if state is None:
        raise DaemonConflictError("parent run state not found")
    return run, state


def _latest_parent_run(session: Session, node_version_id: UUID) -> NodeRun | None:
    return session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == node_version_id)
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()


def _load_child_failure_context(session: Session, *, parent_node_version_id: UUID, child_node_id: UUID) -> ChildFailureContext:
    child_version = _authoritative_version(session, child_node_id)
    edge = session.execute(
        select(NodeChild).where(
            NodeChild.parent_node_version_id == parent_node_version_id,
            NodeChild.child_node_version_id == child_version.id,
        )
    ).scalar_one_or_none()
    if edge is None:
        raise DaemonConflictError("child node is not an authoritative child of the parent node")
    lifecycle = session.get(NodeLifecycleState, str(child_node_id))
    if lifecycle is None or lifecycle.lifecycle_state != "FAILED_TO_PARENT":
        raise DaemonConflictError("child node is not currently failed to parent")
    run = session.execute(
        select(NodeRun)
        .where(NodeRun.node_version_id == child_version.id)
        .order_by(NodeRun.run_number.desc())
    ).scalars().first()
    if run is None or run.run_status != "FAILED":
        raise DaemonConflictError("child node has no durable failed run to ingest")
    child = session.get(HierarchyNode, child_node_id)
    if child is None:
        raise DaemonNotFoundError("child hierarchy node not found")
    attempt = session.execute(
        select(SubtaskAttempt)
        .where(SubtaskAttempt.node_run_id == run.id)
        .order_by(SubtaskAttempt.ended_at.desc(), SubtaskAttempt.created_at.desc())
    ).scalars().first()
    summary = (None if attempt is None else attempt.summary) or run.summary or "child failed without a recorded summary"
    source_subtask_key = None
    if attempt is not None and attempt.compiled_subtask_id is not None:
        from aicoding.db.models import CompiledSubtask

        subtask = session.get(CompiledSubtask, attempt.compiled_subtask_id)
        source_subtask_key = None if subtask is None else subtask.source_subtask_key
    classification = _classify_failure(
        attempt=attempt,
        run=run,
        lifecycle=lifecycle,
        source_subtask_key=source_subtask_key,
    )
    classification_reason, failure_origin = _classify_failure_reason(
        attempt=attempt,
        run=run,
        lifecycle=lifecycle,
        source_subtask_key=source_subtask_key,
        classification=classification,
    )
    return ChildFailureContext(
        child_node_id=child_node_id,
        child_node_version_id=child_version.id,
        child_run_id=run.id,
        child_title=child.title,
        child_kind=child.kind,
        classification=classification,
        classification_reason=classification_reason,
        failure_origin=failure_origin,
        summary=summary,
        source_subtask_key=source_subtask_key,
        failed_attempt_number=None if attempt is None else attempt.attempt_number,
    )


def _classify_failure(*, attempt: SubtaskAttempt | None, run: NodeRun, lifecycle: NodeLifecycleState, source_subtask_key: str | None) -> str:
    summary_text = ((None if attempt is None else attempt.summary) or run.summary or "").lower()
    if attempt is not None and attempt.validation_json:
        return "validation_failure"
    if attempt is not None and attempt.review_json:
        return "review_failure"
    if attempt is not None and attempt.testing_json:
        return "test_failure"
    if source_subtask_key:
        if source_subtask_key.startswith("validate_"):
            return "validation_failure"
        if source_subtask_key.startswith("review_"):
            return "review_failure"
        if source_subtask_key.startswith("run_tests"):
            return "test_failure"
        if source_subtask_key.startswith("reconcile_") or source_subtask_key.startswith("merge_"):
            return "merge_conflict_unresolved"
        if source_subtask_key.startswith("rectify_") or source_subtask_key.startswith("regenerate_"):
            return "rectification_failure"
    if "merge conflict" in summary_text or "conflict" in summary_text:
        return "merge_conflict_unresolved"
    if "hybrid tree" in summary_text or "reconciliation" in summary_text or "layout authority" in summary_text or "manual tree" in summary_text:
        return "manual_tree_conflict"
    if "provider session" in summary_text or "session recovery" in summary_text or "tmux session" in summary_text:
        return "provider_recovery_failure"
    if "rectification" in summary_text or "rebuild" in summary_text or "regeneration" in summary_text:
        return "rectification_failure"
    if "layout" in summary_text or "requirement" in summary_text or "plan" in summary_text:
        return "bad_layout_or_bad_requirements"
    if "dependency" in summary_text or "context" in summary_text or "blocked" in summary_text:
        return "dependency_or_context_failure"
    if "environment" in summary_text or "timeout" in summary_text or "tool" in summary_text:
        return "environment_failure"
    if summary_text:
        return "transient_execution_failure"
    if lifecycle.pause_flag_name:
        return "unknown_failure"
    return "unknown_failure"


def _classify_failure_reason(
    *,
    attempt: SubtaskAttempt | None,
    run: NodeRun,
    lifecycle: NodeLifecycleState,
    source_subtask_key: str | None,
    classification: str,
) -> tuple[str, str]:
    if attempt is not None and attempt.validation_json:
        return ("validation payload was present on the failed attempt", "validation_gate")
    if attempt is not None and attempt.review_json:
        return ("review payload was present on the failed attempt", "review_gate")
    if attempt is not None and attempt.testing_json:
        return ("testing payload was present on the failed attempt", "testing_gate")
    if source_subtask_key:
        if source_subtask_key.startswith("validate_"):
            return (f"failed source subtask '{source_subtask_key}' is a validation stage", "validation_gate")
        if source_subtask_key.startswith("review_"):
            return (f"failed source subtask '{source_subtask_key}' is a review stage", "review_gate")
        if source_subtask_key.startswith("run_tests"):
            return (f"failed source subtask '{source_subtask_key}' is a testing stage", "testing_gate")
        if source_subtask_key.startswith("reconcile_") or source_subtask_key.startswith("merge_"):
            return (f"failed source subtask '{source_subtask_key}' is a reconcile or merge stage", "merge_or_reconcile")
        if source_subtask_key.startswith("rectify_") or source_subtask_key.startswith("regenerate_"):
            return (f"failed source subtask '{source_subtask_key}' is a rectification stage", "rectification")
    summary = ((None if attempt is None else attempt.summary) or run.summary or "no summary recorded").strip()
    return (f"classified as {classification} from failure summary and lifecycle context: {summary}", lifecycle.lifecycle_state.lower())


def _increment_child_failure_counter(
    session: Session,
    *,
    node_run_id: UUID,
    child_failure: ChildFailureContext,
) -> NodeRunChildFailureCounter:
    row = session.get(
        NodeRunChildFailureCounter,
        {
            "node_run_id": node_run_id,
            "child_node_version_id": child_failure.child_node_version_id,
        },
    )
    if row is None:
        row = NodeRunChildFailureCounter(
            node_run_id=node_run_id,
            child_node_version_id=child_failure.child_node_version_id,
            failure_count=0,
        )
        session.add(row)
    row.failure_count += 1
    row.last_failure_at = datetime.now(timezone.utc)
    row.last_failure_class = child_failure.classification
    row.last_failure_summary = child_failure.summary
    row.last_failure_subtask_key = child_failure.source_subtask_key
    row.last_failed_node_run_id = child_failure.child_run_id
    session.flush()
    return row


def _parent_failure_policy(session: Session, parent_version: NodeVersion) -> ParentFailurePolicySnapshot:
    policies: dict[str, object] = {}
    if parent_version.compiled_workflow_id is not None:
        # resolved_yaml freezes the node policy at compile time, so use that when available
        # instead of reaching back into mutable YAML sources.
        compiled_workflow = session.get(CompiledWorkflow, parent_version.compiled_workflow_id)
        if compiled_workflow is not None:
            policies = (
                dict(compiled_workflow.resolved_yaml.get("node_definition", {})).get("policies", {})
                if isinstance(compiled_workflow.resolved_yaml, dict)
                else {}
            )
    return ParentFailurePolicySnapshot(
        total_threshold=int(policies.get("child_failure_threshold_total", 3)),
        consecutive_threshold=int(policies.get("child_failure_threshold_consecutive", 2)),
        per_child_threshold=int(policies.get("child_failure_threshold_per_child", 2)),
    )


def _evaluate_parent_decision(
    *,
    child_failure: ChildFailureContext,
    counter_row: NodeRunChildFailureCounter,
    parent_state: NodeRunState,
    policy: ParentFailurePolicySnapshot,
    requested_action: str | None,
) -> dict[str, object]:
    options_considered = ["retry_child", "regenerate_child", "replan_parent", "pause_for_user"]
    if requested_action is not None:
        return {
            "decision_type": requested_action,
            "decision_reason": f"operator override selected '{requested_action}'",
            "options_considered": options_considered,
            "threshold_triggered": False,
            "threshold_reason": None,
        }
    if (
        parent_state.failure_count_from_children >= policy.total_threshold
        or parent_state.failure_count_consecutive >= policy.consecutive_threshold
        or counter_row.failure_count >= policy.per_child_threshold
    ):
        threshold_reason = (
            f"threshold exceeded for class {child_failure.classification}: "
            f"per_child={counter_row.failure_count}/{policy.per_child_threshold}, "
            f"total={parent_state.failure_count_from_children}/{policy.total_threshold}, "
            f"consecutive={parent_state.failure_count_consecutive}/{policy.consecutive_threshold}"
        )
        return {
            "decision_type": "pause_for_user",
            "decision_reason": "parent failure thresholds were exceeded",
            "options_considered": options_considered,
            "threshold_triggered": True,
            "threshold_reason": threshold_reason,
        }
    if child_failure.classification in {"transient_execution_failure", "environment_failure"}:
        return {
            "decision_type": "retry_child",
            "decision_reason": "failure appears transient or environment-linked and remains within retry budget",
            "options_considered": options_considered,
            "threshold_triggered": False,
            "threshold_reason": None,
        }
    if child_failure.classification in {"merge_conflict_unresolved", "rectification_failure"}:
        return {
            "decision_type": "regenerate_child",
            "decision_reason": "failure suggests stale child state or rectification drift that is safer to regenerate than retry",
            "options_considered": options_considered,
            "threshold_triggered": False,
            "threshold_reason": None,
        }
    if child_failure.classification in {
        "validation_failure",
        "review_failure",
        "test_failure",
        "bad_layout_or_bad_requirements",
        "dependency_or_context_failure",
        "manual_tree_conflict",
    }:
        return {
            "decision_type": "replan_parent",
            "decision_reason": "failure suggests parent inputs, layout, or quality expectations need revision rather than child-only retry",
            "options_considered": options_considered,
            "threshold_triggered": False,
            "threshold_reason": None,
        }
    if child_failure.classification in {"provider_recovery_failure", "unknown_failure"}:
        return {
            "decision_type": "pause_for_user",
            "decision_reason": "failure is too ambiguous or operator-facing to recover safely without user guidance",
            "options_considered": options_considered,
            "threshold_triggered": False,
            "threshold_reason": None,
        }
    return {
        "decision_type": "pause_for_user",
        "decision_reason": "default safe fallback was selected",
        "options_considered": options_considered,
        "threshold_triggered": False,
        "threshold_reason": None,
    }


def _build_parent_decision_summary(
    *,
    parent_node_id: UUID,
    child_failure: ChildFailureContext,
    evaluation: dict[str, object],
    counter_row: NodeRunChildFailureCounter,
    parent_state: NodeRunState,
    policy: ParentFailurePolicySnapshot,
) -> str:
    return (
        f"Parent node {parent_node_id} observed child {child_failure.child_node_id} fail with "
        f"{child_failure.classification} ({child_failure.classification_reason}). "
        f"Decision: {evaluation['decision_type']}. Reason: {evaluation['decision_reason']}. "
        f"Child failure count={counter_row.failure_count}, total child failures={parent_state.failure_count_from_children}, "
        f"consecutive child failures={parent_state.failure_count_consecutive}, thresholds="
        f"{policy.per_child_threshold}/{policy.total_threshold}/{policy.consecutive_threshold}. "
        f"Latest child summary: {child_failure.summary}"
    )


def _reset_child_after_failure(session: Session, *, child_node_id: UUID) -> None:
    session.execute(text("select pg_advisory_xact_lock(hashtext(:node_id))"), {"node_id": str(child_node_id)})
    lifecycle = session.get(NodeLifecycleState, str(child_node_id))
    if lifecycle is None:
        raise DaemonNotFoundError("child lifecycle record not found")
    lifecycle.lifecycle_state = "READY"
    lifecycle.run_status = None
    lifecycle.current_run_id = None
    lifecycle.current_task_id = None
    lifecycle.current_subtask_id = None
    lifecycle.current_subtask_attempt = None
    lifecycle.last_completed_subtask_id = None
    lifecycle.execution_cursor_json = {}
    lifecycle.pause_flag_name = None
    lifecycle.is_resumable = False
    lifecycle.working_tree_state = None
    state = session.get(DaemonNodeState, str(child_node_id))
    if state is not None:
        event_id = uuid4()
        session.add(
            DaemonMutationEvent(
                id=event_id,
                node_id=str(child_node_id),
                command="node.run.retry.reset",
                previous_state=state.lifecycle_state,
                resulting_state="ready",
                run_id=None,
                payload_json={"source": "parent_failure_decision"},
            )
        )
        state.current_run_id = None
        state.lifecycle_state = "ready"
        state.last_command = "node.run.retry.reset"
        state.last_event_id = event_id


def _counter_snapshot(session: Session, row: NodeRunChildFailureCounter) -> ChildFailureCounterSnapshot:
    child_version = session.get(NodeVersion, row.child_node_version_id)
    if child_version is None:
        raise DaemonNotFoundError("child node version not found")
    child = session.get(HierarchyNode, child_version.logical_node_id)
    if child is None:
        raise DaemonNotFoundError("child hierarchy node not found")
    return ChildFailureCounterSnapshot(
        child_node_id=child.node_id,
        child_node_version_id=row.child_node_version_id,
        child_title=child.title,
        child_kind=child.kind,
        failure_count=row.failure_count,
        last_failure_at=None if row.last_failure_at is None else row.last_failure_at.isoformat(),
        last_failure_class=row.last_failure_class,
        last_failure_summary=row.last_failure_summary,
        last_failure_subtask_key=row.last_failure_subtask_key,
        last_failed_node_run_id=row.last_failed_node_run_id,
        last_decision_type=row.last_decision_type,
        last_decision_at=None if row.last_decision_at is None else row.last_decision_at.isoformat(),
    )


def _child_failure_catalog_from_session(session: Session, *, logical_node_id: UUID) -> ChildFailureCatalogSnapshot:
    parent_version = _authoritative_version(session, logical_node_id)
    run = _latest_parent_run(session, parent_version.id)
    lifecycle = session.get(NodeLifecycleState, str(logical_node_id))
    if run is None:
        return ChildFailureCatalogSnapshot(
            node_id=logical_node_id,
            node_run_id=None,
            failure_count_from_children=0 if lifecycle is None else lifecycle.failure_count_from_children,
            failure_count_consecutive=0 if lifecycle is None else lifecycle.failure_count_consecutive,
            counters=[],
        )
    rows = session.execute(
        select(NodeRunChildFailureCounter)
        .where(NodeRunChildFailureCounter.node_run_id == run.id)
        .order_by(NodeRunChildFailureCounter.updated_at, NodeRunChildFailureCounter.child_node_version_id)
    ).scalars().all()
    counters = [_counter_snapshot(session, row) for row in rows]
    state = session.get(NodeRunState, run.id)
    return ChildFailureCatalogSnapshot(
        node_id=logical_node_id,
        node_run_id=run.id,
        failure_count_from_children=0 if state is None else state.failure_count_from_children,
        failure_count_consecutive=0 if state is None else state.failure_count_consecutive,
        counters=counters,
    )


def _decision_snapshot(row: WorkflowEvent) -> ParentDecisionSnapshot:
    payload = dict(row.payload_json or {})
    child_node_id = payload.get("child_node_id")
    child_node_version_id = payload.get("child_node_version_id")
    child_node_run_id = payload.get("child_node_run_id")
    return ParentDecisionSnapshot(
        id=row.id,
        node_id=row.logical_node_id,
        node_version_id=row.node_version_id,
        node_run_id=row.node_run_id,
        child_node_id=None if child_node_id is None else UUID(str(child_node_id)),
        child_node_version_id=None if child_node_version_id is None else UUID(str(child_node_version_id)),
        child_node_run_id=None if child_node_run_id is None else UUID(str(child_node_run_id)),
        failure_class=None if payload.get("failure_class") is None else str(payload["failure_class"]),
        failure_origin=None if payload.get("failure_origin") is None else str(payload["failure_origin"]),
        decision_type=row.event_type,
        decision_source=None if payload.get("decision_source") is None else str(payload["decision_source"]),
        decision_reason=None if payload.get("decision_reason") is None else str(payload["decision_reason"]),
        options_considered=[str(item) for item in payload.get("options_considered", [])],
        threshold_triggered=bool(payload.get("threshold_triggered", False)),
        threshold_reason=None if payload.get("threshold_reason") is None else str(payload["threshold_reason"]),
        summary=None if payload.get("summary") is None else str(payload["summary"]),
        payload_json=payload,
        created_at=row.created_at.isoformat(),
    )


def _authoritative_version(session: Session, logical_node_id: UUID) -> NodeVersion:
    selector = session.get(LogicalNodeCurrentVersion, logical_node_id)
    if selector is None:
        raise DaemonNotFoundError("logical node version selector not found")
    version = session.get(NodeVersion, selector.authoritative_node_version_id)
    if version is None:
        raise DaemonNotFoundError("node version not found")
    return version
