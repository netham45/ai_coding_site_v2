from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_08_handle_failure_and_escalate_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    parent_start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 08 Parent",
        "--prompt",
        "Run a parent node and respond to a real failed child through the daemon and CLI runtime.",
    )
    assert parent_start_result.exit_code == 0, parent_start_result.stderr
    parent_payload = parent_start_result.json()
    parent_id = str(parent_payload["node"]["node_id"])

    materialize_result = real_daemon_harness.cli("node", "materialize-children", "--node", parent_id)
    assert materialize_result.exit_code == 0, materialize_result.stderr
    materialize_payload = materialize_result.json()
    child_record = next(child for child in materialize_payload["children"] if child["layout_child_id"] == "discovery")
    child_id = str(child_record["node_id"])

    child_show_result = real_daemon_harness.cli("node", "show", "--node", child_id)
    child_run_start_result = real_daemon_harness.cli("node", "run", "start", "--node", child_id)

    assert child_show_result.exit_code == 0, child_show_result.stderr
    assert child_run_start_result.exit_code == 0, child_run_start_result.stderr

    child_current_result = real_daemon_harness.cli("subtask", "current", "--node", child_id)
    assert child_current_result.exit_code == 0, child_current_result.stderr
    child_current_payload = child_current_result.json()
    child_compiled_subtask_id = str(child_current_payload["state"]["current_compiled_subtask_id"])

    child_subtask_start_result = real_daemon_harness.cli(
        "subtask",
        "start",
        "--node",
        child_id,
        "--compiled-subtask",
        child_compiled_subtask_id,
    )
    child_fail_result = real_daemon_harness.cli(
        "subtask",
        "fail",
        "--node",
        child_id,
        "--compiled-subtask",
        child_compiled_subtask_id,
        "--summary",
        "environment timeout on remote tool",
    )
    parent_respond_result = real_daemon_harness.cli(
        "node",
        "respond-to-child-failure",
        "--node",
        parent_id,
        "--child",
        child_id,
        "--action",
        "retry_child",
    )
    child_failures_result = real_daemon_harness.cli("node", "child-failures", "--node", parent_id)
    decision_history_result = real_daemon_harness.cli("node", "decision-history", "--node", parent_id)

    assert child_subtask_start_result.exit_code == 0, child_subtask_start_result.stderr
    assert child_fail_result.exit_code == 0, child_fail_result.stderr
    assert parent_respond_result.exit_code == 0, parent_respond_result.stderr
    assert child_failures_result.exit_code == 0, child_failures_result.stderr
    assert decision_history_result.exit_code == 0, decision_history_result.stderr

    child_fail_payload = child_fail_result.json()
    parent_respond_payload = parent_respond_result.json()
    child_failures_payload = child_failures_result.json()
    decision_history_payload = decision_history_result.json()

    assert materialize_payload["status"] == "created"
    assert child_record["kind"] == "phase"
    assert child_record["scheduling_status"] == "ready"
    assert child_show_result.json()["lifecycle_state"] == "READY"
    assert child_fail_payload["run"]["logical_node_id"] == child_id
    assert child_fail_payload["run"]["run_status"] == "FAILED"
    assert child_fail_payload["latest_attempt"]["status"] == "FAILED"
    assert child_fail_payload["latest_attempt"]["summary"] == "environment timeout on remote tool"

    assert parent_respond_payload["node_id"] == parent_id
    assert parent_respond_payload["child_node_id"] == child_id
    assert parent_respond_payload["decision_type"] == "retry_child"
    assert parent_respond_payload["decision_reason"] == "operator override selected 'retry_child'"
    assert parent_respond_payload["options_considered"] == [
        "retry_child",
        "regenerate_child",
        "replan_parent",
        "pause_for_user",
    ]
    assert parent_respond_payload["counters"]["failure_count_from_children"] >= 1

    assert child_failures_payload["node_id"] == parent_id
    assert child_failures_payload["failure_count_from_children"] == 1
    assert child_failures_payload["counters"][0]["child_node_id"] == child_id
    assert child_failures_payload["counters"][0]["last_decision_type"] == "retry_child"
    assert child_failures_payload["counters"][0]["last_failure_summary"] == "environment timeout on remote tool"

    assert decision_history_payload["node_id"] == parent_id
    assert decision_history_payload["decisions"]
    assert decision_history_payload["decisions"][-1]["decision_type"] == "parent_retry_child"
