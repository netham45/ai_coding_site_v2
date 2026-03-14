from __future__ import annotations

import subprocess
import time

import pytest


def _create_node(real_daemon_harness, *, kind: str, title: str, prompt: str, parent_id: str | None = None) -> str:
    command = ["node", "create", "--kind", kind, "--title", title, "--prompt", prompt]
    if parent_id is not None:
        command.extend(["--parent", parent_id])
    result = real_daemon_harness.cli(*command)
    assert result.exit_code == 0, result.stderr
    return str(result.json()["node_id"])


def _dedupe_preserving_order(values: list[str]) -> list[str]:
    ordered: list[str] = []
    for value in values:
        if value not in ordered:
            ordered.append(value)
    return ordered


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
@pytest.mark.parametrize(
    ("flow_id", "kind", "ancestor_kinds", "expected_task_keys"),
    [
        ("15", "epic", (), ["research_context", "execute_node", "validate_node", "review_node"]),
        ("16", "phase", ("epic",), ["research_context", "execute_node", "validate_node", "review_node"]),
        ("17", "plan", ("epic", "phase"), ["research_context", "execute_node", "validate_node", "review_node"]),
        ("18", "task", ("epic", "phase", "plan"), ["execute_node", "validate_node", "review_node"]),
    ],
)
def test_default_blueprint_flows_run_against_real_daemon_and_real_cli(
    real_daemon_harness,
    flow_id: str,
    kind: str,
    ancestor_kinds: tuple[str, ...],
    expected_task_keys: list[str],
) -> None:
    parent_id: str | None = None
    for index, ancestor_kind in enumerate(ancestor_kinds, start=1):
        parent_id = _create_node(
            real_daemon_harness,
            kind=ancestor_kind,
            title=f"Real E2E Flow {flow_id} Ancestor {index}",
            prompt=f"ancestor prompt {index}",
            parent_id=parent_id,
        )

    node_id = _create_node(
        real_daemon_harness,
        kind=kind,
        title=f"Real E2E Flow {flow_id} Node",
        prompt=f"{kind} blueprint prompt",
        parent_id=parent_id,
    )

    compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    current_result = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    chain_result = real_daemon_harness.cli("workflow", "chain", "--node", node_id)

    assert compile_result.exit_code == 0, compile_result.stderr
    assert current_result.exit_code == 0, current_result.stderr
    assert chain_result.exit_code == 0, chain_result.stderr

    current_payload = current_result.json()
    chain_payload = chain_result.json()
    task_keys = [item["task_key"] for item in current_payload["tasks"]]
    chain_task_keys = _dedupe_preserving_order([item["task_key"] for item in chain_payload["chain"]])

    start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert start_result.exit_code == 0, start_result.stderr
    assert start_result.json()["status"] == "admitted", start_result.stdout
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

    assert compile_result.json()["status"] == "compiled"
    assert task_keys == expected_task_keys
    assert chain_task_keys == expected_task_keys
    assert run_show_payload is not None, (
        "Expected the default blueprint flow to produce durable run state after a real started run and bound tmux/provider session.\n"
        f"flow_id={flow_id}\n"
        f"kind={kind}\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )
