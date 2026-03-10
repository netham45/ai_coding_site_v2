from __future__ import annotations

import pytest


def _write_broken_compile_inputs(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    node_override = workspace_root / "resources" / "yaml" / "overrides" / "nodes" / "epic_tasks.yaml"
    task_override = workspace_root / "resources" / "yaml" / "overrides" / "tasks" / "review_node_reviews.yaml"

    project_policy.parent.mkdir(parents=True, exist_ok=True)
    node_override.parent.mkdir(parents=True, exist_ok=True)
    task_override.parent.mkdir(parents=True, exist_ok=True)

    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Broken project policy for real E2E compile diagnostics.",
                "  defaults:",
                "    auto_run_children: true",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs: invalid",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )
    node_override.write_text(
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
                "    - review_node",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    task_override.write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: review_node",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: append_list",
                "value:",
                "  uses_reviews:",
                "    - policy_compliance_review",
            ]
        ),
        encoding="utf-8",
    )


def _repair_project_policy(workspace_root) -> None:
    project_policy = workspace_root / "resources" / "yaml" / "project" / "project-policies" / "default_project_policy.yaml"
    project_policy.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Repaired project policy for real E2E compile diagnostics.",
                "  defaults:",
                "    auto_run_children: true",
                "  runtime_policy_refs: []",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
                "  review_refs: []",
                "  testing_refs: []",
                "  docs_refs: []",
                "  enabled_node_kinds: [epic, phase, plan, task]",
                "  prompt_pack: default",
                "  environment_profiles: []",
            ]
        ),
        encoding="utf-8",
    )


@pytest.mark.e2e_real
def test_e2e_compile_variants_and_diagnostics(real_daemon_harness) -> None:
    _write_broken_compile_inputs(real_daemon_harness.workspace_root)

    create_result = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real E2E Compile Diagnostics Epic",
        "--prompt",
        "Compile this node through broken and repaired YAML policy states.",
    )
    assert create_result.exit_code == 0, create_result.stderr
    node_id = str(create_result.json()["node_id"])

    failed_compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    failed_compile_failures_result = real_daemon_harness.cli("workflow", "compile-failures", "--node", node_id)

    assert failed_compile_result.exit_code == 0, failed_compile_result.stderr
    assert failed_compile_failures_result.exit_code == 0, failed_compile_failures_result.stderr

    failed_compile_payload = failed_compile_result.json()
    failed_compile_failures_payload = failed_compile_failures_result.json()

    assert failed_compile_payload["status"] == "failed"
    assert failed_compile_payload["compile_failure"]["failure_class"] == "schema_validation_failure"
    assert failed_compile_payload["compile_failure"]["failure_stage"] == "schema_validation"
    assert failed_compile_failures_payload["failures"]
    assert failed_compile_failures_payload["failures"][0]["failure_class"] == "schema_validation_failure"
    assert failed_compile_failures_payload["failures"][0]["target_id"] == "project-policies/default_project_policy.yaml"

    _repair_project_policy(real_daemon_harness.workspace_root)

    compile_result = real_daemon_harness.cli("workflow", "compile", "--node", node_id)
    current_result = real_daemon_harness.cli("workflow", "current", "--node", node_id)
    source_discovery_result = real_daemon_harness.cli("workflow", "source-discovery", "--node", node_id)
    schema_validation_result = real_daemon_harness.cli("workflow", "schema-validation", "--node", node_id)
    override_resolution_result = real_daemon_harness.cli("workflow", "override-resolution", "--node", node_id)
    hook_policy_result = real_daemon_harness.cli("workflow", "hook-policy", "--node", node_id)
    rendering_result = real_daemon_harness.cli("workflow", "rendering", "--node", node_id)
    failures_result = real_daemon_harness.cli("workflow", "compile-failures", "--node", node_id)
    override_chain_result = real_daemon_harness.cli("yaml", "override-chain", "--node", node_id)
    resolved_result = real_daemon_harness.cli("yaml", "resolved", "--node", node_id, "--family", "task_definition", "--id", "review_node")
    effective_policy_result = real_daemon_harness.cli("yaml", "effective-policy")
    policy_impact_result = real_daemon_harness.cli("yaml", "policy-impact", "--kind", "epic")

    assert compile_result.exit_code == 0, compile_result.stderr
    assert current_result.exit_code == 0, current_result.stderr
    assert source_discovery_result.exit_code == 0, source_discovery_result.stderr
    assert schema_validation_result.exit_code == 0, schema_validation_result.stderr
    assert override_resolution_result.exit_code == 0, override_resolution_result.stderr
    assert hook_policy_result.exit_code == 0, hook_policy_result.stderr
    assert rendering_result.exit_code == 0, rendering_result.stderr
    assert failures_result.exit_code == 0, failures_result.stderr
    assert override_chain_result.exit_code == 0, override_chain_result.stderr
    assert resolved_result.exit_code == 0, resolved_result.stderr
    assert effective_policy_result.exit_code == 0, effective_policy_result.stderr
    assert policy_impact_result.exit_code == 0, policy_impact_result.stderr

    compile_payload = compile_result.json()
    current_payload = current_result.json()
    source_discovery_payload = source_discovery_result.json()
    schema_validation_payload = schema_validation_result.json()
    override_resolution_payload = override_resolution_result.json()
    hook_policy_payload = hook_policy_result.json()
    rendering_payload = rendering_result.json()
    failures_payload = failures_result.json()
    override_chain_payload = override_chain_result.json()
    resolved_payload = resolved_result.json()
    effective_policy_payload = effective_policy_result.json()
    policy_impact_payload = policy_impact_result.json()

    assert compile_payload["status"] == "compiled"
    assert current_payload["id"] == compile_payload["compiled_workflow"]["id"]
    assert source_discovery_payload["discovery_order"]
    assert {
        item["relative_path"] for item in source_discovery_payload["discovery_order"]
    } >= {"nodes/epic.yaml", "project-policies/default_project_policy.yaml"}
    assert schema_validation_payload["validated_document_count"] > 0
    assert schema_validation_payload["family_counts"]["node_definition"] >= 1
    assert override_resolution_payload["resolved_document_count"] > 0
    assert "applied_overrides" in override_resolution_payload
    assert hook_policy_payload["compiled_workflow_id"] == compile_payload["compiled_workflow"]["id"]
    assert hook_policy_payload["selected_hooks"][0]["hook_id"] == "default_hooks"
    assert rendering_payload["compile_context"]["compile_variant"] == "authoritative"
    assert failures_payload["failures"]
    assert failures_payload["failures"][0]["failure_class"] == "schema_validation_failure"
    assert failures_payload["failures"][0]["target_id"] == "project-policies/default_project_policy.yaml"
    assert {
        item["override_relative_path"] for item in override_chain_payload["applied_overrides"]
    } == {"nodes/epic_tasks.yaml", "tasks/review_node_reviews.yaml"}
    assert resolved_payload["resolved_documents"][0]["target_id"] == "review_node"
    assert resolved_payload["resolved_documents"][0]["resolved_document"]["uses_reviews"] == [
        "reviews/node_against_requirements.yaml",
        "policy_compliance_review",
    ]
    assert "default_project_policy" in effective_policy_payload["project_policy_ids"]
    assert policy_impact_payload["node_kind"] == "epic"
    assert policy_impact_payload["enabled_for_node_kind"] is True

    supersede_result = real_daemon_harness.cli("node", "supersede", "--node", node_id, "--title", "Real E2E Compile Diagnostics Epic v2")
    assert supersede_result.exit_code == 0, supersede_result.stderr
    candidate_version_id = str(supersede_result.json()["id"])

    candidate_compile_result = real_daemon_harness.cli("workflow", "compile", "--version", candidate_version_id)
    candidate_show_result = real_daemon_harness.cli("workflow", "show", "--version", candidate_version_id)
    candidate_discovery_result = real_daemon_harness.cli("workflow", "source-discovery", "--version", candidate_version_id)

    assert candidate_compile_result.exit_code == 0, candidate_compile_result.stderr
    assert candidate_show_result.exit_code == 0, candidate_show_result.stderr
    assert candidate_discovery_result.exit_code == 0, candidate_discovery_result.stderr

    assert candidate_compile_result.json()["compile_context"]["compile_variant"] == "candidate"
    assert candidate_show_result.json()["compile_context"]["compile_variant"] == "candidate"
    assert candidate_discovery_result.json()["compile_context"]["compile_variant"] == "candidate"

    regenerate_result = real_daemon_harness.cli("node", "regenerate", "--node", node_id)
    assert regenerate_result.exit_code == 0, regenerate_result.stderr
    rebuild_version_id = str(regenerate_result.json()["created_candidate_version_ids"][0])

    rebuild_compile_result = real_daemon_harness.cli("workflow", "compile", "--version", rebuild_version_id)
    rebuild_rendering_result = real_daemon_harness.cli("workflow", "rendering", "--version", rebuild_version_id)
    rebuild_failures_result = real_daemon_harness.cli("workflow", "compile-failures", "--version", rebuild_version_id)

    assert rebuild_compile_result.exit_code == 0, rebuild_compile_result.stderr
    assert rebuild_rendering_result.exit_code == 0, rebuild_rendering_result.stderr
    assert rebuild_failures_result.exit_code == 0, rebuild_failures_result.stderr

    assert rebuild_compile_result.json()["compile_context"]["compile_variant"] == "rebuild_candidate"
    assert rebuild_compile_result.json()["compile_context"]["rebuild_context"]["scope"] == "subtree"
    assert rebuild_rendering_result.json()["compile_context"]["compile_variant"] == "rebuild_candidate"
    assert rebuild_failures_result.json()["failures"] == []
