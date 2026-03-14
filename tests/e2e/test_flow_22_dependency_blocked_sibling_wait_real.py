from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest

PARENT_SIBLING_CREATION_TIMEOUT_SECONDS = 900.0
CHILD_COMPLETION_TIMEOUT_SECONDS = 1800.0
DEPENDENCY_UNBLOCK_TIMEOUT_SECONDS = 60.0


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux capture failed for {session_name}: {result.stderr.strip()}]"
    return result.stdout


def _write_cat_workspace_fixture(workspace_root: Path) -> None:
    src_dir = workspace_root / "src"
    tests_dir = workspace_root / "tests"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "cat_clone.py").write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "import sys",
                "",
                "",
                "def main(argv: list[str] | None = None) -> int:",
                "    raise NotImplementedError('implement me')",
                "",
                "",
                "if __name__ == '__main__':",
                "    raise SystemExit(main())",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    (tests_dir / "test_cat_clone.py").write_text(
        "\n".join(
            [
                "from __future__ import annotations",
                "",
                "from pathlib import Path",
                "import subprocess",
                "import sys",
                "",
                "",
                "def _run_cat(*paths: Path) -> subprocess.CompletedProcess[str]:",
                "    return subprocess.run(",
                "        [sys.executable, 'src/cat_clone.py', *[str(path) for path in paths]],",
                "        text=True,",
                "        capture_output=True,",
                "        check=False,",
                "    )",
                "",
                "",
                "def test_cat_clone_prints_files_in_order(tmp_path: Path) -> None:",
                "    first = tmp_path / 'first.txt'",
                "    second = tmp_path / 'second.txt'",
                "    first.write_text('alpha\\n', encoding='utf-8')",
                "    second.write_text('beta\\n', encoding='utf-8')",
                "",
                "    result = _run_cat(first, second)",
                "",
                "    assert result.returncode == 0",
                "    assert result.stdout == 'alpha\\nbeta\\n'",
                "    assert result.stderr == ''",
                "",
                "",
                "def test_cat_clone_returns_non_zero_on_missing_input(tmp_path: Path) -> None:",
                "    existing = tmp_path / 'existing.txt'",
                "    missing = tmp_path / 'missing.txt'",
                "    existing.write_text('alpha\\n', encoding='utf-8')",
                "",
                "    result = _run_cat(existing, missing)",
                "",
                "    assert result.returncode != 0",
                "    assert result.stdout == 'alpha\\n'",
                "    assert 'missing.txt' in result.stderr",
                "",
                "",
                "def test_cat_clone_returns_non_zero_without_arguments() -> None:",
                "    result = _run_cat()",
                "",
                "    assert result.returncode != 0",
                "    assert result.stdout == ''",
                "    assert result.stderr",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "e2e@example.com"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "E2E Harness"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed cat workspace"], cwd=workspace_root, check=True, capture_output=True, text=True)

def _children_by_parent(tree_payload: dict[str, object], *, parent_id: str, kind: str) -> list[dict[str, object]]:
    return [node for node in tree_payload["nodes"] if node["parent_node_id"] == parent_id and node["kind"] == kind]


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_flow_22_dependency_blocked_sibling_wait_requires_live_completion_of_dependency_sibling(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(
        session_backend="tmux",
        extra_env={
            "AICODING_SESSION_IDLE_THRESHOLD_SECONDS": "10.0",
            "AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.2",
        },
    )
    _write_cat_workspace_fixture(harness.workspace_root)
    sessions_to_cleanup: set[str] = set()
    try:
        parent_start_result = harness.cli(
            "workflow",
            "start",
            "--kind",
            "epic",
            "--title",
            "Real E2E Flow 22 Parent",
            "--prompt",
            "Use the existing cat_clone workspace. Create exactly two real phase siblings under this parent. "
            "The first sibling must be the prerequisite lane that fixes `src/cat_clone.py` so `python3 -m pytest -q tests/test_cat_clone.py` passes. "
            "The second sibling must remain blocked on the first until the first completes through a live tmux session. "
            "Do not create extra coordination phases or intermediary siblings.",
        )
        assert parent_start_result.exit_code == 0, parent_start_result.stderr
        parent_id = str(parent_start_result.json()["node"]["node_id"])

        parent_bind_result = harness.cli("session", "bind", "--node", parent_id)
        assert parent_bind_result.exit_code == 0, parent_bind_result.stderr
        parent_session_name = str(parent_bind_result.json()["session_name"])
        sessions_to_cleanup.add(parent_session_name)

        tree_payload = None
        sibling_records = None
        deadline = time.time() + PARENT_SIBLING_CREATION_TIMEOUT_SECONDS
        while time.time() < deadline:
            tree_result = harness.cli("tree", "show", "--node", parent_id, "--full")
            assert tree_result.exit_code == 0, tree_result.stderr
            tree_payload = tree_result.json()
            sibling_records = _children_by_parent(tree_payload, parent_id=parent_id, kind="phase")
            if len(sibling_records) >= 2:
                break
            time.sleep(2.0)

        assert sibling_records is not None and len(sibling_records) >= 2, (
            "Expected the live parent tmux/Codex session to create at least two phase siblings before Flow 22 "
            "proceeds.\n"
            f"The parent never created those siblings within {PARENT_SIBLING_CREATION_TIMEOUT_SECONDS:.0f} seconds.\n"
            f"parent_session_name={parent_session_name}\n"
            f"parent_pane=\n{_tmux_capture(parent_session_name)}\n"
            f"tree_payload={tree_payload}"
        )

        left_record = sibling_records[0]
        right_record = sibling_records[1]
        left_id = str(left_record["node_id"])
        right_id = str(right_record["node_id"])

        left_show_result = harness.cli("node", "show", "--node", left_id)
        right_show_result = harness.cli("node", "show", "--node", right_id)
        assert left_show_result.exit_code == 0, left_show_result.stderr
        assert right_show_result.exit_code == 0, right_show_result.stderr

        dependency_status_before_result = harness.cli("node", "dependency-status", "--node", right_id)
        blocked_start_result = harness.cli("node", "run", "start", "--node", right_id)
        assert dependency_status_before_result.exit_code == 0, dependency_status_before_result.stderr
        assert blocked_start_result.exit_code != 0, blocked_start_result.stderr

        left_start_result = harness.cli("node", "run", "start", "--node", left_id)
        assert left_start_result.exit_code == 0, left_start_result.stderr

        bind_result = harness.cli("session", "bind", "--node", left_id)
        assert bind_result.exit_code == 0, bind_result.stderr
        session_name = str(bind_result.json()["session_name"])
        sessions_to_cleanup.add(session_name)

        left_finished_payload = None
        last_pane_text = ""
        deadline = time.time() + CHILD_COMPLETION_TIMEOUT_SECONDS
        while time.time() < deadline:
            lifecycle_result = harness.cli("node", "lifecycle", "show", "--node", left_id)
            assert lifecycle_result.exit_code == 0, lifecycle_result.stderr
            lifecycle_payload = lifecycle_result.json()
            if lifecycle_payload["lifecycle_state"] in {"COMPLETE", "FAILED"}:
                left_finished_payload = lifecycle_payload
                break
            last_pane_text = _tmux_capture(session_name)
            time.sleep(1.0)

        assert left_finished_payload is not None, (
            "Expected the dependency sibling to reach a terminal lifecycle state through a live tmux/Codex execution path so the dependent sibling could unblock. "
            f"The left sibling never reached COMPLETE or FAILED within {CHILD_COMPLETION_TIMEOUT_SECONDS:.0f} seconds.\n"
            f"session_name={session_name}\n"
            f"pane_text=\n{last_pane_text}"
        )

        dependency_status_after_payload = None
        last_dependency_status = None
        deadline = time.time() + DEPENDENCY_UNBLOCK_TIMEOUT_SECONDS
        while time.time() < deadline:
            dependency_status_after_result = harness.cli("node", "dependency-status", "--node", right_id)
            assert dependency_status_after_result.exit_code == 0, dependency_status_after_result.stderr
            last_dependency_status = dependency_status_after_result.json()
            if last_dependency_status["status"] == "ready":
                dependency_status_after_payload = last_dependency_status
                break
            time.sleep(1.0)

        assert dependency_status_after_payload is not None, (
            "Expected the dependent sibling to become ready only after the daemon advanced the incremental merge lane.\n"
            f"last_dependency_status={last_dependency_status}"
        )

        unblocked_start_result = harness.cli("node", "run", "start", "--node", right_id)
        assert unblocked_start_result.exit_code == 0, unblocked_start_result.stderr

        dependency_status_before_payload = dependency_status_before_result.json()
        unblocked_start_payload = unblocked_start_result.json()

        assert left_record["scheduling_status"] == "ready"
        assert right_record["scheduling_status"] == "ready"
        assert left_show_result.json()["lifecycle_state"] == "READY"
        assert right_show_result.json()["lifecycle_state"] == "READY"
        assert left_finished_payload["lifecycle_state"] in {"COMPLETE", "FAILED"}
        assert dependency_status_before_payload["status"] == "blocked"
        assert dependency_status_before_payload["blockers"]
        assert dependency_status_after_payload["status"] == "ready"
        assert dependency_status_after_payload["blockers"] == []
        assert unblocked_start_payload["status"] == "admitted"
    finally:
        for session_name in sessions_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)
