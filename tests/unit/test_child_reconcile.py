from __future__ import annotations

from sqlalchemy import select

from aicoding.daemon.admission import add_node_dependency, admit_node_run
from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.child_reconcile import collect_child_results, execute_child_merge_pipeline
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
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


def test_collect_child_results_orders_children_by_dependency_and_ordinal(
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
    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=discovery_version, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=discovery_version, commit_sha="def5678")
    record_seed_commit(db_session_factory, version_id=implementation_version, commit_sha="987abcd")
    record_final_commit(db_session_factory, version_id=implementation_version, commit_sha="987efab")
    add_node_dependency(
        db_session_factory,
        node_id=implementation.node.node_id,
        depends_on_node_id=discovery.node.node_id,
        required_state="COMPLETE",
    )

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
    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_v1, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_v1, commit_sha="def5678")
    child_v2 = create_superseding_node_version(db_session_factory, logical_node_id=child.node.node_id)
    record_final_commit(db_session_factory, version_id=child_v2.id, commit_sha="fed5678")
    cutover_candidate_version(db_session_factory, version_id=child_v2.id)

    snapshot = collect_child_results(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.children[0].edge_child_node_version_id == child_v1
    assert snapshot.children[0].child_node_version_id == child_v2.id
    assert snapshot.children[0].reconcile_status == "superseded_with_authoritative_replacement"


def test_execute_child_merge_pipeline_persists_events_and_parent_reconcile_context(
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
    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_version, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_version, commit_sha="def5678")

    snapshot = execute_child_merge_pipeline(db_session_factory, catalog, logical_node_id=parent.node_id)
    context = load_current_subtask_context(db_session_factory, logical_node_id=parent.node_id)

    assert snapshot.status == "merged"
    assert len(snapshot.merge_events) == 1
    assert snapshot.merge_events[0].merge_order == 1
    assert context.input_context_json["parent_reconcile_context"]["merge_events"][0]["child_final_commit_sha"] == "def5678"
    with session_scope(db_session_factory) as session:
        events = session.execute(select(MergeEvent).where(MergeEvent.parent_node_version_id == parent_version.id)).scalars().all()
        authority = session.get(ParentChildAuthority, parent_version.id)
        assert len(events) == 1
        assert authority is not None
        assert authority.last_reconciled_at is not None
