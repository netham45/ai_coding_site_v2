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


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
def test_flow_07_pause_resume_and_recover_runs_against_real_daemon_real_cli_and_tmux(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "1.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1",
        },
    )
    session_names_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 07 Node",
            "--prompt",
            "Bind a real tmux session, let it go stale, then recover it through the real daemon and real CLI path.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        start_payload = start_result.json()
        node_id = str(start_payload["node"]["node_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        bind_payload = bind_result.json()
        session_names_to_cleanup.add(bind_payload["session_name"])

        current_initial_result = harness.cli("session", "show-current")
        assert current_initial_result.exit_code == 0, current_initial_result.stderr
        current_initial_payload = current_initial_result.json()

        assert bind_payload["status"] == "bound"
        assert bind_payload["logical_node_id"] == node_id
        assert bind_payload["tmux_session_exists"] is True
        assert bind_payload["session_name"].startswith("aicoding-pri-r")
        assert current_initial_payload["logical_node_id"] == node_id
        assert current_initial_payload["recovery_classification"] in {"detached", "stale_but_recoverable"}
        if current_initial_payload["recovery_classification"] == "detached":
            assert current_initial_payload["recommended_action"] == "attach_existing_session"
            time.sleep(1.6)
            current_stale_result = harness.cli("session", "show-current")
        else:
            assert current_initial_payload["recommended_action"] == "resume_existing_session"
            current_stale_result = current_initial_result

        recovery_result = harness.cli("node", "recovery-status", "--node", node_id)
        resume_result = harness.cli("session", "resume", "--node", node_id)

        assert current_stale_result.exit_code == 0, current_stale_result.stderr
        assert recovery_result.exit_code == 0, recovery_result.stderr
        assert resume_result.exit_code == 0, resume_result.stderr

        current_stale_payload = current_stale_result.json()
        recovery_payload = recovery_result.json()
        resume_payload = resume_result.json()
        session_names_to_cleanup.add(resume_payload["session"]["session_name"])

        assert current_stale_payload["logical_node_id"] == node_id
        assert current_stale_payload["recovery_classification"] == "stale_but_recoverable"
        assert current_stale_payload["recommended_action"] == "resume_existing_session"
        assert current_stale_payload["tmux_session_exists"] is True

        assert recovery_payload["node_id"] == node_id
        assert recovery_payload["recovery_classification"] == "stale_but_recoverable"
        assert recovery_payload["recommended_action"] == "resume_existing_session"
        assert recovery_payload["tmux_session_exists"] is True

        assert resume_payload["status"] in {"reused_existing_session", "replacement_session_created"}
        assert resume_payload["recovery_status"]["recovery_classification"] in {
            "healthy",
            "detached",
            "stale_but_recoverable",
        }
        assert resume_payload["session"]["logical_node_id"] == node_id
        assert resume_payload["session"]["status"] == "resumed"
    finally:
        for session_name in session_names_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
def test_flow_07_background_supervision_restarts_killed_tmux_session_automatically(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "1.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1",
        },
    )
    session_names_to_cleanup: set[str] = set()
    try:
        start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 07 Supervision Restart Node",
            "--prompt",
            "Bind a tmux session, kill it externally, and require the daemon supervision loop to replace it without a manual resume command.",
        )
        assert start_result.exit_code == 0, start_result.stderr
        node_id = str(start_result.json()["node"]["node_id"])

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        bind_payload = bind_result.json()
        original_session_name = str(bind_payload["session_name"])
        original_session_id = str(bind_payload["session_id"])
        session_names_to_cleanup.add(original_session_name)

        subprocess.run(["tmux", "kill-session", "-t", original_session_name], check=False, capture_output=True, text=True)
        assert _tmux_has_session(original_session_name) is False

        deadline = time.time() + 20.0
        latest_list_payload: dict[str, object] | None = None
        latest_show_payload: dict[str, object] | None = None
        while time.time() < deadline:
            harness.assert_process_alive(prefix="Real daemon process exited while waiting for automatic session supervision restart.")
            list_result = harness.cli("session", "list", "--node", node_id)
            show_result = harness.cli("session", "show", "--node", node_id)
            if list_result.exit_code == 0:
                latest_list_payload = list_result.json()
            if show_result.exit_code == 0:
                latest_show_payload = show_result.json()
                new_session_name = str(latest_show_payload["session_name"])
                if new_session_name != original_session_name and latest_show_payload["status"] == "resumed":
                    session_names_to_cleanup.add(new_session_name)
                    break
            time.sleep(0.2)

        assert latest_list_payload is not None
        assert latest_show_payload is not None
        sessions = latest_list_payload["sessions"]
        assert any(item["session_id"] == original_session_id and item["status"] == "lost" for item in sessions)
        assert latest_show_payload["session_name"] != original_session_name
        assert latest_show_payload["tmux_session_exists"] is True
        assert latest_show_payload["status"] == "resumed"
    finally:
        for session_name in session_names_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
