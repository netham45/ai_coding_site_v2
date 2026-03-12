from __future__ import annotations

import subprocess
import time

import pytest


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_01_create_top_level_node_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 01 Epic",
        "--prompt",
        "Create a top level epic through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    node_version_id = str(start_payload["node_version_id"])

    bind_result = real_daemon_harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])

    run_show_payload = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        run_show = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
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

    workflow_current = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    node_show = real_daemon_harness.cli("node", "show", "--node", node_id)
    node_versions = real_daemon_harness.cli("node", "versions", "--node", node_id)
    node_sources = real_daemon_harness.cli("node", "sources", "--node", node_id)
    resolved_version_id = str(node_versions.json()["versions"][0]["id"])
    branch_show = real_daemon_harness.cli("git", "branch", "show", "--version", resolved_version_id)
    node_audit = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert workflow_current.exit_code == 0, workflow_current.stderr
    assert node_show.exit_code == 0, node_show.stderr
    assert node_versions.exit_code == 0, node_versions.stderr
    assert node_sources.exit_code == 0, node_sources.stderr
    assert branch_show.exit_code == 0, branch_show.stderr
    assert node_audit.exit_code == 0, node_audit.stderr

    workflow_payload = workflow_current.json()
    node_payload = node_show.json()
    versions_payload = node_versions.json()
    sources_payload = node_sources.json()
    branch_payload = branch_show.json()
    audit_payload = node_audit.json()

    assert start_payload["status"] == "started"
    assert start_payload["requested_start_run"] is True
    assert start_payload["compile"]["status"] == "compiled"
    assert start_payload["lifecycle"]["lifecycle_state"] in {"RUNNING", "READY", "PAUSED_FOR_USER", "FAILED"}
    assert start_payload["run_admission"] is not None
    assert run_show_payload is not None, (
        "Expected the real top-level workflow start to produce durable run state after binding a real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )

    assert workflow_payload["logical_node_id"] == node_id
    assert workflow_payload["node_version_id"] == node_version_id
    assert workflow_payload["task_count"] >= 1

    assert node_payload["node_id"] == node_id
    assert node_payload["kind"] == "epic"
    assert node_payload["lifecycle_state"] in {"RUNNING", "PAUSED_FOR_USER", "FAILED", "COMPLETE", "READY"}
    assert node_payload["authoritative_node_version_id"] == node_version_id

    assert versions_payload["versions"][0]["id"] == node_version_id
    assert sources_payload["node_version_id"] == node_version_id
    assert len(sources_payload["source_documents"]) >= 1
    assert branch_payload["node_version_id"] == resolved_version_id
    assert branch_payload["active_branch_name"]

    assert audit_payload["node_id"] == node_id
    assert audit_payload["authoritative_version_id"] == node_version_id
    assert audit_payload["current_workflow"]["node_version_id"] == node_version_id
    assert audit_payload["source_lineage"]["node_version_id"] == node_version_id
    assert audit_payload["run_count"] >= 1
    assert audit_payload["compile_failures"] == []
