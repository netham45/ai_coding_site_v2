from __future__ import annotations

import json
from pathlib import Path
import subprocess
import time

import pytest


def _git(repo_path: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result.stdout.strip()


def _cli_json(real_daemon_harness, *args: str) -> dict[str, object]:
    result = real_daemon_harness.cli(*args)
    assert result.exit_code == 0, result.stderr
    return result.json()


def _cli_dump(real_daemon_harness, label: str, *args: str) -> dict[str, object]:
    payload = _cli_json(real_daemon_harness, *args)
    print(f"\n=== {label} ===")
    print(f"$ python3 -m aicoding.cli.main {' '.join(args)}")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return payload


def _print_payload(label: str, payload: dict[str, object]) -> None:
    print(f"\n=== {label} ===")
    print(json.dumps(payload, indent=2, sort_keys=True))


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


def _dump_tmux_pane(session_name: str, *, label: str) -> None:
    print(f"\n=== {label}: tmux pane ===")
    print(_tmux_capture(session_name))


def _write_workspace_leaf_task_fixture(workspace_root: Path) -> None:
    src_dir = workspace_root / "src"
    tests_dir = workspace_root / "tests"
    src_dir.mkdir(parents=True, exist_ok=True)
    tests_dir.mkdir(parents=True, exist_ok=True)
    (src_dir / "__init__.py").write_text("", encoding="utf-8")
    (src_dir / "app.py").write_text(
        "def greet() -> str:\n"
        "    return 'pending'\n",
        encoding="utf-8",
    )
    (tests_dir / "test_app.py").write_text(
        "from src.app import greet\n\n\n"
        "def test_greet_returns_expected_message() -> None:\n"
        "    assert greet() == 'hello from runtime'\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "e2e@example.com"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "E2E Harness"], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=workspace_root, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "seed workspace"], cwd=workspace_root, check=True, capture_output=True, text=True)


def _write_json(path: Path, payload: dict[str, str]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


def _authoritative_version_id(real_daemon_harness, node_id: str) -> str:
    versions_payload = _cli_json(real_daemon_harness, "node", "versions", "--node", node_id)
    return str(versions_payload["versions"][0]["id"])


def _bootstrap_version_with_seed(real_daemon_harness, version_id: str, seed_files_path: Path) -> dict[str, object]:
    payload = _cli_json(
        real_daemon_harness,
        "git",
        "bootstrap-node",
        "--version",
        version_id,
        "--files-file",
        str(seed_files_path),
        "--replace-existing",
    )
    _print_payload(f"git bootstrap {version_id}", payload)
    return payload


def _bootstrap_version_from_parent(real_daemon_harness, version_id: str, parent_version_id: str) -> dict[str, object]:
    payload = _cli_json(
        real_daemon_harness,
        "git",
        "bootstrap-node",
        "--version",
        version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    _print_payload(f"git bootstrap child {version_id}", payload)
    return payload


def _repo_path_for_version(real_daemon_harness, version_id: str) -> Path:
    status_payload = _cli_json(real_daemon_harness, "git", "status", "show", "--version", version_id)
    _print_payload(f"git status {version_id}", status_payload)
    return Path(str(status_payload["repo_path"]))


def _assert_merge_boundary(
    real_daemon_harness,
    *,
    parent_id: str,
    parent_version_id: str,
    child_id: str,
    child_final_commit_sha: str,
    expected_files: dict[str, str],
    untouched_files: dict[str, str],
) -> None:
    child_results = _cli_dump(real_daemon_harness, f"{parent_id} child results", "node", "child-results", "--node", parent_id)
    reconcile = _cli_dump(real_daemon_harness, f"{parent_id} reconcile", "node", "reconcile", "--node", parent_id)
    merge_payload = _cli_dump(real_daemon_harness, f"{parent_id} merge children", "git", "merge-children", "--node", parent_id)
    finalize_payload = _cli_dump(real_daemon_harness, f"{parent_id} finalize", "git", "finalize-node", "--node", parent_id)
    final_status = _cli_dump(real_daemon_harness, f"{parent_id} final status", "git", "status", "show", "--version", parent_version_id)
    final_show = _cli_dump(real_daemon_harness, f"{parent_id} final show", "git", "final", "show", "--node", parent_id)
    merge_events = _cli_dump(real_daemon_harness, f"{parent_id} merge events", "git", "merge-events", "show", "--node", parent_id)
    parent_repo = Path(str(final_status["repo_path"]))

    assert child_results["status"] == "ready_for_reconcile"
    assert child_results["children"][0]["child_node_id"] == child_id
    assert child_results["children"][0]["final_commit_sha"] == child_final_commit_sha
    assert reconcile["status"] == "ready_for_reconcile"
    assert merge_payload["status"] == "merged"
    assert merge_payload["merge_events"][0]["child_final_commit_sha"] == child_final_commit_sha
    assert finalize_payload["final_commit_sha"] == _git(parent_repo, "rev-parse", "HEAD")
    assert final_show["final_commit_sha"] == finalize_payload["final_commit_sha"]
    assert final_status["working_tree_state"] == "finalized_clean"
    assert _git(parent_repo, "status", "--short") == ""
    assert [event["child_final_commit_sha"] for event in merge_events["events"]][-1:] == [child_final_commit_sha]
    for relative_path, expected_content in expected_files.items():
        assert (parent_repo / relative_path).read_text(encoding="utf-8") == expected_content
    for relative_path, expected_content in untouched_files.items():
        assert (parent_repo / relative_path).read_text(encoding="utf-8") == expected_content


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_full_epic_tree_runtime_real(real_daemon_harness) -> None:
    _write_workspace_leaf_task_fixture(real_daemon_harness.workspace_root)
    print("\n=== workspace_root ===")
    print(real_daemon_harness.workspace_root)
    start_payload = _cli_dump(
        real_daemon_harness,
        "workflow start",
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Full Epic Tree",
        "--prompt",
        "In the workspace, update src/app.py so greet() returns 'hello from runtime' and tests/test_app.py passes. "
        "Descend through phase, plan, and task, then execute the leaf task through real runtime commands.",
        "--no-run",
    )
    epic_id = str(start_payload["node"]["node_id"])

    epic_tree_before = _cli_dump(real_daemon_harness, "epic tree before", "tree", "show", "--node", epic_id, "--full")
    epic_materialize = _cli_dump(real_daemon_harness, "epic materialize", "node", "materialize-children", "--node", epic_id)
    epic_children = _cli_dump(real_daemon_harness, "epic children", "node", "children", "--node", epic_id, "--versions")

    assert epic_tree_before["root_node_id"] == epic_id
    assert len(epic_tree_before["nodes"]) == 1
    assert epic_materialize["child_count"] == 2
    assert {child["layout_child_id"] for child in epic_materialize["children"]} == {"discovery", "implementation"}
    assert len(epic_children["children"]) == 2

    discovery_phase = next(child for child in epic_materialize["children"] if child["layout_child_id"] == "discovery")
    discovery_phase_id = str(discovery_phase["node_id"])
    phase_show = _cli_dump(real_daemon_harness, "phase show", "node", "show", "--node", discovery_phase_id)
    phase_workflow = _cli_dump(real_daemon_harness, "phase workflow", "workflow", "current", "--node", discovery_phase_id)
    phase_materialize = _cli_dump(real_daemon_harness, "phase materialize", "node", "materialize-children", "--node", discovery_phase_id)

    assert phase_show["kind"] == "phase"
    assert phase_show["parent_node_id"] == epic_id
    assert phase_workflow["logical_node_id"] == discovery_phase_id
    assert phase_materialize["child_count"] == 1

    plan_node = phase_materialize["children"][0]
    plan_id = str(plan_node["node_id"])
    plan_show = _cli_dump(real_daemon_harness, "plan show", "node", "show", "--node", plan_id)
    plan_workflow = _cli_dump(real_daemon_harness, "plan workflow", "workflow", "current", "--node", plan_id)
    plan_materialize = _cli_dump(real_daemon_harness, "plan materialize", "node", "materialize-children", "--node", plan_id)

    assert plan_show["kind"] == "plan"
    assert plan_show["parent_node_id"] == discovery_phase_id
    assert plan_workflow["logical_node_id"] == plan_id
    assert plan_materialize["child_count"] == 1

    task_node = plan_materialize["children"][0]
    task_id = str(task_node["node_id"])
    task_show = _cli_dump(real_daemon_harness, "task show", "node", "show", "--node", task_id)
    task_workflow = _cli_dump(real_daemon_harness, "task workflow", "workflow", "current", "--node", task_id)
    full_tree = _cli_dump(real_daemon_harness, "full tree", "tree", "show", "--node", epic_id, "--full")

    assert task_show["kind"] == "task"
    assert task_show["parent_node_id"] == plan_id
    assert task_show["lifecycle_state"] == "READY"
    assert task_workflow["logical_node_id"] == task_id
    assert len(full_tree["nodes"]) == 5
    assert {node["kind"] for node in full_tree["nodes"]} == {"epic", "phase", "plan", "task"}

    run_start = _cli_dump(real_daemon_harness, "task run start", "node", "run", "start", "--node", task_id)
    subtask_current = _cli_dump(real_daemon_harness, "subtask current", "subtask", "current", "--node", task_id)
    subtask_prompt = _cli_dump(real_daemon_harness, "subtask prompt", "subtask", "prompt", "--node", task_id)
    subtask_context = _cli_dump(real_daemon_harness, "subtask context", "subtask", "context", "--node", task_id)
    compiled_subtask_id = str(subtask_current["state"]["current_compiled_subtask_id"])

    assert run_start["status"] == "admitted"
    assert run_start["current_state"] == "RUNNING"
    assert subtask_current["run"]["logical_node_id"] == task_id
    assert subtask_prompt["compiled_subtask_id"] == compiled_subtask_id
    assert subtask_prompt["prompt_text"]
    assert subtask_context["compiled_subtask_id"] == compiled_subtask_id
    assert subtask_context["input_context_json"]["stage_context_json"]

    bind_result = _cli_dump(real_daemon_harness, "session bind", "session", "bind", "--node", task_id)
    session_name = str(bind_result["session_name"])
    _dump_tmux_pane(session_name, label="after session bind")

    progress_payload = None
    summary_history = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        progress_payload = _cli_json(real_daemon_harness, "node", "run", "show", "--node", task_id)
        summary_history = _cli_json(real_daemon_harness, "summary", "history", "--node", task_id)
        last_pane_text = _tmux_capture(session_name)
        latest_attempt = progress_payload["latest_attempt"]
        if latest_attempt is not None or summary_history["summaries"] or progress_payload["state"]["last_completed_compiled_subtask_id"] is not None:
            break
        time.sleep(2.0)

    print("\n=== task run show ===")
    print(json.dumps(progress_payload, indent=2, sort_keys=True))
    print("\n=== summary history ===")
    print(json.dumps(summary_history, indent=2, sort_keys=True))
    _dump_tmux_pane(session_name, label="after live task progress wait")

    assert bind_result["logical_node_id"] == task_id
    assert bind_result["tmux_session_exists"] is True
    assert progress_payload is not None
    assert summary_history is not None
    assert progress_payload["run"]["logical_node_id"] == task_id
    assert progress_payload["run"]["run_status"] in {"RUNNING", "COMPLETED", "FAILED", "PAUSED"}
    assert progress_payload["latest_attempt"] is not None or summary_history["summaries"] or progress_payload["state"]["last_completed_compiled_subtask_id"] is not None, (
        "Expected the real primary tmux/Codex session to create durable leaf-task progress without manual "
        "subtask advancement from the test.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_e2e_full_epic_tree_git_merge_propagates_task_changes_to_plan_phase_and_epic(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    start_payload = _cli_json(
        real_daemon_harness,
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real E2E Full Epic Tree Git Merge",
        "--prompt",
        "Create a hierarchy that can prove real git merge propagation from task to plan to phase to epic.",
        "--no-run",
    )
    _print_payload(
        "workflow start no-run",
        {
            "node": start_payload["node"],
            "node_version_id": start_payload["node_version_id"],
            "status": start_payload["status"],
        },
    )
    epic_id = str(start_payload["node"]["node_id"])
    epic_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", epic_id)
    _print_payload("epic materialize", epic_materialize)
    discovery_phase = next(child for child in epic_materialize["children"] if child["layout_child_id"] == "discovery")
    implementation_phase = next(child for child in epic_materialize["children"] if child["layout_child_id"] == "implementation")
    phase_id = str(discovery_phase["node_id"])
    implementation_phase_id = str(implementation_phase["node_id"])
    phase_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", phase_id)
    _print_payload("phase materialize", phase_materialize)
    plan_id = str(phase_materialize["children"][0]["node_id"])
    plan_materialize = _cli_json(real_daemon_harness, "node", "materialize-children", "--node", plan_id)
    _print_payload("plan materialize", plan_materialize)
    task_id = str(plan_materialize["children"][0]["node_id"])

    epic_version_id = _authoritative_version_id(real_daemon_harness, epic_id)
    phase_version_id = _authoritative_version_id(real_daemon_harness, phase_id)
    implementation_phase_version_id = _authoritative_version_id(real_daemon_harness, implementation_phase_id)
    plan_version_id = _authoritative_version_id(real_daemon_harness, plan_id)
    task_version_id = _authoritative_version_id(real_daemon_harness, task_id)

    seed_files_path = tmp_path / "full-tree-seed-files.json"
    _write_json(
        seed_files_path,
        {
            "shared.txt": "seed\n",
            "docs/notes.md": "seed docs\n",
            "src/module.py": "VALUE = 'seed'\n",
        },
    )

    _bootstrap_version_with_seed(real_daemon_harness, epic_version_id, seed_files_path)
    _bootstrap_version_from_parent(real_daemon_harness, phase_version_id, epic_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, implementation_phase_version_id, epic_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, plan_version_id, phase_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, task_version_id, plan_version_id)

    task_repo = _repo_path_for_version(real_daemon_harness, task_version_id)
    phase_repo = _repo_path_for_version(real_daemon_harness, phase_version_id)
    plan_repo = _repo_path_for_version(real_daemon_harness, plan_version_id)
    epic_repo = _repo_path_for_version(real_daemon_harness, epic_version_id)

    (task_repo / "docs/notes.md").write_text("seed docs\ntask merged note\n", encoding="utf-8")
    (task_repo / "src/module.py").write_text("VALUE = 'task-merged'\n", encoding="utf-8")
    _git(task_repo, "add", ".")
    _git(task_repo, "commit", "-m", "Task merged content")

    task_finalize = _cli_dump(real_daemon_harness, "task finalize", "git", "finalize-node", "--node", task_id)
    task_final_commit_sha = str(task_finalize["final_commit_sha"])
    implementation_phase_finalize = _cli_dump(
        real_daemon_harness,
        "implementation phase finalize",
        "git",
        "finalize-node",
        "--node",
        implementation_phase_id,
    )
    implementation_phase_final_commit_sha = str(implementation_phase_finalize["final_commit_sha"])

    _assert_merge_boundary(
        real_daemon_harness,
        parent_id=plan_id,
        parent_version_id=plan_version_id,
        child_id=task_id,
        child_final_commit_sha=task_final_commit_sha,
        expected_files={
            "docs/notes.md": "seed docs\ntask merged note\n",
            "src/module.py": "VALUE = 'task-merged'\n",
        },
        untouched_files={"shared.txt": "seed\n"},
    )
    assert (plan_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\ntask merged note\n"
    assert (plan_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'task-merged'\n"

    plan_final_show = _cli_dump(real_daemon_harness, "plan final show", "git", "final", "show", "--node", plan_id)
    plan_final_commit_sha = str(plan_final_show["final_commit_sha"])
    _assert_merge_boundary(
        real_daemon_harness,
        parent_id=phase_id,
        parent_version_id=phase_version_id,
        child_id=plan_id,
        child_final_commit_sha=plan_final_commit_sha,
        expected_files={
            "docs/notes.md": "seed docs\ntask merged note\n",
            "src/module.py": "VALUE = 'task-merged'\n",
        },
        untouched_files={"shared.txt": "seed\n"},
    )
    assert (phase_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\ntask merged note\n"
    assert (phase_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'task-merged'\n"

    phase_final_show = _cli_dump(real_daemon_harness, "phase final show", "git", "final", "show", "--node", phase_id)
    phase_final_commit_sha = str(phase_final_show["final_commit_sha"])
    epic_child_results = _cli_dump(real_daemon_harness, "epic child results", "node", "child-results", "--node", epic_id)
    epic_reconcile = _cli_dump(real_daemon_harness, "epic reconcile", "node", "reconcile", "--node", epic_id)
    epic_merge = _cli_dump(real_daemon_harness, "epic merge children", "git", "merge-children", "--node", epic_id)
    epic_finalize = _cli_dump(real_daemon_harness, "epic finalize", "git", "finalize-node", "--node", epic_id)
    epic_final_status = _cli_dump(real_daemon_harness, "epic final status", "git", "status", "show", "--version", epic_version_id)
    epic_final_show = _cli_dump(real_daemon_harness, "epic final show", "git", "final", "show", "--node", epic_id)
    epic_merge_events = _cli_dump(real_daemon_harness, "epic merge events", "git", "merge-events", "show", "--node", epic_id)

    assert epic_child_results["status"] == "ready_for_reconcile"
    assert len(epic_child_results["children"]) == 2
    event_by_child = {event["child_final_commit_sha"] for event in epic_merge["merge_events"]}
    assert phase_final_commit_sha in event_by_child
    assert implementation_phase_final_commit_sha in event_by_child
    assert epic_reconcile["status"] == "ready_for_reconcile"
    assert epic_merge["status"] == "merged"
    assert epic_finalize["final_commit_sha"] == _git(epic_repo, "rev-parse", "HEAD")
    assert epic_final_show["final_commit_sha"] == epic_finalize["final_commit_sha"]
    assert epic_final_status["working_tree_state"] == "finalized_clean"
    assert _git(epic_repo, "status", "--short") == ""
    assert {event["child_final_commit_sha"] for event in epic_merge_events["events"]} >= {
        phase_final_commit_sha,
        implementation_phase_final_commit_sha,
    }
    assert (epic_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\ntask merged note\n"
    assert (epic_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'task-merged'\n"
    assert (epic_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
