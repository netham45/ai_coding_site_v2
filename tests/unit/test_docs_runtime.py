from __future__ import annotations

from aicoding.daemon.docs_runtime import build_node_docs, build_tree_docs, list_docs_for_node, show_docs_for_node
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from aicoding.daemon.errors import DaemonNotFoundError
import pytest


def test_build_node_docs_persists_local_and_custom_docs(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory

    factory = create_session_factory(engine=migrated_public_schema)
    epic = create_hierarchy_node(factory, registry, kind="epic", title="Docs Epic", prompt="top prompt")
    phase = create_hierarchy_node(factory, registry, kind="phase", title="Docs Phase", prompt="phase prompt", parent_node_id=epic.node_id)
    plan = create_hierarchy_node(factory, registry, kind="plan", title="Docs Plan", prompt="plan prompt", parent_node_id=phase.node_id)
    node = create_hierarchy_node(factory, registry, kind="task", title="Docs Node", prompt="document the work", parent_node_id=plan.node_id)
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    build = build_node_docs(factory, logical_node_id=node.node_id)
    docs = list_docs_for_node(factory, logical_node_id=node.node_id)
    shown = show_docs_for_node(factory, logical_node_id=node.node_id, scope="local")

    assert build.mode == "node"
    assert {item.scope for item in build.documents} >= {"local", "custom"}
    assert docs.documents
    assert shown.scope == "local"
    assert "Docs Node" in shown.content
    assert "## Goal" in shown.content


def test_build_tree_docs_persists_merged_tree_view(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory

    factory = create_session_factory(engine=migrated_public_schema)
    root = create_hierarchy_node(factory, registry, kind="epic", title="Root Epic", prompt="merge the tree")
    child = create_hierarchy_node(factory, registry, kind="phase", title="Child Phase", prompt="child prompt", parent_node_id=root.node_id)
    seed_node_lifecycle(factory, node_id=str(root.node_id), initial_state="DRAFT")
    seed_node_lifecycle(factory, node_id=str(child.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=root.node_id)
    initialize_node_version(factory, logical_node_id=child.node_id)
    compile_node_workflow(factory, logical_node_id=root.node_id, catalog=catalog)

    build = build_tree_docs(factory, logical_node_id=root.node_id)
    shown = show_docs_for_node(factory, logical_node_id=root.node_id, scope="merged")

    assert build.mode == "tree"
    assert {item.scope for item in build.documents} >= {"merged", "custom", "rationale_view"}
    assert "Root Epic" in shown.content
    assert "Child Phase" in shown.content
    assert "## Tree" in shown.content


def test_show_docs_for_node_raises_when_scope_missing(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory

    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="No Docs", prompt="none")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)

    with pytest.raises(DaemonNotFoundError):
        show_docs_for_node(factory, logical_node_id=node.node_id, scope="local")
