from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import text

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node, list_ancestors, list_children, sync_hierarchy_definitions
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.operator_views import list_sibling_nodes, load_tree_catalog
from aicoding.hierarchy import load_hierarchy_registry


def test_load_hierarchy_registry_reads_builtin_node_definitions() -> None:
    registry = load_hierarchy_registry()

    assert sorted(registry.definitions) == ["epic", "phase", "plan", "task"]
    assert registry.top_level_kinds() == ["epic"]
    assert registry.get("epic").parent_constraints.allow_parentless is True
    assert registry.get("phase").parent_constraints.allowed_kinds == ["epic"]


def test_hierarchy_registry_allows_custom_ladder(tmp_path: Path) -> None:
    root = tmp_path / "resources" / "yaml" / "builtin" / "system-yaml" / "nodes"
    root.mkdir(parents=True)
    (root / "root.yaml").write_text(
        """
node_definition:
  id: root
  kind: root
  tier: alpha
  description: Top node
  main_prompt: prompts/layouts/root.md
  entry_task: research_context
  available_tasks: [research_context]
  parent_constraints:
    allowed_kinds: []
    allowed_tiers: []
    allow_parentless: true
  child_constraints:
    allowed_kinds: [branch]
    allowed_tiers: [beta]
    min_children: 0
    max_children: 5
  policies:
    max_node_regenerations: 1
    max_subtask_retries: 1
    child_failure_threshold_total: 1
    child_failure_threshold_consecutive: 1
    child_failure_threshold_per_child: 1
    require_review_before_finalize: false
    require_testing_before_finalize: false
    require_docs_before_finalize: false
    auto_run_children: false
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
""".strip(),
        encoding="utf-8",
    )
    (root / "branch.yaml").write_text(
        """
node_definition:
  id: branch
  kind: branch
  tier: beta
  description: Child node
  main_prompt: prompts/layouts/branch.md
  entry_task: execute_node
  available_tasks: [execute_node]
  parent_constraints:
    allowed_kinds: [root]
    allowed_tiers: [alpha]
    allow_parentless: false
  child_constraints:
    allowed_kinds: []
    allowed_tiers: []
    min_children: 0
    max_children: 0
  policies:
    max_node_regenerations: 1
    max_subtask_retries: 1
    child_failure_threshold_total: 0
    child_failure_threshold_consecutive: 0
    child_failure_threshold_per_child: 0
    require_review_before_finalize: false
    require_testing_before_finalize: false
    require_docs_before_finalize: false
    auto_run_children: false
    auto_rectify_upstream: false
    auto_merge_to_parent: false
    auto_merge_to_base: false
  hooks: []
""".strip(),
        encoding="utf-8",
    )

    class CustomCatalog:
        yaml_builtin_system_dir = tmp_path / "resources" / "yaml" / "builtin" / "system-yaml"

    registry = load_hierarchy_registry(CustomCatalog())

    assert sorted(registry.definitions) == ["branch", "root"]
    registry.validate_parent_child(parent_kind=None, child_kind="root")
    registry.validate_parent_child(parent_kind="root", child_kind="branch")


def test_create_hierarchy_node_persists_and_enforces_legality(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry()
    sync_hierarchy_definitions(db_session_factory, registry)

    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top")
    phase = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Phase",
        prompt="child",
        parent_node_id=epic.node_id,
    )

    assert phase.parent_node_id == epic.node_id
    assert phase.kind == "phase"

    with pytest.raises(DaemonConflictError):
        create_hierarchy_node(
            db_session_factory,
            registry,
            kind="task",
            title="Invalid child",
            prompt="bad",
            parent_node_id=epic.node_id,
        )


def test_hierarchy_children_and_ancestors_queries(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry()
    sync_hierarchy_definitions(db_session_factory, registry)

    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top")
    phase = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Phase", prompt="mid", parent_node_id=epic.node_id)
    plan = create_hierarchy_node(db_session_factory, registry, kind="plan", title="Plan", prompt="low", parent_node_id=phase.node_id)

    children = list_children(db_session_factory, epic.node_id)
    ancestors = list_ancestors(db_session_factory, plan.node_id)

    assert [child.kind for child in children] == ["phase"]
    assert [ancestor.kind for ancestor in ancestors] == ["phase", "epic"]

    with migrated_public_schema.begin() as connection:
        count = connection.execute(text("select count(*) from node_hierarchy_definitions")).scalar_one()

    assert count == 4


def test_hierarchy_tree_and_sibling_queries(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry()
    sync_hierarchy_definitions(db_session_factory, registry)

    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top")
    seed_node_lifecycle(db_session_factory, node_id=str(epic.node_id), initial_state="DRAFT")
    phase_one = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Phase One", prompt="mid", parent_node_id=epic.node_id)
    phase_two = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Phase Two", prompt="mid", parent_node_id=epic.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(phase_one.node_id), initial_state="DRAFT")
    seed_node_lifecycle(db_session_factory, node_id=str(phase_two.node_id), initial_state="DRAFT")
    plan = create_hierarchy_node(db_session_factory, registry, kind="plan", title="Plan", prompt="low", parent_node_id=phase_one.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(plan.node_id), initial_state="DRAFT")

    tree = load_tree_catalog(db_session_factory, root_node_id=epic.node_id)
    siblings = list_sibling_nodes(db_session_factory, node_id=phase_one.node_id)

    assert [(item.title, item.depth) for item in tree.nodes] == [
        ("Epic", 0),
        ("Phase One", 1),
        ("Plan", 2),
        ("Phase Two", 1),
    ]
    assert [item.title for item in siblings] == ["Phase Two"]
