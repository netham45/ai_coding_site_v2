from __future__ import annotations

import concurrent.futures

import pytest
from sqlalchemy import text

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.orchestration import apply_authority_mutation, load_authority_state
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.db.models import DaemonNodeState, LogicalNodeCurrentVersion, NodeLifecycleState, NodeVersion
from aicoding.db.session import query_session_scope, session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_apply_authority_mutation_persists_start_pause_resume(db_session_factory, migrated_public_schema) -> None:
    started = apply_authority_mutation(db_session_factory, node_id="node-123", command="node.run.start")
    paused = apply_authority_mutation(db_session_factory, node_id="node-123", command="node.pause")
    resumed = apply_authority_mutation(db_session_factory, node_id="node-123", command="node.resume")

    assert started.current_state == "RUNNING"
    assert paused.current_state == "PAUSED_FOR_USER"
    assert resumed.current_state == "RUNNING"
    assert resumed.current_run_id == started.current_run_id
    assert resumed.event_count == 3


def test_load_authority_state_raises_for_missing_node(db_session_factory, migrated_public_schema) -> None:
    with pytest.raises(DaemonNotFoundError):
        load_authority_state(db_session_factory, "missing-node")


def test_apply_authority_mutation_rejects_illegal_transitions(db_session_factory, migrated_public_schema) -> None:
    with pytest.raises(DaemonNotFoundError):
        apply_authority_mutation(db_session_factory, node_id="missing-node", command="node.pause")

    apply_authority_mutation(db_session_factory, node_id="node-123", command="node.run.start")

    with pytest.raises(DaemonConflictError):
        apply_authority_mutation(db_session_factory, node_id="node-123", command="node.run.start")

    apply_authority_mutation(db_session_factory, node_id="node-123", command="node.pause")
    with pytest.raises(DaemonConflictError):
        apply_authority_mutation(db_session_factory, node_id="node-123", command="node.pause")


def test_concurrent_start_requests_serialize_per_node(db_session_factory, migrated_public_schema) -> None:
    def attempt_start() -> str:
        try:
            apply_authority_mutation(db_session_factory, node_id="node-race", command="node.run.start")
            return "accepted"
        except DaemonConflictError:
            return "conflict"

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        results = sorted(executor.map(lambda _: attempt_start(), range(2)))

    assert results == ["accepted", "conflict"]

    with migrated_public_schema.begin() as connection:
        event_count = connection.execute(
            text("select count(*) from daemon_mutation_events where node_id = 'node-race'")
        ).scalar_one()

    assert event_count == 1


def test_apply_authority_mutation_rebinds_stale_live_authority_to_current_version(
    db_session_factory, migrated_public_schema
) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Versioned", prompt="boot prompt")
    version_one = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    version_two = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="READY")

    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, node.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, version_one.id)
        new_version = session.get(NodeVersion, version_two.id)
        assert old_version is not None and new_version is not None
        old_version.status = "superseded"
        new_version.status = "authoritative"
        selector.authoritative_node_version_id = new_version.id
        selector.latest_created_node_version_id = new_version.id
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        assert lifecycle is not None
        lifecycle.node_version_id = old_version.id
        lifecycle.current_run_id = version_one.id
        lifecycle.run_status = "RUNNING"
        daemon_state = DaemonNodeState(
            node_id=str(node.node_id),
            node_version_id=old_version.id,
            current_run_id=version_one.id,
            lifecycle_state="active",
            authority="daemon",
            last_command="node.run.start",
            last_event_id=version_one.id,
        )
        session.merge(daemon_state)
        session.flush()

    started = apply_authority_mutation(db_session_factory, node_id=str(node.node_id), command="node.run.start")

    assert started.node_version_id == version_two.id
    with query_session_scope(db_session_factory) as session:
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        daemon_state = session.get(DaemonNodeState, str(node.node_id))
        assert lifecycle is not None
        assert daemon_state is not None
        assert lifecycle.node_version_id == version_two.id
        assert daemon_state.node_version_id == version_two.id
