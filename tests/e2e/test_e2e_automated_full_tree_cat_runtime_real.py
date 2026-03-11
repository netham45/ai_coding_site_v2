from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time

import pytest


def _cli_json(harness, *args: str) -> dict[str, object]:
    harness.assert_process_alive(prefix="Real daemon process exited before CLI inspection.")
    result = harness.cli(*args)
    assert result.exit_code == 0, result.stderr
    return result.json()


def _tmux_capture(session_name: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-p", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return f"[tmux capture failed] {result.stderr.strip()}"
    return result.stdout


def _write_scoped_parent_overrides(workspace_root: Path) -> None:
    overrides_root = workspace_root / "resources" / "yaml" / "overrides" / "nodes"
    overrides_root.mkdir(parents=True, exist_ok=True)
    for node_kind in ("epic", "phase", "plan"):
        (overrides_root / f"{node_kind}_entry_task.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace",
                    "value:",
                    "  entry_task: generate_child_layout",
                ]
            ),
            encoding="utf-8",
        )
        (overrides_root / f"{node_kind}_available_tasks.yaml").write_text(
            "\n".join(
                [
                    "target_family: node_definition",
                    f"target_id: {node_kind}",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace_list",
                    "value:",
                    "  available_tasks:",
                    "    - generate_child_layout",
                    "    - review_child_layout",
                    "    - spawn_children",
                ]
            ),
            encoding="utf-8",
        )


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


def _first_child(tree_payload: dict[str, object], *, parent_id: str, kind: str) -> dict[str, object] | None:
    for node in tree_payload["nodes"]:
        if node["parent_node_id"] == parent_id and node["kind"] == kind:
            return node
    return None


def _session_debug_lines(node_audit: dict[str, object]) -> list[str]:
    lines: list[str] = []
    for session_entry in node_audit.get("sessions", []):
        session = session_entry["session"]
        session_name = session.get("session_name")
        lines.append(
            json.dumps(
                {
                    "node_id": node_audit["node_id"],
                    "session_id": session.get("id"),
                    "session_name": session_name,
                    "status": session.get("status"),
                    "event_count": len(session_entry.get("events", [])),
                },
                sort_keys=True,
            )
        )
        if session_name:
            lines.append(_tmux_capture(str(session_name)))
    return lines


def _run_workspace_verification(workspace_root: Path) -> tuple[subprocess.CompletedProcess[str], subprocess.CompletedProcess[str]]:
    fixture_dir = workspace_root / ".e2e-fixtures"
    fixture_dir.mkdir(parents=True, exist_ok=True)
    first = fixture_dir / "first.txt"
    second = fixture_dir / "second.txt"
    first.write_text("alpha\n", encoding="utf-8")
    second.write_text("beta\n", encoding="utf-8")
    cat_result = subprocess.run(
        [sys.executable, "src/cat_clone.py", str(first), str(second)],
        cwd=workspace_root,
        text=True,
        capture_output=True,
        check=False,
    )
    test_result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "tests/test_cat_clone.py"],
        cwd=workspace_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return cat_result, test_result


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_automated_full_tree_cat_runtime_real(real_daemon_harness_factory) -> None:
    harness = real_daemon_harness_factory(extra_env={"AICODING_SESSION_POLL_INTERVAL_SECONDS": "0.5"})
    _write_scoped_parent_overrides(harness.workspace_root)
    _write_cat_workspace_fixture(harness.workspace_root)

    start_payload = _cli_json(
        harness,
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Automated Full Tree Cat Runtime",
        "--prompt",
        "Create exactly one minimal execution path to build a basic Python recreation of the cat command in this workspace. "
        "Use one phase, one plan, and one task unless impossible. "
        "The final implementation must live in src/cat_clone.py and must satisfy tests/test_cat_clone.py. "
        "The program must print each input file to stdout in order, return non-zero when an input is missing or unreadable, "
        "and return non-zero when invoked without file arguments. "
        "Do not ask for operator materialization help; drive child creation through the runtime command loop.",
    )
    epic_id = str(start_payload["node"]["node_id"])
    epic_bind = _cli_json(harness, "session", "bind", "--node", epic_id)

    tree_payload: dict[str, object] | None = None
    epic_materialization: dict[str, object] | None = None
    phase_materialization: dict[str, object] | None = None
    plan_materialization: dict[str, object] | None = None
    epic_audit: dict[str, object] | None = None
    phase_audit: dict[str, object] | None = None
    plan_audit: dict[str, object] | None = None
    task_audit: dict[str, object] | None = None
    epic_prompt_history: dict[str, object] | None = None
    phase_prompt_history: dict[str, object] | None = None
    plan_prompt_history: dict[str, object] | None = None
    task_prompt_history: dict[str, object] | None = None
    phase_runs: dict[str, object] | None = None
    plan_runs: dict[str, object] | None = None
    task_runs: dict[str, object] | None = None
    cat_result: subprocess.CompletedProcess[str] | None = None
    test_result: subprocess.CompletedProcess[str] | None = None

    # This narrative requires four real AI-driven hops (epic -> phase -> plan -> task)
    # plus leaf implementation, validation, review, and local pytest. Live
    # provider-backed reruns proved that 420s and then 600s were still too tight:
    # the task node was still actively running at expiry rather than stalled.
    deadline = time.time() + 900.0
    while time.time() < deadline:
        harness.assert_process_alive(prefix="Real daemon process exited during automated full-tree cat E2E.")
        tree_payload = _cli_json(harness, "tree", "show", "--node", epic_id, "--full")
        epic_materialization = _cli_json(harness, "node", "child-materialization", "--node", epic_id)
        epic_audit = _cli_json(harness, "node", "audit", "--node", epic_id)
        epic_prompt_history = _cli_json(harness, "prompts", "history", "--node", epic_id)

        phase_node = _first_child(tree_payload, parent_id=epic_id, kind="phase")
        plan_node = None
        task_node = None
        if phase_node is not None:
            phase_id = str(phase_node["node_id"])
            phase_materialization = _cli_json(harness, "node", "child-materialization", "--node", phase_id)
            phase_audit = _cli_json(harness, "node", "audit", "--node", phase_id)
            phase_prompt_history = _cli_json(harness, "prompts", "history", "--node", phase_id)
            phase_runs = _cli_json(harness, "node", "runs", "--node", phase_id)
            plan_node = _first_child(tree_payload, parent_id=phase_id, kind="plan")
        if plan_node is not None:
            plan_id = str(plan_node["node_id"])
            plan_materialization = _cli_json(harness, "node", "child-materialization", "--node", plan_id)
            plan_audit = _cli_json(harness, "node", "audit", "--node", plan_id)
            plan_prompt_history = _cli_json(harness, "prompts", "history", "--node", plan_id)
            plan_runs = _cli_json(harness, "node", "runs", "--node", plan_id)
            task_node = _first_child(tree_payload, parent_id=plan_id, kind="task")
        if task_node is not None:
            task_id = str(task_node["node_id"])
            task_audit = _cli_json(harness, "node", "audit", "--node", task_id)
            task_prompt_history = _cli_json(harness, "prompts", "history", "--node", task_id)
            task_runs = _cli_json(harness, "node", "runs", "--node", task_id)
            cat_result, test_result = _run_workspace_verification(harness.workspace_root)
            if (
                task_audit["summary_history"]["summaries"]
                and task_runs["runs"]
                and task_runs["runs"][0]["run_status"] == "COMPLETE"
                and cat_result.returncode == 0
                and cat_result.stdout == "alpha\nbeta\n"
                and test_result.returncode == 0
            ):
                break
        time.sleep(5.0)

    assert tree_payload is not None
    assert epic_materialization is not None
    assert epic_audit is not None
    assert phase_materialization is not None
    assert phase_audit is not None
    assert phase_runs is not None
    assert plan_materialization is not None
    assert plan_audit is not None
    assert plan_runs is not None
    assert task_audit is not None
    assert epic_prompt_history is not None
    assert phase_prompt_history is not None
    assert plan_prompt_history is not None
    assert task_prompt_history is not None
    assert task_runs is not None
    assert cat_result is not None
    assert test_result is not None, (
        "The automated full-tree runtime did not reach a completed leaf task with a working cat implementation.\n"
        f"epic_bind={json.dumps(epic_bind, indent=2, sort_keys=True)}\n"
        f"tree_payload={json.dumps(tree_payload, indent=2, sort_keys=True)}\n"
        f"epic_materialization={json.dumps(epic_materialization, indent=2, sort_keys=True)}\n"
        f"phase_materialization={json.dumps(phase_materialization, indent=2, sort_keys=True) if phase_materialization else None}\n"
        f"plan_materialization={json.dumps(plan_materialization, indent=2, sort_keys=True) if plan_materialization else None}\n"
        f"epic_audit_sessions={_session_debug_lines(epic_audit)}\n"
        f"phase_audit_sessions={_session_debug_lines(phase_audit) if phase_audit else []}\n"
        f"plan_audit_sessions={_session_debug_lines(plan_audit) if plan_audit else []}\n"
        f"task_audit_sessions={_session_debug_lines(task_audit) if task_audit else []}\n"
        f"cat_stdout={cat_result.stdout if cat_result else ''}\n"
        f"cat_stderr={cat_result.stderr if cat_result else ''}\n"
        f"pytest_stdout={test_result.stdout if test_result else ''}\n"
        f"pytest_stderr={test_result.stderr if test_result else ''}"
    )

    kinds = {node["kind"] for node in tree_payload["nodes"]}
    assert {"epic", "phase", "plan", "task"}.issubset(kinds)
    # Late inspection can legitimately report `reconciliation_required` after
    # descendants overwrite the shared workspace layout file, even though the
    # earlier generated layout was durably registered and already used.
    assert epic_materialization["status"] in {"materialized", "already_materialized", "reconciliation_required"}
    assert phase_materialization["status"] in {"materialized", "already_materialized", "reconciliation_required"}
    assert plan_materialization["status"] in {"materialized", "already_materialized", "reconciliation_required"}
    assert any(event["event_type"] == "registered_generated_layout" for event in epic_audit["workflow_events"])
    assert any(event["event_type"] == "registered_generated_layout" for event in phase_audit["workflow_events"])
    assert any(event["event_type"] == "registered_generated_layout" for event in plan_audit["workflow_events"])
    assert epic_audit["sessions"]
    assert phase_audit["sessions"]
    assert plan_audit["sessions"]
    assert task_audit["sessions"]
    assert phase_runs["runs"][0]["trigger_reason"] == "auto_run_child"
    assert plan_runs["runs"][0]["trigger_reason"] == "auto_run_child"
    assert task_runs["runs"][0]["trigger_reason"] == "auto_run_child"
    assert task_runs["runs"][0]["run_status"] == "COMPLETE"
    assert task_audit["summary_history"]["summaries"]
    assert all(
        "confirm the parent node run is finished" not in prompt["content"]
        and "confirm final parent state" not in prompt["content"]
        for history in (epic_prompt_history, phase_prompt_history, plan_prompt_history)
        for prompt in history["prompts"]
    )
    assert all(
        "confirm the node run is finished" not in prompt["content"]
        and "active node run not found" not in prompt["content"]
        for prompt in task_prompt_history["prompts"]
    )
    assert cat_result.returncode == 0
    assert cat_result.stdout == "alpha\nbeta\n"
    assert test_result.returncode == 0, test_result.stdout + "\n" + test_result.stderr
