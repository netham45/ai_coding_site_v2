from __future__ import annotations

from uuid import UUID

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.interventions import apply_node_intervention, list_node_interventions
from aicoding.daemon.live_git import bootstrap_live_git_repo, execute_live_merge_children, stage_live_git_change
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.manual_tree import create_manual_node
from aicoding.daemon.materialization import materialize_layout_children
from aicoding.daemon.operator_views import list_node_events, load_pause_state
from aicoding.daemon.run_orchestration import sync_paused_run
from aicoding.daemon.versioning import initialize_node_version
from aicoding.db.models import NodeLifecycleState
from aicoding.db.session import session_scope
from aicoding.db.session import create_session_factory
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_ready_running_node(factory, *, title: str):
    from aicoding.daemon.workflows import compile_node_workflow

    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    node = create_hierarchy_node(factory, registry, kind="epic", title=title, prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=node.node_id)
    compile_node_workflow(factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(factory, node_id=node.node_id, trigger_reason="test")
    return node, catalog, registry


def test_pause_approval_intervention_catalog_and_apply(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    node, catalog, _registry = _create_ready_running_node(factory, title="Pause intervention")
    sync_paused_run(factory, logical_node_id=node.node_id, pause_flag_name="user_guidance_required")
    with session_scope(factory) as session:
        state = session.get(NodeLifecycleState, str(node.node_id))
        assert state is not None
        cursor = dict(state.execution_cursor_json or {})
        pause_context = dict(cursor.get("pause_context", {}))
        pause_context["approval_required"] = True
        state.execution_cursor_json = {**cursor, "pause_context": pause_context}
        session.flush()

    catalog_snapshot = list_node_interventions(factory, catalog, logical_node_id=node.node_id)

    pause_item = next(item for item in catalog_snapshot.interventions if item.kind == "pause_approval")
    assert pause_item.recommended_action == "approve_pause"
    applied = apply_node_intervention(
        factory,
        catalog,
        logical_node_id=node.node_id,
        intervention_kind="pause_approval",
        action="approve_pause",
        summary="approved",
        pause_flag_name="user_guidance_required",
    )

    assert applied.status == "accepted"
    assert applied.result_json["approved"] is True
    assert any(item.event_scope == "intervention" for item in list_node_events(factory, node_id=node.node_id))


def test_child_reconciliation_intervention_catalog_and_apply(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Hybrid parent", prompt="boot prompt")
    seed_node_lifecycle(factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(factory, logical_node_id=parent.node_id)
    materialize_layout_children(factory, registry, catalog, logical_node_id=parent.node_id)
    create_manual_node(factory, registry, kind="phase", title="Manual child", prompt="manual", parent_node_id=parent.node_id)

    catalog_snapshot = list_node_interventions(factory, catalog, logical_node_id=parent.node_id)

    reconcile_item = next(item for item in catalog_snapshot.interventions if item.kind == "child_reconciliation")
    assert reconcile_item.recommended_action == "preserve_manual"
    applied = apply_node_intervention(
        factory,
        catalog,
        logical_node_id=parent.node_id,
        intervention_kind="child_reconciliation",
        action="preserve_manual",
    )

    assert applied.status == "accepted"
    assert applied.result_json["materialization_status"] == "manual"


def test_merge_conflict_intervention_catalog_and_abort(migrated_public_schema) -> None:
    factory = create_session_factory(engine=migrated_public_schema)
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(factory, registry)
    parent = create_hierarchy_node(factory, registry, kind="epic", title="Merge parent", prompt="boot prompt")
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
    execute_live_merge_children(
        factory,
        logical_node_id=parent.node_id,
        ordered_child_versions=[
            (child_a.node_version_id, child_a_status.final_commit_sha, 1),
            (child_b.node_version_id, child_b_status.final_commit_sha, 2),
        ],
    )

    catalog_snapshot = list_node_interventions(factory, catalog, logical_node_id=parent.node_id)

    conflict_item = next(item for item in catalog_snapshot.interventions if item.kind == "merge_conflict")
    assert conflict_item.recommended_action == "abort_merge"
    applied = apply_node_intervention(
        factory,
        catalog,
        logical_node_id=parent.node_id,
        intervention_kind="merge_conflict",
        action="abort_merge",
    )

    assert applied.status == "accepted"
    assert applied.result_json["working_tree_state"] == "seed_ready"
