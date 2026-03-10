from __future__ import annotations

import subprocess
import time

import pytest


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux capture failed] {result.stderr.strip()}"
    return result.stdout


def _write_workspace_quality_inputs(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    override_path = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_test_node.yaml"
    source_path = workspace_root / "src" / "quality_app.py"

    project_policy.parent.mkdir(parents=True, exist_ok=True)
    override_path.parent.mkdir(parents=True, exist_ok=True)
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
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
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
    override_path.write_text(
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
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
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
    bind_result = real_daemon_harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    bind_payload = bind_result.json()
    session_name = str(bind_payload["session_name"])

    quality_chain_payload = None
    last_run_payload = None
    last_pane_text = ""
    deadline = time.time() + 90.0
    while time.time() < deadline:
        run_show_result = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
        quality_chain_result = real_daemon_harness.cli("node", "quality-chain", "--node", node_id)
        assert run_show_result.exit_code == 0, run_show_result.stderr
        assert quality_chain_result.exit_code == 0, quality_chain_result.stderr
        last_run_payload = run_show_result.json()
        quality_chain_payload = quality_chain_result.json()
        last_pane_text = _tmux_capture(session_name)
        if quality_chain_payload["run_status"] == "COMPLETE":
            break
        time.sleep(2.0)

    assert quality_chain_payload is not None
    assert last_run_payload is not None
    assert quality_chain_payload["run_status"] == "COMPLETE", (
        "Expected the real primary tmux/Codex session to drive the node through the quality chain without manual "
        "subtask completion or workflow advancement from the test.\n"
        f"session_name={session_name}\n"
        f"final_run_status={last_run_payload['run']['run_status']}\n"
        f"pane_text=\n{last_pane_text}"
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

    assert bind_payload["logical_node_id"] == node_id
    assert bind_payload["tmux_session_exists"] is True
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
