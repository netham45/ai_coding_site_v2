from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_06_inspect_state_and_blockers_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 06 Node",
        "--prompt",
        "Inspect state, workflow, sources, and blockers through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    node_version_id = str(start_payload["node_version_id"])

    node_show_result = real_daemon_harness.cli("node", "show", "--node", node_id)
    tree_result = real_daemon_harness.cli("tree", "show", "--node", node_id, "--full")
    task_current_result = real_daemon_harness.cli("task", "current", "--node", node_id)
    subtask_current_result = real_daemon_harness.cli("subtask", "current", "--node", node_id)
    blockers_result = real_daemon_harness.cli("node", "blockers", "--node", node_id)
    sources_result = real_daemon_harness.cli("yaml", "sources", "--node", node_id)
    workflow_show_result = real_daemon_harness.cli("workflow", "show", "--node", node_id)

    assert node_show_result.exit_code == 0, node_show_result.stderr
    assert tree_result.exit_code == 0, tree_result.stderr
    assert task_current_result.exit_code == 0, task_current_result.stderr
    assert subtask_current_result.exit_code == 0, subtask_current_result.stderr
    assert blockers_result.exit_code == 0, blockers_result.stderr
    assert sources_result.exit_code == 0, sources_result.stderr
    assert workflow_show_result.exit_code == 0, workflow_show_result.stderr

    node_show_payload = node_show_result.json()
    tree_payload = tree_result.json()
    task_current_payload = task_current_result.json()
    subtask_current_payload = subtask_current_result.json()
    blockers_payload = blockers_result.json()
    sources_payload = sources_result.json()
    workflow_show_payload = workflow_show_result.json()

    assert node_show_payload["node_id"] == node_id
    assert node_show_payload["authoritative_node_version_id"] == node_version_id
    assert node_show_payload["lifecycle_state"] in {"RUNNING", "READY"}
    assert node_show_payload["run_status"] == "RUNNING"

    assert tree_payload["root_node_id"] == node_id
    assert len(tree_payload["nodes"]) == 1
    assert tree_payload["nodes"][0]["node_id"] == node_id
    assert tree_payload["nodes"][0]["depth"] == 0

    assert task_current_payload["node_id"] == node_id
    assert task_current_payload["current_task"] is not None
    assert task_current_payload["current_task"]["task_key"]

    assert subtask_current_payload["run"]["logical_node_id"] == node_id
    assert subtask_current_payload["state"]["node_run_id"] == start_payload["run_progress"]["run"]["id"]
    assert subtask_current_payload["current_subtask"] is not None
    assert subtask_current_payload["current_subtask"]["id"] == subtask_current_payload["state"]["current_compiled_subtask_id"]
    assert subtask_current_payload["current_subtask"]["source_subtask_key"]

    assert isinstance(blockers_payload, list)

    assert sources_payload["node_version_id"] == node_version_id
    assert sources_payload["source_documents"]

    assert workflow_show_payload["node_version_id"] == node_version_id
    assert workflow_show_payload["logical_node_id"] == node_id
    assert workflow_show_payload["task_count"] >= 1
    assert workflow_show_payload["subtask_count"] >= 1
