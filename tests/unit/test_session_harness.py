from __future__ import annotations

from uuid import uuid4

from aicoding.daemon.session_harness import FakeSessionAdapter, SessionPoller, TmuxSessionAdapter
from tests.helpers.session_harness import FakeClock


def test_fake_session_adapter_creates_and_lists_sessions() -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)

    snapshot = adapter.create_session("node-1", "printf 'ready'", ".")

    assert snapshot.backend == "fake"
    assert adapter.list_sessions() == ["node-1"]
    assert adapter.session_exists("node-1") is True


def test_fake_session_adapter_alt_screen_capture_hook_is_deterministic() -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    adapter.create_session("node-1", "printf 'ready'", ".")
    adapter.set_alt_screen("node-1", True)

    assert adapter.capture_pane("node-1") == ""
    assert adapter.capture_pane("node-1", include_alt_screen=True)


def test_session_poller_detects_idle_state_deterministically() -> None:
    clock = FakeClock()
    adapter = FakeSessionAdapter(now=clock.now)
    adapter.create_session("node-1", "printf 'ready'", ".")
    poller = SessionPoller(adapter=adapter, idle_threshold_seconds=10.0, now=clock.now)

    clock.advance(seconds=15)
    result = poller.poll("node-1")

    assert result.is_idle is True
    assert result.idle_seconds >= 15


def test_tmux_session_adapter_smoke_lifecycle() -> None:
    adapter = TmuxSessionAdapter()
    session_name = f"aicoding-test-{uuid4().hex[:8]}"
    try:
        snapshot = adapter.create_session(session_name, "bash", ".")
        adapter.send_input(session_name, "printf 'ready'")
        captured = adapter.capture_pane(session_name, include_alt_screen=True)

        assert snapshot.backend == "tmux"
        assert snapshot.command
        assert snapshot.working_directory
        assert adapter.session_exists(session_name) is True
        assert "ready" in captured
    finally:
        adapter.kill_session(session_name)
