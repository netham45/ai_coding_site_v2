from __future__ import annotations

import pytest


@pytest.mark.e2e_real
def test_flow_04_manual_tree_edit_and_reconcile_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    parent_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 04 Parent",
        "--prompt",
        "Create a parent node and then mix layout-generated and manual children through the real daemon and real CLI path.",
    )
    assert parent_result.exit_code == 0, parent_result.stderr
    parent_id = str(parent_result.json()["node_id"])

    materialize_result = real_daemon_harness.cli("node", "materialize-children", "--node", parent_id)
    assert materialize_result.exit_code == 0, materialize_result.stderr
    materialize_payload = materialize_result.json()
    assert materialize_payload["authority_mode"] == "layout_authoritative"
    assert materialize_payload["status"] == "created"
    assert materialize_payload["child_count"] == 2

    manual_child_result = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Manual Extra Phase",
        "--prompt",
        "Keep this manual child even after reconciliation.",
    )
    assert manual_child_result.exit_code == 0, manual_child_result.stderr
    manual_child_payload = manual_child_result.json()
    manual_child_id = str(manual_child_payload["node_id"])
    assert manual_child_payload["parent_node_id"] == parent_id

    inspection_result = real_daemon_harness.cli("node", "child-reconciliation", "--node", parent_id)
    reconcile_result = real_daemon_harness.cli(
        "node",
        "reconcile-children",
        "--node",
        parent_id,
        "--decision",
        "preserve_manual",
    )
    materialization_after_result = real_daemon_harness.cli("node", "child-materialization", "--node", parent_id)
    children_result = real_daemon_harness.cli("node", "children", "--node", parent_id, "--versions")
    tree_result = real_daemon_harness.cli("tree", "show", "--node", parent_id, "--full")

    assert inspection_result.exit_code == 0, inspection_result.stderr
    assert reconcile_result.exit_code == 0, reconcile_result.stderr
    assert materialization_after_result.exit_code == 0, materialization_after_result.stderr
    assert children_result.exit_code == 0, children_result.stderr
    assert tree_result.exit_code == 0, tree_result.stderr

    inspection_payload = inspection_result.json()
    reconcile_payload = reconcile_result.json()
    materialization_after_payload = materialization_after_result.json()
    children_payload = children_result.json()
    tree_payload = tree_result.json()

    assert inspection_payload["authority_mode"] == "hybrid"
    assert inspection_payload["materialization_status"] == "reconciliation_required"
    assert inspection_payload["available_decisions"] == ["preserve_manual"]
    assert inspection_payload["manual_child_count"] == 1
    assert inspection_payload["layout_generated_child_count"] == 2

    assert reconcile_payload["authority_mode"] == "manual"
    assert reconcile_payload["materialization_status"] == "manual"
    assert reconcile_payload["manual_child_count"] == 3
    assert reconcile_payload["layout_generated_child_count"] == 0
    assert len(reconcile_payload["children"]) == 3
    assert all(child["layout_child_id"].startswith("manual-") for child in reconcile_payload["children"])

    assert materialization_after_payload["authority_mode"] == "manual"
    assert materialization_after_payload["status"] == "manual"
    assert materialization_after_payload["child_count"] == 3

    assert children_payload["include_versions"] is True
    child_rows = {child["node_id"]: child for child in children_payload["children"]}
    assert manual_child_id in child_rows
    assert len(child_rows) == 3
    assert {child["kind"] for child in child_rows.values()} == {"phase"}
    assert all("authoritative_node_version_id" in child for child in child_rows.values())

    assert tree_payload["root_node_id"] == parent_id
    tree_nodes = tree_payload["nodes"]
    root_row = next(item for item in tree_nodes if item["depth"] == 0)
    assert root_row["node_id"] == parent_id
    child_titles = {item["title"] for item in tree_nodes if item["depth"] == 1}
    assert child_titles == {"Discovery And Framing", "Implementation", "Manual Extra Phase"}
