from __future__ import annotations

import subprocess
import time

import pytest


def _write_broken_compile_inputs(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    node_override = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_tasks.yaml"

    project_policy.parent.mkdir(parents=True, exist_ok=True)
    node_override.parent.mkdir(parents=True, exist_ok=True)

    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Broken project policy for real E2E flow 20.",
                "  defaults:",
                "    auto_run_children: true",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs: invalid",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    node_override.write_text(
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
            ]
        ),
        encoding="utf-8",
    )


def _repair_project_policy(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Repaired project policy for real E2E flow 20.",
                "  defaults:",
                "    auto_run_children: true",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs: []",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_20_compile_failure_and_reattempt_runs_against_real_daemon_and_real_cli(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(session_backend="tmux")
    _write_broken_compile_inputs(harness.workspace_root)

    create_result = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 20 Epic",
        "--prompt",
        "Compile this node against a broken project policy, then repair the source and recompile it.",
    )
    assert create_result.exit_code == 0, create_result.stderr
    node_id = str(create_result.json()["node_id"])

    failed_compile_result = harness.cli("workflow", "compile", "--node", node_id)
    failed_compile_failures_result = harness.cli("workflow", "compile-failures", "--node", node_id)
    source_discovery_result = harness.cli("workflow", "source-discovery", "--node", node_id)

    assert failed_compile_result.exit_code == 0, failed_compile_result.stderr
    assert failed_compile_failures_result.exit_code == 0, failed_compile_failures_result.stderr
    assert source_discovery_result.exit_code == 4, source_discovery_result.stderr

    failed_compile_payload = failed_compile_result.json()
    failed_failures_payload = failed_compile_failures_result.json()
    source_discovery_error = source_discovery_result.stderr_json()

    assert failed_compile_payload["status"] == "failed"
    assert failed_compile_payload["compile_failure"]["failure_class"] == "schema_validation_failure"
    assert failed_compile_payload["compile_failure"]["failure_stage"] == "schema_validation"
    assert failed_failures_payload["failures"]
    assert failed_failures_payload["failures"][0]["target_id"] == "project-policies/default_project_policy.yaml"
    assert source_discovery_error["error"] == "not_found"
    assert source_discovery_error["details"]["response"]["detail"] == "compiled workflow not found"

    _repair_project_policy(harness.workspace_root)

    compile_result = harness.cli("workflow", "compile", "--node", node_id)
    current_result = harness.cli("workflow", "current", "--node", node_id)
    compile_failures_result = harness.cli("workflow", "compile-failures", "--node", node_id)
    schema_validation_result = harness.cli("workflow", "schema-validation", "--node", node_id)
    source_discovery_after_repair = harness.cli("workflow", "source-discovery", "--node", node_id)

    assert compile_result.exit_code == 0, compile_result.stderr
    assert current_result.exit_code == 0, current_result.stderr
    assert compile_failures_result.exit_code == 0, compile_failures_result.stderr
    assert schema_validation_result.exit_code == 0, schema_validation_result.stderr
    assert source_discovery_after_repair.exit_code == 0, source_discovery_after_repair.stderr

    compile_payload = compile_result.json()
    current_payload = current_result.json()
    compile_failures_payload = compile_failures_result.json()
    schema_validation_payload = schema_validation_result.json()
    source_discovery_payload = source_discovery_after_repair.json()

    assert compile_payload["status"] == "compiled"
    assert current_payload["tasks"]
    assert compile_failures_payload["failures"]
    assert compile_failures_payload["failures"][0]["failure_class"] == "schema_validation_failure"
    assert schema_validation_payload["validated_document_count"] > 0
    assert any(item["relative_path"] == "project-policies/default_project_policy.yaml" for item in source_discovery_payload["resolved_documents"])

    start_result = harness.cli("node", "run", "start", "--node", node_id)
    assert start_result.exit_code == 0, start_result.stderr
    bind_result = harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    run_show_payload = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        run_show = harness.cli("node", "run", "show", "--node", node_id)
        assert run_show.exit_code == 0, run_show.stderr
        run_show_payload = run_show.json()
        last_pane_text = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", session_name],
            text=True,
            capture_output=True,
            check=False,
        ).stdout
        if (
            run_show_payload["latest_attempt"] is not None
            or run_show_payload["state"]["last_completed_compiled_subtask_id"] is not None
            or run_show_payload["run"]["run_status"] in {"FAILED", "PAUSED", "COMPLETED", "COMPLETE"}
        ):
            break
        time.sleep(2.0)

    assert run_show_payload is not None, (
        "Expected the repaired compile-retry flow to produce durable run state after a real started run and bound tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )
