from __future__ import annotations

import concurrent.futures

import pytest
from sqlalchemy import text

from aicoding.daemon.errors import DaemonConflictError, DaemonNotFoundError
from aicoding.daemon.orchestration import apply_authority_mutation, load_authority_state


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
