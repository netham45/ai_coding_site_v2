from __future__ import annotations

import pytest


def _create_node(real_daemon_harness, *, kind: str, title: str, prompt: str, parent_id: str | None = None) -> str:
    command = ["node", "create", "--kind", kind, "--title", title, "--prompt", prompt]
    if parent_id is not None:
        command.extend(["--parent", parent_id])
    result = real_daemon_harness.cli(*command)
    assert result.exit_code == 0, result.stderr
    return str(result.json()["node_id"])


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
def test_flow_19_hook_expansion_compile_stage_runs_against_real_daemon_and_real_cli(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(session_backend="tmux")

    epic_id = _create_node(
        harness,
        kind="epic",
        title="Real E2E Flow 19 Epic",
        prompt="Create the ancestor required for the task hook-expansion compile-stage flow.",
    )
    phase_id = _create_node(
        harness,
        kind="phase",
        title="Real E2E Flow 19 Phase",
        prompt="Create the phase ancestor required for the task hook-expansion compile-stage flow.",
        parent_id=epic_id,
    )
    plan_id = _create_node(
        harness,
        kind="plan",
        title="Real E2E Flow 19 Plan",
        prompt="Create the plan ancestor required for the task hook-expansion compile-stage flow.",
        parent_id=phase_id,
    )
    task_id = _create_node(
        harness,
        kind="task",
        title="Real E2E Flow 19 Task",
        prompt="Compile a task workflow and inspect deterministic hook expansion over the real daemon and CLI boundary.",
        parent_id=plan_id,
    )

    compile_result = harness.cli("workflow", "compile", "--node", task_id)
    hooks_result = harness.cli("workflow", "hooks", "--node", task_id)
    hook_policy_result = harness.cli("workflow", "hook-policy", "--node", task_id)
    current_result = harness.cli("workflow", "current", "--node", task_id)

    assert compile_result.exit_code == 0, compile_result.stderr
    assert hooks_result.exit_code == 0, hooks_result.stderr
    assert hook_policy_result.exit_code == 0, hook_policy_result.stderr
    assert current_result.exit_code == 0, current_result.stderr

    compile_payload = compile_result.json()
    hooks_payload = hooks_result.json()
    hook_policy_payload = hook_policy_result.json()
    current_payload = current_result.json()

    assert compile_payload["status"] == "compiled"
    assert current_payload["tasks"]

    selected_hook_ids = [item["hook_id"] for item in hooks_payload["selected_hooks"]]
    expanded_step_keys = [item["source_subtask_key"] for item in hooks_payload["expanded_steps"]]

    assert selected_hook_ids == [
        "before_review_default",
        "before_testing_default",
        "before_validation_default",
        "after_node_complete_build_docs",
        "after_node_complete_update_provenance",
    ]
    assert hook_policy_payload["selected_hooks"][0]["hook_id"] == "before_review_default"
    assert hook_policy_payload["policy_impact"]["node_kind"] == "task"
    assert expanded_step_keys == [
        "validate_node.hook.before_validation_default.1",
        "review_node.hook.before_review_default.1",
    ]
