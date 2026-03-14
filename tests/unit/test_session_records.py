from __future__ import annotations

import pytest
from types import SimpleNamespace
from uuid import uuid4

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.live_git import repo_path_for_version
from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller
from aicoding.daemon.session_records import (
    _render_recovery_prompt,
    _maybe_rematerialize_dependency_invalidated_child,
    auto_advance_incremental_parent_merge_and_refresh_children,
    auto_supervise_primary_sessions,
    attach_primary_session,
    bind_primary_session,
    get_session_for_node,
    inspect_primary_session_screen_state,
    load_provider_recovery_status,
    load_recovery_status,
    list_session_events,
    list_sessions_for_node,
    nudge_primary_session,
    push_or_queue_primary_session_stage_prompt,
    recover_primary_session_provider_specific,
    recover_primary_session,
    resume_primary_session,
    show_current_primary_session,
)
from aicoding.daemon.materialization import inspect_materialized_children, materialize_layout_children
from aicoding.daemon.regeneration import _record_rebuild_event
from aicoding.daemon.run_orchestration import sync_paused_run
from aicoding.daemon.run_orchestration import cancel_active_run
from aicoding.db.models import Session as DurableSession
from aicoding.db.models import CompiledSubtask, LogicalNodeCurrentVersion, NodeLifecycleState, NodeRun, NodeRunState, NodeVersion, ParentChildAuthority, SessionEvent, SubtaskAttempt
from aicoding.db.session import session_scope
from aicoding.daemon.versioning import create_superseding_node_version, cutover_candidate_version, initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from tests.helpers.session_harness import FakeClock


def _create_started_node(db_session_factory):
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Session Node", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admit_node_run(db_session_factory, node_id=node.node_id)
    return node


def test_bind_attach_resume_and_list_sessions(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    attached = attach_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    resumed = resume_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert bound.status == "BOUND"
    assert bound.logical_node_id == node.node_id
    assert bound.node_kind == "epic"
    assert bound.node_title == "Session Node"
    assert bound.run_status == "RUNNING"
    assert bound.tmux_session_name is not None
    assert bound.tmux_session_name.startswith("aicoding-pri-r1-")
    assert bound.tmux_session_exists is True
    assert bound.attach_command is None
    assert bound.recommended_action == "attach_existing_session"
    assert bound.cwd
    assert attached.session_id == bound.session_id
    assert resumed.session_id == bound.session_id
    assert resumed.recovery_classification == "healthy"
    assert len(catalog.sessions) == 1
    assert [item.event_type for item in events][:4] == ["bound", "attached", "recovery_attempted", "recovery_resumed_existing"]
    assert "launch_command" in events[0].payload_json
    assert events[0].payload_json["tmux_session_name"] == bound.tmux_session_name


def test_bind_primary_session_uses_authoritative_node_runtime_repo_when_present(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    monkeypatch.chdir(tmp_path)
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    with session_scope(db_session_factory) as session:
        current = session.get(LogicalNodeCurrentVersion, node.node_id)
        assert current is not None
        repo_path = repo_path_for_version(current.authoritative_node_version_id)
    repo_path.mkdir(parents=True, exist_ok=True)
    (repo_path / ".git").mkdir()

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert bound.cwd == str(repo_path)
    assert events[0].payload_json["cwd"] == str(repo_path)


def test_bind_primary_session_uses_stage_specific_layout_prompt_on_initial_bind(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "run_prompt"
        subtask.source_subtask_key = "generate_child_layout.render_layout_prompt"
        subtask.prompt_text = "Generate a child layout."

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    events = list_session_events(db_session_factory, session_id=bound.session_id)
    stage_prompt_event = next(
        item for item in reversed(events) if item.event_type in {"stage_prompt_pushed", "stage_prompt_queued"}
    )
    prompt_text = str(stage_prompt_event.payload_json.get("prompt_text", ""))

    assert "Read the full current-stage prompt from" in prompt_text
    assert "The daemon routed you to the layout-generation stage." in prompt_text
    assert "node register-layout --node" in prompt_text
    assert "subtask succeed --node" in prompt_text
    assert "Do not start by re-fetching `subtask prompt`" in prompt_text


def test_show_current_primary_session_reports_binding_metadata_and_stale_recovery(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    current = show_current_primary_session(db_session_factory, adapter=adapter, poller=poller)
    assert current is not None
    assert current.session_id == bound.session_id
    assert current.logical_node_id == node.node_id
    assert current.node_kind == "epic"
    assert current.node_title == "Session Node"
    assert current.run_status == "RUNNING"
    assert current.recovery_classification == "detached"
    assert current.recommended_action == "attach_existing_session"

    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    stale = show_current_primary_session(db_session_factory, adapter=adapter, poller=poller)

    assert stale is not None
    assert stale.session_id == bound.session_id
    assert stale.recovery_classification == "stale_but_recoverable"
    assert stale.recommended_action == "resume_existing_session"


def test_show_current_primary_session_ignores_superseded_version_session_after_cutover(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    cancel_active_run(db_session_factory, logical_node_id=node.node_id)
    candidate = create_superseding_node_version(db_session_factory, logical_node_id=node.node_id)
    cutover_candidate_version(db_session_factory, version_id=candidate.id, adapter=adapter)

    current = show_current_primary_session(db_session_factory, adapter=adapter, poller=poller)

    assert bound.node_version_id != candidate.id
    assert current is None
    assert bound.tmux_session_name is not None
    assert adapter.session_exists(bound.tmux_session_name) is False


def test_bind_primary_session_rejects_duplicate_active_primary_sessions(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    with session_scope(db_session_factory) as session:
        original = session.get(DurableSession, bound.session_id)
        assert original is not None
        duplicate = DurableSession(
            id=uuid4(),
            node_version_id=original.node_version_id,
            node_run_id=original.node_run_id,
            session_role="primary",
            provider=original.provider,
            provider_session_id="duplicate-provider",
            tmux_session_name="duplicate-session",
            cwd=original.cwd,
            status="BOUND",
            started_at=original.started_at,
            last_heartbeat_at=original.last_heartbeat_at,
        )
        session.add(duplicate)

    with pytest.raises(DaemonConflictError, match="duplicate active primary sessions detected"):
        bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)


def test_bind_primary_session_keeps_live_tmux_session_when_codex_ready_banner_is_missed(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    adapter.backend_name = "tmux"
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    from aicoding.errors import ConfigurationError

    def _raise_codex_not_ready(*args, **kwargs):
        raise ConfigurationError(message="Timed out waiting for Codex session readiness banner.", code="codex_not_ready")

    monkeypatch.setattr("aicoding.daemon.session_records.wait_for_codex_ready", _raise_codex_not_ready)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert bound.tmux_session_name is not None
    assert adapter.session_exists(bound.tmux_session_name) is True
    assert any(item.event_type == "codex_ready_pending" for item in events)
    assert [item.event_type for item in events if item.event_type == "codex_ready"] == []


def test_resume_replaces_missing_session(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    adapter.kill_session(bound.tmux_session_name or "")
    resumed = resume_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert resumed.session_id != bound.session_id
    assert resumed.recovery_classification == "lost"
    assert [item.status for item in catalog.sessions] == ["LOST", "RESUMED"]


def test_resume_replacement_cleans_up_preserved_dead_tmux_session(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    original_session_name = bound.tmux_session_name
    assert original_session_name is not None
    adapter.terminate_process(original_session_name, exit_status=12)

    resumed = resume_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    original_events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert resumed.session_id != bound.session_id
    assert adapter.session_exists(original_session_name) is False
    assert any(item.event_type == "tmux_session_cleaned" for item in original_events)


def test_auto_supervise_primary_sessions_replaces_missing_tracked_session(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    adapter.kill_session(bound.tmux_session_name or "")

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    latest_events = list_session_events(db_session_factory, session_id=catalog.sessions[-1].session_id)

    assert [item.status for item in catalog.sessions] == ["LOST", "RESUMED"]
    assert snapshots[0].status == "recovered"
    assert snapshots[0].action == "replacement_created"
    assert latest_events[-1].event_type == "supervision_recovery_succeeded"


def test_auto_supervise_primary_sessions_replaces_dead_tracked_tmux_process(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    adapter.terminate_process(bound.tmux_session_name or "", exit_status=23)

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    original_events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert [item.status for item in catalog.sessions] == ["LOST", "RESUMED"]
    assert snapshots[0].status == "recovered"
    assert snapshots[0].action == "replacement_created"
    assert any(
        item.event_type == "supervision_recovery_attempted"
        and item.payload_json["reason"] == "tracked_tmux_process_exited"
        and item.payload_json["tmux_process_alive"] is False
        and item.payload_json["tmux_exit_status"] == 23
        for item in original_events
    )


def test_auto_supervise_primary_sessions_replaces_session_when_codex_falls_back_to_shell(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    adapter.backend_name = "tmux"
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    session_name = bound.tmux_session_name or ""
    adapter._sessions[session_name].command = "/bin/bash -li"

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    original_events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert [item.status for item in catalog.sessions] == ["LOST", "RESUMED"]
    assert snapshots[0].status == "recovered"
    assert snapshots[0].action == "replacement_created"
    assert any(
        item.event_type == "supervision_recovery_attempted"
        and item.payload_json["reason"] == "tracked_codex_process_missing"
        and item.payload_json["tmux_process_command_line"] == "/bin/bash -li"
        for item in original_events
    )


def test_auto_supervise_primary_sessions_replaces_lost_paused_for_user_session(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    sync_paused_run(db_session_factory, logical_node_id=node.node_id, pause_flag_name="user_guidance_required")
    adapter.kill_session(bound.tmux_session_name or "")

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert [item.status for item in catalog.sessions] == ["LOST", "RESUMED"]
    assert snapshots[0].status == "recovered"
    assert snapshots[0].action == "replacement_created"


def test_auto_supervise_primary_sessions_fails_unrestartable_unfinished_run(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    sync_paused_run(db_session_factory, logical_node_id=node.node_id, pause_flag_name="manual_pause")
    with session_scope(db_session_factory) as session:
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        state = session.query(NodeRunState).one()
        assert lifecycle is not None
        lifecycle.lifecycle_state = "DRAFT"
        state.lifecycle_state = "DRAFT"
    adapter.kill_session(bound.tmux_session_name or "")

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    catalog = list_sessions_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).one()

    assert snapshots[0].status == "failed"
    assert snapshots[0].reason == "restart_not_allowed_for_lifecycle_state"
    assert catalog.sessions[0].status == "LOST"
    assert any(item.event_type == "supervision_recovery_failed" for item in events)
    assert run.run_status == "FAILED"
    assert state.lifecycle_state == "FAILED_TO_PARENT"


def test_recovery_status_distinguishes_stale_and_providerless_sessions(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    with session_scope(db_session_factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        durable.provider_session_id = None
    healthy = load_recovery_status(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    stale = load_recovery_status(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert healthy.recovery_classification == "detached"
    assert healthy.reason == "provider_identity_unavailable"
    assert healthy.provider_session_id_present is False
    assert stale.recovery_classification == "stale_but_recoverable"
    assert stale.recommended_action == "resume_existing_session"


def test_recovery_status_marks_preserved_dead_tmux_pane_as_lost(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    adapter.terminate_process(bound.tmux_session_name or "", exit_status=9)

    shown = get_session_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    recovery = load_recovery_status(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert shown.tmux_session_exists is True
    assert shown.tmux_process_alive is False
    assert shown.tmux_exit_status == 9
    assert shown.recovery_classification == "lost"
    assert shown.recommended_action == "create_replacement_session"
    assert shown.screen_state is None
    assert recovery.recovery_classification == "lost"
    assert recovery.reason == "tmux_process_exited"
    assert recovery.tmux_session_exists is True
    assert recovery.tmux_process_alive is False
    assert recovery.tmux_exit_status == 9


def test_provider_specific_recovery_rebinds_restorable_provider_session(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    original_session_name = bound.tmux_session_name
    assert original_session_name is not None

    with session_scope(db_session_factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        durable.tmux_session_name = "missing-session-name"

    provider_status = load_provider_recovery_status(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
    )
    decision = recover_primary_session_provider_specific(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert provider_status.provider_supported is True
    assert provider_status.provider_session_exists is True
    assert provider_status.provider_rebind_possible is True
    assert provider_status.provider_recommended_action == "rebind_provider_session"
    assert decision.status == "provider_session_rebound"
    assert decision.session is not None
    assert decision.session.session_id == bound.session_id
    assert decision.session.tmux_session_name == original_session_name
    assert decision.recovery_status.recovery_classification in {"healthy", "detached", "stale_but_recoverable"}
    assert [item.event_type for item in events][-2:] == ["provider_recovery_attempted", "provider_recovery_rebound"]


def test_auto_advance_incremental_parent_merge_and_refresh_children_runs_merge_prepass_and_refreshes_stale_children(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent_node_id = uuid4()
    stale_child_node_id = uuid4()
    ready_child_node_id = uuid4()
    stale_child_version_id = uuid4()
    merge_parent_version_id = uuid4()

    monkeypatch.setattr(
        "aicoding.daemon.session_records.process_pending_incremental_parent_merges",
        lambda session_factory: [
            SimpleNamespace(parent_node_version_id=merge_parent_version_id, child_node_version_id=uuid4(), status="merged")
        ],
    )
    monkeypatch.setattr(
        "aicoding.daemon.session_records._list_auto_run_child_candidate_pairs",
        lambda session_factory, hierarchy_registry, resources: [
            (parent_node_id, stale_child_node_id),
            (parent_node_id, ready_child_node_id),
        ],
    )

    refresh_calls: list[object] = []
    refreshed = {"done": False}

    def fake_check(session_factory, *, node_id):
        if node_id == stale_child_node_id and not refreshed["done"]:
            return SimpleNamespace(
                status="blocked",
                node_version_id=stale_child_version_id,
                blockers=[SimpleNamespace(blocker_kind="blocked_on_parent_refresh")],
            )
        return SimpleNamespace(status="ready", node_version_id=uuid4(), blockers=[])

    def fake_refresh(session_factory, *, child_version_id):
        refresh_calls.append(child_version_id)
        refreshed["done"] = True
        return SimpleNamespace()

    monkeypatch.setattr("aicoding.daemon.session_records.check_node_dependency_readiness", fake_check)
    monkeypatch.setattr("aicoding.daemon.session_records.refresh_child_live_git_from_parent_head", fake_refresh)
    monkeypatch.setattr("aicoding.daemon.session_records.transition_node_lifecycle", lambda *args, **kwargs: SimpleNamespace())

    snapshot = auto_advance_incremental_parent_merge_and_refresh_children(
        db_session_factory,
        hierarchy_registry=registry,
        resources=catalog,
    )

    assert snapshot.processed_merge_count == 1
    assert snapshot.refreshed_child_node_ids == [stale_child_node_id]
    assert refresh_calls == [stale_child_version_id]


def test_auto_advance_incremental_parent_merge_transitions_fresh_restart_child_to_ready_after_refresh(
    monkeypatch, db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent_node_id = uuid4()
    stale_child_node_id = uuid4()
    stale_child_version_id = uuid4()

    monkeypatch.setattr(
        "aicoding.daemon.session_records.process_pending_incremental_parent_merges",
        lambda session_factory: [SimpleNamespace(parent_node_version_id=uuid4(), child_node_version_id=uuid4(), status="merged")],
    )
    monkeypatch.setattr(
        "aicoding.daemon.session_records._list_auto_run_child_candidate_pairs",
        lambda session_factory, hierarchy_registry, resources: [(parent_node_id, stale_child_node_id)],
    )

    refresh_calls: list[object] = []
    transition_calls: list[tuple[str, str]] = []
    readiness_sequence = iter(
        [
            SimpleNamespace(
                status="blocked",
                node_version_id=stale_child_version_id,
                blockers=[SimpleNamespace(blocker_kind="blocked_on_parent_refresh")],
            ),
            SimpleNamespace(
                status="blocked",
                node_version_id=stale_child_version_id,
                blockers=[SimpleNamespace(blocker_kind="lifecycle_not_ready")],
            ),
            SimpleNamespace(status="ready", node_version_id=stale_child_version_id, blockers=[]),
        ]
    )

    def fake_check(session_factory, *, node_id):
        assert node_id == stale_child_node_id
        return next(readiness_sequence)

    def fake_refresh(session_factory, *, child_version_id):
        refresh_calls.append(child_version_id)
        return SimpleNamespace()

    def fake_transition(session_factory, *, node_id, target_state):
        transition_calls.append((node_id, target_state))
        return SimpleNamespace()

    monkeypatch.setattr("aicoding.daemon.session_records.check_node_dependency_readiness", fake_check)
    monkeypatch.setattr("aicoding.daemon.session_records.refresh_child_live_git_from_parent_head", fake_refresh)
    monkeypatch.setattr("aicoding.daemon.session_records._maybe_rematerialize_dependency_invalidated_child", lambda *args, **kwargs: True)
    monkeypatch.setattr("aicoding.daemon.session_records.transition_node_lifecycle", fake_transition)

    snapshot = auto_advance_incremental_parent_merge_and_refresh_children(
        db_session_factory,
        hierarchy_registry=registry,
        resources=catalog,
    )

    assert snapshot.processed_merge_count == 1
    assert snapshot.refreshed_child_node_ids == [stale_child_node_id]
    assert refresh_calls == [stale_child_version_id]
    assert transition_calls == [(str(stale_child_node_id), "READY")]


def test_auto_advance_incremental_parent_merge_keeps_manual_fresh_restart_child_blocked_after_refresh(
    monkeypatch, db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent_node_id = uuid4()
    stale_child_node_id = uuid4()
    stale_child_version_id = uuid4()

    monkeypatch.setattr(
        "aicoding.daemon.session_records.process_pending_incremental_parent_merges",
        lambda session_factory: [SimpleNamespace(parent_node_version_id=uuid4(), child_node_version_id=uuid4(), status="merged")],
    )
    monkeypatch.setattr(
        "aicoding.daemon.session_records._list_auto_run_child_candidate_pairs",
        lambda session_factory, hierarchy_registry, resources: [(parent_node_id, stale_child_node_id)],
    )

    refresh_calls: list[object] = []
    transition_calls: list[tuple[str, str]] = []
    readiness_sequence = iter(
        [
            SimpleNamespace(
                status="blocked",
                node_version_id=stale_child_version_id,
                blockers=[SimpleNamespace(blocker_kind="blocked_on_parent_refresh")],
            ),
            SimpleNamespace(
                status="blocked",
                node_version_id=stale_child_version_id,
                blockers=[
                    SimpleNamespace(blocker_kind="child_tree_rebuild_required"),
                    SimpleNamespace(blocker_kind="lifecycle_not_ready"),
                ],
            ),
        ]
    )

    def fake_check(session_factory, *, node_id):
        assert node_id == stale_child_node_id
        return next(readiness_sequence)

    def fake_refresh(session_factory, *, child_version_id):
        refresh_calls.append(child_version_id)
        return SimpleNamespace()

    def fake_transition(session_factory, *, node_id, target_state):
        transition_calls.append((node_id, target_state))
        return SimpleNamespace()

    monkeypatch.setattr("aicoding.daemon.session_records.check_node_dependency_readiness", fake_check)
    monkeypatch.setattr("aicoding.daemon.session_records.refresh_child_live_git_from_parent_head", fake_refresh)
    monkeypatch.setattr("aicoding.daemon.session_records._maybe_rematerialize_dependency_invalidated_child", lambda *args, **kwargs: False)
    monkeypatch.setattr("aicoding.daemon.session_records.transition_node_lifecycle", fake_transition)

    snapshot = auto_advance_incremental_parent_merge_and_refresh_children(
        db_session_factory,
        hierarchy_registry=registry,
        resources=catalog,
    )

    assert snapshot.processed_merge_count == 1
    assert snapshot.refreshed_child_node_ids == [stale_child_node_id]
    assert refresh_calls == [stale_child_version_id]
    assert transition_calls == []


def test_maybe_rematerialize_dependency_invalidated_child_rebuilds_empty_layout_tree(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    right = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(right.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=right.node_id)

    first_materialization = materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=right.node_id,
    )
    assert first_materialization.child_count > 0

    fresh = create_superseding_node_version(
        db_session_factory,
        logical_node_id=right.node_id,
        clone_structure=False,
    )
    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, right.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        fresh_version = session.get(NodeVersion, fresh.id)
        assert old_version is not None
        assert fresh_version is not None
        old_version.status = "superseded"
        fresh_version.status = "authoritative"
        selector.authoritative_node_version_id = fresh.id
        selector.latest_created_node_version_id = fresh.id
        session.flush()
    _record_rebuild_event(
        db_session_factory,
        root_logical_node_id=right.node_id,
        root_node_version_id=fresh.id,
        target_node_version_id=fresh.id,
        event_kind="candidate_created",
        event_status="pending",
        scope="subtree",
        trigger_reason="test_fresh_dependency_restart",
        details_json={"supersedes_node_version_id": str(first_materialization.parent_node_version_id), "fresh_dependency_restart": True},
    )

    rematerialized = _maybe_rematerialize_dependency_invalidated_child(
        db_session_factory,
        logical_node_id=right.node_id,
        node_version_id=fresh.id,
        hierarchy_registry=registry,
        resources=catalog,
    )
    inspected = inspect_materialized_children(
        db_session_factory,
        catalog,
        logical_node_id=right.node_id,
    )

    assert rematerialized is True
    assert inspected.parent_node_version_id == fresh.id
    assert inspected.child_count > 0


def test_maybe_rematerialize_dependency_invalidated_child_resets_placeholder_manual_authority(
    db_session_factory, migrated_public_schema
) -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    parent = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent", prompt="p")
    seed_node_lifecycle(db_session_factory, node_id=str(parent.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=parent.node_id)
    right = create_hierarchy_node(db_session_factory, registry, kind="phase", title="Right", prompt="right", parent_node_id=parent.node_id)
    seed_node_lifecycle(db_session_factory, node_id=str(right.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=right.node_id)

    first_materialization = materialize_layout_children(
        db_session_factory,
        registry,
        catalog,
        logical_node_id=right.node_id,
    )
    assert first_materialization.child_count > 0

    fresh = create_superseding_node_version(
        db_session_factory,
        logical_node_id=right.node_id,
        clone_structure=False,
    )
    with session_scope(db_session_factory) as session:
        selector = session.get(LogicalNodeCurrentVersion, right.node_id)
        assert selector is not None
        old_version = session.get(NodeVersion, selector.authoritative_node_version_id)
        fresh_version = session.get(NodeVersion, fresh.id)
        assert old_version is not None
        assert fresh_version is not None
        old_version.status = "superseded"
        fresh_version.status = "authoritative"
        selector.authoritative_node_version_id = fresh.id
        selector.latest_created_node_version_id = fresh.id
        session.add(
            ParentChildAuthority(
                parent_node_version_id=fresh.id,
                authority_mode="manual",
                authoritative_layout_hash=None,
            )
        )
        session.flush()
    _record_rebuild_event(
        db_session_factory,
        root_logical_node_id=right.node_id,
        root_node_version_id=fresh.id,
        target_node_version_id=fresh.id,
        event_kind="candidate_created",
        event_status="pending",
        scope="subtree",
        trigger_reason="test_fresh_dependency_restart",
        details_json={"supersedes_node_version_id": str(first_materialization.parent_node_version_id), "fresh_dependency_restart": True},
    )

    rematerialized = _maybe_rematerialize_dependency_invalidated_child(
        db_session_factory,
        logical_node_id=right.node_id,
        node_version_id=fresh.id,
        hierarchy_registry=registry,
        resources=catalog,
    )
    inspected = inspect_materialized_children(
        db_session_factory,
        catalog,
        logical_node_id=right.node_id,
    )

    assert rematerialized is True
    assert inspected.authority_mode == "layout_authoritative"
    assert inspected.child_count > 0


def test_screen_classifier_distinguishes_active_quiet_and_idle(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    first = inspect_primary_session_screen_state(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        persist=True,
    )
    quiet = inspect_primary_session_screen_state(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        persist=True,
    )
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    idle = inspect_primary_session_screen_state(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        persist=True,
    )
    adapter.set_alt_screen(bound.tmux_session_name or "", True)
    alt_screen = inspect_primary_session_screen_state(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        persist=True,
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert first.classification == "active"
    assert first.reason == "first_sample"
    assert quiet.classification == "quiet"
    assert quiet.reason == "unchanged_screen_within_threshold"
    assert idle.classification == "idle"
    assert idle.reason == "unchanged_screen_past_idle_threshold"
    assert alt_screen.classification == "idle"
    assert alt_screen.reason == "unchanged_screen_past_idle_threshold"
    assert [item.event_type for item in events if item.event_type == "screen_polled"] == ["screen_polled"] * 4


def test_recover_primary_session_rejects_non_resumable_run(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    with session_scope(db_session_factory) as session:
        state = session.query(NodeRunState).one()
        state.is_resumable = False

    decision = recover_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert decision.status == "recovery_rejected"
    assert decision.recovery_status.recovery_classification == "non_resumable"
    assert decision.session is None


def test_nudge_primary_session_skips_recent_sessions_and_allows_idle_alt_screen_sessions(
    db_session_factory, migrated_public_schema
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    recent = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle",
        repeated_nudge_text="repeat",
    )
    adapter.set_alt_screen(bound.tmux_session_name or "", True)
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    alt_screen_idle = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle",
        repeated_nudge_text="repeat",
    )

    assert recent.status == "not_idle"
    assert recent.action == "none"
    assert recent.screen_state is not None
    assert recent.screen_state["classification"] in {"active", "quiet"}
    assert alt_screen_idle.status == "nudged"
    assert alt_screen_idle.in_alt_screen is True
    assert alt_screen_idle.screen_state is not None
    assert alt_screen_idle.screen_state["classification"] == "idle"
    assert alt_screen_idle.screen_state["reason"] == "unchanged_screen_past_idle_threshold"


def test_nudge_primary_session_uses_repeated_prompt_then_escalates(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    first = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    second = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    escalated = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert first.status == "nudged"
    assert first.prompt_relative_path == "recovery/idle_nudge.md"
    assert first.screen_state is not None
    assert first.screen_state["classification"] == "idle"
    assert second.status == "nudged"
    assert second.prompt_relative_path == "recovery/repeated_missed_step.md"
    assert escalated.status == "escalated_to_pause"
    assert escalated.pause_flag_name == "idle_nudge_limit_exceeded"
    assert [item.event_type for item in events if item.event_type in {"nudged", "nudge_escalated"}] == ["nudged", "nudged", "nudge_escalated"]


def test_nudge_primary_session_skips_idle_recovery_when_stage_prompt_is_still_queued(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None
    adapter.backend_name = "tmux"

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        compiled_subtask_id = state.current_compiled_subtask_id
        subtask = session.get(CompiledSubtask, compiled_subtask_id)
        assert compiled_subtask_id is not None
        assert subtask is not None

    adapter._sessions[bound.tmux_session_name].pane_text = "• Working (28s • esc to interrupt)\n"
    push_or_queue_primary_session_stage_prompt(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        prompt_text="Read the full task prompt from `prompt.md`.",
        compiled_subtask_id=compiled_subtask_id,
        prompt_source="file",
        source_subtask_key=subtask.source_subtask_key,
        subtask_type=subtask.subtask_type,
        initial_instruction_target="prompt.md",
    )

    adapter.backend_name = "tmux"
    adapter._sessions[bound.tmux_session_name].pane_text = ""
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "pending_stage_prompt"
    assert result.action == "none"
    assert "idle prompt" not in pane_text
    assert [item.event_type for item in events if item.event_type == "nudged"] == []
    assert [item.payload_json.get("reason") for item in events if item.event_type == "nudge_skipped"][-1] == "pending_stage_prompt"


def test_nudge_primary_session_waits_for_codex_ready_before_idle_recovery(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        events = (
            session.query(SessionEvent)
            .filter(
                SessionEvent.session_id == durable.id,
                SessionEvent.event_type.in_(("codex_ready", "stage_prompt_pushed", "stage_prompt_queued")),
            )
            .all()
        )
        for event in events:
            session.delete(event)

    adapter.backend_name = "tmux"
    adapter._sessions[bound.tmux_session_name].pane_text = ""
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "awaiting_codex_ready"
    assert result.action == "none"
    assert "idle prompt" not in pane_text
    assert [item.event_type for item in events if item.event_type == "nudged"] == []
    assert [item.payload_json.get("reason") for item in events if item.event_type == "nudge_skipped"][-1] == "awaiting_codex_ready"


def test_nudge_primary_session_recovers_missing_codex_ready_from_visible_banner(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        events = (
            session.query(SessionEvent)
            .filter(
                SessionEvent.session_id == durable.id,
                SessionEvent.event_type.in_(("codex_ready", "stage_prompt_pushed", "stage_prompt_queued")),
            )
            .all()
        )
        for event in events:
            session.delete(event)

    adapter.backend_name = "tmux"
    adapter._sessions[bound.tmux_session_name].pane_text = "OpenAI Codex\n>_\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)
    pane_text = adapter.capture_pane(bound.tmux_session_name, include_alt_screen=True)

    assert result.status != "awaiting_codex_ready"
    assert any(item.event_type == "codex_ready" for item in events)
    assert "Current hook-stage action:" in pane_text or "idle prompt" in pane_text


def test_nudge_primary_session_reseeds_missing_stage_prompt_and_restarts_missing_attempt(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        durable = session.get(DurableSession, bound.session_id)
        assert durable is not None
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        session.query(SubtaskAttempt).filter(SubtaskAttempt.node_run_id == run.id).delete(synchronize_session=False)
        session.query(SessionEvent).filter(
            SessionEvent.session_id == durable.id,
            SessionEvent.event_type.in_(("stage_prompt_pushed", "stage_prompt_queued")),
        ).delete(synchronize_session=False)
        state.current_subtask_attempt = None

    adapter.backend_name = "tmux"
    adapter._sessions[bound.tmux_session_name].pane_text = "OpenAI Codex\n>_\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        attempt = (
            session.query(SubtaskAttempt)
            .filter(
                SubtaskAttempt.node_run_id == run.id,
                SubtaskAttempt.compiled_subtask_id == state.current_compiled_subtask_id,
            )
            .order_by(SubtaskAttempt.attempt_number.desc())
            .first()
        )

    assert result.status in {"stage_prompt_seeded", "pending_stage_prompt"}
    assert any(item.event_type in {"stage_prompt_pushed", "stage_prompt_queued"} for item in events)
    assert attempt is not None
    assert attempt.status == "RUNNING"
    assert state.current_subtask_attempt == attempt.attempt_number


def test_nudge_primary_session_skips_recently_pushed_stage_prompt_grace_window(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    adapter._sessions[bound.tmux_session_name].pane_text = "OpenAI Codex\n>_\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=15.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert result.status == "recent_stage_prompt_grace"
    assert result.action == "none"
    assert [item.event_type for item in events if item.event_type == "nudged"] == []
    assert [item.payload_json.get("reason") for item in events if item.event_type == "nudge_skipped"][-1] == "recent_stage_prompt_grace"

    adapter.advance_idle(bound.tmux_session_name, seconds=20.0)
    later = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )

    assert later.status == "nudged"
    assert later.prompt_relative_path == "recovery/idle_nudge.md"


def test_nudge_primary_session_skips_already_paused_run_after_idle_escalation(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=0,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    paused = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=0,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert paused.status == "run_paused"
    assert paused.pause_flag_name == "idle_nudge_limit_exceeded"
    assert [item.event_type for item in events if item.event_type in {"nudge_escalated", "nudge_skipped"}][-1] == "nudge_skipped"


def test_nudge_primary_session_does_not_pause_wait_for_children_while_child_is_running(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    monkeypatch.setattr(
        "aicoding.daemon.session_records._current_subtask_for_recovery",
        lambda session, compiled_subtask_id: SimpleNamespace(
            subtask_type="wait_for_children",
            id=uuid4(),
            source_subtask_key="wait_for_children.wait_for_child_completion",
        ),
    )
    monkeypatch.setattr(
        "aicoding.daemon.session_records._wait_stage_active_children",
        lambda session, logical_node_id: [
            {
                "node_id": str(uuid4()),
                "title": "Running Child",
                "kind": "task",
                "lifecycle_state": "RUNNING",
                "run_status": "RUNNING",
            }
        ],
    )

    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)
    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=0,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert result.status == "waiting_on_children"
    assert result.action == "none"
    assert result.pause_flag_name is None
    assert [item.event_type for item in events if item.event_type == "nudge_escalated"] == []
    assert [item.payload_json.get("reason") for item in events if item.event_type == "nudge_skipped"][-1] == "waiting_on_children"


def test_nudge_primary_session_wait_for_children_treats_paused_child_as_terminal_blocker(
    db_session_factory,
    migrated_public_schema,
    monkeypatch,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    monkeypatch.setattr(
        "aicoding.daemon.session_records._current_subtask_for_recovery",
        lambda session, compiled_subtask_id: SimpleNamespace(
            subtask_type="wait_for_children",
            id=uuid4(),
            source_subtask_key="wait_for_children.wait_for_child_completion",
        ),
    )
    monkeypatch.setattr(
        "aicoding.daemon.session_records._wait_stage_active_children",
        lambda session, logical_node_id: [],
    )

    adapter._sessions[bound.tmux_session_name or ""].pane_text = "• Waited for background terminal\n"
    adapter.advance_idle(bound.tmux_session_name or "", seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name or "")

    assert result.status == "nudged"
    assert "Current child-wait action:" in pane_text
    assert "PAUSED_FOR_USER" in pane_text
    assert "subtask fail" in pane_text
    assert "instead of waiting forever" in pane_text
    assert "do not run `subtask succeed`" in pane_text
    assert "`subtask fail" in pane_text and "then run `python3 -m aicoding.cli.main subtask succeed" not in pane_text


def test_nudge_primary_session_uses_layout_generation_action_guidance(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "run_prompt"
        subtask.source_subtask_key = "generate_child_layout.render_layout_prompt"
        subtask.prompt_text = "Generate a child layout."

    adapter._sessions[bound.tmux_session_name].pane_text = "• Waited for background terminal\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "nudged"
    assert "Current layout-generation action:" in pane_text
    assert f"write `layouts/generated/{node.node_id}.yaml` now" in pane_text
    assert f"node register-layout --node {node.node_id} --file layouts/generated/{node.node_id}.yaml" in pane_text
    assert f"subtask succeed --node {node.node_id}" in pane_text
    assert "do not fetch `subtask prompt` again" in pane_text


def test_nudge_primary_session_reseeds_missing_stage_prompt_after_codex_ready(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "run_prompt"
        subtask.source_subtask_key = "generate_child_layout.render_layout_prompt"
        subtask.prompt_text = "Generate a child layout."
        session.query(SessionEvent).filter(
            SessionEvent.session_id == bound.session_id,
            SessionEvent.event_type.in_(("stage_prompt_pushed", "stage_prompt_queued")),
        ).delete(synchronize_session=False)

    adapter._sessions[bound.tmux_session_name].pane_text = "OpenAI Codex\n>_\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name)
    events = list_session_events(db_session_factory, session_id=bound.session_id)

    assert result.status == "stage_prompt_seeded"
    assert "The daemon routed you to the layout-generation stage." in pane_text
    assert "idle prompt" not in pane_text
    assert any(item.event_type == "stage_prompt_pushed" for item in events)


def test_nudge_primary_session_uses_compiled_task_review_prompt(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "review"
        subtask.source_subtask_key = "review_node.review_current_output"
        subtask.prompt_text = (
            "Review the current node output against its requirements.\n\n"
            "Record the judgment through the CLI:\n"
            f"- `python3 -m aicoding.cli.main review run --node {node.node_id} --status pass --summary \"Approved the current node output.\"`\n"
        )

    adapter._sessions[bound.tmux_session_name].pane_text = "• Waited for background terminal\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "nudged"
    assert "Current review-stage action:" in pane_text
    assert "Review the current node output against its requirements." in pane_text
    assert "Approved the current node output." in pane_text
    assert "Approved the generated layout." not in pane_text


def test_nudge_primary_session_review_prompt_resolves_current_compiled_subtask_token(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "review"
        subtask.source_subtask_key = "review_child_layout.review_layout"
        subtask.prompt_text = (
            "Review the generated layout and submit the decision through the CLI:\n"
            f"- `python3 -m aicoding.cli.main review run --node {node.node_id} --compiled-subtask CURRENT_COMPILED_SUBTASK_ID --status pass --summary \"Approved the generated layout.\"`\n"
        )
        expected_subtask_id = str(subtask.id)

    adapter._sessions[bound.tmux_session_name].pane_text = "• Waited for background terminal\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "nudged"
    assert "Current review-stage action:" in pane_text
    assert "CURRENT_COMPILED_SUBTASK_ID" not in pane_text
    assert f"--compiled-subtask {expected_subtask_id}" in pane_text


def test_nudge_primary_session_rolls_child_summaries_without_sleep_polling(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    assert bound.tmux_session_name is not None

    with session_scope(db_session_factory) as session:
        run = session.query(NodeRun).one()
        state = session.query(NodeRunState).filter_by(node_run_id=run.id).one()
        subtask = session.get(CompiledSubtask, state.current_compiled_subtask_id)
        assert subtask is not None
        subtask.subtask_type = "build_context"
        subtask.source_subtask_key = "wait_for_children.collect_child_summaries"
        subtask.prompt_text = "Collect child summaries after the direct children have already completed."

    adapter._sessions[bound.tmux_session_name].pane_text = "• Waited for background terminal\n"
    adapter.advance_idle(bound.tmux_session_name, seconds=30.0)

    result = nudge_primary_session(
        db_session_factory,
        logical_node_id=node.node_id,
        adapter=adapter,
        poller=poller,
        max_nudge_count=2,
        idle_nudge_text="idle prompt",
        repeated_nudge_text="repeat prompt",
    )
    pane_text = adapter.capture_pane(bound.tmux_session_name)

    assert result.status == "nudged"
    assert "Current child-summary rollup action:" in pane_text
    assert "do not run `sleep` or a polling loop" in pane_text
    assert "tree show --node" in pane_text
    assert "summaries/child_rollup.md" in pane_text


def test_render_recovery_prompt_includes_live_prompt_command() -> None:
    node_id = uuid4()

    rendered = _render_recovery_prompt(
        "Fetch `{{prompt.cli_command}}` for node `{{node_id}}`.",
        logical_node_id=node_id,
    )

    assert f"subtask prompt --node {node_id}" in rendered
    assert "{{prompt.cli_command}}" not in rendered


def test_failed_supervision_run_remains_inspectable_through_session_and_recovery_reads(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)

    bound = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    sync_paused_run(db_session_factory, logical_node_id=node.node_id, pause_flag_name="manual_pause")
    with session_scope(db_session_factory) as session:
        lifecycle = session.get(NodeLifecycleState, str(node.node_id))
        state = session.query(NodeRunState).one()
        assert lifecycle is not None
        lifecycle.lifecycle_state = "DRAFT"
        state.lifecycle_state = "DRAFT"
    adapter.kill_session(bound.tmux_session_name or "")

    snapshots = auto_supervise_primary_sessions(db_session_factory, adapter=adapter, poller=poller)
    shown = get_session_for_node(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    recovery = load_recovery_status(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    decision = recover_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    assert snapshots[0].status == "failed"
    assert shown.session_id == bound.session_id
    assert shown.run_status == "FAILED"
    assert shown.recovery_classification == "non_resumable"
    assert shown.recommended_action == "inspect_failed_run"
    assert shown.terminal_failure is not None
    assert shown.terminal_failure["failure_origin"] == "session_supervision"
    assert shown.terminal_failure["failure_reason"] == "restart_not_allowed_for_lifecycle_state"
    assert recovery.recovery_classification == "non_resumable"
    assert recovery.recommended_action == "inspect_failed_run"
    assert recovery.terminal_failure is not None
    assert recovery.terminal_failure["failed_session_id"] == str(bound.session_id)
    assert decision.status == "recovery_rejected"
    assert decision.session is not None
    assert decision.session.terminal_failure is not None
