from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_02_compile_or_recompile_workflow_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 02 Epic",
        "--prompt",
        "Compile and inspect the workflow through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    node_version_id = str(start_payload["node_version_id"])

    run_start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert run_start_result.exit_code == 0, run_start_result.stderr

    recompile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    assert recompile_result.exit_code == 4, recompile_result.stderr
    recompile_error = recompile_result.stderr_json()
    assert recompile_error["error"] == "daemon_conflict"
    assert recompile_error["details"]["response"]["detail"] == "cannot compile a node with an active lifecycle run"

    current_result = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    chain_result = real_daemon_harness.cli("workflow", "chain", "--node", node_id)
    source_discovery_result = real_daemon_harness.cli("workflow", "source-discovery", "--node", node_id)
    schema_validation_result = real_daemon_harness.cli("workflow", "schema-validation", "--node", node_id)
    override_resolution_result = real_daemon_harness.cli("workflow", "override-resolution", "--node", node_id)
    hook_policy_result = real_daemon_harness.cli("workflow", "hook-policy", "--node", node_id)
    rendering_result = real_daemon_harness.cli("workflow", "rendering", "--node", node_id)
    compile_failures_result = real_daemon_harness.cli("workflow", "compile-failures", "--node", node_id)
    version_source_discovery_result = real_daemon_harness.cli("workflow", "source-discovery", "--version", node_version_id)
    version_rendering_result = real_daemon_harness.cli("workflow", "rendering", "--version", node_version_id)

    assert current_result.exit_code == 0, current_result.stderr
    assert chain_result.exit_code == 0, chain_result.stderr
    assert source_discovery_result.exit_code == 0, source_discovery_result.stderr
    assert schema_validation_result.exit_code == 0, schema_validation_result.stderr
    assert override_resolution_result.exit_code == 0, override_resolution_result.stderr
    assert hook_policy_result.exit_code == 0, hook_policy_result.stderr
    assert rendering_result.exit_code == 0, rendering_result.stderr
    assert compile_failures_result.exit_code == 0, compile_failures_result.stderr
    assert version_source_discovery_result.exit_code == 0, version_source_discovery_result.stderr
    assert version_rendering_result.exit_code == 0, version_rendering_result.stderr

    current_payload = current_result.json()
    chain_payload = chain_result.json()
    source_discovery_payload = source_discovery_result.json()
    schema_validation_payload = schema_validation_result.json()
    override_resolution_payload = override_resolution_result.json()
    hook_policy_payload = hook_policy_result.json()
    rendering_payload = rendering_result.json()
    compile_failures_payload = compile_failures_result.json()
    version_source_discovery_payload = version_source_discovery_result.json()
    version_rendering_payload = version_rendering_result.json()

    assert start_payload["status"] == "started"
    assert start_payload["requested_start_run"] is True
    assert start_payload["compile"]["status"] == "compiled"
    assert start_payload["run_admission"] is not None
    assert start_payload["lifecycle"]["lifecycle_state"] in {"RUNNING", "PAUSED_FOR_USER", "FAILED", "COMPLETE", "READY"}
    assert run_start_result.json()["status"] in {"admitted", "already_running", "blocked"}

    assert current_payload["node_version_id"] == node_version_id
    assert current_payload["task_count"] >= 1
    assert current_payload["subtask_count"] >= 1

    assert chain_payload["node_version_id"] == node_version_id
    assert len(chain_payload["chain"]) >= 1
    assert chain_payload["chain"][0]["task_key"]

    assert source_discovery_payload["node_version_id"] == node_version_id
    assert len(source_discovery_payload["discovery_order"]) >= 1
    assert len(source_discovery_payload["resolved_documents"]) >= 1

    assert schema_validation_payload["node_version_id"] == node_version_id
    assert schema_validation_payload["validated_document_count"] >= 1
    assert schema_validation_payload["family_counts"]

    assert override_resolution_payload["node_version_id"] == node_version_id
    assert "applied_overrides" in override_resolution_payload
    assert "resolved_documents" in override_resolution_payload

    assert hook_policy_payload["node_version_id"] == node_version_id
    assert "effective_policy" in hook_policy_payload
    assert "selected_hooks" in hook_policy_payload
    assert "expanded_steps" in hook_policy_payload

    assert rendering_payload["node_version_id"] == node_version_id
    assert rendering_payload["compiled_subtask_count"] >= 1
    assert rendering_payload["compiled_subtasks"]

    assert compile_failures_payload["failures"] == []

    assert version_source_discovery_payload["node_version_id"] == node_version_id
    assert version_source_discovery_payload["discovery_order"] == source_discovery_payload["discovery_order"]

    assert version_rendering_payload["node_version_id"] == node_version_id
    assert version_rendering_payload["compiled_subtask_count"] == rendering_payload["compiled_subtask_count"]
