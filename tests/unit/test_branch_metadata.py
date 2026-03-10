from __future__ import annotations

import pytest
from sqlalchemy import update

from aicoding.daemon.branches import (
    build_canonical_branch_name,
    load_node_branch_metadata,
    load_node_version_branch_metadata,
    record_final_commit,
    record_seed_commit,
)
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.versioning import create_superseding_node_version, initialize_node_version
from aicoding.db.models import NodeVersion
from aicoding.db.session import session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_initialize_node_version_uses_canonical_branch_name(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="epic",
        title="Hello, Branch World",
        prompt="top prompt",
    )

    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    branch = load_node_branch_metadata(db_session_factory, logical_node_id=node.node_id)

    assert version.active_branch_name == build_canonical_branch_name(
        tier=node.tier,
        kind=node.kind,
        title="Hello, Branch World",
        logical_node_id=node.node_id,
        version_number=1,
    )
    assert branch.branch_status == "valid"
    assert branch.violations == []


def test_seed_and_final_commit_recording_enforces_invariants(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    with pytest.raises(DaemonConflictError):
        record_final_commit(db_session_factory, version_id=version.id, commit_sha="abcdef1")

    seeded = record_seed_commit(db_session_factory, version_id=version.id, commit_sha="ABCDEF1")
    finalized = record_final_commit(db_session_factory, version_id=version.id, commit_sha="1234abc")

    assert seeded.seed_commit_sha == "abcdef1"
    assert finalized.final_commit_sha == "1234abc"

    with pytest.raises(DaemonConflictError):
        record_seed_commit(db_session_factory, version_id=version.id, commit_sha="fedcba9")
    with pytest.raises(DaemonConflictError):
        record_final_commit(db_session_factory, version_id=version.id, commit_sha="7654321")


def test_superseding_version_inherits_latest_final_as_seed(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    record_seed_commit(db_session_factory, version_id=version.id, commit_sha="abcdef1")
    record_final_commit(db_session_factory, version_id=version.id, commit_sha="1234abc")

    candidate = create_superseding_node_version(
        db_session_factory,
        logical_node_id=node.node_id,
        title="Epic Rebuilt",
    )

    assert candidate.seed_commit_sha == "1234abc"
    assert candidate.active_branch_name == build_canonical_branch_name(
        tier=node.tier,
        kind=node.kind,
        title="Epic Rebuilt",
        logical_node_id=node.node_id,
        version_number=2,
    )


def test_branch_metadata_detects_stale_branch_rows(db_session_factory, migrated_public_schema) -> None:
    registry = load_hierarchy_registry(load_resource_catalog())
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Epic", prompt="top prompt")
    version = initialize_node_version(db_session_factory, logical_node_id=node.node_id)

    with session_scope(db_session_factory) as session:
        session.execute(
            update(NodeVersion)
            .where(NodeVersion.id == version.id)
            .values(active_branch_name="broken/branch", branch_generation_number=99)
        )

    branch = load_node_version_branch_metadata(db_session_factory, version_id=version.id)

    assert branch.branch_status == "stale"
    assert branch.violations == ["branch_name_mismatch", "branch_generation_mismatch"]
