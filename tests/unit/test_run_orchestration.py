from __future__ import annotations

from dataclasses import replace

import pytest

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.history import get_prompt_record, get_summary_record, list_prompt_history, list_summary_history
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.run_orchestration import (
    approve_paused_run,
    advance_workflow,
    cancel_active_run,
    complete_current_subtask,
    fail_current_subtask,
    heartbeat_current_subtask,
    list_node_runs,
    load_current_subtask_context,
    load_current_subtask_prompt,
    load_current_run_progress,
    register_summary,
    retry_current_subtask,
    start_subtask_attempt,
    sync_resumed_run,
)
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.daemon.errors import DaemonConflictError
from aicoding.db.models import CompiledSubtask, NodeRunState
from aicoding.db.session import session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _pause_gate_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_pause_gate.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
                "    - pause_for_user",
                "    - validate_node",
                "    - review_node",
            ]
        ),
        encoding="utf-8",
    )
    return replace(base_catalog, yaml_overrides_dir=overrides_root)


def _create_started_run(db_session_factory, *, catalog=None):
    catalog = load_resource_catalog() if catalog is None else catalog
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Runnable", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admission = admit_node_run(db_session_factory, node_id=node.node_id)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
    return node, admission, progress


def test_start_complete_and_advance_workflow(db_session_factory, migrated_public_schema) -> None:
    node, admission, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    started = start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    completed = complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="done",
    )
    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)

    assert admission.status == "admitted"
    assert started.latest_attempt is not None
    assert started.latest_attempt.status == "RUNNING"
    assert completed.latest_attempt.status == "COMPLETE"
    assert completed.state.last_completed_compiled_subtask_id == current_subtask_id
    assert advanced.run.run_status in {"RUNNING", "COMPLETE"}


def test_fail_current_subtask_marks_run_failed(db_session_factory, migrated_public_schema) -> None:
    node, admission, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    failed = fail_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="boom",
    )

    assert failed.run.run_status == "FAILED"
    assert failed.state.lifecycle_state == "FAILED_TO_PARENT"
    assert failed.latest_attempt.status == "FAILED"


def test_start_subtask_attempt_records_execution_environment_metadata(db_session_factory, migrated_public_schema) -> None:
    node, _, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id
    with session_scope(db_session_factory) as session:
        subtask = session.get(CompiledSubtask, current_subtask_id)
        assert subtask is not None
        subtask.environment_policy_ref = "environments/local_default.yaml"
        subtask.environment_request_json = {
            "policy_ref": "environments/local_default.yaml",
            "policy_id": "local_default",
            "isolation_mode": "none",
            "allow_network": True,
            "runtime_profile": None,
            "mandatory": False,
        }

    started = start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)

    assert started.latest_attempt is not None
    assert started.latest_attempt.status == "RUNNING"
    assert started.latest_attempt.execution_environment_json["launch_status"] == "active"
    assert started.latest_attempt.execution_environment_json["resolved_mode"] == "none"
    assert started.latest_attempt.input_context_json["execution_environment"]["policy_id"] == "local_default"


def test_start_subtask_attempt_fails_immediately_for_unsupported_mandatory_environment(
    db_session_factory,
    migrated_public_schema,
) -> None:
    node, _, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id
    with session_scope(db_session_factory) as session:
        subtask = session.get(CompiledSubtask, current_subtask_id)
        assert subtask is not None
        subtask.environment_policy_ref = "environments/isolated_test_profile.yaml"
        subtask.environment_request_json = {
            "policy_ref": "environments/isolated_test_profile.yaml",
            "policy_id": "isolated_test_profile",
            "isolation_mode": "container",
            "allow_network": False,
            "runtime_profile": "isolated_test_profile",
            "mandatory": True,
        }

    failed = start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)

    assert failed.run.run_status == "FAILED"
    assert failed.state.lifecycle_state == "FAILED_TO_PARENT"
    assert failed.latest_attempt is not None
    assert failed.latest_attempt.status == "FAILED"
    assert failed.latest_attempt.execution_environment_json["failure_class"] == "environment_launch_failure"


def test_retry_current_subtask_reopens_failed_run(db_session_factory, migrated_public_schema) -> None:
    node, _, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    failed = fail_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="boom",
    )

    retried = retry_current_subtask(db_session_factory, logical_node_id=node.node_id)

    assert failed.run.run_status == "FAILED"
    assert retried.run.run_status == "RUNNING"
    assert retried.state.lifecycle_state == "RUNNING"
    assert retried.latest_attempt is not None
    assert retried.latest_attempt.attempt_number == 2
    assert retried.latest_attempt.status == "RUNNING"


def test_cancel_active_run_marks_run_cancelled(db_session_factory, migrated_public_schema) -> None:
    node, _, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    cancelled = cancel_active_run(db_session_factory, logical_node_id=node.node_id)

    assert cancelled.run.run_status == "CANCELLED"
    assert cancelled.state.lifecycle_state == "CANCELLED"
    assert cancelled.state.current_compiled_subtask_id is None
    assert cancelled.latest_attempt is None
    assert cancelled.state.execution_cursor_json["cancellation"]["summary"] == "Run cancelled by operator request."


def test_list_node_runs_returns_started_run(db_session_factory, migrated_public_schema) -> None:
    node, admission, progress = _create_started_run(db_session_factory)

    runs = list_node_runs(db_session_factory, logical_node_id=node.node_id)

    assert len(runs) == 1
    assert runs[0].id == progress.run.id
    assert runs[0].run_status == "RUNNING"


def test_subtask_prompt_context_heartbeat_and_summary_registration(db_session_factory, migrated_public_schema, tmp_path) -> None:
    node, admission, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    prompt_before = load_current_subtask_prompt(db_session_factory, logical_node_id=node.node_id)
    context_before = load_current_subtask_context(db_session_factory, logical_node_id=node.node_id)
    started = start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    heartbeat = heartbeat_current_subtask(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    registration = register_summary(
        db_session_factory,
        logical_node_id=node.node_id,
        summary_type="subtask",
        summary_path=str(tmp_path / "summary.md"),
        content="summary body",
    )
    context_after = load_current_subtask_context(db_session_factory, logical_node_id=node.node_id)
    prompt_history = list_prompt_history(db_session_factory, logical_node_id=node.node_id)
    summary_history = list_summary_history(db_session_factory, logical_node_id=node.node_id)
    prompt_record = get_prompt_record(db_session_factory, prompt_id=prompt_before.prompt_id)
    summary_record = get_summary_record(db_session_factory, summary_id=registration.summary_id)

    assert admission.status == "admitted"
    assert prompt_before.compiled_subtask_id == current_subtask_id
    assert prompt_before.prompt_id
    assert prompt_before.source_subtask_key
    assert prompt_before.stage_context_json["startup"]["node_id"] == str(node.node_id)
    assert prompt_before.stage_context_json["startup"]["trigger_reason"] == "manual_start"
    assert prompt_before.stage_context_json["stage"]["compiled_subtask_id"] == str(current_subtask_id)
    assert context_before.compiled_subtask_id == current_subtask_id
    assert context_before.input_context_json["compiled_subtask_id"] == str(current_subtask_id)
    assert context_before.stage_context_json["startup"]["node_prompt"] == "boot prompt"
    assert context_before.input_context_json["stage_context_json"]["startup"]["node_title"] == "Runnable"
    assert started.latest_attempt is not None
    assert heartbeat.latest_attempt is not None
    assert heartbeat.latest_attempt.output_json["last_heartbeat_at"]
    assert registration.summary_id
    assert registration.compiled_subtask_id == current_subtask_id
    assert registration.summary_type == "subtask"
    assert context_after.attempt_number == 1
    assert context_after.latest_summary == "summary body"
    assert [item.id for item in prompt_history.prompts] == [prompt_before.prompt_id]
    assert prompt_record.id == prompt_before.prompt_id
    assert prompt_record.prompt_role == "subtask_prompt"
    assert prompt_record.template_path
    assert prompt_record.template_hash
    assert prompt_record.content_hash
    assert [item.id for item in summary_history.summaries] == [registration.summary_id]
    assert summary_record.id == registration.summary_id
    assert summary_record.summary_type == "subtask"
    assert summary_record.summary_scope == "subtask_attempt"
    assert summary_record.summary_path == str(tmp_path / "summary.md")
    assert summary_record.content == "summary body"


def test_subtask_context_includes_dependency_and_child_summary_context(db_session_factory, migrated_public_schema) -> None:
    node, _, progress = _create_started_run(db_session_factory)
    sibling = create_hierarchy_node(
        db_session_factory,
        load_hierarchy_registry(load_resource_catalog()),
        kind="epic",
        title="Dependency Epic",
        prompt="dep prompt",
    )
    seed_node_lifecycle(db_session_factory, node_id=str(sibling.node_id), initial_state="READY")
    initialize_node_version(db_session_factory, logical_node_id=sibling.node_id)

    from aicoding.daemon.admission import add_node_dependency, check_node_dependency_readiness

    add_node_dependency(db_session_factory, node_id=node.node_id, depends_on_node_id=sibling.node_id)
    check_node_dependency_readiness(db_session_factory, node_id=node.node_id)

    with session_scope(db_session_factory) as session:
        state = session.get(NodeRunState, progress.state.node_run_id)
        assert state is not None
        state.execution_cursor_json = {
            **dict(state.execution_cursor_json or {}),
            "child_session_results": [{"session_id": "child-1", "summary": "child summary"}],
        }
        session.flush()

    context = load_current_subtask_context(db_session_factory, logical_node_id=node.node_id)

    assert context.stage_context_json["dependencies"]["dependencies"]
    assert context.stage_context_json["dependencies"]["blockers"]
    assert context.stage_context_json["cursor"]["child_session_results"][0]["summary"] == "child summary"


def test_user_gate_pause_requires_approval_before_resume(db_session_factory, migrated_public_schema, tmp_path) -> None:
    catalog = _pause_gate_catalog(tmp_path)
    node, _, progress = _create_started_run(db_session_factory, catalog=catalog)
    current_subtask_id = progress.state.current_compiled_subtask_id

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="context gathered",
    )
    progressed = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    while progressed.run.run_status == "RUNNING" and not progressed.current_subtask["source_subtask_key"].startswith("pause_for_user."):
        compiled_subtask_id = progressed.state.current_compiled_subtask_id
        start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=compiled_subtask_id)
        complete_current_subtask(
            db_session_factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=compiled_subtask_id,
            summary="advanced",
        )
        progressed = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)

    paused = progressed

    assert paused.run.run_status == "PAUSED"
    assert paused.state.pause_flag_name == "user_guidance_required"
    assert paused.current_subtask["source_subtask_key"].startswith("pause_for_user.")

    with pytest.raises(DaemonConflictError):
        sync_resumed_run(db_session_factory, logical_node_id=node.node_id)

    approved = approve_paused_run(
        db_session_factory,
        logical_node_id=node.node_id,
        pause_flag_name="user_guidance_required",
        approval_summary="approved to continue",
    )
    resumed = sync_resumed_run(db_session_factory, logical_node_id=node.node_id)

    assert approved.state.pause_flag_name == "user_guidance_required"
    assert approved.state.execution_cursor_json["pause_context"]["approved"] is True
    assert resumed.run.run_status == "RUNNING"
    assert resumed.state.pause_flag_name is None
