from __future__ import annotations

from time import perf_counter
from dataclasses import replace

import pytest
from sqlalchemy import text

from aicoding.bootstrap import bootstrap_status
from aicoding.cli.app import run
from aicoding.config import Settings
from aicoding.db.models import NodeLifecycleState, Session as DurableSession
from aicoding.operational_library import inspect_builtin_operational_library
from aicoding.quality_library import inspect_builtin_quality_library
from aicoding.rendering import build_render_context, render_text
from aicoding.structural_library import inspect_builtin_structural_library
from aicoding.daemon.admission import add_node_dependency, check_node_dependency_readiness, list_node_blockers
from aicoding.daemon.app import create_app
from aicoding.daemon.auth import initialize_auth_context
from aicoding.daemon.branches import load_node_branch_metadata
from aicoding.daemon.child_reconcile import collect_child_results
from aicoding.daemon.docs_runtime import build_node_docs
from aicoding.daemon.environments import list_environment_policies
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle, update_node_cursor, load_node_lifecycle
from aicoding.daemon.live_git import bootstrap_live_git_repo, execute_live_merge_children, finalize_live_git_state, stage_live_git_change
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.materialization import inspect_child_reconciliation, inspect_materialized_children, materialize_layout_children, reconcile_child_authority
from aicoding.daemon.models import MutationEnvelope
from aicoding.daemon.orchestration import apply_authority_mutation
from aicoding.daemon.parent_failures import handle_child_failure_at_parent
from aicoding.daemon.provenance import refresh_node_provenance, show_entity_by_name
from aicoding.daemon.rebuild_coordination import inspect_cutover_readiness, inspect_rebuild_coordination
from aicoding.daemon.reproducibility import load_node_audit_snapshot
from aicoding.daemon.child_sessions import pop_child_session, push_child_session
from aicoding.daemon.session_records import (
    bind_primary_session,
    inspect_primary_session_screen_state,
    load_provider_recovery_status,
    load_recovery_status,
    nudge_primary_session,
    recover_primary_session,
    show_current_primary_session,
)
from aicoding.daemon.run_orchestration import (
    complete_current_subtask,
    fail_current_subtask,
    list_subtask_attempts_for_node,
    load_current_run_progress,
    load_current_subtask_context,
    load_current_subtask_prompt,
    load_subtask_attempt,
    start_subtask_attempt,
    sync_paused_run,
)
from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller
from aicoding.daemon.operator_views import load_pause_state, load_tree_catalog
from aicoding.daemon.review_runtime import load_review_summary_for_node
from aicoding.daemon.testing_runtime import load_testing_summary_for_node
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.history import list_prompt_history
from aicoding.daemon.interventions import list_node_interventions
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.daemon.admission import admit_node_run
from aicoding.db.migrations import expected_database_revision, migration_status
from aicoding.db.session import create_engine_from_settings, create_session_factory, probe_database, query_session_scope, session_scope
from aicoding.resources import load_resource_catalog
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.yaml_schemas import validate_yaml_document
from tests.helpers.benchmarks import measure
from tests.helpers.resource_loader import load_text
from tests.helpers.session_harness import FakeClock


@pytest.mark.performance
def test_bootstrap_status_completes_quickly() -> None:
    start = perf_counter()
    payload = bootstrap_status()
    elapsed = perf_counter() - start

    assert payload["missing_directories"] == []
    assert elapsed < 0.25


@pytest.mark.performance
def test_cli_doctor_completes_quickly(capsys) -> None:
    start = perf_counter()
    exit_code = run(["admin", "doctor"])
    capsys.readouterr()
    elapsed = perf_counter() - start

    assert exit_code == 0
    assert elapsed < 0.5


@pytest.mark.performance
def test_database_probe_completes_quickly() -> None:
    start = perf_counter()
    payload = probe_database()
    elapsed = perf_counter() - start

    assert payload["database_name"] == "aicoding"
    assert elapsed < 0.5


@pytest.mark.performance
def test_session_factory_creation_completes_quickly() -> None:
    factory, elapsed = measure(create_session_factory)

    try:
        assert factory is not None
        assert elapsed < 0.3
    finally:
        factory.kw["bind"].dispose()


@pytest.mark.performance
def test_transactional_session_roundtrip_completes_quickly() -> None:
    engine = create_engine_from_settings()
    factory = create_session_factory(engine=engine)

    try:
        _, elapsed = measure(lambda: _transaction_roundtrip(factory))
        assert elapsed < 0.25
    finally:
        engine.dispose()


@pytest.mark.performance
def test_query_session_roundtrip_completes_quickly() -> None:
    engine = create_engine_from_settings()
    factory = create_session_factory(engine=engine)

    try:
        _, elapsed = measure(lambda: _query_roundtrip(factory))
        assert elapsed < 0.25
    finally:
        engine.dispose()


@pytest.mark.performance
def test_expected_revision_lookup_completes_quickly() -> None:
    expected_database_revision()
    _, elapsed = measure(expected_database_revision)

    assert elapsed < 0.25


@pytest.mark.performance
def test_migration_status_probe_completes_quickly() -> None:
    engine = create_engine_from_settings()

    try:
        payload, elapsed = measure(lambda: migration_status(engine))
        assert payload["expected_revision"] == "0029_incr_parent_merge_state"
        assert elapsed < 0.3
    finally:
        engine.dispose()


@pytest.mark.performance
def test_settings_parse_completes_quickly() -> None:
    _, elapsed = measure(Settings)

    assert elapsed < 0.1


@pytest.mark.performance
def test_template_render_completes_quickly() -> None:
    context = build_render_context(
        scopes={
            "node": {"id": "node-123", "title": "Rendered Node", "kind": "task"},
            "task": {"key": "execute_node"},
            "compat": {"node_id": "node-123"},
            "invoker": {"mode": "compile"},
        }
    )

    _, elapsed = measure(
        lambda: render_text(
            "Prompt {{node.title}} {{task.key}} {{mode}} <node_id>",
            context=context,
            field_name="prompt",
        )
    )

    assert elapsed < 0.02


@pytest.mark.performance
def test_builtin_subtask_catalog_validation_completes_quickly() -> None:
    catalog = load_resource_catalog()
    subtask_root = catalog.yaml_builtin_system_dir / "subtasks"

    def validate_subtasks() -> list[bool]:
        return [
            validate_yaml_document(
                catalog,
                source_group="yaml_builtin_system",
                relative_path=f"subtasks/{path.name}",
            ).valid
            for path in sorted(subtask_root.glob("*.yaml"))
        ]

    reports, elapsed = measure(validate_subtasks)

    assert all(reports)
    assert elapsed < 0.3


@pytest.mark.performance
def test_higher_order_yaml_family_validation_completes_quickly() -> None:
    catalog = load_resource_catalog()
    families = ("validations", "reviews", "testing", "docs", "rectification")
    relative_paths = [
        f"{family}/{path.name}"
        for family in families
        for path in sorted((catalog.yaml_builtin_system_dir / family).glob("*.yaml"))
    ]

    def validate_family_pack() -> list[bool]:
        return [
            validate_yaml_document(
                catalog,
                source_group="yaml_builtin_system",
                relative_path=relative_path,
            ).valid
            for relative_path in relative_paths
        ]

    reports, elapsed = measure(validate_family_pack)

    assert reports
    assert all(reports)
    assert elapsed < 0.5


@pytest.mark.performance
def test_runtime_and_prompt_yaml_family_validation_completes_quickly() -> None:
    catalog = load_resource_catalog()
    families = ("runtime", "policies", "prompts")
    relative_paths = [
        f"{family}/{path.name}"
        for family in families
        for path in sorted((catalog.yaml_builtin_system_dir / family).glob("*.yaml"))
    ]

    def validate_runtime_and_prompt_families() -> list[bool]:
        return [
            validate_yaml_document(
                catalog,
                source_group="yaml_builtin_system",
                relative_path=relative_path,
            ).valid
            for relative_path in relative_paths
        ]

    reports, elapsed = measure(validate_runtime_and_prompt_families)

    assert reports
    assert all(reports)
    assert elapsed < 0.45


@pytest.mark.performance
def test_structural_library_inspection_completes_quickly() -> None:
    catalog = load_resource_catalog()

    report, elapsed = measure(lambda: inspect_builtin_structural_library(catalog).to_payload())

    assert report["valid"] is True
    assert elapsed < 1.0


@pytest.mark.performance
def test_quality_library_inspection_completes_quickly() -> None:
    catalog = load_resource_catalog()

    report, elapsed = measure(lambda: inspect_builtin_quality_library(catalog).to_payload())

    assert report["valid"] is True
    assert elapsed < 0.85


@pytest.mark.performance
def test_operational_library_inspection_completes_quickly() -> None:
    catalog = load_resource_catalog()

    report, elapsed = measure(lambda: inspect_builtin_operational_library(catalog).to_payload())

    assert report["valid"] is True
    assert elapsed < 1.5


@pytest.mark.performance
def test_default_prompt_pack_load_and_render_complete_quickly() -> None:
    catalog = load_resource_catalog()
    prompt_paths = sorted(
        path.relative_to(catalog.prompt_pack_default_dir).as_posix()
        for path in catalog.prompt_pack_default_dir.rglob("*.md")
        if path.name != "README.md"
    )
    context = build_render_context(
        scopes={
            "node": {"id": "node-123", "title": "Prompt Pack Performance", "prompt": "Author the prompt pack."},
            "task": {
                "key": "execute_node",
                "name": "Execute Node",
                "description": "Render the default prompt pack.",
                "definition_yaml": "kind: task_definition",
            },
            "subtask": {
                "key": "execute_node.run_leaf_prompt",
                "id": "execute_node.run_leaf_prompt",
            },
            "prompt": {
                "pack": "default",
                "template_path": "execution/implement_leaf_task.md",
            },
            "command": {
                "template_path": "inline/execute_node/execute_node.run_leaf_prompt",
            },
            "compat": {
                "node_id": "node-123",
                "compiled_subtask_id": "subtask-456",
                "user_request": "Author the prompt pack.",
                "acceptance_criteria": "Prompts are authored and renderable.",
                "task_key": "execute_node",
                "source_subtask_key": "execute_node.run_leaf_prompt",
                "node_prompt": "Author the prompt pack.",
            },
        }
    )

    def load_and_render() -> list[str]:
        rendered: list[str] = []
        for relative_path in prompt_paths:
            content = catalog.read_text("prompt_pack_default", relative_path)
            rendered.append(render_text(content, context=context, field_name="prompt").rendered_text)
        return rendered

    rendered, elapsed = measure(load_and_render)

    assert len(rendered) == len(prompt_paths)
    assert all(rendered)
    assert elapsed < 0.25


@pytest.mark.performance
def test_pydantic_model_validation_completes_quickly() -> None:
    _, elapsed = measure(lambda: MutationEnvelope.model_validate({"node_id": "node-123"}))

    assert elapsed < 0.05


@pytest.mark.performance
def test_resource_metadata_build_completes_quickly() -> None:
    catalog = load_resource_catalog()

    _, elapsed = measure(lambda: catalog.prompt_metadata("prompt_pack_default", "layouts/generate_phase_layout.md"))

    assert elapsed < 0.05


@pytest.mark.performance
def test_environment_policy_listing_completes_quickly() -> None:
    policies, elapsed = measure(list_environment_policies)

    assert any(item.policy_id == "local_default" for item in policies)
    assert elapsed < 0.1


@pytest.mark.performance
def test_provenance_and_docs_views_query_quickly(migrated_public_schema) -> None:
    def load_view_catalogs() -> tuple[int, int, int]:
        with migrated_public_schema.begin() as connection:
            docs = connection.execute(text("select count(*) from latest_documentation_outputs")).scalar_one()
            changes = connection.execute(text("select count(*) from latest_node_entity_changes")).scalar_one()
            relations = connection.execute(text("select count(*) from latest_code_relations")).scalar_one()
        return docs, changes, relations

    payload, elapsed = measure(load_view_catalogs)

    assert payload == (0, 0, 0)
    assert elapsed < 0.15


@pytest.mark.performance
def test_auth_context_initialization_completes_quickly(tmp_path) -> None:
    settings = Settings(auth_token="seed-token", auth_token_file=tmp_path / ".runtime" / "daemon.token")

    _, elapsed = measure(lambda: initialize_auth_context(settings))

    assert elapsed < 0.1


@pytest.mark.performance
def test_fixture_startup_helpers_complete_quickly(cli_runner, resource_catalog) -> None:
    _, cli_elapsed = measure(lambda: cli_runner(["admin", "doctor"]))
    _, resource_elapsed = measure(lambda: resource_catalog.load_text("yaml_builtin_system", "nodes/epic.yaml"))

    assert cli_elapsed < 0.5
    assert resource_elapsed < 0.1


@pytest.mark.performance
def test_yaml_schema_validation_completes_quickly() -> None:
    from aicoding.yaml_schemas import validate_yaml_document
    from aicoding.resources import load_resource_catalog

    catalog = load_resource_catalog()
    _, elapsed = measure(lambda: validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path="nodes/epic.yaml"))

    assert elapsed < 0.3


@pytest.mark.performance
def test_daemon_app_creation_completes_quickly() -> None:
    start = perf_counter()
    app = create_app()
    elapsed = perf_counter() - start

    assert app.title == "AI Coding Orchestrator"
    assert elapsed < 0.6


@pytest.mark.performance
def test_node_lifecycle_lookup_completes_quickly(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    seed_node_lifecycle(factory, node_id="perf-node", initial_state="DRAFT")

    _, elapsed = measure(lambda: load_node_lifecycle(factory, "perf-node"))

    assert elapsed < 0.1


@pytest.mark.performance
def test_pause_state_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.run_orchestration import sync_paused_run

    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf pause", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    sync_paused_run(factory, logical_node_id=node.node_id, pause_flag_name="manual_pause")

    _, elapsed = measure(lambda: load_pause_state(factory, node_id=node.node_id))

    assert elapsed < 0.15


@pytest.mark.performance
def test_intervention_catalog_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.workflows import compile_node_workflow

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf intervention", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id, trigger_reason="test")
    sync_paused_run(factory, logical_node_id=node.node_id, pause_flag_name="user_guidance_required")
    with session_scope(factory) as session:
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        assert lifecycle is not None
        cursor = dict(lifecycle.execution_cursor_json or {})
        pause_context = dict(cursor.get("pause_context", {}))
        pause_context["approval_required"] = True
        lifecycle.execution_cursor_json = {**cursor, "pause_context": pause_context}
        session.flush()

    snapshot, elapsed = measure(lambda: list_node_interventions(factory, catalog, logical_node_id=node.node_id))

    assert snapshot.pending_count >= 1
    assert elapsed < 0.35


@pytest.mark.performance
def test_runtime_state_view_queries_complete_quickly(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    from aicoding.daemon.hierarchy import sync_hierarchy_definitions

    sync_hierarchy_definitions(factory, registry)

    running_node = create_hierarchy_node(factory, registry, kind="epic", title="Perf Running", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(running_node.node_id), initial_state="DRAFT")
    running_version = initialize_node_version(factory, logical_node_id=running_node.node_id)
    compile_node_workflow(factory, logical_node_id=running_node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(running_node.node_id), target_state="READY")
    admit_node_run(factory, node_id=running_node.node_id)

    blocked_node = create_hierarchy_node(factory, registry, kind="epic", title="Perf Blocked", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(blocked_node.node_id), initial_state="DRAFT")
    blocked_version = initialize_node_version(factory, logical_node_id=blocked_node.node_id)
    compile_node_workflow(factory, logical_node_id=blocked_node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(blocked_node.node_id), target_state="READY")
    add_node_dependency(factory, node_id=blocked_node.node_id, depends_on_node_id=running_node.node_id)
    check_node_dependency_readiness(factory, node_id=blocked_node.node_id)

    def query_runtime_views() -> tuple[object, object]:
        with migrated_public_schema.begin() as connection:
            latest_run = connection.execute(
                text("select node_version_id, run_number from latest_node_runs where node_version_id = :node_version_id"),
                {"node_version_id": str(running_version.id)},
            ).mappings().one()
            blocker = connection.execute(
                text("select node_version_id, blocker_kind from pending_dependency_nodes where node_version_id = :node_version_id"),
                {"node_version_id": str(blocked_version.id)},
            ).mappings().one()
            return latest_run, blocker

    payload, elapsed = measure(query_runtime_views)

    assert payload[0]["node_version_id"] == running_version.id
    assert payload[1]["blocker_kind"] == "blocked_on_dependency"
    assert elapsed < 0.15


@pytest.mark.performance
def test_parent_failure_decision_path_completes_quickly(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)

    parent = create_hierarchy_node(factory, registry, kind="epic", title="Perf Parent", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=parent.node_id)
    compile_node_workflow(factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(factory, node_id=parent.node_id)

    child = create_manual_node(factory, registry, kind="phase", title="Perf Child", prompt="child prompt", parent_node_id=parent.node_id)
    compile_node_workflow(factory, logical_node_id=child.node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(child.node.node_id), target_state="READY")
    admit_node_run(factory, node_id=child.node.node_id)
    progress = load_current_run_progress(factory, logical_node_id=child.node.node_id)
    start_subtask_attempt(factory, logical_node_id=child.node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    fail_current_subtask(
        factory,
        logical_node_id=child.node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        summary="environment timeout while running tool",
    )

    _, elapsed = measure(
        lambda: handle_child_failure_at_parent(
            factory,
            logical_node_id=parent.node_id,
            child_node_id=child.node.node_id,
            requested_action="retry_child",
        )
    )

    assert elapsed < 0.5


@pytest.mark.performance
def test_review_summary_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.admission import admit_node_run
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry

    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf Review", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    progress = load_current_run_progress(factory, logical_node_id=node.node_id)

    for payload in ({}, {}, {"exit_code": 0}):
        start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
        complete_current_subtask(
            factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=progress.state.current_compiled_subtask_id,
            output_json=payload,
            summary="done",
        )
        progress = advance_workflow(factory, logical_node_id=node.node_id)

    start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={"status": "pass", "findings": [{"message": "ok"}]},
        summary="approved",
    )
    advance_workflow(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: load_review_summary_for_node(factory, logical_node_id=node.node_id))

    assert elapsed < 0.25


@pytest.mark.performance
def test_testing_summary_lookup_completes_quickly(migrated_public_schema, tmp_path) -> None:
    from aicoding.daemon.admission import admit_node_run
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry

    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Perf testing fixture policy.",
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
                "description: Perf durable test gate.",
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
    catalog = replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )

    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf Testing Epic", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    progress = load_current_run_progress(factory, logical_node_id=node.node_id)

    while progress.current_subtask["subtask_type"] != "run_tests":
        start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
        if progress.current_subtask["subtask_type"] == "validate":
            payload = {"exit_code": 0}
        elif progress.current_subtask["subtask_type"] == "review":
            payload = {
                "status": "pass",
                "findings": [{"message": "ok"}],
                "criteria_results": [{"criterion": "ok", "status": "passed"}],
            }
        else:
            payload = None
        complete_current_subtask(
            factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=progress.state.current_compiled_subtask_id,
            output_json=payload,
            summary="done",
        )
        progress = advance_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=progress.state.current_compiled_subtask_id)
    complete_current_subtask(
        factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=progress.state.current_compiled_subtask_id,
        output_json={
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
                {
                    "testing_definition_id": "custom_retry_gate",
                    "suite_name": "Custom Retry Gate",
                    "exit_code": 0,
                    "failed_tests": 0,
                    "summary": "tests passed",
                }
            ]
        },
        summary="tests passed",
    )
    advance_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    _, elapsed = measure(lambda: load_testing_summary_for_node(factory, logical_node_id=node.node_id))

    assert elapsed < 0.25


@pytest.mark.performance
def test_turnkey_quality_chain_completes_quickly(migrated_public_schema, tmp_path) -> None:
    from aicoding.daemon.admission import admit_node_run
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
    from aicoding.daemon.quality_chain import run_turnkey_quality_chain
    from aicoding.daemon.run_orchestration import advance_workflow, complete_current_subtask, load_current_run_progress, start_subtask_attempt
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Perf quality-chain fixture policy.",
                "  defaults:",
                "    auto_run_children: true",
                "    auto_merge_to_parent: false",
                "    auto_merge_to_base: false",
                "    require_review_before_finalize: true",
                "    require_testing_before_finalize: true",
                "    require_docs_before_finalize: true",
                "  runtime_policy_refs: []",
                "  hook_refs: []",
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
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "nodes" / "epic_quality_chain.yaml").write_text(
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
    catalog = replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )
    registry = load_hierarchy_registry()
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf quality chain", prompt="p")
    initialize_node_version(factory, logical_node_id=node.node_id)
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)

    progress = load_current_run_progress(factory, logical_node_id=node.node_id)
    while progress.current_subtask is not None and progress.current_subtask["subtask_type"] not in {"validate", "review", "run_tests"}:
        compiled_subtask_id = progress.state.current_compiled_subtask_id
        assert compiled_subtask_id is not None
        start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=compiled_subtask_id)
        complete_current_subtask(factory, logical_node_id=node.node_id, compiled_subtask_id=compiled_subtask_id, summary="done")
        progress = advance_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    result, elapsed = measure(lambda: run_turnkey_quality_chain(factory, logical_node_id=node.node_id, catalog=catalog))

    assert result.run_status == "COMPLETE"
    assert result.final_summary is not None
    assert elapsed < 6.0


@pytest.mark.performance
def test_workflow_compile_with_hook_expansion_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry

    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)
    epic = create_hierarchy_node(factory, registry, kind="epic", title="Perf Epic", prompt="boot")
    phase = create_hierarchy_node(factory, registry, kind="phase", title="Perf Phase", prompt="boot", parent_node_id=epic.node_id)
    plan = create_hierarchy_node(factory, registry, kind="plan", title="Perf Plan", prompt="boot", parent_node_id=phase.node_id)
    task = create_hierarchy_node(factory, registry, kind="task", title="Perf Task", prompt="boot", parent_node_id=plan.node_id)
    seed_node_lifecycle(factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=task.node_id)

    _, elapsed = measure(lambda: compile_node_workflow(factory, logical_node_id=task.node_id, catalog=catalog))

    assert elapsed < 3.5


@pytest.mark.performance
def test_build_node_docs_completes_quickly(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    factory = create_session_factory(engine=migrated_public_schema)
    epic = create_hierarchy_node(factory, registry, kind="epic", title="Docs Epic", prompt="boot")
    phase = create_hierarchy_node(factory, registry, kind="phase", title="Docs Phase", prompt="boot", parent_node_id=epic.node_id)
    plan = create_hierarchy_node(factory, registry, kind="plan", title="Docs Plan", prompt="boot", parent_node_id=phase.node_id)
    task = create_hierarchy_node(factory, registry, kind="task", title="Docs Task", prompt="boot", parent_node_id=plan.node_id)
    seed_node_lifecycle(factory, node_id=str(task.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=task.node_id)
    compile_node_workflow(factory, logical_node_id=task.node_id, catalog=catalog)

    _, elapsed = measure(lambda: build_node_docs(factory, logical_node_id=task.node_id))

    assert elapsed < 1.5


@pytest.mark.performance
def test_node_cursor_update_completes_quickly(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    seed_node_lifecycle(factory, node_id="perf-run-node", initial_state="DRAFT")
    transition_node_lifecycle(factory, node_id="perf-run-node", target_state="COMPILED")
    transition_node_lifecycle(factory, node_id="perf-run-node", target_state="READY")
    apply_authority_mutation(factory, node_id="perf-run-node", command="node.run.start")

    _, elapsed = measure(
        lambda: update_node_cursor(
            factory,
            node_id="perf-run-node",
            current_task_id="task.execute",
            current_subtask_id="subtask.render",
            current_subtask_attempt=1,
            execution_cursor_json={"ordinal": 1},
            is_resumable=True,
        )
    )

    assert elapsed < 0.15


@pytest.mark.performance
def test_node_lineage_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version, load_node_lineage
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf lineage", prompt="p")
    initialize_node_version(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: load_node_lineage(factory, node.node_id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_current_subtask_prompt_and_context_lookup_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf prompt", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)

    _, prompt_elapsed = measure(lambda: load_current_subtask_prompt(factory, logical_node_id=node.node_id))
    _, context_elapsed = measure(lambda: load_current_subtask_context(factory, logical_node_id=node.node_id))

    assert prompt_elapsed < 0.1
    assert context_elapsed < 0.1


@pytest.mark.performance
def test_prompt_history_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf prompt history", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    load_current_subtask_prompt(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: list_prompt_history(factory, logical_node_id=node.node_id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_node_audit_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf audit", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    load_current_subtask_prompt(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: load_node_audit_snapshot(factory, logical_node_id=node.node_id))

    assert elapsed < 0.25


@pytest.mark.performance
def test_session_recovery_status_and_recover_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf recovery", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    _, status_elapsed = measure(lambda: load_recovery_status(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller))
    _, recover_elapsed = measure(lambda: recover_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller))

    assert status_elapsed < 0.15
    assert recover_elapsed < 0.25


@pytest.mark.performance
def test_child_materialization_and_inspection_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf parent", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)

    _, materialize_elapsed = measure(lambda: materialize_layout_children(factory, registry, catalog, logical_node_id=node.node_id))
    _, inspect_elapsed = measure(lambda: inspect_materialized_children(factory, catalog, logical_node_id=node.node_id))

    assert materialize_elapsed < 8.0
    assert inspect_elapsed < 0.2


@pytest.mark.performance
def test_rebuild_coordination_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    root = create_hierarchy_node(factory, registry, kind="epic", title="Perf coord root", prompt="root prompt")
    initialize_node_version(factory, logical_node_id=root.node_id)
    child = create_manual_node(factory, registry, kind="phase", title="Perf coord child", prompt="child prompt", parent_node_id=root.node_id)
    seed_node_lifecycle(factory, node_id=str(child.node.node_id), initial_state="DRAFT")
    transition_node_lifecycle(factory, node_id=str(child.node.node_id), target_state="COMPILED")
    transition_node_lifecycle(factory, node_id=str(child.node.node_id), target_state="READY")
    apply_authority_mutation(factory, node_id=str(child.node.node_id), command="node.run.start")

    snapshot, elapsed = measure(lambda: inspect_rebuild_coordination(factory, logical_node_id=child.node.node_id, scope="upstream"))

    assert snapshot.status == "blocked"
    assert elapsed < 0.75


@pytest.mark.performance
def test_cutover_readiness_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf cutover", prompt="boot prompt")
    initialize_node_version(factory, logical_node_id=node.node_id)
    candidate = create_superseding_node_version(factory, logical_node_id=node.node_id)

    snapshot, elapsed = measure(lambda: inspect_cutover_readiness(factory, version_id=candidate.id))

    assert snapshot.status in {"ready", "blocked"}
    assert elapsed < 0.75


@pytest.mark.performance
def test_live_git_merge_and_finalize_complete_quickly(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Perf live git parent", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(factory, logical_node_id=parent.node_id)
    child = create_manual_node(factory, registry, kind="phase", title="Perf live git child", prompt="child prompt", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=child.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        factory,
        version_id=child.node_version_id,
        files={"shared.txt": "base\nperf child change\n"},
        message="Perf child final",
        record_as_final=True,
    )

    merge_result, merge_elapsed = measure(
        lambda: execute_live_merge_children(
            factory,
            logical_node_id=parent.node_id,
            ordered_child_versions=[(child.node_version_id, child_status.final_commit_sha, 1)],
        )
    )
    finalize_result, finalize_elapsed = measure(lambda: finalize_live_git_state(factory, logical_node_id=parent.node_id))

    assert merge_result.status == "merged"
    assert finalize_result.status == "finalized"
    assert merge_elapsed < 3.0
    assert finalize_elapsed < 1.5


@pytest.mark.performance
def test_manual_child_creation_and_authority_inspection_complete_quickly(migrated_public_schema) -> None:
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_manual_node(factory, registry, kind="epic", title="Perf manual parent", prompt="boot prompt")

    _, create_elapsed = measure(
        lambda: create_manual_node(
            factory,
            registry,
            kind="phase",
            title="Perf manual child",
            prompt="child prompt",
            parent_node_id=parent.node.node_id,
        )
    )
    _, inspect_elapsed = measure(lambda: inspect_materialized_children(factory, catalog, logical_node_id=parent.node.node_id))

    assert create_elapsed < 0.35
    assert inspect_elapsed < 0.2


@pytest.mark.performance
def test_hybrid_child_reconciliation_inspection_and_preserve_manual_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.materialization import inspect_child_reconciliation, materialize_layout_children, reconcile_child_authority
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_manual_node(factory, registry, kind="epic", title="Perf hybrid parent", prompt="boot prompt")
    materialize_layout_children(factory, registry, catalog, logical_node_id=parent.node.node_id)
    create_manual_node(
        factory,
        registry,
        kind="phase",
        title="Perf manual child",
        prompt="child prompt",
        parent_node_id=parent.node.node_id,
    )

    _, inspect_elapsed = measure(lambda: inspect_child_reconciliation(factory, catalog, logical_node_id=parent.node.node_id))
    _, reconcile_elapsed = measure(
        lambda: reconcile_child_authority(factory, catalog, logical_node_id=parent.node.node_id, decision="preserve_manual")
    )

    assert inspect_elapsed < 0.25
    assert reconcile_elapsed < 0.4


@pytest.mark.performance
def test_subtask_attempt_result_reads_complete_quickly(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Attempt Perf", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    progress = load_current_run_progress(factory, logical_node_id=node.node_id)
    current_subtask_id = progress.state.current_compiled_subtask_id
    started = start_subtask_attempt(factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    complete_current_subtask(
        factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        execution_result_json={"exit_code": 0, "stdout": "done"},
        summary="done",
    )

    _, list_elapsed = measure(lambda: list_subtask_attempts_for_node(factory, logical_node_id=node.node_id))
    _, show_elapsed = measure(lambda: load_subtask_attempt(factory, attempt_id=started.latest_attempt.id))

    assert list_elapsed < 0.15
    assert show_elapsed < 0.1


@pytest.mark.performance
def test_provider_recovery_status_lookup_completes_quickly(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Provider recovery perf", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    bound = bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    with session_scope(factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        durable.tmux_session_name = "missing-session-name"

    _, elapsed = measure(
        lambda: load_provider_recovery_status(
            factory,
            logical_node_id=node.node_id,
            adapter=adapter,
            poller=poller,
        )
    )

    assert elapsed < 0.1


@pytest.mark.performance
def test_session_nudge_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf nudge", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    bound = bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)

    _, elapsed = measure(
        lambda: nudge_primary_session(
            factory,
            logical_node_id=node.node_id,
            adapter=adapter,
            poller=poller,
            max_nudge_count=2,
            idle_nudge_text="idle prompt",
            repeated_nudge_text="repeat prompt",
        )
    )

    assert elapsed < 0.2


@pytest.mark.performance
def test_session_screen_classifier_completes_quickly(migrated_public_schema) -> None:
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf classifier", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    _, elapsed = measure(
        lambda: inspect_primary_session_screen_state(
            factory,
            logical_node_id=node.node_id,
            adapter=adapter,
            poller=poller,
            persist=True,
        )
    )

    assert elapsed < 0.15


@pytest.mark.performance
def test_child_result_collection_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.branches import record_final_commit, record_seed_commit
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Perf Parent", prompt="p")
    child = create_hierarchy_node(factory, registry, kind="phase", title="Perf Child", prompt="c", parent_node_id=parent.node_id)
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    seed_node_lifecycle(factory, node_id=str(child.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(factory, logical_node_id=parent.node_id)
    child_version = initialize_node_version(factory, logical_node_id=child.node_id)
    transition_node_lifecycle(factory, node_id=str(child.node_id), target_state="COMPILED")
    transition_node_lifecycle(factory, node_id=str(child.node_id), target_state="READY")
    transition_node_lifecycle(factory, node_id=str(child.node_id), target_state="RUNNING")
    transition_node_lifecycle(factory, node_id=str(child.node_id), target_state="COMPLETE")
    record_seed_commit(factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(factory, version_id=child_version.id, commit_sha="def1234")
    record_final_commit(factory, version_id=child_version.id, commit_sha="def5678")

    _, elapsed = measure(lambda: collect_child_results(factory, logical_node_id=parent.node_id))

    assert elapsed < 0.25


@pytest.mark.performance
def test_child_session_push_and_pop_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf child", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    child, push_elapsed = measure(
        lambda: push_child_session(
            factory,
            logical_node_id=node.node_id,
            reason="research_context",
            adapter=adapter,
            poller=poller,
            delegated_prompt_text="delegated prompt",
            delegated_prompt_path="runtime/delegated_child_session.md",
        )
    )
    _, pop_elapsed = measure(
        lambda: pop_child_session(
            factory,
            child_session_id=child.session_id,
            result_payload={"status": "success", "summary": "done", "findings": [], "artifacts": [], "suggested_next_actions": []},
        )
    )

    assert push_elapsed < 0.3
    assert pop_elapsed < 0.2


@pytest.mark.performance
def test_tree_catalog_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    root = create_hierarchy_node(factory, registry, kind="epic", title="Perf root", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(root.node_id), initial_state="DRAFT")
    child = create_hierarchy_node(factory, registry, kind="phase", title="Perf child", prompt="boot prompt", parent_node_id=root.node_id)
    seed_node_lifecycle(factory, node_id=str(child.node_id), initial_state="DRAFT")

    _, elapsed = measure(lambda: load_tree_catalog(factory, root_node_id=root.node_id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_session_bind_and_lookup_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.daemon.admission import admit_node_run
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf session", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    _, bind_elapsed = measure(lambda: bind_primary_session(factory, logical_node_id=node.node_id, adapter=adapter, poller=poller))
    _, lookup_elapsed = measure(lambda: show_current_primary_session(factory, adapter=adapter, poller=poller))

    assert bind_elapsed < 0.2
    assert lookup_elapsed < 0.1


@pytest.mark.performance
def test_source_lineage_capture_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog
    from aicoding.source_lineage import capture_node_version_source_lineage

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf source", prompt="p")
    version = initialize_node_version(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: capture_node_version_source_lineage(factory, node_version_id=version.id, catalog=catalog))

    assert elapsed < 1.0


@pytest.mark.performance
def test_source_lineage_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog
    from aicoding.source_lineage import capture_node_version_source_lineage, load_node_version_source_lineage

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf source", prompt="p")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    capture_node_version_source_lineage(factory, node_version_id=version.id, catalog=catalog)

    _, elapsed = measure(lambda: load_node_version_source_lineage(factory, node_version_id=version.id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_workflow_compile_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf workflow", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)

    result, elapsed = measure(lambda: compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog))

    assert result.status == "compiled"
    assert elapsed < 3.5


@pytest.mark.performance
def test_top_level_workflow_start_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.workflow_start import start_top_level_workflow
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    result, elapsed = measure(
        lambda: start_top_level_workflow(
            factory,
            hierarchy_registry=registry,
            resource_catalog=catalog,
            kind="epic",
            title="Perf workflow start",
            prompt="Start a top-level workflow for performance coverage.",
            start_run=True,
        )
    )

    assert result.status == "started"
    assert elapsed < 4.5


@pytest.mark.performance
def test_workflow_compile_with_overrides_completes_quickly(migrated_public_schema, tmp_path) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    base_catalog = load_resource_catalog()
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
                "    - review_node",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf override workflow", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)

    result, elapsed = measure(lambda: compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog))

    assert result.status == "compiled"
    assert elapsed < 4.0


@pytest.mark.performance
def test_workflow_source_discovery_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow, load_workflow_source_discovery_for_node
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf source discovery", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    result, elapsed = measure(lambda: load_workflow_source_discovery_for_node(factory, logical_node_id=node.node_id))

    assert result["discovery_order"]
    assert elapsed < 0.5


@pytest.mark.performance
def test_workflow_schema_validation_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow, load_workflow_schema_validation_for_node
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf schema validation", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    result, elapsed = measure(lambda: load_workflow_schema_validation_for_node(factory, logical_node_id=node.node_id))

    assert result["validated_document_count"] > 0
    assert elapsed < 0.4


@pytest.mark.performance
def test_workflow_hook_policy_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow, load_workflow_hook_policy_for_node
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf hook policy", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    result, elapsed = measure(lambda: load_workflow_hook_policy_for_node(factory, logical_node_id=node.node_id))

    assert result["compiled_workflow_id"] is not None
    assert elapsed < 0.4


@pytest.mark.performance
def test_workflow_rendering_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow, load_workflow_rendering_for_node
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf rendering", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    result, elapsed = measure(lambda: load_workflow_rendering_for_node(factory, logical_node_id=node.node_id))

    assert result["compiled_subtask_count"] > 0
    assert elapsed < 0.4


@pytest.mark.performance
def test_candidate_workflow_compile_and_version_stage_lookup_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
    from aicoding.daemon.workflows import compile_node_version_workflow, load_workflow_source_discovery_for_version
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf candidate compile", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    candidate = create_superseding_node_version(factory, logical_node_id=node.node_id, title="Perf candidate compile v2")

    compile_result, compile_elapsed = measure(lambda: compile_node_version_workflow(factory, version_id=candidate.id, catalog=catalog))
    stage_result, stage_elapsed = measure(lambda: load_workflow_source_discovery_for_version(factory, version_id=candidate.id))

    assert compile_result.status == "compiled"
    assert compile_result.compile_context["compile_variant"] == "candidate"
    assert stage_result["compile_context"]["compile_variant"] == "candidate"
    assert compile_elapsed < 3.5
    assert stage_elapsed < 0.5


@pytest.mark.performance
def test_compiled_workflow_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.lifecycle import seed_node_lifecycle
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow, load_current_workflow
    from aicoding.hierarchy import load_hierarchy_registry
    from aicoding.resources import load_resource_catalog

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf current workflow", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    _, elapsed = measure(lambda: load_current_workflow(factory, logical_node_id=node.node_id))

    assert elapsed < 0.2


@pytest.mark.performance
def test_dependency_readiness_check_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Perf deps parent", prompt="p")
    initialize_node_version(factory, logical_node_id=parent.node_id)
    left = _create_runnable_perf_node(factory, registry=registry, catalog=catalog, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_perf_node(factory, registry=registry, catalog=catalog, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(factory, node_id=right.node_id, depends_on_node_id=left.node_id)

    _, elapsed = measure(lambda: check_node_dependency_readiness(factory, node_id=right.node_id))

    assert elapsed < 0.2


@pytest.mark.performance
def test_dependency_blocker_query_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Perf blockers parent", prompt="p")
    initialize_node_version(factory, logical_node_id=parent.node_id)
    left = _create_runnable_perf_node(factory, registry=registry, catalog=catalog, kind="phase", title="Left", parent_node_id=parent.node_id)
    right = _create_runnable_perf_node(factory, registry=registry, catalog=catalog, kind="phase", title="Right", parent_node_id=parent.node_id)
    add_node_dependency(factory, node_id=right.node_id, depends_on_node_id=left.node_id)
    check_node_dependency_readiness(factory, node_id=right.node_id)

    _, elapsed = measure(lambda: list_node_blockers(factory, node_id=right.node_id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_branch_metadata_lookup_completes_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf branch", prompt="p")
    initialize_node_version(factory, logical_node_id=node.node_id)

    _, elapsed = measure(lambda: load_node_branch_metadata(factory, logical_node_id=node.node_id))

    assert elapsed < 0.1


@pytest.mark.performance
def test_cli_parser_namespace_command_completes_quickly(capsys) -> None:
    start = perf_counter()
    exit_code = run(["yaml", "sources", "--scope", "builtin"])
    capsys.readouterr()
    elapsed = perf_counter() - start

    assert exit_code == 0
    assert elapsed < 0.5


@pytest.mark.performance
def test_resource_load_completes_quickly() -> None:
    loaded, elapsed = measure(lambda: load_text("yaml_builtin", "system-yaml/nodes/epic.yaml"))

    assert "node_definition" in loaded.content
    assert elapsed < 0.25


@pytest.mark.performance
def test_session_poller_completes_quickly() -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    adapter.create_session("node-1", "printf 'ready'", ".")
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=30.0, now=clock.now)

    _, elapsed = measure(lambda: poller.poll("node-1"))

    assert elapsed < 0.1


@pytest.mark.performance
def test_provenance_refresh_and_lookup_complete_quickly(migrated_public_schema) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf provenance", prompt="p")
    initialize_node_version(factory, logical_node_id=node.node_id)

    _, refresh_elapsed = measure(lambda: refresh_node_provenance(factory, logical_node_id=node.node_id))
    _, lookup_elapsed = measure(lambda: show_entity_by_name(factory, canonical_name="src.aicoding.daemon.app.create_app"))

    assert refresh_elapsed < 5.0
    assert lookup_elapsed < 0.25


@pytest.mark.performance
def test_multilanguage_provenance_refresh_complete_quickly(migrated_public_schema, tmp_path) -> None:
    from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.hierarchy import load_hierarchy_registry

    (tmp_path / "src" / "pkg").mkdir(parents=True)
    (tmp_path / "src" / "pkg" / "app.py").write_text("def helper(name):\n    return name.upper()\n", encoding="utf-8")
    (tmp_path / "src" / "web").mkdir(parents=True)
    (tmp_path / "src" / "web" / "app.ts").write_text(
        "export function greet(name: string) {\n  return helper(name);\n}\n",
        encoding="utf-8",
    )

    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Perf multilanguage provenance", prompt="p")
    initialize_node_version(factory, logical_node_id=node.node_id)

    snapshot, elapsed = measure(lambda: refresh_node_provenance(factory, logical_node_id=node.node_id, workspace_root=tmp_path))

    assert snapshot.entity_count >= 3
    assert elapsed < 5.0


def _transaction_roundtrip(factory) -> int:
    with session_scope(factory) as session:
        return session.execute(text("select 1")).scalar_one()


def _query_roundtrip(factory) -> int:
    with query_session_scope(factory) as session:
        return session.execute(text("select 1")).scalar_one()


def _create_runnable_perf_node(factory, *, registry, catalog, kind: str, title: str, parent_node_id=None):
    from aicoding.daemon.hierarchy import create_hierarchy_node
    from aicoding.daemon.versioning import initialize_node_version
    from aicoding.daemon.workflows import compile_node_workflow

    node = create_hierarchy_node(
        factory,
        registry,
        kind=kind,
        title=title,
        prompt="p",
        parent_node_id=parent_node_id,
    )
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    return node
