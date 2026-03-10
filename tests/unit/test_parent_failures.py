from __future__ import annotations

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.parent_failures import (
    handle_child_failure_at_parent,
    list_child_failure_counters,
    list_parent_decision_history,
)
from aicoding.daemon.run_orchestration import fail_current_subtask, load_current_run_progress, start_subtask_attempt
from aicoding.daemon.versioning import initialize_node_version, list_node_versions
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import DaemonNodeState
from aicoding.db.models import SubtaskAttempt
from aicoding.db.session import create_session_factory, query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_parent_and_failed_child(session_factory, *, child_summary: str) -> tuple[object, object]:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    parent = create_hierarchy_node(session_factory, registry, kind="epic", title="Parent", prompt="boot prompt")
    seed_node_lifecycle(session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(session_factory, logical_node_id=parent.node_id)
    compile_node_workflow(session_factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(session_factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(session_factory, node_id=parent.node_id)

    child = create_manual_node(
        session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="child prompt",
        parent_node_id=parent.node_id,
    )
    compile_node_workflow(session_factory, logical_node_id=child.node.node_id, catalog=catalog)
    transition_node_lifecycle(session_factory, node_id=str(child.node.node_id), target_state="READY")
    admit_node_run(session_factory, node_id=child.node.node_id)
    progress = load_current_run_progress(session_factory, logical_node_id=child.node.node_id)
    start_subtask_attempt(
        session_factory,
        logical_node_id=child.node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
    )
    fail_current_subtask(
        session_factory,
        logical_node_id=child.node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        summary=child_summary,
    )
    return parent, child


def _fail_child_again(session_factory, *, child_node_id, summary: str) -> None:
    admit_node_run(session_factory, node_id=child_node_id)
    progress = load_current_run_progress(session_factory, logical_node_id=child_node_id)
    start_subtask_attempt(
        session_factory,
        logical_node_id=child_node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
    )
    fail_current_subtask(
        session_factory,
        logical_node_id=child_node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        summary=summary,
    )


def _set_latest_attempt_fields(session_factory, *, child_node_id, **updates) -> None:
    with session_scope(session_factory) as session:
        latest_attempt = session.query(SubtaskAttempt).order_by(SubtaskAttempt.created_at.desc()).first()
        assert latest_attempt is not None
        for field_name, value in updates.items():
            setattr(latest_attempt, field_name, value)


def test_retry_child_clears_failed_child_state_and_records_decision(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="environment timeout while running tool")

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
        requested_action="retry_child",
    )
    child_lifecycle = load_node_lifecycle(session_factory, str(child.node.node_id))
    counters = list_child_failure_counters(session_factory, logical_node_id=parent.node_id)
    history = list_parent_decision_history(session_factory, logical_node_id=parent.node_id)

    assert decision.decision_type == "retry_child"
    assert decision.decision_source == "override"
    assert decision.decision_reason == "operator override selected 'retry_child'"
    assert decision.options_considered == ["retry_child", "regenerate_child", "replan_parent", "pause_for_user"]
    assert decision.post_action_status == "child_ready_for_retry"
    assert child_lifecycle.lifecycle_state == "READY"
    assert child_lifecycle.current_run_id is None
    assert counters.failure_count_from_children == 1
    assert counters.failure_count_consecutive == 1
    assert len(counters.counters) == 1
    assert counters.counters[0].failure_count == 1
    assert counters.counters[0].last_failure_class == "environment_failure"
    assert counters.counters[0].last_decision_type == "retry_child"
    assert history.decisions[-1].decision_type == "parent_retry_child"
    assert history.decisions[-1].decision_reason == "operator override selected 'retry_child'"

    with query_session_scope(session_factory) as session:
        daemon_state = session.get(DaemonNodeState, str(child.node.node_id))
        assert daemon_state is not None
        assert daemon_state.current_run_id is None
        assert daemon_state.lifecycle_state == "ready"


def test_bad_layout_failure_auto_replans_parent(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="layout requirements contradict the requested outcome")

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )
    parent_lifecycle = load_node_lifecycle(session_factory, str(parent.node_id))
    history = list_parent_decision_history(session_factory, logical_node_id=parent.node_id)

    assert decision.decision_type == "replan_parent"
    assert decision.decision_source == "auto"
    assert decision.failure_origin == "failed_to_parent"
    assert decision.decision_reason == "failure suggests parent inputs, layout, or quality expectations need revision rather than child-only retry"
    assert decision.parent_lifecycle_state == "PAUSED_FOR_USER"
    assert decision.parent_run_status == "PAUSED"
    assert decision.post_action_status == "parent_paused"
    assert parent_lifecycle.lifecycle_state == "PAUSED_FOR_USER"
    assert parent_lifecycle.pause_flag_name == "parent_replan_required"
    assert history.decisions[-1].decision_type == "parent_replan"
    assert history.decisions[-1].failure_class == "bad_layout_or_bad_requirements"
    assert history.decisions[-1].threshold_triggered is False


def test_repeated_transient_failures_pause_parent_after_threshold(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="environment timeout on remote tool")

    first = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )
    _fail_child_again(session_factory, child_node_id=child.node.node_id, summary="environment timeout on remote tool")
    second = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )
    parent_lifecycle = load_node_lifecycle(session_factory, str(parent.node_id))
    counters = list_child_failure_counters(session_factory, logical_node_id=parent.node_id)
    history = list_parent_decision_history(session_factory, logical_node_id=parent.node_id)

    assert first.decision_type == "retry_child"
    assert second.decision_type == "pause_for_user"
    assert second.threshold_triggered is True
    assert second.threshold_reason is not None
    assert second.post_action_status == "parent_paused"
    assert second.parent_run_status == "PAUSED"
    assert parent_lifecycle.pause_flag_name == "parent_child_failure_pause"
    assert counters.failure_count_from_children == 2
    assert counters.failure_count_consecutive == 2
    assert counters.counters[0].failure_count == 2
    assert [item.decision_type for item in history.decisions] == ["parent_retry_child", "parent_pause_for_user"]


def test_merge_conflict_failure_auto_regenerates_child(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="merge conflict while reconciling child branch")

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
        catalog=load_resource_catalog(),
    )
    versions = list_node_versions(session_factory, child.node.node_id)
    history = list_parent_decision_history(session_factory, logical_node_id=parent.node_id)

    assert decision.decision_type == "regenerate_child"
    assert decision.decision_source == "auto"
    assert decision.failure_class == "merge_conflict_unresolved"
    assert decision.decision_reason == "failure suggests stale child state or rectification drift that is safer to regenerate than retry"
    assert decision.post_action_status == "child_regeneration_requested"
    assert any(item.status == "candidate" for item in versions)
    assert history.decisions[-1].decision_type == "parent_regenerate_child"


def test_validation_failure_auto_replans_parent(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="validation rejected output")
    _set_latest_attempt_fields(session_factory, child_node_id=child.node.node_id, validation_json={"status": "failed"})

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )

    assert decision.failure_class == "validation_failure"
    assert decision.failure_origin == "validation_gate"
    assert decision.decision_type == "replan_parent"


def test_manual_tree_conflict_auto_replans_parent(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="hybrid tree requires reconciliation before child can continue")

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )

    assert decision.failure_class == "manual_tree_conflict"
    assert decision.decision_type == "replan_parent"


def test_provider_recovery_failure_pauses_parent(migrated_public_schema) -> None:
    session_factory = create_session_factory(engine=migrated_public_schema)
    parent, child = _create_parent_and_failed_child(session_factory, child_summary="provider session could not be rebound after tmux session loss")

    decision = handle_child_failure_at_parent(
        session_factory,
        logical_node_id=parent.node_id,
        child_node_id=child.node.node_id,
    )

    assert decision.failure_class == "provider_recovery_failure"
    assert decision.decision_type == "pause_for_user"
