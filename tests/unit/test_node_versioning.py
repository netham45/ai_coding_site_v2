from __future__ import annotations

import pytest

from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller
from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.orchestration import apply_authority_mutation
from aicoding.daemon.run_orchestration import cancel_active_run
from aicoding.daemon.session_records import bind_primary_session
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.daemon.versioning import (
    create_superseding_node_version,
    cutover_candidate_version,
    initialize_node_version,
    list_node_versions,
    load_node_lineage,
)
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_initialize_node_version_seeds_authoritative_v1(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")

    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    lineage = load_node_lineage(db_session_factory, node.node_id)

    assert version.version_number == 1
    assert version.status == "authoritative"
    assert lineage.authoritative_node_version_id == version.id
    assert lineage.latest_created_node_version_id == version.id


def test_create_superseding_version_and_cutover(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    first = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    candidate = create_superseding_node_version(
        db_session_factory,
        logical_node_id=node.node_id,
        title="Epic v2",
        prompt="new prompt",
    )
    assert candidate.version_number == 2
    assert candidate.status == "candidate"
    assert candidate.supersedes_node_version_id == first.id

    lineage = cutover_candidate_version(db_session_factory, version_id=candidate.id)

    assert lineage.authoritative_node_version_id == candidate.id
    versions = {item.version_number: item for item in lineage.versions}
    assert versions[1].status == "superseded"
    assert versions[2].status == "authoritative"


def test_cutover_cleans_up_tmux_sessions_for_superseded_version(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    first = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=load_resource_catalog())
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=node.node_id)
    adapter = FakeSessionAdapter()
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=lambda: adapter.now())
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    session_name = bound.tmux_session_name
    assert session_name is not None
    cancel_active_run(db_session_factory, logical_node_id=node.node_id)
    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id, title="Epic v2", prompt="new prompt")

    lineage = cutover_candidate_version(db_session_factory, version_id=candidate.id, adapter=adapter)

    assert lineage.authoritative_node_version_id == candidate.id
    assert first.id != candidate.id
    assert adapter.session_exists(session_name) is False


def test_superseding_rejects_live_candidate_and_active_run(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    first_candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    with pytest.raises(DaemonConflictError):
        create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)

    cutover_candidate_version(db_session_factory, version_id=first_candidate.id)
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    apply_authority_mutation(db_session_factory, node_id=str(node.node_id), command="node.run.start")

    with pytest.raises(DaemonConflictError):
        create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)


def test_parent_child_version_lineage_uses_current_authoritative_parent(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    child = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    parent_v1 = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_v1 = initialize_node_version(db_session_factory, logical_node_id=child.node_id)
    assert child_v1.parent_node_version_id == parent_v1.id

    parent_candidate = create_superseding_node_version(db_session_factory, logical_node_id=parent.node_id)
    cutover_candidate_version(db_session_factory, version_id=parent_candidate.id)
    child_candidate = create_superseding_node_version(db_session_factory, logical_node_id=child.node_id)

    assert child_candidate.parent_node_version_id == parent_candidate.id
    assert [item.version_number for item in list_node_versions(db_session_factory, child.node_id)] == [1, 2]
