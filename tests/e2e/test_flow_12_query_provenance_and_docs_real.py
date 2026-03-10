from __future__ import annotations

import pytest


def _write_workspace_provenance_inputs(workspace_root) -> None:
    source_path = workspace_root / "src" / "pkg" / "app.py"
    source_path.parent.mkdir(parents=True, exist_ok=True)
    source_path.write_text(
        "\n".join(
            [
                "def helper(name: str) -> str:",
                "    return name.strip().upper()",
                "",
                "class Greeter:",
                "    def greet(self, name: str) -> str:",
                "        return helper(name)",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
def test_flow_12_query_provenance_and_docs_runs_against_real_daemon_and_real_cli(real_daemon_harness, tmp_path) -> None:
    _write_workspace_provenance_inputs(real_daemon_harness.workspace_root)

    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 12 Node",
        "--prompt",
        "Refresh provenance and build docs through the real daemon and real CLI path.",
    )
    assert start_result.exit_code == 0, start_result.stderr
    node_id = str(start_result.json()["node"]["node_id"])

    current_result = real_daemon_harness.cli("subtask", "current", "--node", node_id)
    assert current_result.exit_code == 0, current_result.stderr
    current_payload = current_result.json()
    compiled_subtask_id = str(current_payload["state"]["current_compiled_subtask_id"])

    prompt_result = real_daemon_harness.cli("subtask", "prompt", "--node", node_id)
    start_subtask_result = real_daemon_harness.cli(
        "subtask",
        "start",
        "--node",
        node_id,
        "--compiled-subtask",
        compiled_subtask_id,
    )
    summary_file = tmp_path / "provenance-summary.md"
    summary_file.write_text("implemented provenance plumbing through the real E2E flow", encoding="utf-8")
    summary_result = real_daemon_harness.cli(
        "summary",
        "register",
        "--node",
        node_id,
        "--type",
        "subtask",
        "--file",
        str(summary_file),
    )

    provenance_result = real_daemon_harness.cli("node", "provenance-refresh", "--node", node_id)
    rationale_result = real_daemon_harness.cli("rationale", "show", "--node", node_id)
    entity_name = "src.pkg.app.Greeter.greet"
    entity_result = real_daemon_harness.cli("entity", "show", "--name", entity_name)
    history_result = real_daemon_harness.cli("entity", "history", "--name", entity_name)
    changed_by_result = real_daemon_harness.cli("entity", "changed-by", "--name", entity_name)
    relations_result = real_daemon_harness.cli("entity", "relations", "--name", entity_name)
    docs_build_result = real_daemon_harness.cli("docs", "build-node-view", "--node", node_id)
    docs_list_result = real_daemon_harness.cli("docs", "list", "--node", node_id)
    docs_show_result = real_daemon_harness.cli("docs", "show", "--node", node_id, "--scope", "local")
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert prompt_result.exit_code == 0, prompt_result.stderr
    assert start_subtask_result.exit_code == 0, start_subtask_result.stderr
    assert summary_result.exit_code == 0, summary_result.stderr
    assert provenance_result.exit_code == 0, provenance_result.stderr
    assert rationale_result.exit_code == 0, rationale_result.stderr
    assert entity_result.exit_code == 0, entity_result.stderr
    assert history_result.exit_code == 0, history_result.stderr
    assert changed_by_result.exit_code == 0, changed_by_result.stderr
    assert relations_result.exit_code == 0, relations_result.stderr
    assert docs_build_result.exit_code == 0, docs_build_result.stderr
    assert docs_list_result.exit_code == 0, docs_list_result.stderr
    assert docs_show_result.exit_code == 0, docs_show_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    provenance_payload = provenance_result.json()
    rationale_payload = rationale_result.json()
    entity_payload = entity_result.json()
    history_payload = history_result.json()
    changed_by_payload = changed_by_result.json()
    relations_payload = relations_result.json()
    docs_build_payload = docs_build_result.json()
    docs_list_payload = docs_list_result.json()
    docs_show_payload = docs_show_result.json()
    audit_payload = audit_result.json()

    assert provenance_payload["entity_count"] >= 4
    assert provenance_payload["relation_count"] >= 3
    assert provenance_payload["change_counts"]["added"] >= 4
    assert rationale_payload["entity_history"]
    assert rationale_payload["change_counts"]["added"] >= 4
    assert entity_payload["entities"][0]["canonical_name"] == entity_name
    assert entity_payload["entities"][0]["entity_type"] == "method"
    assert history_payload["history"]
    assert changed_by_payload["history"]
    assert relations_payload["relations"]
    assert docs_build_payload["documents"]
    assert docs_list_payload["documents"]
    assert "Real E2E Flow 12 Node" in docs_show_payload["content"]
    assert audit_payload["node_id"] == node_id
    assert audit_payload["documentation_outputs"]
    assert any(
        item["summary_type"] == "provenance"
        for item in audit_payload["summary_history"]["summaries"]
    )
