from __future__ import annotations

from sqlalchemy import select

from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.materialization import (
    inspect_child_reconciliation,
    inspect_materialized_children,
    materialize_layout_children,
    reconcile_child_authority,
)
from aicoding.db.models import NodeChild, ParentChildAuthority
from aicoding.db.session import query_session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_manual_child_creation_persists_manual_authority_and_edge(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_manual_node(
        db_session_factory,
        registry,
        kind="epic",
        title="Manual Parent",
        prompt="top prompt",
    )

    child = create_manual_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Manual Child",
        prompt="child prompt",
        parent_node_id=parent.node.node_id,
    )
    inspection = inspect_materialized_children(
        db_session_factory,
        catalog,
        logical_node_id=parent.node.node_id,
    )

    assert child.parent_authority_mode == "manual"
    assert inspection.status == "manual"
    assert inspection.authority_mode == "manual"
    assert inspection.children[0].layout_child_id == f"manual-{child.node_version_id}"

    with query_session_scope(db_session_factory) as session:
        edge = session.execute(select(NodeChild)).scalar_one()
        authority = session.execute(select(ParentChildAuthority)).scalar_one()

    assert edge.origin_type == "manual"
    assert authority.authority_mode == "manual"
    assert authority.authoritative_layout_hash is None


def test_manual_child_creation_under_layout_authoritative_parent_enters_hybrid(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_manual_node(
        db_session_factory,
        registry,
        kind="epic",
        title="Hybrid Parent",
        prompt="top prompt",
    )
    materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=parent.node.node_id,
    )

    child = create_manual_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Manual Extra Child",
        prompt="child prompt",
        parent_node_id=parent.node.node_id,
    )
    inspection = inspect_materialized_children(
        db_session_factory,
        catalog,
        logical_node_id=parent.node.node_id,
    )

    assert child.parent_authority_mode == "hybrid"
    assert inspection.status == "reconciliation_required"
    assert inspection.authority_mode == "hybrid"

    with query_session_scope(db_session_factory) as session:
        edges = session.execute(select(NodeChild).order_by(NodeChild.ordinal)).scalars().all()
        authority = session.execute(select(ParentChildAuthority)).scalar_one()

    assert len(edges) == 3
    assert edges[-1].origin_type == "manual"
    assert authority.authority_mode == "hybrid"
    assert authority.authoritative_layout_hash is None


def test_preserve_manual_reconciliation_converts_hybrid_tree_to_manual(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_manual_node(
        db_session_factory,
        registry,
        kind="epic",
        title="Hybrid Parent",
        prompt="top prompt",
    )
    materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=parent.node.node_id,
    )
    create_manual_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Manual Extra Child",
        prompt="child prompt",
        parent_node_id=parent.node.node_id,
    )

    before = inspect_child_reconciliation(db_session_factory, catalog, logical_node_id=parent.node.node_id)
    after = reconcile_child_authority(
        db_session_factory,
        catalog,
        logical_node_id=parent.node.node_id,
        decision="preserve_manual",
    )

    assert before.authority_mode == "hybrid"
    assert before.available_decisions == ["preserve_manual"]
    assert after.authority_mode == "manual"
    assert after.materialization_status == "manual"
    assert after.manual_child_count == 3
    assert after.layout_generated_child_count == 0

    with query_session_scope(db_session_factory) as session:
        edges = session.execute(select(NodeChild).order_by(NodeChild.ordinal)).scalars().all()
        authority = session.execute(select(ParentChildAuthority)).scalar_one()

    assert all(edge.origin_type == "manual" for edge in edges)
    assert all(edge.layout_child_id.startswith("manual-") for edge in edges)
    assert authority.authority_mode == "manual"
    assert authority.authoritative_layout_hash is None
