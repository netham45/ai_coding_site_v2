from __future__ import annotations

import subprocess

import pytest


def _compile_ready_and_start_node(harness, *, node_id: str) -> None:
    compile_result = harness.cli("workflow", "compile", "--node", node_id)
    ready_result = harness.cli("node", "lifecycle", "transition", "--node", node_id, "--state", "READY")
    start_result = harness.cli("node", "run", "start", "--node", node_id)
    assert compile_result.exit_code == 0, compile_result.stderr
    assert ready_result.exit_code == 0, ready_result.stderr
    assert start_result.exit_code == 0, start_result.stderr


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
def test_e2e_rebuild_cutover_coordination_blocks_upstream_rectify_while_authoritative_run_is_active(
    real_daemon_harness_factory,
) -> None:
    harness = real_daemon_harness_factory(session_backend="tmux")

    root_create = harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Rebuild Coordination Root",
        "--prompt",
        "Create the parent node for real rebuild coordination blocking coverage.",
    )
    assert root_create.exit_code == 0, root_create.stderr
    root_id = str(root_create.json()["node_id"])

    child_create = harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Rebuild Coordination Child",
        "--prompt",
        "Start a real authoritative run and require upstream rectification to stay blocked.",
        "--parent",
        root_id,
    )
    assert child_create.exit_code == 0, child_create.stderr
    child_id = str(child_create.json()["node_id"])

    _compile_ready_and_start_node(harness, node_id=child_id)

    coordination_result = harness.cli("node", "rebuild-coordination", "--node", child_id, "--scope", "upstream")
    blocked_rectify_result = harness.cli("node", "rectify-upstream", "--node", child_id)
    history_result = harness.cli("node", "rebuild-history", "--node", child_id)

    assert coordination_result.exit_code == 0, coordination_result.stderr
    assert blocked_rectify_result.exit_code != 0, blocked_rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr

    coordination_payload = coordination_result.json()
    history_payload = history_result.json()

    assert coordination_payload["scope"] == "upstream"
    assert coordination_payload["status"] == "blocked"
    assert any(item["blocker_type"] == "active_or_paused_run" for item in coordination_payload["blockers"])
    assert "live runtime state blocks upstream rectification" in blocked_rectify_result.stderr
    assert any(event["event_kind"] == "live_conflict_blocked" and event["scope"] == "upstream" for event in history_payload["events"])


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
def test_e2e_rebuild_cutover_coordination_blocks_candidate_cutover_while_authoritative_primary_session_is_active(
    real_daemon_harness_factory,
) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.1"},
    )
    session_names_to_cleanup: set[str] = set()
    try:
        create_result = harness.cli(
            "node",
            "create",
            "--kind",
            "epic",
            "--title",
            "Cutover Coordination Node",
            "--prompt",
            "Create a node whose active authoritative tmux session blocks candidate cutover.",
        )
        assert create_result.exit_code == 0, create_result.stderr
        node_id = str(create_result.json()["node_id"])

        supersede_result = harness.cli(
            "node",
            "supersede",
            "--node",
            node_id,
            "--title",
            "Cutover Coordination Node v2",
        )
        assert supersede_result.exit_code == 0, supersede_result.stderr
        candidate_version_id = str(supersede_result.json()["id"])

        _compile_ready_and_start_node(harness, node_id=node_id)

        bind_result = harness.cli("session", "bind", "--node", node_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        session_names_to_cleanup.add(str(bind_result.json()["session_name"]))

        readiness_result = harness.cli("node", "version", "cutover-readiness", "--version", candidate_version_id)
        blocked_cutover_result = harness.cli("node", "version", "cutover", "--version", candidate_version_id)
        history_result = harness.cli("node", "rebuild-history", "--node", node_id)

        assert readiness_result.exit_code == 0, readiness_result.stderr
        assert blocked_cutover_result.exit_code != 0, blocked_cutover_result.stderr
        assert history_result.exit_code == 0, history_result.stderr

        readiness_payload = readiness_result.json()
        history_payload = history_result.json()

        assert readiness_payload["node_version_id"] == candidate_version_id
        assert readiness_payload["status"] == "blocked"
        assert any(item["blocker_type"] == "authoritative_active_run" for item in readiness_payload["blockers"])
        assert any(item["blocker_type"] == "authoritative_active_primary_sessions" for item in readiness_payload["blockers"])
        assert "active primary sessions" in blocked_cutover_result.stderr
        assert any(event["event_kind"] == "cutover_blocked" and event["scope"] == "cutover" for event in history_payload["events"])
    finally:
        for session_name in session_names_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
