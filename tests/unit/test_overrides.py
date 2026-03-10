from __future__ import annotations

from aicoding.overrides import (
    OverrideResolutionError,
    OverrideSourceSnapshot,
    SourceDocumentInput,
    build_base_document_index,
    resolve_overrides,
)
from aicoding.yaml_schemas import OverrideCompatibility, OverrideDefinitionDocument


def test_resolve_overrides_deep_merges_node_policy_fields() -> None:
    base_documents = build_base_document_index(
        [
            SourceDocumentInput(
                source_group="yaml_builtin_system",
                relative_path="nodes/epic.yaml",
                source_role="base_definition",
                content="""
node_definition:
  id: epic
  kind: epic
  tier: 0
  description: Epic node.
  main_prompt: prompts/layouts/generate_phase_layout.md
  entry_task: research_context
  available_tasks: [research_context, execute_node]
  parent_constraints: {allowed_kinds: [], allowed_tiers: [], allow_parentless: true}
  child_constraints: {allowed_kinds: [phase], allowed_tiers: [1], min_children: 0, max_children: 12}
  policies:
    max_node_regenerations: 3
    max_subtask_retries: 2
    child_failure_threshold_total: 3
    child_failure_threshold_consecutive: 2
    child_failure_threshold_per_child: 2
    require_review_before_finalize: false
    require_testing_before_finalize: false
    require_docs_before_finalize: false
    auto_run_children: true
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
""",
                content_hash="hash-node",
            )
        ]
    )
    override_documents = [
        OverrideSourceSnapshot(
            relative_path="nodes/epic_policy.yaml",
            content_hash="hash-override",
            document=OverrideDefinitionDocument(
                target_family="node_definition",
                target_id="epic",
                compatibility=OverrideCompatibility(min_schema_version=2, built_in_version="builtin-system-v1"),
                merge_mode="deep_merge",
                value={"policies": {"max_subtask_retries": 5, "auto_merge_to_parent": True}},
            ),
        )
    ]

    resolution = resolve_overrides(base_documents, override_documents, built_in_library_version="builtin-system-v1")
    resolved_node = resolution.document_for("node_definition", "epic")

    assert resolved_node is not None
    assert resolved_node.resolved_document["policies"]["max_subtask_retries"] == 5
    assert resolved_node.resolved_document["policies"]["auto_merge_to_parent"] is True
    assert resolution.applied_overrides[0].merge_mode == "deep_merge"


def test_resolve_overrides_rejects_missing_target() -> None:
    base_documents = build_base_document_index([])
    override_documents = [
        OverrideSourceSnapshot(
            relative_path="tasks/missing.yaml",
            content_hash="hash-override",
            document=OverrideDefinitionDocument(
                target_family="task_definition",
                target_id="missing_task",
                compatibility=OverrideCompatibility(min_schema_version=2, built_in_version="builtin-system-v1"),
                merge_mode="replace",
                value={"description": "updated"},
            ),
        )
    ]

    try:
        resolve_overrides(base_documents, override_documents, built_in_library_version="builtin-system-v1")
    except OverrideResolutionError as exc:
        assert exc.failure_class == "override_missing_target"
        assert exc.target_family == "task_definition"
        assert exc.target_id == "missing_task"
    else:
        raise AssertionError("expected override resolution failure")


def test_resolve_overrides_rejects_wrong_merge_mode_for_field() -> None:
    base_documents = build_base_document_index(
        [
            SourceDocumentInput(
                source_group="yaml_builtin_system",
                relative_path="nodes/epic.yaml",
                source_role="base_definition",
                content="""
node_definition:
  id: epic
  kind: epic
  tier: 0
  description: Epic node.
  main_prompt: prompts/layouts/generate_phase_layout.md
  entry_task: research_context
  available_tasks: [research_context, execute_node]
  parent_constraints: {allowed_kinds: [], allowed_tiers: [], allow_parentless: true}
  child_constraints: {allowed_kinds: [phase], allowed_tiers: [1], min_children: 0, max_children: 12}
  policies:
    max_node_regenerations: 3
    max_subtask_retries: 2
    child_failure_threshold_total: 3
    child_failure_threshold_consecutive: 2
    child_failure_threshold_per_child: 2
    require_review_before_finalize: false
    require_testing_before_finalize: false
    require_docs_before_finalize: false
    auto_run_children: true
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
""",
                content_hash="hash-node",
            )
        ]
    )
    override_documents = [
        OverrideSourceSnapshot(
            relative_path="nodes/epic_tasks.yaml",
            content_hash="hash-override",
            document=OverrideDefinitionDocument(
                target_family="node_definition",
                target_id="epic",
                compatibility=OverrideCompatibility(min_schema_version=2, built_in_version="builtin-system-v1"),
                merge_mode="append_list",
                value={"available_tasks": ["review_node"]},
            ),
        )
    ]

    try:
        resolve_overrides(base_documents, override_documents, built_in_library_version="builtin-system-v1")
    except OverrideResolutionError as exc:
        assert exc.failure_class == "override_merge_conflict"
        assert exc.target_family == "node_definition"
        assert exc.target_id == "epic"
    else:
        raise AssertionError("expected override resolution failure")
