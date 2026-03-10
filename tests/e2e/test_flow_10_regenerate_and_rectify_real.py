from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_10_regenerate_and_rectify_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    root_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 10 Root",
        "--prompt",
        "Create the root node for a real regenerate-and-rectify cycle.",
    )
    assert root_create_result.exit_code == 0, root_create_result.stderr
    root_id = str(root_create_result.json()["node_id"])

    child_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Real E2E Flow 10 Child",
        "--prompt",
        "Create the child node that will be rectified upstream.",
        "--parent",
        root_id,
    )
    assert child_create_result.exit_code == 0, child_create_result.stderr
    child_id = str(child_create_result.json()["node_id"])

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", root_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", child_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", child_id)
    versions_result = real_daemon_harness.cli("node", "versions", "--node", child_id)

    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert versions_result.exit_code == 0, versions_result.stderr

    regenerate_payload = regenerate_result.json()
    rectify_payload = rectify_result.json()
    history_payload = history_result.json()
    versions_payload = versions_result.json()

    candidate_version_id = str(versions_payload["versions"][-1]["id"])

    cutover_readiness_result = real_daemon_harness.cli(
        "node",
        "version",
        "cutover-readiness",
        "--version",
        candidate_version_id,
    )
    coordination_result = real_daemon_harness.cli(
        "node",
        "rebuild-coordination",
        "--node",
        child_id,
        "--scope",
        "upstream",
    )

    assert cutover_readiness_result.exit_code == 0, cutover_readiness_result.stderr
    assert coordination_result.exit_code == 0, coordination_result.stderr

    cutover_readiness_payload = cutover_readiness_result.json()
    coordination_payload = coordination_result.json()

    assert regenerate_payload["scope"] == "subtree"
    assert rectify_payload["scope"] == "upstream"
    assert {event["scope"] for event in history_payload["events"]} >= {"subtree", "upstream"}
    assert len(versions_payload["versions"]) >= 2
    assert cutover_readiness_payload["node_version_id"] == candidate_version_id
    assert cutover_readiness_payload["status"] in {"ready", "blocked"}
    assert coordination_payload["scope"] == "upstream"
    assert coordination_payload["status"] in {"clear", "blocked"}
