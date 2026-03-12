from __future__ import annotations

import subprocess
import time

import pytest


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_operator_cli_surface_inspects_and_pauses_a_real_run(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Operator Surface Node",
        "--prompt",
        "Exercise operator inspection and pause commands through the real daemon and real CLI path.",
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

    assert run_show_payload is not None, (
        "Expected the operator CLI surface flow to produce durable run state after binding a real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )

    workflow_current_result = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    node_show_result = real_daemon_harness.cli("node", "show", "--node", node_id)
    tree_result = real_daemon_harness.cli("tree", "show", "--node", node_id, "--full")
    task_current_result = real_daemon_harness.cli("task", "current", "--node", node_id)
    subtask_current_result = real_daemon_harness.cli("subtask", "current", "--node", node_id)
    blockers_result = real_daemon_harness.cli("node", "blockers", "--node", node_id)
    sources_result = real_daemon_harness.cli("yaml", "sources", "--node", node_id)
    pause_result = real_daemon_harness.cli("node", "pause", "--node", node_id)
    pause_state_result = real_daemon_harness.cli("node", "pause-state", "--node", node_id)
    events_result = real_daemon_harness.cli("node", "events", "--node", node_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert workflow_current_result.exit_code == 0, workflow_current_result.stderr
    assert node_show_result.exit_code == 0, node_show_result.stderr
    assert tree_result.exit_code == 0, tree_result.stderr
    assert task_current_result.exit_code == 0, task_current_result.stderr
    assert subtask_current_result.exit_code == 0, subtask_current_result.stderr
    assert blockers_result.exit_code == 0, blockers_result.stderr
    assert sources_result.exit_code == 0, sources_result.stderr
    assert pause_result.exit_code == 0, pause_result.stderr
    assert pause_state_result.exit_code == 0, pause_state_result.stderr
    assert events_result.exit_code == 0, events_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    workflow_current_payload = workflow_current_result.json()
    node_show_payload = node_show_result.json()
    tree_payload = tree_result.json()
    task_current_payload = task_current_result.json()
    subtask_current_payload = subtask_current_result.json()
    blockers_payload = blockers_result.json()
    sources_payload = sources_result.json()
    pause_state_payload = pause_state_result.json()
    events_payload = events_result.json()
    audit_payload = audit_result.json()

    assert start_payload["run_progress"]["run"]["run_status"] == "RUNNING"
    assert workflow_current_payload["logical_node_id"] == node_id
    assert workflow_current_payload["node_version_id"] == node_version_id

    assert node_show_payload["node_id"] == node_id
    assert node_show_payload["authoritative_node_version_id"] == node_version_id
    assert node_show_payload["run_status"] in {"RUNNING", "PAUSED"}

    assert tree_payload["root_node_id"] == node_id
    assert len(tree_payload["nodes"]) == 1
    assert tree_payload["nodes"][0]["node_id"] == node_id

    assert task_current_payload["node_id"] == node_id
    assert task_current_payload["current_task"] is not None
    assert task_current_payload["current_task"]["task_key"]

    assert subtask_current_payload["run"]["logical_node_id"] == node_id
    assert subtask_current_payload["current_subtask"] is not None
    assert subtask_current_payload["current_subtask"]["source_subtask_key"]

    assert isinstance(blockers_payload, list)
    assert sources_payload["node_version_id"] == node_version_id
    assert sources_payload["source_documents"]

    assert pause_state_payload["lifecycle_state"] == "PAUSED_FOR_USER"
    assert pause_state_payload["pause_flag_name"] == "manual_pause"
    assert events_payload["events"]
    assert {item["command"] for item in events_payload["events"]} >= {"node.run.start", "node.pause", "pause_entered"}

    assert audit_payload["node_id"] == node_id
    assert audit_payload["authoritative_version_id"] == node_version_id
    assert audit_payload["run_count"] >= 1
