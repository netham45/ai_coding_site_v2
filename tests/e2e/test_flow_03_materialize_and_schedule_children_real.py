from __future__ import annotations

import subprocess
import time

import pytest


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_03_materialize_and_schedule_children_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 03 Epic",
        "--prompt",
        "Materialize built-in child phases through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])

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

    before_result = real_daemon_harness.cli("node", "child-materialization", "--node", node_id)
    materialize_result = real_daemon_harness.cli("node", "materialize-children", "--node", node_id)
    after_result = real_daemon_harness.cli("node", "child-materialization", "--node", node_id)
    children_result = real_daemon_harness.cli("node", "children", "--node", node_id, "--versions")
    tree_result = real_daemon_harness.cli("tree", "show", "--node", node_id, "--full")

    assert before_result.exit_code == 0, before_result.stderr
    assert materialize_result.exit_code == 0, materialize_result.stderr
    assert after_result.exit_code == 0, after_result.stderr
    assert children_result.exit_code == 0, children_result.stderr
    assert tree_result.exit_code == 0, tree_result.stderr

    before_payload = before_result.json()
    materialize_payload = materialize_result.json()
    after_payload = after_result.json()
    children_payload = children_result.json()
    tree_payload = tree_result.json()

    assert start_payload["status"] == "started"
    assert start_payload["requested_start_run"] is True
    assert run_show_payload is not None, (
        "Expected the real started workflow to produce durable run state before child materialization is exercised.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )

    assert materialize_payload["status"] == "created"
    assert materialize_payload["authority_mode"] == "layout_authoritative"
    assert materialize_payload["child_count"] == 2
    assert materialize_payload["created_count"] == 2
    assert materialize_payload["ready_child_count"] == 1
    assert materialize_payload["blocked_child_count"] == 1

    child_by_layout_id = {child["layout_child_id"]: child for child in materialize_payload["children"]}
    assert set(child_by_layout_id) == {"discovery", "implementation"}
    assert child_by_layout_id["discovery"]["kind"] == "phase"
    assert child_by_layout_id["discovery"]["scheduling_status"] == "ready"
    assert child_by_layout_id["implementation"]["kind"] == "phase"
    assert child_by_layout_id["implementation"]["scheduling_status"] == "blocked_on_dependency"
    assert child_by_layout_id["implementation"]["scheduling_reason"] == "blocked_on_dependency"
    assert child_by_layout_id["implementation"]["blockers"]

    assert after_payload["status"] == "materialized"
    assert after_payload["authority_mode"] == "layout_authoritative"
    assert after_payload["child_count"] == 2
    assert after_payload["ready_child_count"] == 0
    assert after_payload["blocked_child_count"] == 2

    assert len(children_payload["children"]) == 2
    assert {child["kind"] for child in children_payload["children"]} == {"phase"}
    assert children_payload["include_versions"] is True
    assert all("authoritative_node_version_id" in child for child in children_payload["children"])

    assert tree_payload["root_node_id"] == node_id
    assert len(tree_payload["nodes"]) == 3
    root_row = next(item for item in tree_payload["nodes"] if item["depth"] == 0)
    assert root_row["node_id"] == node_id
    child_rows = {child["title"]: child for child in tree_payload["nodes"] if child["depth"] == 1}
    assert child_rows["Discovery And Framing"]["scheduling_status"] == "already_running"
    assert child_rows["Implementation"]["scheduling_status"] == "blocked"
