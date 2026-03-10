from __future__ import annotations

import pytest


def _write_workspace_pause_override(workspace_root) -> None:
    override_path = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_pause_gate.yaml"
    override_path.parent.mkdir(parents=True, exist_ok=True)
    override_path.write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
                "    - pause_for_user",
                "    - validate_node",
                "    - review_node",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
def test_flow_13_human_gate_and_intervention_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    _write_workspace_pause_override(real_daemon_harness.workspace_root)

    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 13 Node",
        "--prompt",
        "Pause for explicit human approval and resume through the real daemon and CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    node_id = str(start_result.json()["node"]["node_id"])

    paused_progress = None
    while True:
        progress_result = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
        assert progress_result.exit_code == 0, progress_result.stderr
        progress_payload = progress_result.json()
        current_subtask = progress_payload["current_subtask"]
        if current_subtask["source_subtask_key"].startswith("pause_for_user."):
            paused_progress = progress_payload
            break
        compiled_subtask_id = str(progress_payload["state"]["current_compiled_subtask_id"])
        start_subtask_result = real_daemon_harness.cli(
            "subtask",
            "start",
            "--node",
            node_id,
            "--compiled-subtask",
            compiled_subtask_id,
        )
        complete_subtask_result = real_daemon_harness.cli(
            "subtask",
            "complete",
            "--node",
            node_id,
            "--compiled-subtask",
            compiled_subtask_id,
            "--summary",
            "advance to pause gate",
        )
        advance_result = real_daemon_harness.cli("workflow", "advance", "--node", node_id)
        assert start_subtask_result.exit_code == 0, start_subtask_result.stderr
        assert complete_subtask_result.exit_code == 0, complete_subtask_result.stderr
        assert advance_result.exit_code == 0, advance_result.stderr

    interventions_result = real_daemon_harness.cli("node", "interventions", "--node", node_id)
    pause_state_result = real_daemon_harness.cli("node", "pause-state", "--node", node_id)
    blocked_resume_result = real_daemon_harness.cli("workflow", "resume", "--node", node_id)
    approve_result = real_daemon_harness.cli(
        "node",
        "intervention-apply",
        "--node",
        node_id,
        "--kind",
        "pause_approval",
        "--action",
        "approve_pause",
        "--pause-flag",
        "user_guidance_required",
        "--summary",
        "approved",
    )
    approved_pause_state_result = real_daemon_harness.cli("node", "pause-state", "--node", node_id)
    resume_result = real_daemon_harness.cli("workflow", "resume", "--node", node_id)

    assert paused_progress is not None
    assert interventions_result.exit_code == 0, interventions_result.stderr
    assert pause_state_result.exit_code == 0, pause_state_result.stderr
    assert blocked_resume_result.exit_code == 4, blocked_resume_result.stderr
    assert approve_result.exit_code == 0, approve_result.stderr
    assert approved_pause_state_result.exit_code == 0, approved_pause_state_result.stderr
    assert resume_result.exit_code == 0, resume_result.stderr

    paused_payload = paused_progress
    interventions_payload = interventions_result.json()
    pause_state_payload = pause_state_result.json()
    blocked_resume_payload = blocked_resume_result.stderr_json()
    approve_payload = approve_result.json()
    approved_pause_state_payload = approved_pause_state_result.json()
    resume_payload = resume_result.json()

    assert paused_payload["run"]["run_status"] == "PAUSED"
    assert paused_payload["current_subtask"]["source_subtask_key"].startswith("pause_for_user.")
    assert any(item["kind"] == "pause_approval" for item in interventions_payload["interventions"])
    assert pause_state_payload["pause_flag_name"] == "user_guidance_required"
    assert pause_state_payload["approval_required"] is True
    assert blocked_resume_payload["error"] == "daemon_conflict"
    assert "requires explicit approval" in blocked_resume_payload["details"]["response"]["detail"]
    assert approve_payload["action"] == "approve_pause"
    assert approve_payload["result_json"]["approved"] is True
    assert approved_pause_state_payload["approved"] is True
    assert resume_payload["status"] == "accepted"
    assert resume_payload["current_state"] == "RUNNING"
