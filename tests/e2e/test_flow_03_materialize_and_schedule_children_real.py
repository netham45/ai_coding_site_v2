from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_03_materialize_and_schedule_children_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 03 Epic",
        "--prompt",
        "Materialize built-in child phases through the real daemon and real CLI path.",
        "--no-run",
    )
    assert start_result.exit_code == 0, start_result.stderr
    node_id = str(start_result.json()["node"]["node_id"])

    before_result = real_daemon_harness.cli("node", "child-materialization", "--node", node_id)
    materialize_result = real_daemon_harness.cli("node", "materialize-children", "--node", node_id)
    after_result = real_daemon_harness.cli("node", "child-materialization", "--node", node_id)
    children_result = real_daemon_harness.cli("node", "children", "--node", node_id, "--versions")
    tree_result = real_daemon_harness.cli("tree", "show", "--node", node_id, "--full")

    assert before_result.exit_code == 0, before_result.stderr
    assert materialize_result.exit_code == 0, materialize_result.stderr
    assert after_result.exit_code == 0, after_result.stderr
    assert children_result.exit_code == 0, children_result.stderr
    assert tree_result.exit_code == 0, tree_result.stderr

    before_payload = before_result.json()
    materialize_payload = materialize_result.json()
    after_payload = after_result.json()
    children_payload = children_result.json()
    tree_payload = tree_result.json()

    assert before_payload["status"] == "not_materialized"
    assert before_payload["child_count"] == 0

    assert materialize_payload["status"] == "created"
    assert materialize_payload["authority_mode"] == "layout_authoritative"
    assert materialize_payload["child_count"] == 2
    assert materialize_payload["created_count"] == 2
    assert materialize_payload["ready_child_count"] == 1
    assert materialize_payload["blocked_child_count"] == 1

    child_by_layout_id = {child["layout_child_id"]: child for child in materialize_payload["children"]}
    assert set(child_by_layout_id) == {"discovery", "implementation"}
    assert child_by_layout_id["discovery"]["kind"] == "phase"
    assert child_by_layout_id["discovery"]["scheduling_status"] == "ready"
    assert child_by_layout_id["implementation"]["kind"] == "phase"
    assert child_by_layout_id["implementation"]["scheduling_status"] == "blocked_on_dependency"
    assert child_by_layout_id["implementation"]["scheduling_reason"] == "blocked_on_dependency"
    assert child_by_layout_id["implementation"]["blockers"]

    assert after_payload["status"] == "materialized"
    assert after_payload["authority_mode"] == "layout_authoritative"
    assert after_payload["child_count"] == 2
    assert after_payload["ready_child_count"] == 0
    assert after_payload["blocked_child_count"] == 2

    assert len(children_payload["children"]) == 2
    assert {child["kind"] for child in children_payload["children"]} == {"phase"}
    assert children_payload["include_versions"] is True
    assert all("authoritative_node_version_id" in child for child in children_payload["children"])

    assert tree_payload["root_node_id"] == node_id
    assert len(tree_payload["nodes"]) == 3
    root_row = next(item for item in tree_payload["nodes"] if item["depth"] == 0)
    assert root_row["node_id"] == node_id
    child_rows = {child["title"]: child for child in tree_payload["nodes"] if child["depth"] == 1}
    assert child_rows["Discovery And Framing"]["scheduling_status"] == "already_running"
    assert child_rows["Implementation"]["scheduling_status"] == "blocked"
