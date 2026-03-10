from __future__ import annotations

import pytest
from uuid import uuid4

from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller
from aicoding.daemon.session_records import (
    attach_primary_session,
    bind_primary_session,
    inspect_primary_session_screen_state,
    load_provider_recovery_status,
    load_recovery_status,
    list_session_events,
    list_sessions_for_node,
    nudge_primary_session,
    recover_primary_session_provider_specific,
    recover_primary_session,
    resume_primary_session,
    show_current_primary_session,
)
from aicoding.db.models import Session as DurableSession
from aicoding.db.models import NodeRunState
from aicoding.db.session import session_scope
from aicoding.daemon.versioning import initialize_node_version
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
    assert alt_screen.classification == "quiet"
    assert alt_screen.reason == "alt_screen_active"
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


def test_nudge_primary_session_skips_recent_or_alt_screen_sessions(db_session_factory, migrated_public_schema) -> None:
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
    alt_screen = nudge_primary_session(
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
    assert alt_screen.status == "suppressed_alt_screen"
    assert alt_screen.in_alt_screen is True
    assert alt_screen.screen_state is not None
    assert alt_screen.screen_state["reason"] == "alt_screen_active"


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
