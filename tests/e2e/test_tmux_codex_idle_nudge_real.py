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


def _tmux_current_command(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "display-message", "-p", "-t", session_name, "#{pane_current_command}"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux command lookup failed] {result.stderr.strip()}"
    return result.stdout.strip()


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_tmux_primary_session_launches_codex_not_shell(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "5.0",
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
            "Real Tmux Codex Launch Node",
            "--prompt",
            "Launch a real Codex session in tmux and begin the current prompt.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        bind_payload = bind_result.json()
        session_name = str(bind_payload["session_name"])
        sessions_to_cleanup.add(session_name)

        pane_command = ""
        pane_text = ""
        deadline = time.time() + 20.0
        while time.time() < deadline:
            pane_command = _tmux_current_command(session_name)
            pane_text = _tmux_capture(session_name)
            if pane_command and not pane_command.startswith("[tmux command lookup failed]"):
                break
            time.sleep(1.0)

        assert bind_payload["tmux_session_exists"] is True
        assert bind_payload["logical_node_id"] == node_id
        assert pane_command == "codex", (
            "Expected the live primary tmux session to launch Codex rather than a shell placeholder.\n"
            f"session_name={session_name}\n"
            f"pane_current_command={pane_command}\n"
            f"pane_text=\n{pane_text}"
        )
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
