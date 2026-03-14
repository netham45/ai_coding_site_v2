from __future__ import annotations

import time

import pytest


def _write_workspace_quality_inputs(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    entry_override_path = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_entry_task.yaml"
    tasks_override_path = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_quality_tasks.yaml"
    source_path = workspace_root / "src" / "quality_app.py"

    project_policy.parent.mkdir(parents=True, exist_ok=True)
    entry_override_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.parent.mkdir(parents=True, exist_ok=True)

    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Real E2E flow 09 project policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: true",
                "  runtime_policy_refs:",
                "    - runtime/session_defaults.yaml",
                "    - runtime/idle_nudge_policy.yaml",
                "  hook_refs: []",
                "  review_refs:",
                "    - reviews/policy_compliance_review.yaml",
                "  testing_refs:",
                "    - testing/default_smoke_test_gate.yaml",
                "  docs_refs:",
                "    - docs/default_doc_views.yaml",
                "  enabled_node_kinds:",
                "    - epic",
                "    - phase",
                "    - plan",
                "    - task",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    entry_override_path.write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace",
                "value:",
                "  entry_task: validate_node",
            ]
        ),
        encoding="utf-8",
    )
    tasks_override_path.write_text(
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
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    source_path.write_text(
        "\n".join(
            [
                "def normalize_name(name: str) -> str:",
                "    return name.strip().title()",
                "",
                "class QualityGreeter:",
                "    def greet(self, name: str) -> str:",
                "        return normalize_name(name)",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
def test_flow_09_run_quality_gates_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    _write_workspace_quality_inputs(real_daemon_harness.workspace_root)

    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 09 Node",
        "--prompt",
        "Run the full quality chain through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    run_start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert run_start_result.exit_code == 0, run_start_result.stderr

    current_result = None
    deadline = time.time() + 20.0
    while time.time() < deadline:
        candidate = real_daemon_harness.cli("subtask", "current", "--node", node_id)
        if candidate.exit_code == 0:
            current_result = candidate
            break
        time.sleep(1.0)

    assert current_result is not None, (
        "Expected a live run before invoking the quality chain.\n"
        f"workflow_start={start_payload}\n"
        f"node_run_start={run_start_result.stdout or run_start_result.stderr}"
    )
    assert str(current_result.json()["current_subtask"]["source_subtask_key"]).startswith("validate_node.")

    quality_chain_payload = None
    last_run_payload = None
    deadline = time.time() + 90.0
    while time.time() < deadline:
        run_show_result = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
        quality_chain_result = real_daemon_harness.cli("node", "quality-chain", "--node", node_id)
        assert run_show_result.exit_code == 0, run_show_result.stderr
        assert quality_chain_result.exit_code == 0, quality_chain_result.stderr
        last_run_payload = run_show_result.json()
        quality_chain_payload = quality_chain_result.json()
        if quality_chain_payload["run_status"] == "COMPLETE":
            break
        time.sleep(2.0)

    assert quality_chain_payload is not None
    assert last_run_payload is not None
    assert quality_chain_payload["run_status"] == "COMPLETE", (
        "Expected the real daemon-owned quality-chain command to drive the node through the built-in quality stages "
        "without manual subtask completion or workflow advancement from the test.\n"
        f"final_run_status={last_run_payload['run']['run_status']}\n"
        f"quality_chain_status={quality_chain_payload['run_status']}"
    )

    validation_result = real_daemon_harness.cli("validation", "show", "--node", node_id)
    review_result = real_daemon_harness.cli("review", "show", "--node", node_id)
    testing_result = real_daemon_harness.cli("testing", "show", "--node", node_id)
    docs_result = real_daemon_harness.cli("docs", "list", "--node", node_id)
    summary_history_result = real_daemon_harness.cli("summary", "history", "--node", node_id)
    rationale_result = real_daemon_harness.cli("rationale", "show", "--node", node_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert validation_result.exit_code == 0, validation_result.stderr
    assert review_result.exit_code == 0, review_result.stderr
    assert testing_result.exit_code == 0, testing_result.stderr
    assert docs_result.exit_code == 0, docs_result.stderr
    assert summary_history_result.exit_code == 0, summary_history_result.stderr
    assert rationale_result.exit_code == 0, rationale_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    validation_payload = validation_result.json()
    review_payload = review_result.json()
    testing_payload = testing_result.json()
    docs_payload = docs_result.json()
    summary_history_payload = summary_history_result.json()
    rationale_payload = rationale_result.json()
    audit_payload = audit_result.json()

    assert start_payload["node"]["node_id"] == node_id
    assert quality_chain_payload["run_status"] == "COMPLETE"
    assert quality_chain_payload["executed_stage_types"] == ["validate", "review", "run_tests"]
    assert quality_chain_payload["validation"]["status"] == "passed"
    assert quality_chain_payload["review"]["status"] == "passed"
    assert quality_chain_payload["testing"]["status"] == "passed"
    assert quality_chain_payload["provenance"]["entity_count"] > 0
    assert quality_chain_payload["docs"]
    assert quality_chain_payload["final_summary"]["summary_path"] == "summaries/final.md"

    assert validation_payload["status"] == "passed"
    assert review_payload["status"] == "passed"
    assert testing_payload["status"] == "passed"
    assert docs_payload["documents"]
    assert any(item["summary_type"] == "node" and item["summary_path"] == "summaries/final.md" for item in summary_history_payload["summaries"])
    assert rationale_payload["node_id"] == node_id
    assert audit_payload["node_id"] == node_id
    assert audit_payload["node_summary"]["node_id"] == node_id
    assert audit_payload["run_count"] >= 1
