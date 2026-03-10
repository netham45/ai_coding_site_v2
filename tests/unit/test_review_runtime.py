from __future__ import annotations

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.review_runtime import list_review_results_for_node, load_review_summary_for_node
from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_review_ready_run(db_session_factory):
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Reviewable", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admit_node_run(db_session_factory, node_id=node.node_id)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
    while not progress.current_subtask["source_subtask_key"].startswith("review_node."):
        start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
        complete_current_subtask(
            db_session_factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=progress.state.current_compiled_subtask_id,
            output_json={"exit_code": 0},
            summary="done",
        )
        progress = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    return node, progress


def test_review_gate_persists_passed_results_and_completes_run(db_session_factory, migrated_public_schema) -> None:
    node, progress = _create_review_ready_run(db_session_factory)

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={
            "status": "pass",
            "findings": [{"message": "looks good"}],
            "criteria_results": [{"criterion": "Requirements are satisfied.", "status": "passed"}],
        },
        summary="approved",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    summary = load_review_summary_for_node(db_session_factory, logical_node_id=node.node_id)
    results = list_review_results_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status in {"RUNNING", "COMPLETE"}
    if advanced.run.run_status == "RUNNING":
        assert advanced.current_subtask["source_subtask_key"].startswith("review_node.hook.")
    assert summary.status == "passed"
    assert summary.action == "continue"
    assert summary.passed_count == 1
    assert results[0].review_definition_id == "node_against_requirements"
    assert results[0].scope == "node_output"
    assert results[0].status == "passed"


def test_review_gate_revise_routes_back_to_execute_stage(db_session_factory, migrated_public_schema) -> None:
    node, progress = _create_review_ready_run(db_session_factory)

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={"status": "revise", "findings": [{"message": "tighten the implementation"}]},
        summary="needs revision",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    summary = load_review_summary_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "RUNNING"
    assert advanced.state.lifecycle_state == "RUNNING"
    assert advanced.current_subtask["source_subtask_key"].startswith(("execute_node.", "execute_node.hook."))
    assert summary.status == "revise"
    assert summary.action == "rerun_task"


def test_review_gate_fail_uses_review_action(db_session_factory, migrated_public_schema) -> None:
    node, progress = _create_review_ready_run(db_session_factory)

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={"status": "fail", "findings": [{"message": "output is not coherent"}]},
        summary="rejected",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    summary = load_review_summary_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "PAUSED"
    assert advanced.state.lifecycle_state == "PAUSED_FOR_USER"
    assert advanced.state.pause_flag_name == "review_failed"
    assert summary.status == "failed"
    assert summary.action == "pause_for_user"
