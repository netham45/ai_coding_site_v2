from __future__ import annotations

import pytest
from sqlalchemy import select

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.materialization import (
    _validate_layout_children,
    inspect_materialized_children,
    materialize_layout_children,
)
from aicoding.daemon.versioning import initialize_node_version
from aicoding.db.models import NodeChild, NodeDependency, ParentChildAuthority
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_materialize_layout_children_creates_child_nodes_and_dependency_state(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Epic", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)

    result = materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=parent.node_id,
    )
    inspected = inspect_materialized_children(
        db_session_factory,
        catalog,
        logical_node_id=parent.node_id,
    )

    assert result.status == "created"
    assert result.child_count == 2
    assert result.created_count == 2
    assert result.ready_child_count == 1
    assert result.blocked_child_count == 1
    assert [item.layout_child_id for item in result.children] == ["discovery", "implementation"]
    assert [item.scheduling_status for item in result.children] == ["ready", "blocked"]
    assert inspected.status == "materialized"
    assert [item.layout_child_id for item in inspected.children] == ["discovery", "implementation"]

    with query_session_scope(db_session_factory) as session:
        node_children = session.execute(select(NodeChild).order_by(NodeChild.ordinal)).scalars().all()
        dependencies = session.execute(select(NodeDependency)).scalars().all()
        authority = session.execute(select(ParentChildAuthority)).scalar_one()

    assert [item.layout_child_id for item in node_children] == ["discovery", "implementation"]
    assert len(dependencies) == 1
    assert dependencies[0].required_state == "COMPLETE"
    assert authority.authoritative_layout_hash == result.layout_hash


def test_materialize_layout_children_is_idempotent_when_layout_matches(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Idempotent Epic", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)

    first = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)
    second = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)

    assert first.status == "created"
    assert second.status == "already_materialized"
    assert second.created_count == 0
    assert second.child_count == 2

    with query_session_scope(db_session_factory) as session:
        count = session.execute(select(NodeChild)).scalars().all()

    assert len(count) == 2


def test_materialize_layout_children_detects_partial_preexisting_state(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Partial Epic", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)

    child = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Partial Child", prompt="child", parent_node_id=parent.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(child.node_id), initial_state="READY")
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    with session_scope(db_session_factory) as session:
        session.add(
            ParentChildAuthority(
                parent_node_version_id=parent_version.id,
                authority_mode="layout_authoritative",
                authoritative_layout_hash=None,
            )
        )
        session.add(
            NodeChild(
                parent_node_version_id=parent_version.id,
                child_node_version_id=child_version.id,
                layout_child_id="discovery",
                origin_type="layout_generated",
                ordinal=1,
            )
        )

    result = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)

    assert result.status == "reconciliation_required"
    assert result.child_count == 1
    assert result.children[0].layout_child_id == "discovery"


def test_validate_layout_children_rejects_cycles() -> None:
    with pytest.raises(DaemonConflictError):
        _validate_layout_children(
            [
                {"id": "first", "ordinal": 1, "dependencies": ["second"]},
                {"id": "second", "ordinal": 2, "dependencies": ["first"]},
            ]
        )
