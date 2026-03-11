from __future__ import annotations

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
from aicoding.daemon.validation_runtime import list_validation_results_for_node, load_validation_summary_for_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import CompiledSubtask
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_validation_ready_run(db_session_factory):
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Validatable", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admit_node_run(db_session_factory, node_id=node.node_id)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
    while not progress.current_subtask["source_subtask_key"].startswith("validate_node."):
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


def test_validation_gate_persists_results_and_completes_run(db_session_factory, migrated_public_schema) -> None:
    node, progress = _create_validation_ready_run(db_session_factory)

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={"exit_code": 0},
        summary="validation ok",
    )
    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    summary = load_validation_summary_for_node(db_session_factory, logical_node_id=node.node_id)
    results = list_validation_results_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "RUNNING"
    assert advanced.current_subtask["source_subtask_key"].startswith(("review_node.", "review_node.hook."))
    assert summary.status == "passed"
    assert summary.passed_count == 1
    assert results[0].check_type == "command_exit_code"
    assert results[0].status == "passed"


def test_validation_gate_defaults_to_exit_code_check_when_compiled_checks_are_empty(
    db_session_factory,
    migrated_public_schema,
) -> None:
    node, progress = _create_validation_ready_run(db_session_factory)

    from aicoding.db.session import session_scope

    with session_scope(db_session_factory) as session:
        subtask = session.get(CompiledSubtask, progress.state.current_compiled_subtask_id)
        assert subtask is not None
        retry_policy = dict(subtask.retry_policy_json or {})
        retry_policy["checks"] = []
        retry_policy["outputs"] = []
        subtask.retry_policy_json = retry_policy
        session.flush()

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={"exit_code": 0},
        summary="validation ok",
    )
    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id)
    summary = load_validation_summary_for_node(db_session_factory, logical_node_id=node.node_id)
    results = list_validation_results_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "RUNNING"
    assert advanced.current_subtask["source_subtask_key"].startswith(("review_node.", "review_node.hook."))
    assert summary.status == "passed"
    assert results[0].check_type == "command_exit_code"
    assert results[0].status == "passed"
