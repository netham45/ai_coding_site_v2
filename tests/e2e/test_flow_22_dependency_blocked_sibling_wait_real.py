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
    assert result.returncode == 0, result.stderr
    return result.stdout


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_22_dependency_blocked_sibling_wait_requires_live_completion_of_dependency_sibling(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "10.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
        },
    )
    sessions_to_cleanup: set[str] = set()
    try:
        parent_start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 22 Parent",
            "--prompt",
            "Create a real parent workflow, materialize sibling children, block one sibling on the other, and require live tmux completion before the dependency clears.",
        )
        assert parent_start_result.exit_code == 0, parent_start_result.stderr
        parent_id = str(parent_start_result.json()["node"]["node_id"])

        materialize_result = harness.cli("node", "materialize-children", "--node", parent_id)
        assert materialize_result.exit_code == 0, materialize_result.stderr
        materialize_payload = materialize_result.json()

        left_record = next(child for child in materialize_payload["children"] if child["layout_child_id"] == "discovery")
        right_record = next(child for child in materialize_payload["children"] if child["layout_child_id"] == "implementation")
        left_id = str(left_record["node_id"])
        right_id = str(right_record["node_id"])

        left_show_result = harness.cli("node", "show", "--node", left_id)
        right_show_result = harness.cli("node", "show", "--node", right_id)
        assert left_show_result.exit_code == 0, left_show_result.stderr
        assert right_show_result.exit_code == 0, right_show_result.stderr

        dependency_status_before_result = harness.cli("node", "dependency-status", "--node", right_id)
        blocked_start_result = harness.cli("node", "run", "start", "--node", right_id)
        assert dependency_status_before_result.exit_code == 0, dependency_status_before_result.stderr
        assert blocked_start_result.exit_code != 0, blocked_start_result.stderr

        left_start_result = harness.cli("node", "run", "start", "--node", left_id)
        assert left_start_result.exit_code == 0, left_start_result.stderr

        bind_result = harness.cli("session", "bind", "--node", left_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        session_name = str(bind_result.json()["session_name"])
        sessions_to_cleanup.add(session_name)

        left_complete_payload = None
        last_pane_text = ""
        deadline = time.time() + 30.0
        while time.time() < deadline:
            lifecycle_result = harness.cli("node", "lifecycle", "show", "--node", left_id)
            assert lifecycle_result.exit_code == 0, lifecycle_result.stderr
            lifecycle_payload = lifecycle_result.json()
            if lifecycle_payload["lifecycle_state"] == "COMPLETE":
                left_complete_payload = lifecycle_payload
                break
            last_pane_text = _tmux_capture(session_name)
            time.sleep(1.0)

        assert left_complete_payload is not None, (
            "Expected the dependency sibling to complete through a live tmux/Codex execution path so the dependent sibling could unblock. "
            "The left sibling never reached COMPLETE.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{last_pane_text}"
        )

        dependency_status_after_payload = None
        last_dependency_status = None
        deadline = time.time() + 30.0
        while time.time() < deadline:
            dependency_status_after_result = harness.cli("node", "dependency-status", "--node", right_id)
            assert dependency_status_after_result.exit_code == 0, dependency_status_after_result.stderr
            last_dependency_status = dependency_status_after_result.json()
            if last_dependency_status["ready"] is True:
                dependency_status_after_payload = last_dependency_status
                break
            time.sleep(1.0)

        assert dependency_status_after_payload is not None, (
            "Expected the dependent sibling to become ready only after the daemon advanced the incremental merge lane.\n"
            f"last_dependency_status={last_dependency_status}"
        )

        unblocked_start_result = harness.cli("node", "run", "start", "--node", right_id)
        assert unblocked_start_result.exit_code == 0, unblocked_start_result.stderr

        dependency_status_before_payload = dependency_status_before_result.json()
        unblocked_start_payload = unblocked_start_result.json()

        assert materialize_payload["status"] == "created"
        assert left_record["scheduling_status"] == "ready"
        assert right_record["scheduling_status"] == "ready"
        assert left_show_result.json()["lifecycle_state"] == "READY"
        assert right_show_result.json()["lifecycle_state"] == "READY"
        assert dependency_status_before_payload["ready"] is False
        assert dependency_status_before_payload["blockers"]
        assert dependency_status_after_payload["ready"] is True
        assert dependency_status_after_payload["blockers"] == []
        assert unblocked_start_payload["status"] == "admitted"
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
