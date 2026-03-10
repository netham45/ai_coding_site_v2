from __future__ import annotations

from dataclasses import replace

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
from aicoding.daemon.testing_runtime import list_test_results_for_node, load_testing_summary_for_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _testing_catalog(tmp_path, *, fail_action: str = "fail_to_parent", max_attempts: int = 2):
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Testing runtime fixture policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: false",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs:",
                "    - testing/custom_retry_gate.yaml",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "testing" / "custom_retry_gate.yaml").write_text(
        "\n".join(
            [
                "kind: testing_definition",
                "id: custom_retry_gate",
                "name: Custom Retry Gate",
                "applies_to:",
                "  node_kinds: [epic, phase, plan, task]",
                "  task_ids: [test_node]",
                "  lifecycle_points: [after_task]",
                "scope: project_custom",
                "description: Exercise durable testing retries.",
                "commands:",
                "  - command: python3 -m pytest tests/unit -q",
                "    working_directory: .",
                "    env: {}",
                "retry_policy:",
                f"  max_attempts: {max_attempts}",
                "  rerun_failed_only: true",
                "pass_rules:",
                "  require_exit_code_zero: true",
                "  max_failed_tests: 0",
                "on_result:",
                "  pass_action: continue",
                f"  fail_action: {fail_action}",
            ]
        ),
        encoding="utf-8",
    )
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_test_node.yaml").write_text(
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
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    return replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )


def _create_testing_ready_run(db_session_factory, tmp_path, *, fail_action: str = "fail_to_parent", max_attempts: int = 2):
    catalog = _testing_catalog(tmp_path, fail_action=fail_action, max_attempts=max_attempts)
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Testable", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    assert compile_result.status == "compiled", None if compile_result.compile_failure is None else compile_result.compile_failure.to_payload()
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admit_node_run(db_session_factory, node_id=node.node_id)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
    while progress.current_subtask["subtask_type"] != "run_tests":
        compiled_subtask_id = progress.state.current_compiled_subtask_id
        start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=compiled_subtask_id)
        if progress.current_subtask["subtask_type"] == "validate":
            payload = {"exit_code": 0}
        elif progress.current_subtask["subtask_type"] == "review":
            payload = {"status": "pass", "findings": [{"message": "ok"}], "criteria_results": [{"criterion": "ok", "status": "passed"}]}
        else:
            payload = None
        complete_current_subtask(
            db_session_factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=compiled_subtask_id,
            output_json=payload,
            summary="done",
        )
        progress = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    return catalog, node, progress


def test_testing_gate_persists_results_for_run_tests_subtask(db_session_factory, migrated_public_schema, tmp_path) -> None:
    catalog, node, progress = _create_testing_ready_run(db_session_factory, tmp_path)

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={
            "test_suites": [
                {
                    "testing_definition_id": "default_unit_test_gate",
                    "suite_name": "Default Unit Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "unit tests passed",
                },
                {
                    "testing_definition_id": "default_integration_test_gate",
                    "suite_name": "Default Integration Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "integration tests passed",
                },
                {
                    "testing_definition_id": "custom_retry_gate",
                    "suite_name": "Custom Retry Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "tests passed",
                }
            ]
        },
        summary="tests passed",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    summary = load_testing_summary_for_node(db_session_factory, logical_node_id=node.node_id)
    results = list_test_results_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status in {"RUNNING", "COMPLETE"}
    assert summary.status == "passed"
    assert summary.retry_pending is False
    assert summary.passed_count >= 3
    assert {item.testing_definition_id for item in results} >= {
        "default_unit_test_gate",
        "default_integration_test_gate",
        "custom_retry_gate",
    }
    assert all(item.status == "passed" for item in results)


def test_testing_gate_failure_with_retry_keeps_same_subtask(db_session_factory, migrated_public_schema, tmp_path) -> None:
    catalog, node, progress = _create_testing_ready_run(db_session_factory, tmp_path)
    current_subtask_id = progress.state.current_compiled_subtask_id

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        output_json={
            "test_suites": [
                {
                    "testing_definition_id": "default_unit_test_gate",
                    "suite_name": "Default Unit Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "unit tests passed",
                },
                {
                    "testing_definition_id": "default_integration_test_gate",
                    "suite_name": "Default Integration Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "integration tests passed",
                },
                {
                    "testing_definition_id": "custom_retry_gate",
                    "suite_name": "Custom Retry Gate",
                    "exit_code": 1,
                    "failed_tests": 1,
                    "summary": "tests failed",
                }
            ]
        },
        summary="tests failed",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    summary = load_testing_summary_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "RUNNING"
    assert advanced.state.current_compiled_subtask_id == current_subtask_id
    assert advanced.state.execution_cursor_json["testing_retry_pending"] is True
    assert advanced.state.execution_cursor_json["testing_rerun_failed_only"] is True
    assert summary.status == "retry_pending"
    assert summary.retry_allowed is True
    assert summary.retry_pending is True
    assert summary.failed_count == 1


def test_testing_gate_pause_route_honors_definition_action(db_session_factory, migrated_public_schema, tmp_path) -> None:
    catalog, node, progress = _create_testing_ready_run(
        db_session_factory,
        tmp_path,
        fail_action="pause_for_user",
        max_attempts=1,
    )

    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={
            "test_suites": [
                {
                    "testing_definition_id": "default_unit_test_gate",
                    "suite_name": "Default Unit Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "unit tests passed",
                },
                {
                    "testing_definition_id": "default_integration_test_gate",
                    "suite_name": "Default Integration Test Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "integration tests passed",
                },
                {
                    "testing_definition_id": "custom_retry_gate",
                    "suite_name": "Custom Retry Gate",
                    "exit_code": 1,
                    "failed_tests": 1,
                    "summary": "tests failed",
                }
            ]
        },
        summary="tests failed",
    )

    advanced = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    summary = load_testing_summary_for_node(db_session_factory, logical_node_id=node.node_id)

    assert advanced.run.run_status == "PAUSED"
    assert advanced.state.lifecycle_state == "PAUSED_FOR_USER"
    assert advanced.state.pause_flag_name == "testing_failed"
    assert summary.status == "failed"
    assert summary.action == "pause_for_user"
