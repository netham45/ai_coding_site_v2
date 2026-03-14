from __future__ import annotations

from pathlib import Path
import pytest

from aicoding.daemon.child_sessions import load_child_session_result, pop_child_session, push_child_session
from aicoding.daemon.errors import DaemonConflictError
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.run_orchestration import load_current_run_progress, load_current_subtask_context
from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller
from aicoding.daemon.session_manager import build_child_session_plan
from aicoding.daemon.session_records import bind_primary_session, list_session_events
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from tests.helpers.session_harness import FakeClock


def _create_started_node(db_session_factory):
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    node = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Child Session Node", prompt="boot prompt")
    seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
    initialize_node_version(db_session_factory, logical_node_id=node.node_id)
    compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=catalog)
    transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
    from aicoding.daemon.admission import admit_node_run

    admit_node_run(db_session_factory, node_id=node.node_id)
    return node


def test_push_and_pop_child_session_attach_result_to_parent_context(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    parent = bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)

    child = push_child_session(
        db_session_factory,
        logical_node_id=node.node_id,
        reason="research_context",
        adapter=adapter,
        poller=poller,
        delegated_prompt_text="delegated prompt",
        delegated_prompt_path="runtime/delegated_child_session.md",
    )
    result = pop_child_session(
        db_session_factory,
        child_session_id=child.session_id,
        result_payload={
            "status": "success",
            "summary": "bounded research done",
            "findings": ["fact one"],
            "artifacts": [{"path": "notes/research.md", "type": "notes"}],
            "suggested_next_actions": ["continue"],
        },
    )
    context = load_current_subtask_context(db_session_factory, logical_node_id=node.node_id)
    events = list_session_events(db_session_factory, session_id=child.session_id)
    loaded = load_child_session_result(db_session_factory, child_session_id=child.session_id)

    assert child.parent_session_id == parent.session_id
    assert child.parent_compiled_subtask_id == progress.state.current_compiled_subtask_id
    assert result.status == "success"
    assert loaded.summary == "bounded research done"
    assert context.compiled_subtask_id == progress.state.current_compiled_subtask_id
    assert context.input_context_json["child_session_results"][0]["child_session_id"] == str(child.session_id)
    assert [item.event_type for item in events] == [
        "child_pushed",
        "child_codex_ready",
        "child_prompt_pushed",
        "child_popped",
    ]


def test_push_child_session_renders_live_node_context_into_delegated_prompt(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    child = push_child_session(
        db_session_factory,
        logical_node_id=node.node_id,
        reason="research_context",
        adapter=adapter,
        poller=poller,
        delegated_prompt_text="Delegated prompt for {{node_id}} and {{node.id}}",
        delegated_prompt_path="runtime/delegated_child_session.md",
    )
    launch_plan = build_child_session_plan(parent_session_id=child.parent_session_id, session_id=child.session_id)

    assert launch_plan.prompt_log_path is not None
    prompt_text = Path(launch_plan.prompt_log_path).read_text(encoding="utf-8")
    assert str(node.node_id) in prompt_text
    assert "{{node_id}}" not in prompt_text
    assert "{{node.id}}" not in prompt_text


def test_push_child_session_injects_prompt_file_instruction_without_immediate_prompt_refetch(
    db_session_factory,
    migrated_public_schema,
) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)

    child = push_child_session(
        db_session_factory,
        logical_node_id=node.node_id,
        reason="research_context",
        adapter=adapter,
        poller=poller,
        delegated_prompt_text="delegated prompt",
        delegated_prompt_path="runtime/delegated_child_session.md",
    )

    assert child.tmux_session_name is not None
    pane_text = adapter.capture_pane(child.tmux_session_name)
    assert "Read the full task prompt from `" in pane_text
    assert "Do not start by re-fetching `subtask prompt`" in pane_text


def test_pop_child_session_rejects_invalid_payload(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    child = push_child_session(
        db_session_factory,
        logical_node_id=node.node_id,
        reason="review_check",
        adapter=adapter,
        poller=poller,
        delegated_prompt_text="delegated prompt",
        delegated_prompt_path="runtime/delegated_child_session.md",
    )

    with pytest.raises(DaemonConflictError):
        pop_child_session(
            db_session_factory,
            child_session_id=child.session_id,
            result_payload={"status": "invalid", "summary": ""},
        )


def test_pop_child_session_cleans_up_tmux_session_when_adapter_is_provided(db_session_factory, migrated_public_schema) -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)
    node = _create_started_node(db_session_factory)
    bind_primary_session(db_session_factory, logical_node_id=node.node_id, adapter=adapter, poller=poller)
    child = push_child_session(
        db_session_factory,
        logical_node_id=node.node_id,
        reason="research_context",
        adapter=adapter,
        poller=poller,
        delegated_prompt_text="delegated prompt",
        delegated_prompt_path="runtime/delegated_child_session.md",
    )
    session_name = child.tmux_session_name
    assert session_name is not None

    pop_child_session(
        db_session_factory,
        child_session_id=child.session_id,
        result_payload={"status": "success", "summary": "done"},
        adapter=adapter,
    )

    assert adapter.session_exists(session_name) is False
