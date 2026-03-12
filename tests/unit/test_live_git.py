from __future__ import annotations

import subprocess

import pytest

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle
from aicoding.daemon.live_git import (
    abort_live_merge,
    bootstrap_live_git_repo,
    execute_live_merge_children,
    execute_live_merge_children_for_version,
    finalize_live_git_state,
    finalize_live_git_state_for_version,
    stage_live_git_change,
)
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.versioning import initialize_node_version
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _git(repo_path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


def test_live_git_merge_children_executes_real_git_and_finalize_records_final_commit(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory, query_session_scope

    factory = create_session_factory(engine=migrated_public_schema)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(factory, logical_node_id=parent.node_id)
    child = create_manual_node(factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=child.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        factory,
        version_id=child.node_version_id,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )

    merge_result = execute_live_merge_children(
        factory,
        logical_node_id=parent.node_id,
        ordered_child_versions=[(child.node_version_id, child_status.final_commit_sha, 1)],
    )
    finalize_result = finalize_live_git_state(factory, logical_node_id=parent.node_id)

    assert merge_result.status == "merged"
    assert merge_result.merge_events
    assert finalize_result.status == "finalized"
    from aicoding.db.models import NodeVersion

    with query_session_scope(factory) as session:
        version = session.get(NodeVersion, parent_version.id)
        assert version is not None
        assert version.final_commit_sha == finalize_result.final_commit_sha


def test_live_git_merge_conflict_can_be_aborted_and_retried(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory

    factory = create_session_factory(engine=migrated_public_schema)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Parent Conflict", prompt="p")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(factory, logical_node_id=parent.node_id)
    child_a = create_manual_node(factory, registry, kind="phase", title="Child A", prompt="a", parent_node_id=parent.node_id)
    child_b = create_manual_node(factory, registry, kind="phase", title="Child B", prompt="b", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=child_a.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=child_b.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)

    child_a_status = stage_live_git_change(
        factory,
        version_id=child_a.node_version_id,
        files={"shared.txt": "base\nchild a\n"},
        message="Child A final",
        record_as_final=True,
    )
    child_b_status = stage_live_git_change(
        factory,
        version_id=child_b.node_version_id,
        files={"shared.txt": "base\nchild b\n"},
        message="Child B final",
        record_as_final=True,
    )

    conflicted = execute_live_merge_children(
        factory,
        logical_node_id=parent.node_id,
        ordered_child_versions=[
            (child_a.node_version_id, child_a_status.final_commit_sha, 1),
            (child_b.node_version_id, child_b_status.final_commit_sha, 2),
        ],
    )
    assert conflicted.status == "conflicted"
    assert conflicted.conflicts

    aborted = abort_live_merge(factory, logical_node_id=parent.node_id)
    assert aborted.working_tree_state == "seed_ready"


def test_finalize_live_git_state_rejects_dirty_worktree(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory

    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Finalize Dirty", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    status = bootstrap_live_git_repo(factory, version_id=version.id, files={"shared.txt": "base\n"}, replace_existing=True)

    from pathlib import Path

    (Path(status.repo_path) / "shared.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(Exception, match="clean working tree"):
        finalize_live_git_state(factory, logical_node_id=node.node_id)


def test_bootstrap_live_git_repo_uses_candidate_inherited_seed_commit(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.session import create_session_factory
    from aicoding.daemon.versioning import create_superseding_node_version

    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Candidate Bootstrap", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    bootstrap_live_git_repo(factory, version_id=version.id, files={"shared.txt": "seed\n"}, replace_existing=True)
    first_final = stage_live_git_change(
        factory,
        version_id=version.id,
        files={"shared.txt": "seed\nv1 final\n"},
        message="Version 1 final",
        record_as_final=True,
    )

    candidate = create_superseding_node_version(factory, logical_node_id=node.node_id, title="Candidate Bootstrap v2")
    candidate_status = bootstrap_live_git_repo(factory, version_id=candidate.id, base_version_id=version.id, replace_existing=True)

    from pathlib import Path

    assert candidate_status.seed_commit_sha == first_final.final_commit_sha
    assert candidate_status.head_commit_sha == first_final.final_commit_sha
    assert (Path(candidate_status.repo_path) / "shared.txt").read_text(encoding="utf-8") == "seed\nv1 final\n"


def test_bootstrap_live_git_repo_from_source_repo_preserves_recorded_seed_commit(migrated_public_schema) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from pathlib import Path

    from aicoding.daemon.versioning import create_superseding_node_version
    from aicoding.db.models import NodeVersion
    from aicoding.db.session import create_session_factory, query_session_scope

    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Source Bootstrap", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    initial_status = bootstrap_live_git_repo(factory, version_id=version.id, files={"shared.txt": "seed\n"}, replace_existing=True)
    initial_seed = initial_status.seed_commit_sha
    assert initial_seed is not None

    stage_live_git_change(
        factory,
        version_id=version.id,
        files={"shared.txt": "seed\nv1 final\n"},
        message="Version 1 final",
        record_as_final=True,
    )

    candidate = create_superseding_node_version(factory, logical_node_id=node.node_id, title="Source Bootstrap v2")
    with query_session_scope(factory) as session:
        candidate_row = session.get(NodeVersion, candidate.id)
        assert candidate_row is not None
        expected_seed_commit = candidate_row.seed_commit_sha
    candidate_status = bootstrap_live_git_repo(
        factory,
        version_id=candidate.id,
        source_repo_path=Path(initial_status.repo_path),
        replace_existing=True,
    )

    assert candidate_status.seed_commit_sha == expected_seed_commit
    assert candidate_status.head_commit_sha == expected_seed_commit
    assert (Path(candidate_status.repo_path) / "shared.txt").read_text(encoding="utf-8") == "seed\nv1 final\n"


def test_finalize_live_git_state_replaces_unreachable_rectified_placeholder_final_commit(
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.db.models import NodeVersion
    from aicoding.db.session import create_session_factory, query_session_scope, session_scope

    factory = create_session_factory(engine=migrated_public_schema)
    node = create_hierarchy_node(factory, registry, kind="epic", title="Rectified Placeholder", prompt="p")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    version = initialize_node_version(factory, logical_node_id=node.node_id)
    status = bootstrap_live_git_repo(factory, version_id=version.id, files={"shared.txt": "seed\n"}, replace_existing=True)

    with session_scope(factory) as session:
        row = session.get(NodeVersion, version.id)
        assert row is not None
        row.final_commit_sha = "a" * 64
        session.flush()

    from pathlib import Path

    repo_path = Path(status.repo_path)
    (repo_path / "shared.txt").write_text("seed\nreal follow-on change\n", encoding="utf-8")
    _git(repo_path, "add", ".")
    _git(repo_path, "commit", "-m", "Real follow-on change")

    finalize_result = finalize_live_git_state(factory, logical_node_id=node.node_id)

    with query_session_scope(factory) as session:
        refreshed = session.get(NodeVersion, version.id)
        assert refreshed is not None
        assert refreshed.final_commit_sha == finalize_result.final_commit_sha
        assert refreshed.final_commit_sha != "a" * 64


def test_version_scoped_live_git_merge_and_finalize_records_real_candidate_final_commit(
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    from aicoding.daemon.versioning import create_superseding_node_version
    from aicoding.db.models import NodeVersion
    from aicoding.db.session import create_session_factory, query_session_scope

    factory = create_session_factory(engine=migrated_public_schema)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Parent Candidate", prompt="p")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(factory, logical_node_id=parent.node_id)
    child = create_manual_node(factory, registry, kind="phase", title="Child Candidate", prompt="c", parent_node_id=parent.node_id)

    bootstrap_live_git_repo(factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(factory, version_id=child.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        factory,
        version_id=child.node_version_id,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )

    candidate = create_superseding_node_version(factory, logical_node_id=parent.node_id, title="Parent Candidate v2")
    candidate_status = bootstrap_live_git_repo(factory, version_id=candidate.id, base_version_id=parent_version.id, replace_existing=True)

    merge_result = execute_live_merge_children_for_version(
        factory,
        node_version_id=candidate.id,
        ordered_child_versions=[(child.node_version_id, child_status.final_commit_sha, 1)],
    )
    finalize_result = finalize_live_git_state_for_version(factory, node_version_id=candidate.id)

    assert merge_result.status == "merged"
    assert finalize_result.status == "finalized"
    assert _git(candidate_status.repo_path, "show", f"{finalize_result.final_commit_sha}:shared.txt") == "base\nchild change"
    with query_session_scope(factory) as session:
        refreshed = session.get(NodeVersion, candidate.id)
        assert refreshed is not None
        assert refreshed.final_commit_sha == finalize_result.final_commit_sha
