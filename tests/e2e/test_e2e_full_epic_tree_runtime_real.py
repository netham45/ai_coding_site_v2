from __future__ import annotations

import pytest


def _cli_json(real_daemon_harness, *args: str) -> dict[str, object]:
    result = real_daemon_harness.cli(*args)
    assert result.exit_code == 0, result.stderr
    return result.json()


@pytest.mark.e2e_real
def test_e2e_full_epic_tree_runtime_real(real_daemon_harness, tmp_path) -> None:
    start_payload = _cli_json(
        real_daemon_harness,
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Full Epic Tree",
        "--prompt",
        "Create one epic, descend through phase, plan, and task, then execute the leaf task through real runtime commands.",
        "--no-run",
    )
    epic_id = str(start_payload["node"]["node_id"])

    epic_tree_before = _cli_json(real_daemon_harness, "tree", "show", "--node", epic_id, "--full")
    epic_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", epic_id)
    epic_children = _cli_json(real_daemon_harness, "node", "children", "--node", epic_id, "--versions")

    assert epic_tree_before["root_node_id"] == epic_id
    assert len(epic_tree_before["nodes"]) == 1
    assert epic_materialize["child_count"] == 2
    assert {child["layout_child_id"] for child in epic_materialize["children"]} == {"discovery", "implementation"}
    assert len(epic_children["children"]) == 2

    discovery_phase = next(child for child in epic_materialize["children"] if child["layout_child_id"] == "discovery")
    discovery_phase_id = str(discovery_phase["node_id"])
    phase_show = _cli_json(real_daemon_harness, "node", "show", "--node", discovery_phase_id)
    phase_workflow = _cli_json(real_daemon_harness, "workflow", "current", "--node", discovery_phase_id)
    phase_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", discovery_phase_id)

    assert phase_show["kind"] == "phase"
    assert phase_show["parent_node_id"] == epic_id
    assert phase_workflow["logical_node_id"] == discovery_phase_id
    assert phase_materialize["child_count"] == 1

    plan_node = phase_materialize["children"][0]
    plan_id = str(plan_node["node_id"])
    plan_show = _cli_json(real_daemon_harness, "node", "show", "--node", plan_id)
    plan_workflow = _cli_json(real_daemon_harness, "workflow", "current", "--node", plan_id)
    plan_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", plan_id)

    assert plan_show["kind"] == "plan"
    assert plan_show["parent_node_id"] == discovery_phase_id
    assert plan_workflow["logical_node_id"] == plan_id
    assert plan_materialize["child_count"] == 1

    task_node = plan_materialize["children"][0]
    task_id = str(task_node["node_id"])
    task_show = _cli_json(real_daemon_harness, "node", "show", "--node", task_id)
    task_workflow = _cli_json(real_daemon_harness, "workflow", "current", "--node", task_id)
    full_tree = _cli_json(real_daemon_harness, "tree", "show", "--node", epic_id, "--full")

    assert task_show["kind"] == "task"
    assert task_show["parent_node_id"] == plan_id
    assert task_show["lifecycle_state"] == "READY"
    assert task_workflow["logical_node_id"] == task_id
    assert len(full_tree["nodes"]) == 5
    assert {node["kind"] for node in full_tree["nodes"]} == {"epic", "phase", "plan", "task"}

    run_start = _cli_json(real_daemon_harness, "node", "run", "start", "--node", task_id)
    subtask_current = _cli_json(real_daemon_harness, "subtask", "current", "--node", task_id)
    subtask_prompt = _cli_json(real_daemon_harness, "subtask", "prompt", "--node", task_id)
    subtask_context = _cli_json(real_daemon_harness, "subtask", "context", "--node", task_id)
    compiled_subtask_id = str(subtask_current["state"]["current_compiled_subtask_id"])

    assert run_start["status"] == "admitted"
    assert run_start["current_state"] == "RUNNING"
    assert subtask_current["run"]["logical_node_id"] == task_id
    assert subtask_prompt["compiled_subtask_id"] == compiled_subtask_id
    assert subtask_prompt["prompt_text"]
    assert subtask_context["compiled_subtask_id"] == compiled_subtask_id
    assert subtask_context["input_context_json"]["stage_context_json"]

    start_subtask = _cli_json(
        real_daemon_harness,
        "subtask",
        "start",
        "--node",
        task_id,
        "--compiled-subtask",
        compiled_subtask_id,
    )
    summary_path = tmp_path / "full-epic-tree-summary.md"
    summary_path.write_text("completed the leaf execution step in the full epic tree e2e test", encoding="utf-8")
    register_summary = _cli_json(
        real_daemon_harness,
        "summary",
        "register",
        "--node",
        task_id,
        "--type",
        "subtask",
        "--file",
        str(summary_path),
    )
    complete_subtask = _cli_json(
        real_daemon_harness,
        "subtask",
        "complete",
        "--node",
        task_id,
        "--compiled-subtask",
        compiled_subtask_id,
        "--summary",
        "completed the leaf task execution step",
    )
    advance = _cli_json(real_daemon_harness, "workflow", "advance", "--node", task_id)
    run_show = _cli_json(real_daemon_harness, "node", "run", "show", "--node", task_id)
    summary_history = _cli_json(real_daemon_harness, "summary", "history", "--node", task_id)

    assert start_subtask["latest_attempt"]["compiled_subtask_id"] == compiled_subtask_id
    assert register_summary["compiled_subtask_id"] == compiled_subtask_id
    assert complete_subtask["latest_attempt"]["status"] == "COMPLETE"
    assert advance["run"]["logical_node_id"] == task_id
    assert advance["run"]["run_status"] in {"RUNNING", "COMPLETED"}
    assert run_show["run"]["logical_node_id"] == task_id
    assert run_show["run"]["run_status"] in {"RUNNING", "COMPLETED"}
    assert summary_history["summaries"]
    assert summary_history["summaries"][0]["id"] == register_summary["summary_id"]
