from __future__ import annotations

import subprocess
import time

import pytest


def _tmux_has_session(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_21_child_session_round_trip_and_mergeback_requires_live_child_codex_execution(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "10.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
        },
    )
    sessions_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 21 Node",
            "--prompt",
            "Delegate child work to a real tmux/Codex child session and wait for durable merge-back without synthetic session-pop payloads.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        sessions_to_cleanup.add(str(bind_result.json()["session_name"]))

        current_before_result = harness.cli("subtask", "current", "--node", node_id)
        assert current_before_result.exit_code == 0, current_before_result.stderr
        before_subtask_id = str(current_before_result.json()["state"]["current_compiled_subtask_id"])

        push_result = harness.cli("session", "push", "--node", node_id, "--reason", "research_context")
        assert push_result.exit_code == 0, push_result.stderr
        push_payload = push_result.json()
        child_session_id = str(push_payload["session_id"])
        child_session_name = str(push_payload["tmux_session_name"])
        sessions_to_cleanup.add(child_session_name)

        assert _tmux_has_session(child_session_name) is True
        time.sleep(1.0)
        pane_text = _tmux_capture(child_session_name)

        result_show_result = None
        deadline = time.time() + 20.0
        while time.time() < deadline:
            candidate = harness.cli("session", "result", "show", "--session", child_session_id)
            if candidate.exit_code == 0:
                result_show_result = candidate
                break
            time.sleep(1.0)

        assert result_show_result is not None, (
            "Expected a real tmux/Codex child session to produce a durable merge-back result without a synthetic "
            "session-pop payload. The child session stayed incomplete instead.\n"
            f"child_session_name={child_session_name}\n"
            f"delegated_prompt_path={push_payload['delegated_prompt_path']}\n"
            f"provider={push_payload['provider']}\n"
            f"pane_text=\n{pane_text}"
        )

        current_after_result = harness.cli("subtask", "current", "--node", node_id)
        context_result = harness.cli("subtask", "context", "--node", node_id)
        assert current_after_result.exit_code == 0, current_after_result.stderr
        assert context_result.exit_code == 0, context_result.stderr

        result_payload = result_show_result.json()
        current_after_payload = current_after_result.json()
        context_payload = context_result.json()

        assert result_payload["child_session_id"] == child_session_id
        assert current_after_payload["state"]["current_compiled_subtask_id"] == before_subtask_id
        assert context_payload["input_context_json"]["child_session_results"]
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
