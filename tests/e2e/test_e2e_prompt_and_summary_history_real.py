from __future__ import annotations

import subprocess
import time

import pytest


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_prompt_and_summary_history_real(real_daemon_harness, tmp_path) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Prompt History Node",
        "--prompt",
        "Exercise prompt delivery and summary history through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    node_id = str(start_result.json()["node"]["node_id"])

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
        "Expected the prompt/summary history flow to produce durable run state after binding a real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )

    current_result = real_daemon_harness.cli("subtask", "current", "--node", node_id)
    assert current_result.exit_code == 0, current_result.stderr
    compiled_subtask_id = str(current_result.json()["state"]["current_compiled_subtask_id"])

    prompt_result = real_daemon_harness.cli("subtask", "prompt", "--node", node_id)
    context_result = real_daemon_harness.cli("subtask", "context", "--node", node_id)
    start_subtask_result = real_daemon_harness.cli(
        "subtask",
        "start",
        "--node",
        node_id,
        "--compiled-subtask",
        compiled_subtask_id,
    )
    heartbeat_result = real_daemon_harness.cli(
        "subtask",
        "heartbeat",
        "--node",
        node_id,
        "--compiled-subtask",
        compiled_subtask_id,
    )

    summary_file = tmp_path / "prompt-history-summary.md"
    summary_file.write_text("prompt history summary body", encoding="utf-8")
    summary_result = real_daemon_harness.cli(
        "summary",
        "register",
        "--node",
        node_id,
        "--file",
        str(summary_file),
        "--type",
        "subtask",
    )

    assert prompt_result.exit_code == 0, prompt_result.stderr
    assert context_result.exit_code == 0, context_result.stderr
    assert start_subtask_result.exit_code == 0, start_subtask_result.stderr
    assert heartbeat_result.exit_code == 0, heartbeat_result.stderr
    assert summary_result.exit_code == 0, summary_result.stderr

    prompt_payload = prompt_result.json()
    context_payload = context_result.json()
    heartbeat_payload = heartbeat_result.json()
    summary_payload = summary_result.json()
    prompt_id = str(prompt_payload["prompt_id"])
    summary_id = str(summary_payload["summary_id"])

    prompt_history_result = real_daemon_harness.cli("prompts", "history", "--node", node_id)
    prompt_show_result = real_daemon_harness.cli("prompts", "delivered-show", "--prompt", prompt_id)
    summary_history_result = real_daemon_harness.cli("summary", "history", "--node", node_id)
    summary_show_result = real_daemon_harness.cli("summary", "show", "--summary", summary_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert prompt_history_result.exit_code == 0, prompt_history_result.stderr
    assert prompt_show_result.exit_code == 0, prompt_show_result.stderr
    assert summary_history_result.exit_code == 0, summary_history_result.stderr
    assert summary_show_result.exit_code == 0, summary_show_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    prompt_history_payload = prompt_history_result.json()
    prompt_show_payload = prompt_show_result.json()
    summary_history_payload = summary_history_result.json()
    summary_show_payload = summary_show_result.json()
    audit_payload = audit_result.json()

    assert prompt_payload["compiled_subtask_id"] == compiled_subtask_id
    assert prompt_payload["prompt_id"]
    assert prompt_payload["prompt_text"]
    assert context_payload["compiled_subtask_id"] == compiled_subtask_id
    assert context_payload["input_context_json"]["stage_context_json"]
    assert heartbeat_payload["latest_attempt"]["compiled_subtask_id"] == compiled_subtask_id
    assert heartbeat_payload["latest_attempt"]["output_json"]["last_heartbeat_at"]

    assert summary_payload["node_id"] == node_id
    assert summary_payload["compiled_subtask_id"] == compiled_subtask_id
    assert summary_payload["summary_type"] == "subtask"

    assert prompt_history_payload["prompts"]
    assert prompt_history_payload["prompts"][0]["id"] == prompt_id
    assert prompt_show_payload["id"] == prompt_id
    assert prompt_show_payload["compiled_subtask_id"] == compiled_subtask_id
    assert prompt_show_payload["content_hash"]

    assert summary_history_payload["summaries"]
    assert summary_history_payload["summaries"][0]["id"] == summary_id
    assert summary_show_payload["id"] == summary_id
    assert summary_show_payload["summary_scope"] == "subtask_attempt"

    assert audit_payload["node_id"] == node_id
    assert audit_payload["prompt_history"]["prompts"][0]["id"] == prompt_id
    assert any(item["id"] == summary_id for item in audit_payload["summary_history"]["summaries"])
