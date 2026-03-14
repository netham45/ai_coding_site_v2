from __future__ import annotations

from sqlalchemy import select

from aicoding.daemon.admission import add_node_dependency, admit_node_run
from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.child_reconcile import collect_child_results, execute_child_merge_pipeline, inspect_parent_reconcile, plan_live_merge_children
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.incremental_parent_merge import process_next_incremental_child_merge, record_completed_child_for_incremental_merge
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import bootstrap_live_git_repo, stage_live_git_change
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.run_orchestration import load_current_subtask_context
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.db.models import MergeEvent, ParentChildAuthority
from aicoding.db.session import session_scope
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _transition_to_complete(db_session_factory, *, node_id: str) -> None:
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="READY")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="RUNNING")
    transition_node_lifecycle(db_session_factory, node_id=node_id, target_state="COMPLETE")


def test_collect_child_results_reads_merge_order_from_incremental_merge_history(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    discovery = create_manual_node(db_session_factory, registry, kind="phase", title="Discovery", prompt="d", parent_node_id=parent.node_id)
    implementation = create_manual_node(db_session_factory, registry, kind="phase", title="Implementation", prompt="i", parent_node_id=parent.node_id)
    discovery_version = discovery.node_version_id
    implementation_version = implementation.node_version_id
    _transition_to_complete(db_session_factory, node_id=str(discovery.node.node_id))
    _transition_to_complete(db_session_factory, node_id=str(implementation.node.node_id))
    add_node_dependency(
        db_session_factory,
        node_id=implementation.node.node_id,
        depends_on_node_id=discovery.node.node_id,
        required_state="COMPLETE",
    )
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=discovery_version, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=implementation_version, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=discovery_version,
        files={"shared.txt": "base\ndiscovery\n"},
        message="Discovery final",
        record_as_final=True,
    )
    stage_live_git_change(
        db_session_factory,
        version_id=implementation_version,
        files={"shared.txt": "base\nimplementation\n"},
        message="Implementation final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=discovery_version)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=implementation_version)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    snapshot = collect_child_results(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.status == "ready_for_reconcile"
    assert [item.child_title for item in snapshot.children] == ["Discovery", "Implementation"]
    assert [item.merge_order for item in snapshot.children] == [1, 2]
    assert snapshot.children[1].dependency_child_node_ids == [discovery.node.node_id]


def test_collect_child_results_marks_superseded_authoritative_replacement(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    child_v1 = child.node_version_id
    _transition_to_complete(db_session_factory, node_id=str(child.node.node_id))
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_v1, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_v1,
        files={"shared.txt": "base\nchild-v1\n"},
        message="Child v1 final",
        record_as_final=True,
    )
    child_v2 = create_superseding_node_version(db_session_factory, logical_node_id=child.node.node_id)
    bootstrap_live_git_repo(
        db_session_factory,
        version_id=child_v2.id,
        base_version_id=child_v1,
        replace_existing=True,
    )
    stage_live_git_change(
        db_session_factory,
        version_id=child_v2.id,
        files={"shared.txt": "base\nchild-v2\n"},
        message="Child v2 final",
        record_as_final=True,
    )
    cutover_candidate_version(db_session_factory, version_id=child_v2.id)
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_v2.id)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    snapshot = collect_child_results(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.children[0].edge_child_node_version_id == child_v1
    assert snapshot.children[0].child_node_version_id == child_v2.id
    assert snapshot.children[0].reconcile_status == "superseded_with_authoritative_replacement"
    assert snapshot.children[0].merge_order == 1


def test_collect_child_results_blocks_reconcile_until_child_has_been_incrementally_merged(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    child_version = child.node_version_id
    _transition_to_complete(db_session_factory, node_id=str(child.node.node_id))
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_version, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_version,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )

    child_results = collect_child_results(db_session_factory, logical_node_id=parent.node_id)
    reconcile = inspect_parent_reconcile(db_session_factory, catalog, logical_node_id=parent.node_id)

    assert child_results.status == "blocked"
    assert child_results.children[0].merge_order is None
    assert "child not incrementally merged" in child_results.children[0].blocking_reasons
    assert reconcile.status == "blocked"
    assert any(reason.endswith("is waiting") for reason in reconcile.blocking_reasons)


def test_plan_live_merge_children_orders_finalized_authoritative_children_before_merge_history_exists(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    discovery = create_manual_node(db_session_factory, registry, kind="phase", title="Discovery", prompt="d", parent_node_id=parent.node_id)
    implementation = create_manual_node(db_session_factory, registry, kind="phase", title="Implementation", prompt="i", parent_node_id=parent.node_id)
    _transition_to_complete(db_session_factory, node_id=str(discovery.node.node_id))
    _transition_to_complete(db_session_factory, node_id=str(implementation.node.node_id))
    add_node_dependency(
        db_session_factory,
        node_id=implementation.node.node_id,
        depends_on_node_id=discovery.node.node_id,
        required_state="COMPLETE",
    )
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=discovery.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=implementation.node_version_id, files={"shared.txt": "base\n"}, replace_existing=True)
    discovery_status = stage_live_git_change(
        db_session_factory,
        version_id=discovery.node_version_id,
        files={"shared.txt": "base\ndiscovery\n"},
        message="Discovery final",
        record_as_final=True,
    )
    implementation_status = stage_live_git_change(
        db_session_factory,
        version_id=implementation.node_version_id,
        files={"shared.txt": "base\nimplementation\n"},
        message="Implementation final",
        record_as_final=True,
    )

    ordered_children = plan_live_merge_children(db_session_factory, logical_node_id=parent.node_id)

    assert ordered_children == [
        (discovery.node_version_id, discovery_status.final_commit_sha, 1),
        (implementation.node_version_id, implementation_status.final_commit_sha, 2),
    ]


def test_execute_child_merge_pipeline_reuses_existing_merge_events_and_parent_reconcile_context(
    db_session_factory,
    migrated_public_schema,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_manual_node(db_session_factory, registry, kind="phase", title="Child", prompt="c", parent_node_id=parent.node_id)
    child_version = child.node_version_id
    compile_node_workflow(db_session_factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="COMPILED")
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=parent.node_id)
    _transition_to_complete(db_session_factory, node_id=str(child.node.node_id))
    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_version, files={"shared.txt": "base\n"}, replace_existing=True)
    child_status = stage_live_git_change(
        db_session_factory,
        version_id=child_version,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version)
    process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)

    snapshot = execute_child_merge_pipeline(db_session_factory, catalog, logical_node_id=parent.node_id)
    context = load_current_subtask_context(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.status == "reconciled"
    assert len(snapshot.merge_events) == 1
    assert snapshot.merge_events[0].merge_order == 1
    assert snapshot.merge_events[0].child_final_commit_sha == child_status.final_commit_sha
    assert context.input_context_json["parent_reconcile_context"]["status"] == "reconciled"
    assert context.input_context_json["parent_reconcile_context"]["merge_events"][0]["child_final_commit_sha"] == child_status.final_commit_sha
    with session_scope(db_session_factory) as session:
        events = session.execute(select(MergeEvent).where(MergeEvent.parent_node_version_id == parent_version.id)).scalars().all()
        authority = session.get(ParentChildAuthority, parent_version.id)
        assert len(events) == 1
        assert authority is not None
        assert authority.last_reconciled_at is not None
