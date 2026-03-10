from __future__ import annotations

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.reproducibility import load_node_audit_snapshot, load_run_audit_snapshot
from aicoding.daemon.run_orchestration import (
    complete_current_subtask,
    load_current_run_progress,
    load_current_subtask_prompt,
    register_summary,
    start_subtask_attempt,
)
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def _create_started_run(db_session_factory):
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Auditable", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=node.node_id)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
    return node, progress


def test_load_node_audit_snapshot_collects_durable_history(db_session_factory, migrated_public_schema, tmp_path) -> None:
    node, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    load_current_subtask_prompt(db_session_factory, logical_node_id=node.node_id)
    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    register_summary(
        db_session_factory,
        logical_node_id=node.node_id,
        summary_type="subtask",
        summary_path=str(tmp_path / "audit-summary.md"),
        content="durable audit summary",
    )
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="first step complete",
    )

    snapshot = load_node_audit_snapshot(db_session_factory, logical_node_id=node.node_id)

    assert snapshot.node_id == node.node_id
    assert snapshot.current_workflow is not None
    assert snapshot.workflow_chain is not None
    assert snapshot.source_lineage["source_documents"]
    assert snapshot.run_count == 1
    assert snapshot.prompt_history["prompts"]
    assert snapshot.summary_history["summaries"]


def test_load_run_audit_snapshot_by_node_includes_attempts_and_prompt_summary_history(
    db_session_factory, migrated_public_schema, tmp_path
) -> None:
    node, progress = _create_started_run(db_session_factory)
    current_subtask_id = progress.state.current_compiled_subtask_id

    prompt = load_current_subtask_prompt(db_session_factory, logical_node_id=node.node_id)
    start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
    register_summary(
        db_session_factory,
        logical_node_id=node.node_id,
        summary_type="subtask",
        summary_path=str(tmp_path / "run-summary.md"),
        content="run summary",
    )
    complete_current_subtask(
        db_session_factory,
        logical_node_id=node.node_id,
        compiled_subtask_id=current_subtask_id,
        summary="done",
    )

    snapshot = load_run_audit_snapshot(db_session_factory, logical_node_id=node.node_id)

    assert snapshot.node_id == node.node_id
    assert snapshot.node_run_id == progress.run.id
    assert snapshot.workflow is not None
    assert snapshot.source_lineage["node_version_id"] == str(snapshot.node_version_id)
    assert snapshot.attempts[0]["status"] == "COMPLETE"
    assert snapshot.prompts[0]["id"] == str(prompt.prompt_id)
    assert snapshot.summaries
