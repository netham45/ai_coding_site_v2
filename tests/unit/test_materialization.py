from __future__ import annotations

from pathlib import Path

import pytest
from sqlalchemy import select

from aicoding.config import get_settings
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.materialization import (
    _child_prompt_from_layout,
    _validate_layout_children,
    inspect_materialized_children,
    materialize_layout_children,
    register_generated_layout,
)
from aicoding.daemon.versioning import initialize_node_version
from aicoding.db.models import NodeChild, NodeDependency, NodeVersion, ParentChildAuthority
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
    assert [item.scheduling_status for item in result.children] == ["ready", "blocked_on_dependency"]
    assert inspected.status == "materialized"
    assert [item.layout_child_id for item in inspected.children] == ["discovery", "implementation"]

    with query_session_scope(db_session_factory) as session:
        node_children = session.execute(select(NodeChild).order_by(NodeChild.ordinal)).scalars().all()
        dependencies = session.execute(select(NodeDependency)).scalars().all()
        authority = session.execute(select(ParentChildAuthority)).scalar_one()
        discovery_child_version = session.get(NodeVersion, node_children[0].child_node_version_id)

    assert [item.layout_child_id for item in node_children] == ["discovery", "implementation"]
    assert len(dependencies) == 1
    assert dependencies[0].required_state == "COMPLETE"
    assert authority.authoritative_layout_hash == result.layout_hash
    assert discovery_child_version is not None
    assert "Parent Epic Request:" in discovery_child_version.prompt
    assert "boot prompt" in discovery_child_version.prompt


def test_child_prompt_from_layout_includes_parent_request_and_acceptance(db_session_factory, migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="epic",
        title="Prompt Parent",
        prompt="Ship the concrete workspace change.",
    )
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    prompt = _child_prompt_from_layout(
        parent_version=version,
        child_spec={
            "goal": "Complete the implementation slice.",
            "acceptance": ["Tests pass.", "Summary is registered."],
        },
    )

    assert "Complete the implementation slice." in prompt
    assert "Parent Epic Request:" in prompt
    assert "Ship the concrete workspace change." in prompt
    assert "Child Acceptance Criteria:" in prompt
    assert "- Tests pass." in prompt


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


def test_materialize_layout_children_prefers_generated_workspace_layout(
    db_session_factory,
    migrated_public_schema,
    tmp_path: Path,
    monkeypatch,
) -> None:
    try:
        workspace_root = tmp_path / "workspace"
        generated_layout = workspace_root / "layouts" / "generated_layout.yaml"
        generated_layout.parent.mkdir(parents=True, exist_ok=True)
        generated_layout.write_text(
            "\n".join(
                [
                    "kind: layout_definition",
                    "id: generated_epic_layout",
                    "name: Generated Epic Layout",
                    "description: Generated layout for testing.",
                    "children:",
                    "  - id: custom_phase",
                    "    kind: phase",
                    "    tier: 2",
                    "    name: Generated Discovery",
                    "    ordinal: 1",
                    "    goal: Build the generated phase first.",
                    "    rationale: Prove registered generated layouts override the built-in fallback.",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
        get_settings.cache_clear()

        catalog = load_resource_catalog()
        registry = load_hierarchy_registry(catalog)
        parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Generated Layout Epic", prompt="boot prompt")
        seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
        initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
        register_generated_layout(db_session_factory, logical_node_id=parent.node_id, file_path=str(generated_layout))

        result = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)
        inspected = inspect_materialized_children(db_session_factory, catalog, logical_node_id=parent.node_id)

        assert result.layout_relative_path == "layouts/generated_layout.yaml"
        assert result.child_count == 1
        assert [item.layout_child_id for item in result.children] == ["custom_phase"]
        assert inspected.layout_relative_path == "layouts/generated_layout.yaml"
        assert [item.layout_child_id for item in inspected.children] == ["custom_phase"]
    finally:
        get_settings.cache_clear()


def test_materialize_layout_children_is_idempotent_for_generated_workspace_layout(
    db_session_factory,
    migrated_public_schema,
    tmp_path: Path,
    monkeypatch,
) -> None:
    try:
        workspace_root = tmp_path / "workspace"
        generated_layout = workspace_root / "layouts" / "generated_layout.yaml"
        generated_layout.parent.mkdir(parents=True, exist_ok=True)
        generated_layout.write_text(
            "\n".join(
                [
                    "kind: layout_definition",
                    "id: generated_epic_layout",
                    "name: Generated Epic Layout",
                    "description: Generated layout for testing.",
                    "children:",
                    "  - id: custom_phase",
                    "    kind: phase",
                    "    tier: 2",
                    "    name: Generated Discovery",
                    "    ordinal: 1",
                    "    goal: Build the generated phase first.",
                    "    rationale: Prove registered generated layouts remain idempotent.",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
        get_settings.cache_clear()

        catalog = load_resource_catalog()
        registry = load_hierarchy_registry(catalog)
        parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Generated Layout Epic", prompt="boot prompt")
        seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
        initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
        register_generated_layout(db_session_factory, logical_node_id=parent.node_id, file_path=str(generated_layout))

        first = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)
        second = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)

        assert first.status == "created"
        assert first.layout_relative_path == "layouts/generated_layout.yaml"
        assert second.status == "already_materialized"
        assert second.layout_relative_path == "layouts/generated_layout.yaml"
        assert second.child_count == 1
    finally:
        get_settings.cache_clear()


def test_materialize_layout_children_ignores_unregistered_generated_workspace_layout(
    db_session_factory,
    migrated_public_schema,
    tmp_path: Path,
    monkeypatch,
) -> None:
    try:
        workspace_root = tmp_path / "workspace"
        generated_layout = workspace_root / "layouts" / "generated_layout.yaml"
        generated_layout.parent.mkdir(parents=True, exist_ok=True)
        generated_layout.write_text(
            "\n".join(
                [
                    "kind: layout_definition",
                    "id: generated_epic_layout",
                    "name: Generated Epic Layout",
                    "description: Unregistered layout should be ignored.",
                    "children:",
                    "  - id: custom_phase",
                    "    kind: phase",
                    "    tier: 2",
                    "    name: Generated Discovery",
                    "    ordinal: 1",
                    "    goal: Build the generated phase first.",
                    "    rationale: Prove unregistered layouts are ignored.",
                ]
            ),
            encoding="utf-8",
        )
        monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
        get_settings.cache_clear()

        catalog = load_resource_catalog()
        registry = load_hierarchy_registry(catalog)
        parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Generated Layout Epic", prompt="boot prompt")
        seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
        initialize_node_version(db_session_factory, logical_node_id=parent.node_id)

        result = materialize_layout_children(db_session_factory, registry, catalog, logical_node_id=parent.node_id)

        assert result.layout_relative_path == "layouts/epic_to_phases.yaml"
        assert [item.layout_child_id for item in result.children] == ["discovery", "implementation"]
    finally:
        get_settings.cache_clear()


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
