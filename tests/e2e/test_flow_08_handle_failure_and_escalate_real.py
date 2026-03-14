from __future__ import annotations

import subprocess
import time
from pathlib import Path

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


def _first_child(tree_payload: dict[str, object], *, parent_id: str, kind: str) -> dict[str, object] | None:
    for node in tree_payload["nodes"]:
        if node["parent_node_id"] == parent_id and node["kind"] == kind:
            return node
    return None


def _write_scoped_parent_overrides(workspace_root: Path, *, node_kinds: tuple[str, ...]) -> None:
    overrides_root = workspace_root / "resources" / "yaml" / "overrides" / "nodes"
    overrides_root.mkdir(parents=True, exist_ok=True)
    for node_kind in node_kinds:
        (overrides_root / f"{node_kind}_entry_task.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace",
                    "value:",
                    "  entry_task: generate_child_layout",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        (overrides_root / f"{node_kind}_available_tasks.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace_list",
                    "value:",
                    "  available_tasks:",
                    "    - generate_child_layout",
                    "    - review_child_layout",
                    "    - spawn_children",
                ]
            )
            + "\n",
            encoding="utf-8",
        )


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_08_handle_failure_and_escalate_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    _write_scoped_parent_overrides(real_daemon_harness.workspace_root, node_kinds=("epic",))
    parent_start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 08 Parent",
        "--prompt",
        "Run a parent node and respond to a real failed child through the daemon and CLI runtime. "
        "Create exactly one phase child through the runtime command loop before that child runs.",
    )
    assert parent_start_result.exit_code == 0, parent_start_result.stderr
    parent_payload = parent_start_result.json()
    parent_id = str(parent_payload["node"]["node_id"])

    parent_bind_result = real_daemon_harness.cli("session", "bind", "--node", parent_id)
    assert parent_bind_result.exit_code == 0, parent_bind_result.stderr
    parent_bind_payload = parent_bind_result.json()
    parent_session_name = str(parent_bind_payload["session_name"])

    child_record = None
    tree_payload = None
    child_wait_deadline = time.time() + 120.0
    while time.time() < child_wait_deadline:
        tree_result = real_daemon_harness.cli("tree", "show", "--node", parent_id, "--full")
        assert tree_result.exit_code == 0, tree_result.stderr
        tree_payload = tree_result.json()
        child_record = _first_child(tree_payload, parent_id=parent_id, kind="phase")
        if child_record is not None:
            break
        time.sleep(2.0)

    assert child_record is not None, (
        "Expected the live parent tmux/Codex session to create a phase child before Flow 08 proceeds.\n"
        f"parent_session_name={parent_session_name}\n"
        f"parent_pane=\n{_tmux_capture(parent_session_name)}\n"
        f"tree_payload={tree_payload}"
    )
    child_id = str(child_record["node_id"])

    child_show_result = real_daemon_harness.cli("node", "show", "--node", child_id)
    child_run_start_result = real_daemon_harness.cli("node", "run", "start", "--node", child_id)
    child_bind_result = real_daemon_harness.cli("session", "bind", "--node", child_id)

    assert child_show_result.exit_code == 0, child_show_result.stderr
    assert child_run_start_result.exit_code == 0, child_run_start_result.stderr
    assert child_bind_result.exit_code == 0, child_bind_result.stderr

    child_bind_payload = child_bind_result.json()
    child_session_name = str(child_bind_payload["session_name"])
    child_progress_payload = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        child_run_show_result = real_daemon_harness.cli("node", "run", "show", "--node", child_id)
        assert child_run_show_result.exit_code == 0, child_run_show_result.stderr
        child_progress_payload = child_run_show_result.json()
        last_pane_text = _tmux_capture(child_session_name)
        run_status = child_progress_payload["run"]["run_status"]
        if run_status in {"FAILED", "PAUSED", "COMPLETED"}:
            break
        time.sleep(2.0)

    assert child_progress_payload is not None
    assert child_progress_payload["run"]["run_status"] == "FAILED", (
        "Expected the real child tmux/Codex session to produce a durable failed child run before the parent "
        "responded to the failure.\n"
        f"child_session_name={child_session_name}\n"
        f"final_run_status={child_progress_payload['run']['run_status']}\n"
        f"pane_text=\n{last_pane_text}"
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

    assert parent_respond_result.exit_code == 0, parent_respond_result.stderr
    assert child_failures_result.exit_code == 0, child_failures_result.stderr
    assert decision_history_result.exit_code == 0, decision_history_result.stderr

    parent_respond_payload = parent_respond_result.json()
    child_failures_payload = child_failures_result.json()
    decision_history_payload = decision_history_result.json()

    assert child_record["kind"] == "phase"
    assert child_record["scheduling_status"] == "ready"
    assert child_show_result.json()["lifecycle_state"] == "READY"
    assert child_bind_payload["logical_node_id"] == child_id
    assert child_bind_payload["tmux_session_exists"] is True
    assert child_progress_payload["run"]["logical_node_id"] == child_id
    assert child_progress_payload["run"]["run_status"] == "FAILED"
    assert child_progress_payload["latest_attempt"] is not None
    assert child_progress_payload["latest_attempt"]["status"] == "FAILED"

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
    assert child_failures_payload["counters"][0]["last_failure_summary"]

    assert decision_history_payload["node_id"] == parent_id
    assert decision_history_payload["decisions"]
    assert decision_history_payload["decisions"][-1]["decision_type"] == "parent_retry_child"
