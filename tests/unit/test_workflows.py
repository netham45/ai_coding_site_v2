from __future__ import annotations

from dataclasses import replace

from sqlalchemy import select

from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.lifecycle import load_node_lifecycle, seed_node_lifecycle
from aicoding.daemon.versioning import initialize_node_version, load_node_version
from aicoding.daemon.workflows import (
    compile_node_workflow,
    list_compile_failures_for_node,
    load_current_workflow,
    load_workflow_hooks_for_node,
    load_workflow_chain_for_node,
)
from aicoding.db.models import CompileFailure, CompiledWorkflow
from aicoding.db.session import query_session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.source_lineage import load_node_version_source_lineage
from aicoding.resources import load_resource_catalog


def _create_task_hierarchy_node(db_session_factory, registry, *, title: str):
    sync_hierarchy_definitions(db_session_factory, registry)
    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Epic", prompt="boot")
    phase = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Parent Phase",
        prompt="boot",
        parent_node_id=epic.node_id,
    )
    plan = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Parent Plan",
        prompt="boot",
        parent_node_id=phase.node_id,
    )
    return create_hierarchy_node(
        db_session_factory,
        registry,
        kind="task",
        title=title,
        prompt="boot",
        parent_node_id=plan.node_id,
    )


def test_compile_node_workflow_persists_linear_snapshot(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Compile Epic", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    current = load_current_workflow(db_session_factory, logical_node_id=node.node_id)
    chain = load_workflow_chain_for_node(db_session_factory, logical_node_id=node.node_id)
    refreshed_version = load_node_version(db_session_factory, version.id)
    lifecycle = load_node_lifecycle(db_session_factory, str(node.node_id))

    assert result.status == "compiled"
    assert result.compiled_workflow is not None
    assert result.compile_failure is None
    assert current.id == result.compiled_workflow.id
    assert current.task_count == 4
    assert current.subtask_count == 5
    assert [task.task_key for task in current.tasks] == ["research_context", "execute_node", "validate_node", "review_node"]
    assert current.tasks[0].subtasks[0].source_subtask_key == "research_context.hook.default_hooks.1"
    assert str(node.node_id) in current.tasks[0].subtasks[0].prompt_text
    assert "<node_id>" not in current.tasks[0].subtasks[0].prompt_text
    assert chain.chain[1].depends_on_compiled_subtask_ids == [chain.chain[0].compiled_subtask_id]
    assert chain.chain[2].depends_on_compiled_subtask_ids == [chain.chain[1].compiled_subtask_id]
    assert refreshed_version.compiled_workflow_id == current.id
    assert lifecycle.lifecycle_state == "COMPILED"
    assert current.resolved_yaml["rendering"]["canonical_syntax"] == "{{variable}}"
    assert current.resolved_yaml["rendering"]["compiled_subtasks"][0]["rendered_fields"][0]["field"] == "prompt"


def test_compile_node_workflow_records_failure_and_clears_binding(db_session_factory, migrated_public_schema) -> None:
    base_catalog = load_resource_catalog()
    registry = load_hierarchy_registry(base_catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Broken Compile", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    class BrokenCatalog:
        yaml_project_policies_dir = base_catalog.yaml_project_policies_dir
        yaml_project_dir = base_catalog.yaml_project_dir
        yaml_builtin_system_dir = base_catalog.yaml_builtin_system_dir

        def read_text(self, group: str, relative_path: str) -> str:
            if group == "yaml_builtin_system" and relative_path == "tasks/execute_node.yaml":
                return "kind: task_definition\nid: execute_node\n"
            return base_catalog.read_text(group, relative_path)

        def __getattr__(self, name: str):
            return getattr(base_catalog, name)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=BrokenCatalog())
    failures = list_compile_failures_for_node(db_session_factory, logical_node_id=node.node_id)
    lifecycle = load_node_lifecycle(db_session_factory, str(node.node_id))
    refreshed_version = load_node_version(db_session_factory, version.id)

    assert result.status == "failed"
    assert result.compiled_workflow is None
    assert result.compile_failure is not None
    assert result.compile_failure.failure_class == "invalid_structural_library"
    assert failures[0].id == result.compile_failure.id
    assert refreshed_version.compiled_workflow_id is None
    assert lifecycle.lifecycle_state == "COMPILE_FAILED"

    with query_session_scope(db_session_factory) as session:
        rows = session.execute(select(CompileFailure).where(CompileFailure.node_version_id == version.id)).scalars().all()
    assert len(rows) == 1


def test_compile_node_workflow_rejects_invalid_quality_library(db_session_factory, migrated_public_schema) -> None:
    base_catalog = load_resource_catalog()
    registry = load_hierarchy_registry(base_catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Broken Quality", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    class BrokenCatalog:
        yaml_project_policies_dir = base_catalog.yaml_project_policies_dir
        yaml_project_dir = base_catalog.yaml_project_dir
        yaml_builtin_system_dir = base_catalog.yaml_builtin_system_dir

        def read_text(self, group: str, relative_path: str) -> str:
            if group == "yaml_builtin_system" and relative_path == "reviews/node_against_requirements.yaml":
                return "kind: review_definition\nid: node_against_requirements\n"
            return base_catalog.read_text(group, relative_path)

        def __getattr__(self, name: str):
            return getattr(base_catalog, name)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=BrokenCatalog())
    failures = list_compile_failures_for_node(db_session_factory, logical_node_id=node.node_id)
    lifecycle = load_node_lifecycle(db_session_factory, str(node.node_id))
    refreshed_version = load_node_version(db_session_factory, version.id)

    assert result.status == "failed"
    assert result.compiled_workflow is None
    assert result.compile_failure is not None
    assert result.compile_failure.failure_class == "invalid_quality_library"
    assert failures[0].id == result.compile_failure.id
    assert refreshed_version.compiled_workflow_id is None
    assert lifecycle.lifecycle_state == "COMPILE_FAILED"


def test_compile_node_workflow_rejects_invalid_operational_library(db_session_factory, migrated_public_schema) -> None:
    base_catalog = load_resource_catalog()
    registry = load_hierarchy_registry(base_catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Broken Operational", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    class BrokenCatalog:
        yaml_project_policies_dir = base_catalog.yaml_project_policies_dir
        yaml_project_dir = base_catalog.yaml_project_dir
        yaml_builtin_system_dir = base_catalog.yaml_builtin_system_dir

        def read_text(self, group: str, relative_path: str) -> str:
            if group == "yaml_builtin_system" and relative_path == "hooks/default_hooks.yaml":
                return "kind: hook_definition\nid: default_hooks\n"
            return base_catalog.read_text(group, relative_path)

        def __getattr__(self, name: str):
            return getattr(base_catalog, name)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=BrokenCatalog())
    failures = list_compile_failures_for_node(db_session_factory, logical_node_id=node.node_id)
    lifecycle = load_node_lifecycle(db_session_factory, str(node.node_id))
    refreshed_version = load_node_version(db_session_factory, version.id)

    assert result.status == "failed"
    assert result.compiled_workflow is None
    assert result.compile_failure is not None
    assert result.compile_failure.failure_class == "invalid_operational_library"
    assert failures[0].id == result.compile_failure.id
    assert refreshed_version.compiled_workflow_id is None
    assert lifecycle.lifecycle_state == "COMPILE_FAILED"


def test_compile_node_workflow_applies_override_and_backfills_required_sources(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "tasks").mkdir(parents=True)
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
                "    - review_node",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    (overrides_root / "tasks" / "review_node_reviews.yaml").write_text(
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
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)

    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Override Compile", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)

    assert result.status == "compiled"
    assert result.compiled_workflow is not None
    assert [task.task_key for task in result.compiled_workflow.tasks] == ["research_context", "review_node", "execute_node"]
    override_resolution = result.compiled_workflow.resolved_yaml["override_resolution"]
    assert {item["override_relative_path"] for item in override_resolution["applied_overrides"]} == {
        "nodes/epic_tasks.yaml",
        "tasks/review_node_reviews.yaml",
    }
    resolved_docs = result.compiled_workflow.resolved_yaml["resolved_documents"]
    review_task = next(item for item in resolved_docs if item["target_family"] == "task_definition" and item["target_id"] == "review_node")
    assert review_task["resolved_document"]["uses_reviews"] == [
        "reviews/node_against_requirements.yaml",
        "policy_compliance_review",
    ]


def test_compile_node_workflow_records_override_missing_target_failure(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "tasks" / "missing_target.yaml").write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: missing_task",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  description: Broken override",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)

    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Broken Override", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)

    assert result.status == "failed"
    assert result.compile_failure is not None
    assert result.compile_failure.failure_stage == "override_resolution"
    assert result.compile_failure.failure_class == "override_missing_target"
    assert result.compile_failure.target_family == "task_definition"
    assert result.compile_failure.target_id == "missing_task"

    with query_session_scope(db_session_factory) as session:
        rows = session.execute(select(CompileFailure).where(CompileFailure.node_version_id == version.id)).scalars().all()
    assert rows[0].failure_class == "override_missing_target"


def test_compile_node_workflow_records_persistence_failure_and_rolls_back_partial_artifacts(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Persistence Failure", prompt="ship it")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    def explode_snapshot(session, workflow_id):
        raise RuntimeError("snapshot exploded")

    monkeypatch.setattr("aicoding.daemon.workflows._workflow_snapshot", explode_snapshot)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    failures = list_compile_failures_for_node(db_session_factory, logical_node_id=node.node_id)
    lifecycle = load_node_lifecycle(db_session_factory, str(node.node_id))
    refreshed_version = load_node_version(db_session_factory, version.id)

    assert result.status == "failed"
    assert result.compiled_workflow is None
    assert result.compile_failure is not None
    assert result.compile_failure.failure_stage == "workflow_persistence"
    assert result.compile_failure.failure_class == "workflow_persistence_failure"
    assert result.compile_failure.details_json["error_type"] == "RuntimeError"
    assert failures[0].id == result.compile_failure.id
    assert refreshed_version.compiled_workflow_id is None
    assert lifecycle.lifecycle_state == "COMPILE_FAILED"

    with query_session_scope(db_session_factory) as session:
        failure_rows = session.execute(select(CompileFailure).where(CompileFailure.node_version_id == version.id)).scalars().all()
        workflow_rows = session.execute(select(CompiledWorkflow).where(CompiledWorkflow.node_version_id == version.id)).scalars().all()

    assert len(failure_rows) == 1
    assert workflow_rows == []


def test_compile_task_node_workflow_expands_configured_hooks_and_captures_hook_sources(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Epic", prompt="boot")
    phase = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Parent Phase",
        prompt="boot",
        parent_node_id=epic.node_id,
    )
    plan = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Parent Plan",
        prompt="boot",
        parent_node_id=phase.node_id,
    )
    node = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="task",
        title="Hook Task",
        prompt="ship it",
        parent_node_id=plan.node_id,
    )
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    current = load_current_workflow(db_session_factory, logical_node_id=node.node_id)
    hooks = load_workflow_hooks_for_node(db_session_factory, logical_node_id=node.node_id)
    lineage = load_node_version_source_lineage(db_session_factory, node_version_id=version.id)

    assert result.status == "compiled"
    assert current.subtask_count == 6
    assert current.tasks[0].subtasks[0].source_subtask_key == "execute_node.hook.default_hooks.1"
    assert current.tasks[0].subtasks[1].source_subtask_key.startswith("execute_node.")
    assert current.tasks[1].subtasks[0].source_subtask_key == "validate_node.hook.before_validation_default.1"
    assert current.tasks[1].subtasks[1].source_subtask_key.startswith("validate_node.")
    assert current.tasks[2].subtasks[0].source_subtask_key == "review_node.hook.before_review_default.1"
    assert current.tasks[2].subtasks[1].source_subtask_key.startswith("review_node.")
    assert current.tasks[0].subtasks[0].inserted_by_hook is True
    assert current.tasks[0].subtasks[0].inserted_by_hook_id is not None
    assert current.tasks[0].subtasks[1].inserted_by_hook is False
    assert hooks["selected_hooks"][0]["hook_id"] == "default_hooks"
    assert {item["hook_id"] for item in hooks["selected_hooks"]} == {
        "default_hooks",
        "before_validation_default",
        "before_review_default",
        "before_testing_default",
        "after_node_complete_build_docs",
        "after_node_complete_update_provenance",
    }
    assert [item["source_subtask_key"] for item in hooks["expanded_steps"]] == [
        "execute_node.hook.default_hooks.1",
        "validate_node.hook.before_validation_default.1",
        "review_node.hook.before_review_default.1",
    ]
    assert "hooks/default_hooks.yaml" in {item.relative_path for item in lineage.source_documents}
    assert "runtime/session_bootstrap.md" in {item.relative_path for item in lineage.source_documents}


def test_compile_task_node_workflow_freezes_environment_request_on_testing_subtask(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "task_adds_testing.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: task",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - execute_node",
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    task = _create_task_hierarchy_node(db_session_factory, registry, title="Task With Tests")
    seed_node_lifecycle(db_session_factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=task.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=task.node_id, catalog=catalog)

    assert result.status == "compiled"
    assert result.compiled_workflow is not None
    test_subtask = next(
        subtask
        for compiled_task in result.compiled_workflow.tasks
        if compiled_task.task_key == "test_node"
        for subtask in compiled_task.subtasks
        if subtask.source_subtask_key == "test_node.run_default_tests"
    )
    assert test_subtask.environment_policy_ref == "environments/local_default.yaml"
    assert test_subtask.environment_request_json["policy_id"] == "local_default"
    assert test_subtask.environment_request_json["isolation_mode"] == "none"


def test_compile_fails_when_environment_profile_is_not_declared_by_project_policy(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "task_adds_testing.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: task",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - execute_node",
                "    - validate_node",
                "    - review_node",
                "    - test_node",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    task = _create_task_hierarchy_node(db_session_factory, registry, title="Task With Isolated Tests")
    seed_node_lifecycle(db_session_factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=task.node_id)

    class BrokenEnvironmentCatalog:
        yaml_project_policies_dir = catalog.yaml_project_policies_dir
        yaml_project_dir = catalog.yaml_project_dir
        yaml_builtin_system_dir = catalog.yaml_builtin_system_dir
        yaml_overrides_dir = catalog.yaml_overrides_dir

        def read_text(self, group: str, relative_path: str) -> str:
            if group == "yaml_builtin_system" and relative_path == "environments/local_default.yaml":
                return "\n".join(
                    [
                        "kind: environment_policy_definition",
                        "id: local_default",
                        "isolation_mode: custom_profile",
                        "allow_network: false",
                        "runtime_profile: isolated-test-profile",
                        "mandatory: true",
                    ]
                )
            return catalog.read_text(group, relative_path)

        def __getattr__(self, name: str):
            return getattr(catalog, name)

    result = compile_node_workflow(db_session_factory, logical_node_id=task.node_id, catalog=BrokenEnvironmentCatalog())

    assert result.status == "failed"
    assert result.compile_failure is not None
    assert result.compile_failure.failure_stage == "environment_resolution"
    assert result.compile_failure.failure_class == "environment_profile_undeclared"


def test_compile_task_workflow_renders_canonical_variables_and_invoker_context(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "tasks" / "execute_node_rendering.yaml").write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: execute_node",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  subtasks:",
                "    - kind: subtask_definition",
                "      id: run_leaf_prompt",
                "      type: run_prompt",
                "      title: Render Prompt",
                "      description: Render a prompt with explicit variables.",
                "      prompt: \"Prompt {{node.title}} / {{task.key}} / {{mode}} / <node_id>\"",
                "      command: \"printf '{{mode}} {{node.kind}}'\"",
                "      render_context:",
                "        variables:",
                "          mode: compile",
                "      retry_policy: {max_attempts: 1, backoff_seconds: 0}",
                "      on_failure: {action: fail_to_parent}",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    task = _create_task_hierarchy_node(db_session_factory, registry, title="Rendered Task")
    seed_node_lifecycle(db_session_factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=task.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=task.node_id, catalog=catalog)

    assert result.status == "compiled"
    assert result.compiled_workflow is not None
    execute_subtask = next(
        subtask
        for subtask in result.compiled_workflow.tasks[0].subtasks
        if subtask.inserted_by_hook is False
    )
    assert "Rendered Task" in execute_subtask.prompt_text
    assert "execute_node" in execute_subtask.prompt_text
    assert "compile" in execute_subtask.prompt_text
    assert str(task.node_id) in execute_subtask.prompt_text
    assert execute_subtask.command_text == "printf 'compile task'"
    rendering = next(
        item
        for item in result.compiled_workflow.resolved_yaml["rendering"]["compiled_subtasks"]
        if item["source_subtask_key"] == execute_subtask.source_subtask_key
    )
    assert rendering["rendered_fields"][0]["variables_used"] == ["mode", "node.title", "node_id", "task.key"]
    assert rendering["rendered_fields"][1]["field"] == "command"


def test_compile_fails_on_illegal_render_target_in_outputs(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "tasks" / "execute_node_illegal_render.yaml").write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: execute_node",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  subtasks:",
                "    - kind: subtask_definition",
                "      id: run_leaf_prompt",
                "      type: run_prompt",
                "      title: Illegal Output Render",
                "      description: Output paths are not renderable in this phase.",
                "      prompt: \"prompts/execution/implement_leaf_task.md\"",
                "      outputs:",
                "        - {type: summary_written, path: \"summaries/{{node.id}}.md\"}",
                "      retry_policy: {max_attempts: 1, backoff_seconds: 0}",
                "      on_failure: {action: fail_to_parent}",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    task = _create_task_hierarchy_node(db_session_factory, registry, title="Illegal Render Task")
    seed_node_lifecycle(db_session_factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=task.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=task.node_id, catalog=catalog)

    assert result.status == "failed"
    assert result.compile_failure is not None
    assert result.compile_failure.failure_stage == "rendering"
    assert result.compile_failure.failure_class == "illegal_render_target"


def test_compile_fails_on_missing_render_variable(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "tasks" / "execute_node_missing_render_var.yaml").write_text(
        "\n".join(
            [
                "target_family: task_definition",
                "target_id: execute_node",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  subtasks:",
                "    - kind: subtask_definition",
                "      id: run_leaf_prompt",
                "      type: run_prompt",
                "      title: Missing Variable Prompt",
                "      description: Prompt references an unavailable variable.",
                "      prompt: \"Prompt {{missing.variable}}\"",
                "      retry_policy: {max_attempts: 1, backoff_seconds: 0}",
                "      on_failure: {action: fail_to_parent}",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    task = _create_task_hierarchy_node(db_session_factory, registry, title="Missing Render Variable Task")
    seed_node_lifecycle(db_session_factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=task.node_id)

    result = compile_node_workflow(db_session_factory, logical_node_id=task.node_id, catalog=catalog)

    assert result.status == "failed"
    assert result.compile_failure is not None
    assert result.compile_failure.failure_stage == "rendering"
    assert result.compile_failure.failure_class == "missing_render_variable"
