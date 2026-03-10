from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from aicoding.resources import load_resource_catalog


REPO_ROOT = Path(__file__).resolve().parents[2]
FLOW_DIR = REPO_ROOT / "flows"
SCENARIO_DOCS = (
    "notes/scenarios/journeys/common_user_journeys_analysis.md",
    "notes/scenarios/walkthroughs/getting_started_hypothetical_task_guide.md",
    "notes/scenarios/walkthroughs/hypothetical_plan_workthrough.md",
)


@dataclass(frozen=True, slots=True)
class FlowCase:
    flow_doc: str
    support_level: str
    scenario_refs: tuple[str, ...]
    limitation: str
    executor_name: str


def _wire_bridge(monkeypatch, daemon_bridge_client) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)


def _create_compiled_node(cli_runner, *, kind: str = "epic", title: str, prompt: str, parent: str | None = None) -> str:
    command = ["node", "create", "--kind", kind, "--title", title, "--prompt", prompt]
    if parent is not None:
        command.extend(["--parent", parent])
    result = cli_runner(command)
    assert result.exit_code == 0
    node_id = result.json()["node_id"]
    compile_result = cli_runner(["workflow", "compile", "--node", node_id])
    assert compile_result.exit_code == 0
    return node_id


def _create_ready_running_node(cli_runner, *, title: str, prompt: str) -> str:
    node_id = _create_compiled_node(cli_runner, title=title, prompt=prompt)
    assert cli_runner(["node", "lifecycle", "transition", "--node", node_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", node_id]).exit_code == 0
    return node_id


def _complete_current_subtask(cli_runner, daemon_bridge_client, *, node_id: str, summary: str = "done") -> dict[str, object]:
    current_result = cli_runner(["subtask", "current", "--node", node_id])
    assert current_result.exit_code == 0
    current_payload = current_result.json()
    compiled_subtask_id = current_payload["state"]["current_compiled_subtask_id"]
    current_subtask = current_payload["current_subtask"]

    assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0

    subtask_type = current_subtask["subtask_type"]
    if subtask_type == "validate":
        daemon_bridge_client.request(
            "POST",
            "/api/subtasks/complete",
            json_payload={
                "node_id": node_id,
                "compiled_subtask_id": compiled_subtask_id,
                "output_json": {"exit_code": 0},
                "summary": "validated",
            },
        )
    elif subtask_type == "review":
        daemon_bridge_client.request(
            "POST",
            "/api/subtasks/complete",
            json_payload={
                "node_id": node_id,
                "compiled_subtask_id": compiled_subtask_id,
                "output_json": {
                    "status": "pass",
                    "findings": [{"message": "ok"}],
                    "criteria_results": [{"criterion": "ok", "status": "passed"}],
                },
                "summary": "reviewed",
            },
        )
    elif subtask_type == "run_tests":
        daemon_bridge_client.request(
            "POST",
            "/api/subtasks/complete",
            json_payload={
                "node_id": node_id,
                "compiled_subtask_id": compiled_subtask_id,
                "output_json": {
                    "test_suites": [
                        {
                            "testing_definition_id": "default_unit_test_gate",
                            "suite_name": "Default Unit Test Gate",
                            "exit_code": 0,
                            "failed_tests": 0,
                            "summary": "unit tests passed",
                        },
                        {
                            "testing_definition_id": "default_integration_test_gate",
                            "suite_name": "Default Integration Test Gate",
                            "exit_code": 0,
                            "failed_tests": 0,
                            "summary": "integration tests passed",
                        },
                    ]
                },
                "summary": "tests passed",
            },
        )
    else:
        assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary", summary]).exit_code == 0

    return current_payload


def _testing_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Flow-suite testing fixture policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: false",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs:",
                "    - testing/custom_retry_gate.yaml",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    (project_root / "testing" / "custom_retry_gate.yaml").write_text(
        "\n".join(
            [
                "kind: testing_definition",
                "id: custom_retry_gate",
                "name: Custom Retry Gate",
                "applies_to:",
                "  node_kinds: [epic, phase, plan, task]",
                "  task_ids: [test_node]",
                "  lifecycle_points: [after_task]",
                "scope: project_custom",
                "description: Flow-suite durable testing gate.",
                "commands:",
                "  - command: python3 -m pytest tests/unit -q",
                "    working_directory: .",
                "    env: {}",
                "retry_policy:",
                "  max_attempts: 2",
                "  rerun_failed_only: true",
                "pass_rules:",
                "  require_exit_code_zero: true",
                "  max_failed_tests: 0",
                "on_result:",
                "  pass_action: continue",
                "  fail_action: fail_to_parent",
            ]
        ),
        encoding="utf-8",
    )
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_test_node.yaml").write_text(
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
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    return replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )


def _pause_gate_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_pause_gate.yaml").write_text(
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
    return replace(base_catalog, yaml_overrides_dir=overrides_root)


def _run_flow_01(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    start_result = cli_runner(["workflow", "start", "--kind", "epic", "--title", "Flow 01 Epic", "--prompt", "boot prompt"])
    payload = start_result.json()
    node_id = payload["node"]["node_id"]

    current_result = cli_runner(["workflow", "current", "--node", node_id])
    show_result = cli_runner(["node", "show", "--node", node_id])

    assert start_result.exit_code == 0
    assert payload["status"] == "started"
    assert payload["compile"]["status"] == "compiled"
    assert payload["run_progress"]["run"]["trigger_reason"] == "workflow_start"
    assert current_result.exit_code == 0
    assert current_result.json()["id"] == payload["compile"]["compiled_workflow"]["id"]
    assert show_result.exit_code == 0
    assert show_result.json()["node_id"] == node_id


def _run_flow_02(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = _create_compiled_node(cli_runner, title="Flow 02 Epic", prompt="compile prompt")

    current_result = cli_runner(["workflow", "current", "--node", node_id])
    chain_result = cli_runner(["workflow", "chain", "--node", node_id])
    sources_result = cli_runner(["workflow", "source-discovery", "--node", node_id])
    schema_result = cli_runner(["workflow", "schema-validation", "--node", node_id])
    override_result = cli_runner(["workflow", "override-resolution", "--node", node_id])
    hook_policy_result = cli_runner(["workflow", "hook-policy", "--node", node_id])
    rendering_result = cli_runner(["workflow", "rendering", "--node", node_id])

    assert current_result.exit_code == 0
    assert chain_result.exit_code == 0
    assert chain_result.json()["chain"]
    assert sources_result.exit_code == 0
    assert sources_result.json()["discovery_order"]
    assert schema_result.exit_code == 0
    assert schema_result.json()["validated_document_count"] > 0
    assert override_result.exit_code == 0
    assert "applied_overrides" in override_result.json()
    assert hook_policy_result.exit_code == 0
    assert "selected_hooks" in hook_policy_result.json()
    assert rendering_result.exit_code == 0
    assert rendering_result.json()["compiled_subtasks"]


def _run_flow_03(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = cli_runner(["node", "create", "--kind", "epic", "--title", "Flow 03 Epic", "--prompt", "layout prompt"]).json()["node_id"]

    before_result = cli_runner(["node", "child-materialization", "--node", node_id])
    materialize_result = cli_runner(["node", "materialize-children", "--node", node_id])
    children_result = cli_runner(["node", "children", "--node", node_id])

    assert before_result.exit_code == 0
    assert before_result.json()["status"] == "not_materialized"
    assert materialize_result.exit_code == 0
    assert materialize_result.json()["status"] == "created"
    assert children_result.exit_code == 0
    assert len(children_result.json()["children"]) >= 2


def _run_flow_04(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    parent_id = cli_runner(["node", "create", "--kind", "epic", "--title", "Flow 04 Parent", "--prompt", "manual prompt"]).json()["node_id"]
    materialize_result = cli_runner(["node", "materialize-children", "--node", parent_id])
    child_result = cli_runner(
        ["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "Flow 04 Child", "--prompt", "child prompt"]
    )
    reconciliation_result = cli_runner(["node", "child-reconciliation", "--node", parent_id])
    preserve_result = cli_runner(["node", "reconcile-children", "--node", parent_id, "--decision", "preserve_manual"])
    materialization_result = cli_runner(["node", "child-materialization", "--node", parent_id])

    assert materialize_result.exit_code == 0
    assert child_result.exit_code == 0
    assert child_result.json()["parent_node_id"] == parent_id
    assert reconciliation_result.exit_code == 0
    assert reconciliation_result.json()["authority_mode"] == "hybrid"
    assert reconciliation_result.json()["available_decisions"] == ["preserve_manual"]
    assert preserve_result.exit_code == 0
    assert preserve_result.json()["authority_mode"] == "manual"
    assert preserve_result.json()["materialization_status"] == "manual"
    assert materialization_result.exit_code == 0
    assert materialization_result.json()["authority_mode"] == "manual"
    assert materialization_result.json()["status"] == "manual"


def _run_flow_05(cli_runner, daemon_bridge_client, monkeypatch, tmp_path, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = _create_ready_running_node(cli_runner, title="Flow 05 Node", prompt="run prompt")
    prompt_result = cli_runner(["subtask", "prompt", "--node", node_id])
    context_result = cli_runner(["subtask", "context", "--node", node_id])
    current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
    compiled_subtask_id = current_payload["state"]["current_compiled_subtask_id"]
    start_result = cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id])
    heartbeat_result = cli_runner(["subtask", "heartbeat", "--node", node_id, "--compiled-subtask", compiled_subtask_id])
    summary_path = tmp_path / "flow-05-summary.md"
    summary_path.write_text("flow 05 summary", encoding="utf-8")
    summary_result = cli_runner(["summary", "register", "--node", node_id, "--file", str(summary_path), "--type", "subtask"])
    complete_result = cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id, "--summary", "done"])
    advance_result = cli_runner(["workflow", "advance", "--node", node_id])

    assert prompt_result.exit_code == 0
    assert context_result.exit_code == 0
    assert start_result.exit_code == 0
    assert heartbeat_result.exit_code == 0
    assert summary_result.exit_code == 0
    assert complete_result.exit_code == 0
    assert advance_result.exit_code == 0


def _run_flow_06(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = _create_ready_running_node(cli_runner, title="Flow 06 Node", prompt="inspect prompt")

    show_result = cli_runner(["node", "show", "--node", node_id])
    tree_result = cli_runner(["tree", "show", "--node", node_id, "--full"])
    task_current = cli_runner(["task", "current", "--node", node_id])
    subtask_current = cli_runner(["subtask", "current", "--node", node_id])
    blockers_result = cli_runner(["node", "blockers", "--node", node_id])
    sources_result = cli_runner(["yaml", "sources", "--node", node_id])
    workflow_result = cli_runner(["workflow", "show", "--node", node_id])

    assert show_result.exit_code == 0
    assert tree_result.exit_code == 0
    assert task_current.exit_code == 0
    assert task_current.json()["current_task"] is not None
    assert subtask_current.exit_code == 0
    assert blockers_result.exit_code == 0
    assert isinstance(blockers_result.json(), list)
    assert sources_result.exit_code == 0
    assert sources_result.json()["source_documents"]
    assert workflow_result.exit_code == 0


def _run_flow_07(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    monkeypatch.setenv("AICODING_SESSION_BACKEND", "fake")
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = _create_ready_running_node(cli_runner, title="Flow 07 Node", prompt="recover prompt")

    bind_result = cli_runner(["session", "bind", "--node", node_id])
    session_name = bind_result.json()["session_name"]
    daemon_bridge_client.client.app.state.session_adapter.advance_idle(session_name, seconds=30.0)

    current_result = cli_runner(["session", "show-current"])
    recovery_result = cli_runner(["node", "recovery-status", "--node", node_id])
    resume_result = cli_runner(["session", "resume", "--node", node_id])

    assert bind_result.exit_code == 0
    assert current_result.exit_code == 0
    assert current_result.json()["recovery_classification"] == "stale_but_recoverable"
    assert recovery_result.exit_code == 0
    assert recovery_result.json()["recommended_action"] == "resume_existing_session"
    assert resume_result.exit_code == 0
    assert resume_result.json()["status"] in {"reused_existing_session", "replacement_session_created"}


def _run_flow_08(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    parent_id = _create_ready_running_node(cli_runner, title="Flow 08 Parent", prompt="parent prompt")
    child_id = _create_compiled_node(
        cli_runner,
        kind="phase",
        title="Flow 08 Child",
        prompt="environment timeout on remote tool",
        parent=parent_id,
    )
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", child_id]).exit_code == 0
    current_result = cli_runner(["subtask", "current", "--node", child_id])
    compiled_subtask_id = current_result.json()["state"]["current_compiled_subtask_id"]
    assert cli_runner(["subtask", "start", "--node", child_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
    failed_result = cli_runner(
        [
            "subtask",
            "fail",
            "--node",
            child_id,
            "--compiled-subtask",
            compiled_subtask_id,
            "--summary",
            "environment timeout on remote tool",
        ]
    )

    response_result = cli_runner(["node", "respond-to-child-failure", "--node", parent_id, "--child", child_id, "--action", "retry_child"])
    child_failures = cli_runner(["node", "child-failures", "--node", parent_id])
    decision_history = cli_runner(["node", "decision-history", "--node", parent_id])

    assert failed_result.exit_code == 0
    assert failed_result.json()["run"]["run_status"] == "FAILED"
    assert response_result.exit_code == 0
    assert response_result.json()["decision_type"] == "retry_child"
    assert child_failures.exit_code == 0
    assert child_failures.json()["failure_count_from_children"] >= 1
    assert decision_history.exit_code == 0
    assert decision_history.json()["decisions"]


def _run_flow_09(cli_runner, daemon_bridge_client, monkeypatch, app_client, tmp_path, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    app_client.app.state.resource_catalog = _testing_catalog(tmp_path)
    node_id = _create_ready_running_node(cli_runner, title="Flow 09 Node", prompt="quality prompt")

    while True:
        current_payload = cli_runner(["subtask", "current", "--node", node_id]).json()
        if current_payload["current_subtask"]["subtask_type"] == "validate":
            break
        _complete_current_subtask(cli_runner, daemon_bridge_client, node_id=node_id)
        assert cli_runner(["workflow", "advance", "--node", node_id]).exit_code == 0

    quality_chain_result = cli_runner(["node", "quality-chain", "--node", node_id])
    show_validation = cli_runner(["validation", "show", "--node", node_id])
    show_review = cli_runner(["review", "show", "--node", node_id])
    show_testing = cli_runner(["testing", "show", "--node", node_id])
    docs_result = cli_runner(["docs", "list", "--node", node_id])
    summary_result = cli_runner(["summary", "history", "--node", node_id])

    assert quality_chain_result.exit_code == 0
    assert quality_chain_result.json()["executed_stage_types"] == ["validate", "review", "run_tests"]
    assert quality_chain_result.json()["run_status"] == "COMPLETE"
    assert quality_chain_result.json()["provenance"]["entity_count"] > 0
    assert quality_chain_result.json()["docs"]
    assert quality_chain_result.json()["final_summary"]["summary_path"] == "summaries/final.md"
    assert show_validation.exit_code == 0
    assert show_validation.json()["status"] == "passed"
    assert show_review.exit_code == 0
    assert show_review.json()["status"] == "passed"
    assert show_testing.exit_code == 0
    assert show_testing.json()["status"] == "passed"
    assert docs_result.exit_code == 0
    assert docs_result.json()["documents"]
    assert summary_result.exit_code == 0
    assert any(item["summary_type"] == "node" and item["summary_path"] == "summaries/final.md" for item in summary_result.json()["summaries"])


def _run_flow_10(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    root_id = cli_runner(["node", "create", "--kind", "epic", "--title", "Flow 10 Root", "--prompt", "root prompt"]).json()["node_id"]
    child_id = cli_runner(["node", "create", "--kind", "phase", "--title", "Flow 10 Child", "--prompt", "child prompt", "--parent", root_id]).json()["node_id"]

    regenerate_result = cli_runner(["node", "regenerate", "--node", root_id])
    rectify_result = cli_runner(["node", "rectify-upstream", "--node", child_id])
    history_result = cli_runner(["node", "rebuild-history", "--node", child_id])
    versions_result = cli_runner(["node", "versions", "--node", child_id])

    assert regenerate_result.exit_code == 0
    assert regenerate_result.json()["scope"] == "subtree"
    assert rectify_result.exit_code == 0
    assert rectify_result.json()["scope"] == "upstream"
    assert history_result.exit_code == 0
    assert {event["scope"] for event in history_result.json()["events"]} >= {"subtree", "upstream"}
    candidate_version_id = versions_result.json()["versions"][-1]["id"]
    cutover_readiness_result = cli_runner(["node", "version", "cutover-readiness", "--version", candidate_version_id])
    coordination_result = cli_runner(["node", "rebuild-coordination", "--node", child_id, "--scope", "upstream"])
    assert cutover_readiness_result.exit_code == 0
    assert cutover_readiness_result.json()["status"] in {"ready", "blocked"}
    assert coordination_result.exit_code == 0
    assert coordination_result.json()["status"] in {"clear", "blocked"}


def _run_flow_11(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    from uuid import UUID

    from aicoding.daemon.live_git import bootstrap_live_git_repo, stage_live_git_change

    _wire_bridge(monkeypatch, daemon_bridge_client)
    parent_id = cli_runner(["node", "create", "--kind", "epic", "--title", "Flow 11 Parent", "--prompt", "parent prompt"]).json()["node_id"]
    child_id = cli_runner(["node", "child", "create", "--parent", parent_id, "--kind", "phase", "--title", "Flow 11 Child", "--prompt", "child prompt"]).json()["node_id"]
    parent_version_id = cli_runner(["node", "versions", "--node", parent_id]).json()["versions"][0]["id"]
    child_version_id = cli_runner(["node", "versions", "--node", child_id]).json()["versions"][0]["id"]

    assert cli_runner(["workflow", "compile", "--node", parent_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", parent_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "run", "start", "--node", parent_id]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "COMPILED"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "READY"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "RUNNING"]).exit_code == 0
    assert cli_runner(["node", "lifecycle", "transition", "--node", child_id, "--state", "COMPLETE"]).exit_code == 0

    factory = daemon_bridge_client.client.app.state.db_session_factory
    bootstrap_live_git_repo(factory, version_id=UUID(parent_version_id), files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=UUID(child_version_id), files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        factory,
        version_id=UUID(child_version_id),
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )

    merge_result = cli_runner(["git", "merge-children", "--node", parent_id])
    finalize_result = cli_runner(["git", "finalize-node", "--node", parent_id])
    events_result = cli_runner(["git", "merge-events", "show", "--node", parent_id])
    final_result = cli_runner(["git", "final", "show", "--node", parent_id])
    status_result = cli_runner(["git", "status", "show", "--version", parent_version_id])

    assert merge_result.exit_code == 0
    assert merge_result.json()["status"] == "merged"
    assert merge_result.json()["merge_events"][0]["child_final_commit_sha"] == child_status.final_commit_sha
    assert finalize_result.exit_code == 0
    assert finalize_result.json()["status"] == "finalized"
    assert events_result.exit_code == 0
    assert events_result.json()["events"]
    assert final_result.exit_code == 0
    assert final_result.json()["final_commit_sha"] == finalize_result.json()["final_commit_sha"]
    assert status_result.exit_code == 0
    assert status_result.json()["working_tree_state"] == "finalized_clean"


def _run_flow_12(cli_runner, daemon_bridge_client, monkeypatch, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    node_id = _create_ready_running_node(cli_runner, title="Flow 12 Node", prompt="provenance prompt")
    _complete_current_subtask(cli_runner, daemon_bridge_client, node_id=node_id)

    provenance_result = cli_runner(["node", "provenance-refresh", "--node", node_id])
    rationale_result = cli_runner(["rationale", "show", "--node", node_id])
    entity_result = cli_runner(["entity", "show", "--name", "src.aicoding.daemon.app.create_app"])
    relations_result = cli_runner(["entity", "relations", "--name", "src.aicoding.daemon.app.create_app"])
    docs_build = cli_runner(["docs", "build-node-view", "--node", node_id])
    docs_list = cli_runner(["docs", "list", "--node", node_id])

    assert provenance_result.exit_code == 0
    assert rationale_result.exit_code == 0
    assert rationale_result.json()["entity_history"]
    assert entity_result.exit_code == 0
    assert entity_result.json()["entities"]
    assert relations_result.exit_code == 0
    assert relations_result.json()["relations"]
    assert docs_build.exit_code == 0
    assert docs_build.json()["documents"]
    assert docs_list.exit_code == 0
    assert docs_list.json()["documents"]


def _run_flow_13(cli_runner, daemon_bridge_client, monkeypatch, app_client, tmp_path, **_kwargs) -> None:
    _wire_bridge(monkeypatch, daemon_bridge_client)
    app_client.app.state.resource_catalog = _pause_gate_catalog(tmp_path)
    node_id = _create_ready_running_node(cli_runner, title="Flow 13 Node", prompt="human gate prompt")

    progress = cli_runner(["node", "run", "show", "--node", node_id]).json()
    paused_result = None
    while progress["run"]["run_status"] == "RUNNING" and not progress["current_subtask"]["source_subtask_key"].startswith("pause_for_user."):
        compiled_subtask_id = progress["state"]["current_compiled_subtask_id"]
        assert cli_runner(["subtask", "start", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
        assert cli_runner(["subtask", "complete", "--node", node_id, "--compiled-subtask", compiled_subtask_id]).exit_code == 0
        paused_result = cli_runner(["workflow", "advance", "--node", node_id])
        progress = cli_runner(["node", "run", "show", "--node", node_id]).json()

    interventions_result = cli_runner(["node", "interventions", "--node", node_id])
    pause_state = cli_runner(["node", "pause-state", "--node", node_id])
    blocked_resume = cli_runner(["workflow", "resume", "--node", node_id])
    approve_result = cli_runner(
        [
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
        ]
    )
    resume_result = cli_runner(["workflow", "resume", "--node", node_id])

    assert paused_result is not None
    assert paused_result.exit_code == 0
    assert interventions_result.exit_code == 0
    assert any(item["kind"] == "pause_approval" for item in interventions_result.json()["interventions"])
    assert pause_state.exit_code == 0
    assert pause_state.json()["approval_required"] is True
    assert blocked_resume.exit_code == 4
    assert approve_result.exit_code == 0
    assert approve_result.json()["result_json"]["approved"] is True
    assert resume_result.exit_code == 0
    assert resume_result.json()["status"] == "accepted"


FLOW_CASES = (
    FlowCase(
        flow_doc="01_create_top_level_node_flow.md",
        support_level="full",
        scenario_refs=(
            SCENARIO_DOCS[0],
            SCENARIO_DOCS[1],
        ),
        limitation="Top-level creation is currently constrained to built-in top-level kinds such as epic.",
        executor_name="_run_flow_01",
    ),
    FlowCase(
        flow_doc="02_compile_or_recompile_workflow_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[1]),
        limitation="This covers the authoritative compile path rather than arbitrary future compile variants.",
        executor_name="_run_flow_02",
    ),
    FlowCase(
        flow_doc="03_materialize_and_schedule_children_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Current scheduling assertions are bounded to the shipped built-in layouts.",
        executor_name="_run_flow_03",
    ),
    FlowCase(
        flow_doc="04_manual_tree_edit_and_reconcile_flow.md",
        support_level="partial",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Explicit preserve-manual reconciliation now exists, but structural layout replacement and richer hybrid merge decisions are still missing.",
        executor_name="_run_flow_04",
    ),
    FlowCase(
        flow_doc="05_admit_and_execute_node_run_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[1]),
        limitation="The suite covers the durable command-loop slice rather than external tool execution semantics.",
        executor_name="_run_flow_05",
    ),
    FlowCase(
        flow_doc="06_inspect_state_and_blockers_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[1]),
        limitation="Inspection depth is limited to the currently exposed operator and source-lineage surfaces.",
        executor_name="_run_flow_06",
    ),
    FlowCase(
        flow_doc="07_pause_resume_and_recover_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[1]),
        limitation="Recovery remains provider-agnostic rather than provider-specific.",
        executor_name="_run_flow_07",
    ),
    FlowCase(
        flow_doc="08_handle_failure_and_escalate_flow.md",
        support_level="partial",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Current flow coverage exercises persisted counters and decisions, but failure classification remains bounded to current heuristics.",
        executor_name="_run_flow_08",
    ),
    FlowCase(
        flow_doc="09_run_quality_gates_flow.md",
        support_level="partial",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="The daemon now exposes one turnkey quality-chain command, but live git finalize execution still belongs to the later git execution slice.",
        executor_name="_run_flow_09",
    ),
    FlowCase(
        flow_doc="10_regenerate_and_rectify_flow.md",
        support_level="partial",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Live rebuild coordination and cutover-readiness inspection now exist, but real live git rebuild/finalize execution is still staged.",
        executor_name="_run_flow_10",
    ),
    FlowCase(
        flow_doc="11_finalize_and_merge_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="The direct parent merge/finalize path is live; rebuild-driven git rectification still belongs to the rebuild-specific flow.",
        executor_name="_run_flow_11",
    ),
    FlowCase(
        flow_doc="12_query_provenance_and_docs_flow.md",
        support_level="full",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Provenance extraction is intentionally bounded to the current Python plus JS/TS module|class|function|method entity model.",
        executor_name="_run_flow_12",
    ),
    FlowCase(
        flow_doc="13_human_gate_and_intervention_flow.md",
        support_level="partial",
        scenario_refs=(SCENARIO_DOCS[0], SCENARIO_DOCS[2]),
        limitation="Unified intervention catalog/apply now covers pause, reconciliation, merge-conflict, and recovery attention, but cutover and rebuild-specific human decisions are still not routed through one apply surface.",
        executor_name="_run_flow_13",
    ),
)


def test_every_flow_doc_has_a_registered_executor() -> None:
    flow_docs = {path.name for path in FLOW_DIR.glob("[0-9][0-9]_*.md")}
    registered = {case.flow_doc for case in FLOW_CASES}

    assert flow_docs == registered


@pytest.mark.parametrize("case", FLOW_CASES, ids=lambda case: case.flow_doc.split("_", 1)[0])
def test_flow_contract_cases(
    case: FlowCase,
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
    app_client,
) -> None:
    executor = globals()[case.executor_name]
    executor(
        cli_runner=cli_runner,
        daemon_bridge_client=daemon_bridge_client,
        migrated_public_schema=migrated_public_schema,
        monkeypatch=monkeypatch,
        tmp_path=tmp_path,
        app_client=app_client,
    )

    assert case.support_level in {"full", "partial", "deferred_heavy"}
    assert case.scenario_refs
    assert case.limitation
