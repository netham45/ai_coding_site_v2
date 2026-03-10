from __future__ import annotations

import pytest

from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.git_conflicts import (
    list_merge_conflicts_for_node,
    list_merge_events_for_node,
    record_merge_conflict,
    resolve_merge_conflict,
)
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version, initialize_node_version
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_record_and_resolve_merge_conflict_persists_history(
    db_session_factory,
    migrated_public_schema,
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    child = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)
    parent_candidate = create_superseding_node_version(db_session_factory, logical_node_id=parent.node_id)

    conflict = record_merge_conflict(
        db_session_factory,
        parent_node_version_id=parent_candidate.id,
        child_node_version_id=child_version.id,
        child_final_commit_sha="childfinal123",
        parent_commit_before="seed123",
        parent_commit_after="mergeattempt123",
        merge_order=1,
        files_json=["src/app.py", "README.md"],
        merge_base_sha="base123",
    )
    events = list_merge_events_for_node(db_session_factory, logical_node_id=parent.node_id)
    conflicts = list_merge_conflicts_for_node(db_session_factory, logical_node_id=parent.node_id)

    assert conflict.resolution_status == "unresolved"
    assert events[0].had_conflict is True
    assert conflicts[0].files_json == ["src/app.py", "README.md"]

    resolved = resolve_merge_conflict(
        db_session_factory,
        conflict_id=conflict.id,
        resolution_summary="Resolved manually in parent branch.",
        resolution_status="resolved",
    )

    assert resolved.resolution_status == "resolved"
    assert resolved.resolution_summary == "Resolved manually in parent branch."


def test_cutover_rejects_unresolved_merge_conflicts_until_resolved(
    db_session_factory,
    migrated_public_schema,
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    child = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)
    parent_candidate = create_superseding_node_version(db_session_factory, logical_node_id=parent.node_id)

    conflict = record_merge_conflict(
        db_session_factory,
        parent_node_version_id=parent_candidate.id,
        child_node_version_id=child_version.id,
        child_final_commit_sha="childfinal123",
        parent_commit_before="seed123",
        parent_commit_after="mergeattempt123",
        merge_order=1,
        files_json=["src/conflicted.py"],
    )

    with pytest.raises(DaemonConflictError):
        cutover_candidate_version(db_session_factory, version_id=parent_candidate.id)

    resolve_merge_conflict(
        db_session_factory,
        conflict_id=conflict.id,
        resolution_summary="Resolved and verified.",
    )
    lineage = cutover_candidate_version(db_session_factory, version_id=parent_candidate.id)

    assert lineage.authoritative_node_version_id == parent_candidate.id
