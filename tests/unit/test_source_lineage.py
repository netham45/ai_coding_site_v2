from __future__ import annotations

from dataclasses import replace

from sqlalchemy import text

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from aicoding.source_lineage import (
    capture_node_version_source_lineage,
    load_node_version_source_lineage,
    sha256_text,
)


def test_sha256_text_is_stable() -> None:
    assert sha256_text("abc") == sha256_text("abc")
    assert len(sha256_text("abc")) == 64


def test_capture_node_version_source_lineage_persists_expected_inputs(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    lineage = capture_node_version_source_lineage(db_session_factory, node_version_id=version.id)

    assert lineage.node_version_id == version.id
    assert [item.relative_path for item in lineage.source_documents] == [
        "nodes/epic.yaml",
        "policies/default_runtime_policy.yaml",
        "prompts/default_prompt_refs.yaml",
        "project-policies/default_project_policy.yaml",
        "layouts/generate_phase_layout.md",
        "hooks/before_validation_default.yaml",
        "hooks/before_review_default.yaml",
        "review/review_node_output.md",
        "hooks/before_testing_default.yaml",
        "hooks/after_node_complete_build_docs.yaml",
        "hooks/after_node_complete_update_provenance.yaml",
        "hooks/default_hooks.yaml",
        "runtime/session_bootstrap.md",
        "tasks/research_context.yaml",
        "tasks/execute_node.yaml",
        "reviews/node_against_requirements.yaml",
        "testing/default_unit_test_gate.yaml",
        "tasks/validate_node.yaml",
        "tasks/review_node.yaml",
        "layouts/epic_to_phases.yaml",
    ]
    assert {item.doc_family for item in lineage.source_documents} >= {
        "node_definition",
        "runtime_policy_definition",
        "project_policy_definition",
        "prompt_reference_definition",
        "prompt_template",
        "task_definition",
        "layout_definition",
    }


def test_capture_node_version_source_lineage_deduplicates_source_documents(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    capture_node_version_source_lineage(db_session_factory, node_version_id=version.id)
    capture_node_version_source_lineage(db_session_factory, node_version_id=version.id)

    with migrated_public_schema.connect() as connection:
        source_count = connection.execute(text("select count(*) from source_documents")).scalar_one()
        link_count = connection.execute(text("select count(*) from node_version_source_documents")).scalar_one()

    assert source_count == 20
    assert link_count == 20
    loaded = load_node_version_source_lineage(db_session_factory, node_version_id=version.id)
    assert loaded.source_documents[3].relative_path == "project-policies/default_project_policy.yaml"


def test_capture_node_version_source_lineage_includes_override_documents(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
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
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    lineage = capture_node_version_source_lineage(db_session_factory, node_version_id=version.id, catalog=catalog)

    assert "nodes/epic_tasks.yaml" in [item.relative_path for item in lineage.source_documents]
    override_doc = next(item for item in lineage.source_documents if item.relative_path == "nodes/epic_tasks.yaml")
    assert override_doc.doc_family == "override_definition"
    assert override_doc.source_role == "override_definition"
