from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from uuid import UUID, uuid4

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.branches import record_final_commit, record_seed_commit
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.hierarchy import create_hierarchy_node, sync_hierarchy_definitions
from aicoding.daemon.git_conflicts import list_merge_conflicts_for_version, list_merge_events_for_node, resolve_merge_conflict
from aicoding.daemon.incremental_parent_merge import (
    get_parent_incremental_merge_lane,
    list_incremental_child_merge_states_for_parent,
    process_next_incremental_child_merge,
    record_completed_child_for_incremental_merge,
)
from aicoding.daemon.live_git import bootstrap_live_git_repo, show_live_git_status, stage_live_git_change
from aicoding.daemon.run_orchestration import advance_workflow, load_current_subtask_context
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog


def test_record_completed_child_for_incremental_merge_creates_lane_and_state(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="c",
        parent_node_id=parent.node_id,
    )
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_version.id, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_version.id, commit_sha="def5678")

    snapshot = record_completed_child_for_incremental_merge(
        db_session_factory,
        child_node_version_id=child_version.id,
    )

    assert snapshot is not None
    assert snapshot.parent_node_version_id == parent_version.id
    assert snapshot.child_node_version_id == child_version.id
    assert snapshot.child_final_commit_sha == "def5678"
    assert snapshot.status == "completed_unmerged"

    lane = get_parent_incremental_merge_lane(db_session_factory, parent_node_version_id=parent_version.id)
    assert lane is not None
    assert lane.status == "pending"
    assert lane.current_parent_head_commit_sha == "abc1234"


def test_record_completed_child_for_incremental_merge_is_idempotent(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="c",
        parent_node_id=parent.node_id,
    )
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_version.id, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_version.id, commit_sha="def5678")

    first = record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version.id)
    second = record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version.id)
    states = list_incremental_child_merge_states_for_parent(db_session_factory, parent_node_version_id=parent_version.id)

    assert first is not None
    assert second is not None
    assert len(states) == 1
    assert states[0].child_node_version_id == child_version.id


def test_record_completed_child_for_incremental_merge_ignores_non_authoritative_child(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="c",
        parent_node_id=parent.node_id,
    )
    child_v1 = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    record_seed_commit(db_session_factory, version_id=parent_version.id, commit_sha="abc1234")
    record_seed_commit(db_session_factory, version_id=child_v1.id, commit_sha="def1234")
    record_final_commit(db_session_factory, version_id=child_v1.id, commit_sha="def5678")

    child_v2 = create_superseding_node_version(db_session_factory, logical_node_id=child.node_id)
    record_final_commit(db_session_factory, version_id=child_v2.id, commit_sha="fed5678")
    cutover_candidate_version(db_session_factory, version_id=child_v2.id)

    snapshot = record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_v1.id)
    states = list_incremental_child_merge_states_for_parent(db_session_factory, parent_node_version_id=parent_version.id)

    assert snapshot is None
    assert states == []


def test_advance_workflow_records_incremental_merge_state_on_terminal_completion(monkeypatch) -> None:
    logical_node_id = uuid4()
    compiled_subtask_id = uuid4()
    compiled_workflow_id = uuid4()
    version_id = uuid4()
    recorded: dict[str, UUID] = {}

    fake_run = SimpleNamespace(id=uuid4(), compiled_workflow_id=compiled_workflow_id, run_status="RUNNING", ended_at=None)
    fake_state = SimpleNamespace(
        current_compiled_subtask_id=compiled_subtask_id,
        lifecycle_state="RUNNING",
        current_task_id=uuid4(),
        current_subtask_attempt=1,
        is_resumable=True,
    )
    fake_version = SimpleNamespace(id=version_id)
    fake_attempt = SimpleNamespace(status="COMPLETE")
    fake_subtask = SimpleNamespace(subtask_type="run_prompt")

    class _FakeSession:
        def get(self, model, object_id):
            if object_id == compiled_subtask_id:
                return fake_subtask
            return None

        def flush(self) -> None:
            return None

    fake_session = _FakeSession()

    @contextmanager
    def _fake_session_scope(_factory):
        yield fake_session

    monkeypatch.setattr("aicoding.daemon.run_orchestration.session_scope", _fake_session_scope)
    monkeypatch.setattr(
        "aicoding.daemon.run_orchestration._load_active_run_bundle",
        lambda session, logical_node_id: (fake_run, fake_state, fake_version),
    )
    monkeypatch.setattr("aicoding.daemon.run_orchestration._latest_attempt", lambda session, run_id, subtask_id: fake_attempt)
    monkeypatch.setattr("aicoding.daemon.run_orchestration._next_subtask", lambda session, workflow_id, current_subtask_id: None)
    monkeypatch.setattr("aicoding.daemon.run_orchestration._sync_lifecycle_with_run", lambda *args, **kwargs: None)
    monkeypatch.setattr("aicoding.daemon.run_orchestration._progress_snapshot", lambda session, run_id: "terminal-progress")

    def _record(session, *, child_node_version_id: UUID):
        recorded["child_node_version_id"] = child_node_version_id
        return None

    monkeypatch.setattr("aicoding.daemon.run_orchestration.record_completed_child_for_incremental_merge_in_session", _record)

    result = advance_workflow(object(), logical_node_id=logical_node_id)

    assert result == "terminal-progress"
    assert recorded["child_node_version_id"] == version_id
    assert fake_run.run_status == "COMPLETE"
    assert fake_state.lifecycle_state == "COMPLETE"


def test_process_next_incremental_child_merge_executes_real_git_and_records_applied_order(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="c",
        parent_node_id=parent.node_id,
    )
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_version.id,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version.id)

    execution = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    lane = get_parent_incremental_merge_lane(db_session_factory, parent_node_version_id=parent_version.id)
    states = list_incremental_child_merge_states_for_parent(db_session_factory, parent_node_version_id=parent_version.id)
    events = list_merge_events_for_node(db_session_factory, logical_node_id=parent.node_id)
    parent_status = show_live_git_status(db_session_factory, version_id=parent_version.id)

    assert execution is not None
    assert execution.status == "merged"
    assert execution.applied_merge_order == 1
    assert lane is not None
    assert lane.status == "idle"
    assert lane.current_parent_head_commit_sha == execution.parent_commit_after
    assert states[0].status == "merged"
    assert states[0].applied_merge_order == 1
    assert events[0].child_node_version_id == child_version.id
    assert events[0].merge_order == 1
    assert parent_status.head_commit_sha == execution.parent_commit_after


def test_process_next_incremental_child_merge_is_idempotent_after_success(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child",
        prompt="c",
        parent_node_id=parent.node_id,
    )
    child_version = initialize_node_version(db_session_factory, logical_node_id=child.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_version.id,
        files={"shared.txt": "base\nchild change\n"},
        message="Child final",
        record_as_final=True,
    )
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_version.id)

    first = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    second = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    states = list_incremental_child_merge_states_for_parent(db_session_factory, parent_node_version_id=parent_version.id)
    events = list_merge_events_for_node(db_session_factory, logical_node_id=parent.node_id)

    assert first is not None
    assert second is None
    assert len(states) == 1
    assert states[0].status == "merged"
    assert len(events) == 1


def test_process_next_incremental_child_merge_records_conflict_against_advanced_lane_head(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    child_a = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child A",
        prompt="a",
        parent_node_id=parent.node_id,
    )
    child_a_version = initialize_node_version(db_session_factory, logical_node_id=child_a.node_id)
    child_b = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child B",
        prompt="b",
        parent_node_id=parent.node_id,
    )
    child_b_version = initialize_node_version(db_session_factory, logical_node_id=child_b.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_a_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_b_version.id, files={"shared.txt": "base\n"}, replace_existing=True)

    stage_live_git_change(
        db_session_factory,
        version_id=child_a_version.id,
        files={"shared.txt": "base\nchild a\n"},
        message="Child A final",
        record_as_final=True,
    )
    stage_live_git_change(
        db_session_factory,
        version_id=child_b_version.id,
        files={"shared.txt": "base\nchild b\n"},
        message="Child B final",
        record_as_final=True,
    )

    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_a_version.id)
    first = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    assert first is not None
    assert first.status == "merged"

    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_b_version.id)
    conflicted = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    lane = get_parent_incremental_merge_lane(db_session_factory, parent_node_version_id=parent_version.id)
    states = list_incremental_child_merge_states_for_parent(db_session_factory, parent_node_version_id=parent_version.id)
    conflicts = list_merge_conflicts_for_version(db_session_factory, node_version_id=parent_version.id)

    assert conflicted is not None
    assert conflicted.status == "conflicted"
    assert conflicted.conflict_id is not None
    assert lane is not None
    assert lane.status == "blocked"
    assert lane.blocked_reason == "merge_conflict"
    assert [item.status for item in states] == ["merged", "conflicted"]
    assert conflicts


def test_incremental_merge_conflict_persists_parent_reconcile_context_and_resolution_updates_it(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    sync_hierarchy_definitions(db_session_factory, registry)

    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    parent_version = initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=parent.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(parent.node_id), target_state="READY")
    admit_node_run(db_session_factory, node_id=parent.node_id, trigger_reason="test")

    child_a = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child A",
        prompt="a",
        parent_node_id=parent.node_id,
    )
    child_b = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Child B",
        prompt="b",
        parent_node_id=parent.node_id,
    )
    child_a_version = initialize_node_version(db_session_factory, logical_node_id=child_a.node_id)
    child_b_version = initialize_node_version(db_session_factory, logical_node_id=child_b.node_id)

    bootstrap_live_git_repo(db_session_factory, version_id=parent_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_a_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    bootstrap_live_git_repo(db_session_factory, version_id=child_b_version.id, files={"shared.txt": "base\n"}, replace_existing=True)
    stage_live_git_change(
        db_session_factory,
        version_id=child_a_version.id,
        files={"shared.txt": "base\nchild a\n"},
        message="Child A final",
        record_as_final=True,
    )
    stage_live_git_change(
        db_session_factory,
        version_id=child_b_version.id,
        files={"shared.txt": "base\nchild b\n"},
        message="Child B final",
        record_as_final=True,
    )

    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_a_version.id)
    first = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    assert first is not None
    assert first.status == "merged"
    record_completed_child_for_incremental_merge(db_session_factory, child_node_version_id=child_b_version.id)

    conflicted = process_next_incremental_child_merge(db_session_factory, parent_node_version_id=parent_version.id)
    assert conflicted is not None
    assert conflicted.status == "conflicted"
    assert conflicted.conflict_id is not None

    conflict_context = load_current_subtask_context(db_session_factory, logical_node_id=parent.node_id)
    payload = conflict_context.input_context_json["parent_reconcile_context"]
    assert payload["context_kind"] == "incremental_merge_conflict"
    assert payload["status"] == "blocked_on_incremental_merge_conflict"
    assert payload["incremental_merge_conflict"]["conflict_id"] == str(conflicted.conflict_id)
    assert payload["incremental_merge_conflict"]["resolution_status"] == "unresolved"
    assert payload["incremental_merge_conflict"]["files_json"] == ["shared.txt"]

    resolve_merge_conflict(
        db_session_factory,
        conflict_id=conflicted.conflict_id,
        resolution_summary="Resolved by parent session.",
    )
    resolved_context = load_current_subtask_context(db_session_factory, logical_node_id=parent.node_id)
    resolved_payload = resolved_context.input_context_json["parent_reconcile_context"]
    assert resolved_payload["status"] == "conflict_resolution_recorded"
    assert resolved_payload["incremental_merge_conflict"]["resolution_status"] == "resolved"
    assert resolved_payload["incremental_merge_conflict"]["resolution_summary"] == "Resolved by parent session."
