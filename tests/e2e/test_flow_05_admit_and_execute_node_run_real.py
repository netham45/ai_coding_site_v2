from __future__ import annotations

import subprocess
import time

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


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_05_admit_and_execute_node_run_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 05 Node",
        "--prompt",
        "Admit a node run and move the first subtask through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    sessions_to_cleanup: set[str] = set()
    try:
        prompt_result = real_daemon_harness.cli("subtask", "prompt", "--node", node_id)
        context_result = real_daemon_harness.cli("subtask", "context", "--node", node_id)
        current_result = real_daemon_harness.cli("subtask", "current", "--node", node_id)
        bind_result = real_daemon_harness.cli("session", "bind", "--node", node_id)

        assert prompt_result.exit_code == 0, prompt_result.stderr
        assert context_result.exit_code == 0, context_result.stderr
        assert current_result.exit_code == 0, current_result.stderr
        assert bind_result.exit_code == 0, bind_result.stderr

        prompt_payload = prompt_result.json()
        context_payload = context_result.json()
        current_payload = current_result.json()
        compiled_subtask_id = str(current_payload["state"]["current_compiled_subtask_id"])
        bind_payload = bind_result.json()
        session_name = str(bind_payload["session_name"])
        sessions_to_cleanup.add(session_name)

        progress_payload = None
        latest_summary_history = None
        last_pane_text = ""
        deadline = time.time() + 45.0
        while time.time() < deadline:
            run_show_result = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
            summary_history_result = real_daemon_harness.cli("summary", "history", "--node", node_id)
            assert run_show_result.exit_code == 0, run_show_result.stderr
            assert summary_history_result.exit_code == 0, summary_history_result.stderr
            progress_payload = run_show_result.json()
            latest_summary_history = summary_history_result.json()
            last_pane_text = _tmux_capture(session_name)

            state = progress_payload["state"]
            latest_attempt = progress_payload["latest_attempt"]
            summaries = latest_summary_history["summaries"]
            if latest_attempt is not None or summaries or state["last_completed_compiled_subtask_id"] is not None:
                break
            time.sleep(2.0)

        assert progress_payload is not None
        assert latest_summary_history is not None

        latest_attempt = progress_payload["latest_attempt"]
        summary_history_payload = latest_summary_history

        assert start_payload["run_admission"]["status"] == "admitted"
        assert start_payload["run_progress"]["run"]["run_status"] == "RUNNING"

        assert prompt_payload["compiled_subtask_id"] == compiled_subtask_id
        assert prompt_payload["prompt_text"]
        assert context_payload["compiled_subtask_id"] == compiled_subtask_id
        assert context_payload["input_context_json"]["stage_context_json"]
        assert current_payload["state"]["current_compiled_subtask_id"] == compiled_subtask_id
        assert current_payload["current_subtask"]["subtask_type"]
        assert bind_payload["logical_node_id"] == node_id
        assert bind_payload["tmux_session_exists"] is True
        assert bind_payload["provider"] == "tmux"

        assert latest_attempt is not None or summary_history_payload["summaries"] or progress_payload["state"]["last_completed_compiled_subtask_id"] is not None, (
            "Expected the real primary tmux/Codex session to create durable workflow progress without manual "
            "subtask advancement from the test.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{last_pane_text}"
        )

        if latest_attempt is not None:
            assert latest_attempt["compiled_subtask_id"] == compiled_subtask_id
        if summary_history_payload["summaries"]:
            assert any(item["summary_type"] in {"subtask", "node"} for item in summary_history_payload["summaries"])
        if progress_payload["state"]["last_completed_compiled_subtask_id"] is not None:
            assert progress_payload["state"]["last_completed_compiled_subtask_id"] == compiled_subtask_id
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
