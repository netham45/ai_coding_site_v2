from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from aicoding.daemon.live_git import bootstrap_live_git_repo, stage_live_git_change
from aicoding.daemon.incremental_parent_merge import process_next_incremental_child_merge
from aicoding.daemon.live_git import refresh_child_live_git_from_parent_head
from aicoding.flow_assets import FlowYamlAsset, load_flow_yaml_asset
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from aicoding.db.models import LogicalNodeCurrentVersion
from aicoding.db.session import query_session_scope


REPO_ROOT = Path(__file__).resolve().parents[2]
FLOWS_DIR = REPO_ROOT / "flows"


@dataclass(frozen=True, slots=True)
class FlowYamlCase:
    flow_yaml: str
    executor_name: str


def _project_bootstrap_catalog(tmp_path: Path):
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "docs").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Flow-yaml bootstrap policy.",
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
                "description: Bootstrap flow testing gate.",
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
    (project_root / "docs" / "local_node_docs.yaml").write_text(
        "\n".join(
            [
                "kind: docs_definition",
                "id: local_node_docs",
                "name: Local Node Docs",
                "applies_to:",
                "  node_kinds: [epic, phase, plan, task]",
                "  lifecycle_points: [before_finalize]",
                "description: Build a local node docs view.",
                "output_targets:",
                "  - local_markdown",
                "prompt_template: docs/build_node_view.md",
                "summary_requirements:",
                "  include_artifacts: true",
                "  include_findings: true",
            ]
        ),
        encoding="utf-8",
    )
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_tasks.yaml").write_text(
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


def _run_flow_yaml_14(app_client, auth_headers, tmp_path: Path) -> None:
    catalog = _project_bootstrap_catalog(tmp_path)
    app_client.app.state.resource_catalog = catalog
    app_client.app.state.hierarchy_registry = load_hierarchy_registry(catalog)

    project_policy_response = app_client.post(
        "/api/yaml/validate",
        headers=auth_headers,
        json={"source_group": "yaml_project", "relative_path": "project-policies/default_project_policy.yaml"},
    )
    testing_response = app_client.post(
        "/api/yaml/validate",
        headers=auth_headers,
        json={"source_group": "yaml_project", "relative_path": "testing/custom_retry_gate.yaml"},
    )
    override_response = app_client.post(
        "/api/yaml/validate",
        headers=auth_headers,
        json={"source_group": "yaml_overrides", "relative_path": "nodes/epic_tasks.yaml"},
    )
    create_response = app_client.post(
        "/api/nodes/create",
        headers=auth_headers,
        json={"kind": "epic", "title": "Bootstrap Epic", "prompt": "bootstrap prompt"},
    )
    node_id = create_response.json()["node_id"]
    compile_response = app_client.post(
        f"/api/nodes/{node_id}/workflow/compile",
        headers=auth_headers,
        json={},
    )
    workflow_id = compile_response.json()["compiled_workflow"]["id"]
    sources_response = app_client.get(f"/api/workflows/{workflow_id}/sources", headers=auth_headers)
    resolved_response = app_client.get(
        f"/api/nodes/{node_id}/yaml/resolved?family=node_definition&document_id=epic",
        headers=auth_headers,
    )

    assert project_policy_response.status_code == 200
    assert project_policy_response.json()["family"] == "project_policy_definition"
    assert project_policy_response.json()["valid"] is True
    assert testing_response.status_code == 200
    assert testing_response.json()["family"] == "testing_definition"
    assert testing_response.json()["valid"] is True
    assert override_response.status_code == 200
    assert override_response.json()["family"] == "override_definition"
    assert override_response.json()["valid"] is True
    assert create_response.status_code == 200
    assert compile_response.status_code == 200
    assert compile_response.json()["status"] == "compiled"
    assert "default_project_policy" in compile_response.json()["compiled_workflow"]["resolved_yaml"]["effective_policy"]["project_policy_ids"]
    assert sources_response.status_code == 200
    source_paths = {item["relative_path"] for item in sources_response.json()["source_documents"]}
    assert "nodes/epic.yaml" in source_paths
    assert "project-policies/default_project_policy.yaml" in source_paths
    assert "nodes/epic_tasks.yaml" in source_paths
    assert resolved_response.status_code == 200
    assert resolved_response.json()["resolved_documents"][0]["target_id"] == "epic"


FLOW_YAML_CASES = (
    FlowYamlCase(
        flow_yaml="14_project_bootstrap_and_yaml_onboarding_flow.yaml",
        executor_name="_run_flow_yaml_14",
    ),
    FlowYamlCase(
        flow_yaml="15_epic_default_workflow_blueprint_flow.yaml",
        executor_name="_run_flow_yaml_15",
    ),
    FlowYamlCase(
        flow_yaml="16_phase_default_workflow_blueprint_flow.yaml",
        executor_name="_run_flow_yaml_16",
    ),
    FlowYamlCase(
        flow_yaml="17_plan_default_workflow_blueprint_flow.yaml",
        executor_name="_run_flow_yaml_17",
    ),
    FlowYamlCase(
        flow_yaml="18_task_default_workflow_blueprint_flow.yaml",
        executor_name="_run_flow_yaml_18",
    ),
    FlowYamlCase(
        flow_yaml="19_hook_expansion_compile_stage_flow.yaml",
        executor_name="_run_flow_yaml_19",
    ),
    FlowYamlCase(
        flow_yaml="20_compile_failure_and_reattempt_flow.yaml",
        executor_name="_run_flow_yaml_20",
    ),
    FlowYamlCase(
        flow_yaml="21_child_session_round_trip_and_mergeback_flow.yaml",
        executor_name="_run_flow_yaml_21",
    ),
    FlowYamlCase(
        flow_yaml="22_dependency_blocked_sibling_wait_flow.yaml",
        executor_name="_run_flow_yaml_22",
    ),
)


def _create_node(app_client, auth_headers, *, kind: str, title: str, prompt: str, parent_node_id: str | None = None) -> str:
    payload: dict[str, object] = {"kind": kind, "title": title, "prompt": prompt}
    if parent_node_id is not None:
        payload["parent_node_id"] = parent_node_id
    response = app_client.post("/api/nodes/create", headers=auth_headers, json=payload)
    assert response.status_code == 200
    return response.json()["node_id"]


def _compile_and_load_task_keys(app_client, auth_headers, node_id: str) -> list[str]:
    compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    assert compile_response.status_code == 200
    current_response = app_client.get(f"/api/nodes/{node_id}/workflow/current", headers=auth_headers)
    assert current_response.status_code == 200
    return [item["task_key"] for item in current_response.json()["tasks"]]


def _run_flow_yaml_15(app_client, auth_headers, **_kwargs) -> None:
    node_id = _create_node(app_client, auth_headers, kind="epic", title="Blueprint Epic", prompt="epic prompt")
    task_keys = _compile_and_load_task_keys(app_client, auth_headers, node_id)

    assert task_keys == ["generate_child_layout", "review_child_layout", "spawn_children", "wait_for_children"]


def _run_flow_yaml_16(app_client, auth_headers, **_kwargs) -> None:
    epic_id = _create_node(app_client, auth_headers, kind="epic", title="Blueprint Epic", prompt="epic prompt")
    phase_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Blueprint Phase",
        prompt="phase prompt",
        parent_node_id=epic_id,
    )
    task_keys = _compile_and_load_task_keys(app_client, auth_headers, phase_id)

    assert task_keys == ["generate_child_layout", "review_child_layout", "spawn_children", "wait_for_children"]


def _run_flow_yaml_17(app_client, auth_headers, **_kwargs) -> None:
    epic_id = _create_node(app_client, auth_headers, kind="epic", title="Blueprint Epic", prompt="epic prompt")
    phase_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Blueprint Phase",
        prompt="phase prompt",
        parent_node_id=epic_id,
    )
    plan_id = _create_node(
        app_client,
        auth_headers,
        kind="plan",
        title="Blueprint Plan",
        prompt="plan prompt",
        parent_node_id=phase_id,
    )
    task_keys = _compile_and_load_task_keys(app_client, auth_headers, plan_id)

    assert task_keys == ["generate_child_layout", "review_child_layout", "spawn_children", "wait_for_children"]


def _run_flow_yaml_18(app_client, auth_headers, **_kwargs) -> None:
    epic_id = _create_node(app_client, auth_headers, kind="epic", title="Blueprint Epic", prompt="epic prompt")
    phase_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Blueprint Phase",
        prompt="phase prompt",
        parent_node_id=epic_id,
    )
    plan_id = _create_node(
        app_client,
        auth_headers,
        kind="plan",
        title="Blueprint Plan",
        prompt="plan prompt",
        parent_node_id=phase_id,
    )
    task_id = _create_node(
        app_client,
        auth_headers,
        kind="task",
        title="Blueprint Task",
        prompt="task prompt",
        parent_node_id=plan_id,
    )
    task_keys = _compile_and_load_task_keys(app_client, auth_headers, task_id)

    assert task_keys == ["execute_node", "validate_node", "review_node"]


def _run_flow_yaml_19(app_client, auth_headers, **_kwargs) -> None:
    epic_id = _create_node(app_client, auth_headers, kind="epic", title="Hook Epic", prompt="epic prompt")
    phase_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Hook Phase",
        prompt="phase prompt",
        parent_node_id=epic_id,
    )
    plan_id = _create_node(
        app_client,
        auth_headers,
        kind="plan",
        title="Hook Plan",
        prompt="plan prompt",
        parent_node_id=phase_id,
    )
    task_id = _create_node(
        app_client,
        auth_headers,
        kind="task",
        title="Hook Task",
        prompt="task prompt",
        parent_node_id=plan_id,
    )

    compile_response = app_client.post(f"/api/nodes/{task_id}/workflow/compile", headers=auth_headers, json={})
    hooks_response = app_client.get(f"/api/nodes/{task_id}/workflow/hooks", headers=auth_headers)
    hook_policy_response = app_client.get(f"/api/nodes/{task_id}/workflow/hook-policy", headers=auth_headers)

    assert compile_response.status_code == 200
    assert hooks_response.status_code == 200
    assert hook_policy_response.status_code == 200
    assert {item["hook_id"] for item in hooks_response.json()["selected_hooks"]} == {
        "default_hooks",
        "before_validation_default",
        "before_review_default",
        "before_testing_default",
        "after_node_complete_build_docs",
        "after_node_complete_update_provenance",
    }
    assert [item["source_subtask_key"] for item in hooks_response.json()["expanded_steps"]] == [
        "execute_node.hook.default_hooks.1",
        "validate_node.hook.before_validation_default.1",
        "review_node.hook.before_review_default.1",
    ]
    assert hook_policy_response.json()["selected_hooks"][0]["hook_id"] == "default_hooks"
    assert hook_policy_response.json()["expanded_steps"][0]["source_subtask_key"] == "execute_node.hook.default_hooks.1"


def _run_flow_yaml_20(app_client, auth_headers, tmp_path: Path, **_kwargs) -> None:
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    policy_path = project_root / "project-policies" / "default_project_policy.yaml"
    policy_path.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Broken project policy for compile failure flow.",
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
    catalog = replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
    )
    app_client.app.state.resource_catalog = catalog
    app_client.app.state.hierarchy_registry = load_hierarchy_registry(catalog)

    node_id = _create_node(app_client, auth_headers, kind="epic", title="Broken Compile Epic", prompt="broken prompt")

    failed_compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    failures_response = app_client.get(f"/api/nodes/{node_id}/workflow/compile-failures", headers=auth_headers)

    assert failed_compile_response.status_code == 200
    failed_payload = failed_compile_response.json()
    assert failed_payload["status"] == "failed"
    assert failed_payload["compile_failure"]["failure_class"] == "schema_validation_failure"
    assert failed_payload["compile_failure"]["failure_stage"] == "schema_validation"
    assert failures_response.status_code == 200
    assert failures_response.json()["failures"][0]["failure_class"] == "schema_validation_failure"
    assert failures_response.json()["failures"][0]["target_id"] == "project-policies/default_project_policy.yaml"

    policy_path.write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Repaired project policy for compile failure flow.",
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

    successful_compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    sources_response = app_client.get(f"/api/nodes/{node_id}/workflow/source-discovery", headers=auth_headers)
    current_workflow_response = app_client.get(f"/api/nodes/{node_id}/workflow/current", headers=auth_headers)

    assert successful_compile_response.status_code == 200
    assert successful_compile_response.json()["status"] == "compiled"
    assert sources_response.status_code == 200
    assert {
        item["relative_path"] for item in sources_response.json()["discovery_order"]
    } >= {"nodes/epic.yaml", "project-policies/default_project_policy.yaml"}
    assert current_workflow_response.status_code == 200
    assert current_workflow_response.json()["tasks"]


def _run_flow_yaml_21(app_client, auth_headers, **_kwargs) -> None:
    node_id = _create_node(app_client, auth_headers, kind="epic", title="Child Flow Epic", prompt="child prompt")

    compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
    ready_response = app_client.post(
        "/api/nodes/lifecycle/transition",
        headers=auth_headers,
        json={"node_id": node_id, "target_state": "READY"},
    )
    run_start_response = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": node_id})
    bind_response = app_client.post("/api/sessions/bind", headers=auth_headers, json={"node_id": node_id})
    current_before_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers=auth_headers)

    child_push_response = app_client.post(
        "/api/sessions/push",
        headers=auth_headers,
        json={"node_id": node_id, "reason": "research_context"},
    )
    child_session_id = child_push_response.json()["session_id"]
    child_pop_response = app_client.post(
        "/api/sessions/pop",
        headers=auth_headers,
        json={
            "session_id": child_session_id,
            "status": "success",
            "summary": "child research done",
            "findings": ["finding-a"],
            "artifacts": [{"path": "notes/research.md", "type": "notes"}],
            "suggested_next_actions": ["continue"],
        },
    )
    child_result_response = app_client.get(f"/api/sessions/{child_session_id}/result", headers=auth_headers)
    current_after_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current", headers=auth_headers)
    context_response = app_client.get(f"/api/nodes/{node_id}/subtasks/current/context", headers=auth_headers)

    assert compile_response.status_code == 200
    assert compile_response.json()["status"] == "compiled"
    assert ready_response.status_code == 200
    assert run_start_response.status_code == 200
    assert run_start_response.json()["current_state"] == "RUNNING"
    assert bind_response.status_code == 200
    assert current_before_response.status_code == 200
    before_subtask_id = current_before_response.json()["state"]["current_compiled_subtask_id"]
    assert before_subtask_id is not None

    assert child_push_response.status_code == 200
    assert child_push_response.json()["reason"] == "research_context"
    assert child_pop_response.status_code == 200
    assert child_pop_response.json()["status"] == "success"
    assert child_result_response.status_code == 200
    assert child_result_response.json()["summary"] == "child research done"
    assert current_after_response.status_code == 200
    assert current_after_response.json()["state"]["current_compiled_subtask_id"] == before_subtask_id
    assert context_response.status_code == 200
    assert context_response.json()["compiled_subtask_id"] == before_subtask_id
    assert context_response.json()["input_context_json"]["child_session_results"][0]["child_session_id"] == child_session_id
    assert context_response.json()["input_context_json"]["child_session_results"][0]["summary"] == "child research done"


def _run_flow_yaml_22(app_client, auth_headers, **_kwargs) -> None:
    app_client.app.state.settings.session.poll_interval_seconds = 3600.0
    parent_id = _create_node(app_client, auth_headers, kind="epic", title="Dependency Parent", prompt="parent prompt")
    left_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Dependency Left",
        prompt="left prompt",
        parent_node_id=parent_id,
    )
    right_id = _create_node(
        app_client,
        auth_headers,
        kind="phase",
        title="Dependency Right",
        prompt="right prompt",
        parent_node_id=parent_id,
    )

    for node_id in (left_id, right_id):
        compile_response = app_client.post(f"/api/nodes/{node_id}/workflow/compile", headers=auth_headers, json={})
        ready_response = app_client.post(
            "/api/nodes/lifecycle/transition",
            headers=auth_headers,
            json={"node_id": node_id, "target_state": "READY"},
        )
        assert compile_response.status_code == 200
        assert compile_response.json()["status"] == "compiled"
        assert ready_response.status_code == 200

    add_response = app_client.post(
        "/api/nodes/dependencies/add",
        headers=auth_headers,
        json={"node_id": right_id, "depends_on_node_id": left_id, "required_state": "COMPLETE"},
    )
    validation_response = app_client.get(f"/api/nodes/{right_id}/dependency-validate", headers=auth_headers)
    status_response = app_client.get(f"/api/nodes/{right_id}/dependency-status", headers=auth_headers)
    blockers_response = app_client.get(f"/api/nodes/{right_id}/blockers", headers=auth_headers)

    assert add_response.status_code == 200
    assert add_response.json()["dependency_type"] == "sibling"
    assert validation_response.status_code == 200
    assert validation_response.json()["status"] == "valid"
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "blocked"
    assert blockers_response.status_code == 200
    assert blockers_response.json()[0]["blocker_kind"] == "blocked_on_dependency"

    session_factory = app_client.app.state.db_session_factory
    with query_session_scope(session_factory) as session:
        parent_selector = session.get(LogicalNodeCurrentVersion, parent_id)
        left_selector = session.get(LogicalNodeCurrentVersion, left_id)
        right_selector = session.get(LogicalNodeCurrentVersion, right_id)
        assert parent_selector is not None
        assert left_selector is not None
        assert right_selector is not None
        parent_version_id = parent_selector.authoritative_node_version_id
        left_version_id = left_selector.authoritative_node_version_id
        right_version_id = right_selector.authoritative_node_version_id

    bootstrap_live_git_repo(
        session_factory,
        version_id=parent_version_id,
        files={"shared.txt": "base\n"},
        replace_existing=True,
    )
    bootstrap_live_git_repo(
        session_factory,
        version_id=left_version_id,
        files={"shared.txt": "base\n"},
        replace_existing=True,
    )
    bootstrap_live_git_repo(
        session_factory,
        version_id=right_version_id,
        files={"shared.txt": "base\n"},
        replace_existing=True,
    )
    stage_live_git_change(
        session_factory,
        version_id=left_version_id,
        files={"shared.txt": "base\nleft final\n"},
        message="Left final",
        record_as_final=True,
    )

    left_start_response = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": left_id})
    left_complete_response = app_client.post(
        "/api/nodes/lifecycle/transition",
        headers=auth_headers,
        json={"node_id": left_id, "target_state": "COMPLETE"},
    )
    blocked_after_complete = app_client.get(f"/api/nodes/{right_id}/dependency-status", headers=auth_headers)
    blockers_after_complete = app_client.get(f"/api/nodes/{right_id}/blockers", headers=auth_headers)
    merge_result = process_next_incremental_child_merge(
        session_factory,
        parent_node_version_id=parent_version_id,
    )
    refresh_child_live_git_from_parent_head(
        session_factory,
        child_version_id=right_version_id,
    )
    ready_after_merge = app_client.get(f"/api/nodes/{right_id}/dependency-status", headers=auth_headers)
    blockers_after_merge = app_client.get(f"/api/nodes/{right_id}/blockers", headers=auth_headers)

    admitted_start_response = app_client.post("/api/node-runs/start", headers=auth_headers, json={"node_id": right_id})

    assert left_start_response.status_code == 200
    left_start_payload = left_start_response.json()
    assert left_start_payload["status"] in {"admitted", "blocked"}
    if left_start_payload["status"] == "blocked":
        assert left_start_payload["reason"] == "active_run_conflict"
        assert any(item["blocker_kind"] == "already_running" for item in left_start_payload["blockers"])
    assert left_complete_response.status_code == 200
    assert blocked_after_complete.status_code == 200
    assert blocked_after_complete.json()["status"] == "blocked"
    assert blockers_after_complete.status_code == 200
    assert blockers_after_complete.json()[0]["blocker_kind"] == "blocked_on_incremental_merge"
    assert merge_result is not None
    assert merge_result.status == "merged"
    assert ready_after_merge.status_code == 200
    assert blockers_after_merge.status_code == 200
    dependency_after_merge = ready_after_merge.json()
    blocker_kinds_after_merge = {item["blocker_kind"] for item in blockers_after_merge.json()}
    assert (
        dependency_after_merge["status"] == "ready"
        or blocker_kinds_after_merge == {"already_running"}
    ), {
        "dependency_status": dependency_after_merge,
        "blockers": blockers_after_merge.json(),
    }
    assert admitted_start_response.status_code == 200
    admitted_start_payload = admitted_start_response.json()
    assert admitted_start_payload["status"] in {"admitted", "blocked"}
    if admitted_start_payload["status"] == "admitted":
        assert admitted_start_payload["current_state"] == "RUNNING"
    else:
        assert admitted_start_payload["reason"] == "active_run_conflict"
        assert any(item["blocker_kind"] == "already_running" for item in admitted_start_payload["blockers"])


def test_every_flow_yaml_has_a_registered_executor() -> None:
    flow_yaml_docs = {path.name for path in FLOWS_DIR.glob("*.yaml")}
    registered = {case.flow_yaml for case in FLOW_YAML_CASES}

    assert registered <= flow_yaml_docs


@pytest.mark.parametrize("case", FLOW_YAML_CASES, ids=lambda case: case.flow_yaml.split("_", 1)[0])
def test_flow_yaml_cases(case: FlowYamlCase, app_client, auth_headers, tmp_path, migrated_public_schema) -> None:
    asset = load_flow_yaml_asset(FLOWS_DIR / case.flow_yaml)
    executor = globals()[case.executor_name]

    executor(app_client=app_client, auth_headers=auth_headers, tmp_path=tmp_path)

    assert asset.expected_tests == [f"tests/integration/test_flow_yaml_contract_suite.py::test_flow_yaml_cases[{case.flow_yaml.split('_', 1)[0]}]"]
