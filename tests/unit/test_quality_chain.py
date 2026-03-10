from __future__ import annotations

from dataclasses import replace

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.quality_chain import run_turnkey_quality_chain
from aicoding.daemon.run_orchestration import complete_current_subtask, load_current_run_progress, start_subtask_attempt
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.session import create_session_factory
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _quality_catalog(tmp_path):
    base_catalog = load_resource_catalog()
    project_root = tmp_path / "project"
    (project_root / "project-policies").mkdir(parents=True)
    (project_root / "testing").mkdir(parents=True)
    (project_root / "project-policies" / "default_project_policy.yaml").write_text(
        "\n".join(
            [
                "project_policy_definition:",
                "  id: default_project_policy",
                "  description: Unit-test quality chain policy.",
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
    return replace(
        base_catalog,
        yaml_project_dir=project_root,
        yaml_project_policies_dir=project_root / "project-policies",
        yaml_overrides_dir=overrides_root,
    )


def test_run_turnkey_quality_chain_executes_gates_and_records_finalize(migrated_public_schema, tmp_path) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    registry = load_hierarchy_registry()
    catalog = _quality_catalog(tmp_path)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Quality Chain", prompt="boot prompt")
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
        complete_current_subtask(
            factory,
            logical_node_id=node.node_id,
            compiled_subtask_id=compiled_subtask_id,
            summary="done",
        )
        from aicoding.daemon.run_orchestration import advance_workflow

        progress = advance_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    snapshot = run_turnkey_quality_chain(factory, logical_node_id=node.node_id, catalog=catalog)

    assert snapshot.executed_stage_types == ["validate", "review", "run_tests"]
    assert snapshot.validation.status == "passed"
    assert snapshot.review.status == "passed"
    assert snapshot.testing.status == "passed"
    assert snapshot.provenance is not None
    assert snapshot.docs
    assert snapshot.final_summary is not None
    assert snapshot.run_status == "COMPLETE"
