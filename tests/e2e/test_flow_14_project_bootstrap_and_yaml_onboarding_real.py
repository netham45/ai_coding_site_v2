from __future__ import annotations

import subprocess
import time

import pytest


def _write_workspace_project_bootstrap_inputs(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    testing_definition = workspace_root / "resources" / "yaml" / "project" / "testing" / "custom_retry_gate.yaml"
    docs_definition = workspace_root / "resources" / "yaml" / "project" / "docs" / "local_node_docs.yaml"
    override_path = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_tasks.yaml"

    project_policy.parent.mkdir(parents=True, exist_ok=True)
    testing_definition.parent.mkdir(parents=True, exist_ok=True)
    docs_definition.parent.mkdir(parents=True, exist_ok=True)
    override_path.parent.mkdir(parents=True, exist_ok=True)

    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Real E2E flow 14 bootstrap policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: true",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs:",
                "    - testing/custom_retry_gate.yaml",
                "  docs_refs:",
                "    - docs/local_node_docs.yaml",
                "  enabled_node_kinds:",
                "    - epic",
                "    - phase",
                "    - plan",
                "    - task",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    testing_definition.write_text(
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
                "description: Real E2E bootstrap testing gate.",
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
    docs_definition.write_text(
        "\n".join(
            [
                "kind: docs_definition",
                "id: local_node_docs",
                "name: Local Node Docs",
                "applies_to:",
                "  node_kinds: [epic, phase, plan, task]",
                "  task_ids: []",
                "  lifecycle_points: [after_node_complete]",
                "scope: custom",
                "description: Build a local node docs view.",
                "inputs:",
                "  include_static_analysis: false",
                "  include_entity_relations: true",
                "  include_node_summaries: true",
                "  include_prompt_history: true",
                "  include_review_results: true",
                "  include_test_results: true",
                "outputs:",
                "  - path: docs/generated/local-node.md",
                "    view: local_node",
            ]
        ),
        encoding="utf-8",
    )
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
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_14_project_bootstrap_and_yaml_onboarding_runs_against_real_daemon_and_real_cli(real_daemon_harness) -> None:
    _write_workspace_project_bootstrap_inputs(real_daemon_harness.workspace_root)

    project_policy_result = real_daemon_harness.cli(
        "yaml",
        "validate",
        "--group",
        "yaml_project",
        "--path",
        "project-policies/default_project_policy.yaml",
    )
    testing_result = real_daemon_harness.cli(
        "yaml",
        "validate",
        "--group",
        "yaml_project",
        "--path",
        "testing/custom_retry_gate.yaml",
    )
    docs_result = real_daemon_harness.cli(
        "yaml",
        "validate",
        "--group",
        "yaml_project",
        "--path",
        "docs/local_node_docs.yaml",
    )
    override_result = real_daemon_harness.cli(
        "yaml",
        "validate",
        "--group",
        "yaml_overrides",
        "--path",
        "nodes/epic_tasks.yaml",
    )
    create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Flow 14 Bootstrap Epic",
        "--prompt",
        "Compile the first project-scoped node against built-in and project-local YAML.",
    )
    assert create_result.exit_code == 0, create_result.stderr
    node_id = str(create_result.json()["node_id"])

    compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    current_result = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    sources_result = real_daemon_harness.cli("workflow", "sources", "--node", node_id)
    resolved_result = real_daemon_harness.cli("yaml", "resolved", "--node", node_id, "--family", "node_definition", "--id", "epic")
    effective_policy_result = real_daemon_harness.cli("yaml", "effective-policy")
    policy_impact_result = real_daemon_harness.cli("yaml", "policy-impact", "--kind", "epic")

    assert project_policy_result.exit_code == 0, project_policy_result.stderr
    assert testing_result.exit_code == 0, testing_result.stderr
    assert docs_result.exit_code == 0, docs_result.stderr
    assert override_result.exit_code == 0, override_result.stderr
    assert compile_result.exit_code == 0, compile_result.stderr
    assert current_result.exit_code == 0, current_result.stderr
    assert sources_result.exit_code == 0, sources_result.stderr
    assert resolved_result.exit_code == 0, resolved_result.stderr
    assert effective_policy_result.exit_code == 0, effective_policy_result.stderr
    assert policy_impact_result.exit_code == 0, policy_impact_result.stderr

    start_result = real_daemon_harness.cli("node", "run", "start", "--node", node_id)
    assert start_result.exit_code == 0, start_result.stderr
    bind_result = real_daemon_harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])
    run_show_payload = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        run_show = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
        assert run_show.exit_code == 0, run_show.stderr
        run_show_payload = run_show.json()
        last_pane_text = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", session_name],
            text=True,
            capture_output=True,
            check=False,
        ).stdout
        if (
            run_show_payload["latest_attempt"] is not None
            or run_show_payload["state"]["last_completed_compiled_subtask_id"] is not None
            or run_show_payload["run"]["run_status"] in {"FAILED", "PAUSED", "COMPLETED", "COMPLETE"}
        ):
            break
        time.sleep(2.0)

    compile_payload = compile_result.json()
    current_payload = current_result.json()
    sources_payload = sources_result.json()
    resolved_payload = resolved_result.json()
    effective_policy_payload = effective_policy_result.json()
    policy_impact_payload = policy_impact_result.json()

    assert project_policy_result.json()["family"] == "project_policy_definition"
    assert project_policy_result.json()["valid"] is True
    assert testing_result.json()["family"] == "testing_definition"
    assert testing_result.json()["valid"] is True
    assert docs_result.json()["family"] == "docs_definition"
    assert docs_result.json()["valid"] is True
    assert override_result.json()["family"] == "override_definition"
    assert override_result.json()["valid"] is True
    assert compile_payload["status"] == "compiled"
    assert run_show_payload is not None, (
        "Expected the project bootstrap/onboarding flow to produce durable run state after a real started run and bound tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )
    assert compile_payload["compiled_workflow"]["resolved_yaml"]["effective_policy"]["project_policy_ids"] == [
        "default_project_policy"
    ]
    assert current_payload["tasks"]
    source_paths = {item["relative_path"] for item in sources_payload["source_documents"]}
    assert "nodes/epic.yaml" in source_paths
    assert "project-policies/default_project_policy.yaml" in source_paths
    assert "nodes/epic_tasks.yaml" in source_paths
    assert resolved_payload["resolved_documents"][0]["target_id"] == "epic"
    assert "default_project_policy" in effective_policy_payload["project_policy_ids"]
    assert policy_impact_payload["node_kind"] == "epic"
    assert policy_impact_payload["enabled_for_node_kind"] is True
