from __future__ import annotations

from pathlib import Path
import tempfile
import time
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


def test_tmux_session_adapter_injects_environment_over_existing_tmux_server() -> None:
    adapter = TmuxSessionAdapter()
    server_session_name = f"aicoding-server-{uuid4().hex[:8]}"
    session_name = f"aicoding-env-{uuid4().hex[:8]}"
    output_path = Path(tempfile.gettempdir()) / f"{session_name}.txt"
    command = f"bash -lc 'printf %s \"$AICODING_TMP_TEST_VAR\" > {output_path}'"
    try:
        adapter.create_session(server_session_name, "bash", ".")
        adapter.create_session(
            session_name,
            command,
            ".",
            environment={"AICODING_TMP_TEST_VAR": "expected-from-plan"},
        )
        for _ in range(20):
            if output_path.exists() and output_path.read_text(encoding="utf-8"):
                break
            time.sleep(0.1)
        assert output_path.read_text(encoding="utf-8") == "expected-from-plan"
    finally:
        adapter.kill_session(session_name)
        adapter.kill_session(server_session_name)
        output_path.unlink(missing_ok=True)
