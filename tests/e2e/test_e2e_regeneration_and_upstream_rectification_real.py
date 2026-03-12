from __future__ import annotations

from uuid import UUID

import pytest
from sqlalchemy import create_engine, text


@pytest.mark.e2e_real
def test_e2e_regeneration_and_upstream_rectification_round_trip_against_real_daemon_and_cli(
    real_daemon_harness,
) -> None:
    root_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real Rectification Root",
        "--prompt",
        "Create the root node for a dedicated real regenerate-and-rectify cycle.",
    )
    assert root_create_result.exit_code == 0, root_create_result.stderr
    root_id = str(root_create_result.json()["node_id"])

    child_create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "phase",
        "--title",
        "Real Rectification Child",
        "--prompt",
        "Create the child node that will be rectified upstream through the dedicated real suite.",
        "--parent",
        root_id,
    )
    assert child_create_result.exit_code == 0, child_create_result.stderr
    child_id = str(child_create_result.json()["node_id"])

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", root_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", child_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", child_id)
    versions_result = real_daemon_harness.cli("node", "versions", "--node", child_id)
    cutover_readiness_result = real_daemon_harness.cli(
        "node",
        "version",
        "cutover-readiness",
        "--version",
        str(real_daemon_harness.cli("node", "versions", "--node", child_id).json()["versions"][-1]["id"]),
    )
    coordination_result = real_daemon_harness.cli(
        "node",
        "rebuild-coordination",
        "--node",
        child_id,
        "--scope",
        "upstream",
    )

    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert versions_result.exit_code == 0, versions_result.stderr
    assert cutover_readiness_result.exit_code == 0, cutover_readiness_result.stderr
    assert coordination_result.exit_code == 0, coordination_result.stderr

    regenerate_payload = regenerate_result.json()
    rectify_payload = rectify_result.json()
    history_payload = history_result.json()
    versions_payload = versions_result.json()
    cutover_readiness_payload = cutover_readiness_result.json()
    coordination_payload = coordination_result.json()

    candidate_version_id = str(versions_payload["versions"][-1]["id"])

    assert regenerate_payload["scope"] == "subtree"
    assert rectify_payload["scope"] == "upstream"
    assert {event["scope"] for event in history_payload["events"]} >= {"subtree", "upstream"}
    assert len(versions_payload["versions"]) >= 2
    assert cutover_readiness_payload["node_version_id"] == candidate_version_id
    assert cutover_readiness_payload["status"] in {"ready", "blocked"}
    assert coordination_payload["scope"] == "upstream"
    assert coordination_payload["status"] in {"clear", "blocked"}


@pytest.mark.e2e_real
def test_e2e_regeneration_and_upstream_rectification_dependency_invalidated_fresh_restart_is_childless_and_remapped(
    real_daemon_harness,
) -> None:
    parent_create = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real Rectification Dependency Parent",
        "--prompt",
        "Create a parent with sibling dependency invalidation during the dedicated real rectify/upstream suite.",
        "--no-run",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node"]["node_id"])

    left_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Prerequisite Phase",
        "--prompt",
        "This sibling will be rectified upward.",
    )
    right_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Dependent Phase",
        "--prompt",
        "This sibling depends on the prerequisite and must fresh-restart.",
    )
    assert left_create.exit_code == 0, left_create.stderr
    assert right_create.exit_code == 0, right_create.stderr
    left_id = str(left_create.json()["node_id"])
    right_id = str(right_create.json()["node_id"])

    materialize_right = real_daemon_harness.cli("node", "materialize-children", "--node", right_id)
    add_dependency = real_daemon_harness.cli("node", "dependency-add", "--node", right_id, "--depends-on", left_id)
    rectify_result = real_daemon_harness.cli("node", "rectify-upstream", "--node", left_id)
    history_result = real_daemon_harness.cli("node", "rebuild-history", "--node", left_id)
    parent_versions_result = real_daemon_harness.cli("node", "versions", "--node", parent_id)
    left_versions_result = real_daemon_harness.cli("node", "versions", "--node", left_id)
    right_versions_result = real_daemon_harness.cli("node", "versions", "--node", right_id)

    assert materialize_right.exit_code == 0, materialize_right.stderr
    assert add_dependency.exit_code == 0, add_dependency.stderr
    assert rectify_result.exit_code == 0, rectify_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert parent_versions_result.exit_code == 0, parent_versions_result.stderr
    assert left_versions_result.exit_code == 0, left_versions_result.stderr
    assert right_versions_result.exit_code == 0, right_versions_result.stderr

    materialize_payload = materialize_right.json()
    history_payload = history_result.json()
    parent_versions_payload = parent_versions_result.json()
    left_versions_payload = left_versions_result.json()
    right_versions_payload = right_versions_result.json()

    parent_candidate_id = str(parent_versions_payload["versions"][-1]["id"])
    left_candidate_id = str(left_versions_payload["versions"][-1]["id"])
    right_candidate_id = str(right_versions_payload["versions"][-1]["id"])

    assert materialize_payload["child_count"] > 0
    assert parent_versions_payload["versions"][-1]["status"] == "candidate"
    assert left_versions_payload["versions"][-1]["status"] == "candidate"
    assert right_versions_payload["versions"][-1]["status"] == "candidate"
    assert any(
        event["event_kind"] == "candidate_created"
        and event["target_node_version_id"] == right_candidate_id
        and event["details_json"].get("candidate_role") == "dependency_invalidated_fresh_restart"
        for event in history_payload["events"]
    )

    engine = create_engine(real_daemon_harness.database_url, future=True)
    try:
        with engine.connect() as connection:
            right_candidate_child_count = connection.execute(
                text("select count(*) from node_children where parent_node_version_id = :version_id"),
                {"version_id": right_candidate_id},
            ).scalar_one()
            right_candidate_parent_version_id = connection.execute(
                text("select parent_node_version_id from node_versions where id = :version_id"),
                {"version_id": right_candidate_id},
            ).scalar_one()
            parent_candidate_child_ids = {
                row[0]
                for row in connection.execute(
                    text(
                        "select child_node_version_id from node_children where parent_node_version_id = :version_id order by ordinal, created_at"
                    ),
                    {"version_id": parent_candidate_id},
                )
            }
        assert right_candidate_child_count == 0
        assert str(right_candidate_parent_version_id) == parent_candidate_id
        assert parent_candidate_child_ids == {UUID(left_candidate_id), UUID(right_candidate_id)}
    finally:
        engine.dispose()
