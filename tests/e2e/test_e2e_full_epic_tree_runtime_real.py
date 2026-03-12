from __future__ import annotations

import json
from pathlib import Path
import shlex
import subprocess
import time
from uuid import uuid4

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


def _wait_for(predicate, *, timeout_seconds: float = 45.0, sleep_seconds: float = 0.5, failure_message: str):
    deadline = time.time() + timeout_seconds
    last_value = None
    while time.time() < deadline:
        last_value = predicate()
        if last_value:
            return last_value
        time.sleep(sleep_seconds)
    raise AssertionError(f"{failure_message}\nlast_value={last_value}")


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


def _tmux_has_session(session_name: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def _tmux_send_enter(session_name: str, text: str) -> None:
    subprocess.run(
        ["tmux", "send-keys", "-t", session_name, text, "Enter"],
        text=True,
        capture_output=True,
        check=False,
    )


def _dump_tmux_pane(session_name: str, *, label: str) -> None:
    print(f"\n=== {label}: tmux pane ===")
    print(_tmux_capture(session_name))


def _git_show_file(repo_path: Path, commit_sha: str, relative_path: str) -> str:
    return _git(repo_path, "show", f"{commit_sha}:{relative_path}")


def _repo_matches_expected_files(repo_path: Path, expected_files: dict[str, str]) -> bool:
    for relative_path, expected_content in expected_files.items():
        file_path = repo_path / relative_path
        if not file_path.is_file():
            return False
        if file_path.read_text(encoding="utf-8") != expected_content:
            return False
    return True


def _print_repo_snapshot(repo_path: Path, *, label: str, tracked_files: list[str]) -> None:
    print(f"\n=== {label}: repo snapshot ===")
    print(f"repo_path={repo_path}")
    print(f"git status --short:\n{_git(repo_path, 'status', '--short')}")
    print(f"latest commit subject: {_git(repo_path, 'log', '-1', '--pretty=%s')}")
    for relative_path in tracked_files:
        file_path = repo_path / relative_path
        if file_path.is_file():
            print(f"--- {relative_path} ---")
            print(file_path.read_text(encoding='utf-8'))
        else:
            print(f"--- {relative_path} missing ---")


def _print_find_snapshot(repo_path: Path, *, label: str, max_depth: int = 4) -> None:
    result = subprocess.run(
        ["find", ".", "-maxdepth", str(max_depth), "-print"],
        cwd=repo_path,
        text=True,
        capture_output=True,
        check=False,
    )
    print(f"\n=== {label}: find snapshot ===")
    print(f"repo_path={repo_path}")
    if result.returncode != 0:
        print(result.stderr or result.stdout)
        return
    print(result.stdout)


def _run_live_codex_repo_edit_in_tmux(
    *,
    repo_path: Path,
    instruction: str,
    expected_files: dict[str, str],
    expected_commit_subject: str,
    timeout_seconds: float = 180.0,
) -> str:
    session_name = f"aicoding-live-merge-{uuid4().hex[:8]}"
    command = f"codex --yolo {shlex.quote(instruction)}"
    print("\n=== live codex repo edit start ===")
    print(f"session_name={session_name}")
    print(f"repo_path={repo_path}")
    print(f"command={command}")
    create_result = subprocess.run(
        ["tmux", "new-session", "-d", "-s", session_name, "-c", str(repo_path), command],
        text=True,
        capture_output=True,
        check=False,
    )
    if create_result.returncode != 0:
        raise AssertionError(create_result.stderr or create_result.stdout)

    deadline = time.time() + timeout_seconds
    trust_prompt_acknowledged = False
    last_pane_text = ""
    poll_count = 0
    while time.time() < deadline:
        poll_count += 1
        last_pane_text = _tmux_capture(session_name) if _tmux_has_session(session_name) else last_pane_text
        if (
            not trust_prompt_acknowledged
            and "Do you trust the contents of this directory?" in last_pane_text
            and "1. Yes, continue" in last_pane_text
        ):
            print("\n=== live codex repo edit ===")
            print("trust prompt detected; sending acceptance")
            _tmux_send_enter(session_name, "1")
            trust_prompt_acknowledged = True

        if poll_count == 1 or poll_count % 5 == 0:
            print("\n=== live codex repo edit poll ===")
            print(f"poll_count={poll_count}")
            print(f"trust_prompt_acknowledged={trust_prompt_acknowledged}")
            print(f"tmux_session_exists={_tmux_has_session(session_name)}")
            _dump_tmux_pane(session_name, label=f"live codex poll {poll_count}")
            _print_find_snapshot(repo_path, label=f"live codex poll {poll_count}")
            _print_repo_snapshot(
                repo_path,
                label=f"live codex poll {poll_count}",
                tracked_files=sorted(expected_files.keys()) + ["shared.txt"],
            )

        if (
            _repo_matches_expected_files(repo_path, expected_files)
            and _git(repo_path, "status", "--short") == ""
            and _git(repo_path, "log", "-1", "--pretty=%s") == expected_commit_subject
        ):
            print("\n=== live codex repo edit complete ===")
            print(f"session_name={session_name}")
            _dump_tmux_pane(session_name, label="live codex final pane")
            _print_find_snapshot(repo_path, label="live codex final")
            _print_repo_snapshot(
                repo_path,
                label="live codex final",
                tracked_files=sorted(expected_files.keys()) + ["shared.txt"],
            )
            return session_name
        time.sleep(2.0)

    raise AssertionError(
        "Timed out waiting for the live tmux/Codex edit to produce the expected committed repo contents.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )


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


def _transition_finalized_node_to_complete(real_daemon_harness, *, node_id: str) -> dict[str, object]:
    lifecycle = _cli_json(real_daemon_harness, "node", "lifecycle", "show", "--node", node_id)
    state = str(lifecycle["lifecycle_state"])
    if state == "FAILED_TO_PARENT":
        _cli_dump(
            real_daemon_harness,
            f"{node_id} lifecycle wait after failure",
            "node",
            "lifecycle",
            "transition",
            "--node",
            node_id,
            "--state",
            "WAITING_ON_SIBLING_DEPENDENCY",
        )
        state = "WAITING_ON_SIBLING_DEPENDENCY"
    if state == "COMPILED":
        _cli_dump(real_daemon_harness, f"{node_id} lifecycle ready", "node", "lifecycle", "transition", "--node", node_id, "--state", "READY")
        state = "READY"
    if state == "WAITING_ON_SIBLING_DEPENDENCY":
        _cli_dump(real_daemon_harness, f"{node_id} lifecycle ready after wait", "node", "lifecycle", "transition", "--node", node_id, "--state", "READY")
        state = "READY"
    if state == "READY":
        _cli_dump(real_daemon_harness, f"{node_id} lifecycle running", "node", "lifecycle", "transition", "--node", node_id, "--state", "RUNNING")
    return _cli_dump(
        real_daemon_harness,
        f"{node_id} lifecycle complete",
        "node",
        "lifecycle",
        "transition",
        "--node",
        node_id,
        "--state",
        "COMPLETE",
    )


def _assert_incremental_merge_boundary(
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
    live_status = _cli_dump(real_daemon_harness, f"{parent_id} live status", "git", "status", "show", "--version", parent_version_id)
    merge_events = _cli_dump(real_daemon_harness, f"{parent_id} merge events", "git", "merge-events", "show", "--node", parent_id)
    parent_repo = Path(str(live_status["repo_path"]))

    assert child_results["status"] == "ready_for_reconcile"
    assert child_results["children"][0]["child_node_id"] == child_id
    assert child_results["children"][0]["final_commit_sha"] == child_final_commit_sha
    assert reconcile["status"] == "ready_for_reconcile"
    assert live_status["working_tree_state"] in {"merged_children", "finalized_clean"}
    assert _git(parent_repo, "status", "--short") == ""
    assert [event["child_final_commit_sha"] for event in merge_events["events"]][-1:] == [child_final_commit_sha]
    for relative_path, expected_content in expected_files.items():
        assert (parent_repo / relative_path).read_text(encoding="utf-8") == expected_content
    for relative_path, expected_content in untouched_files.items():
        assert (parent_repo / relative_path).read_text(encoding="utf-8") == expected_content


def _setup_bootstrapped_full_tree_git_hierarchy(
    real_daemon_harness,
    tmp_path: Path,
    *,
    title: str,
    root_prompt: str | None = None,
) -> dict[str, object]:
    start_payload = _cli_json(
        real_daemon_harness,
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        title,
        "--prompt",
        root_prompt
        or "Create a hierarchy that can prove real git merge propagation and rectification from task to plan to phase to epic.",
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

    seed_files_path = tmp_path / f"{title.lower().replace(' ', '-')}-seed-files.json"
    _write_json(
        seed_files_path,
        {
            "shared.txt": "seed\n",
            "docs/notes.md": "seed docs\n",
            "src/module.py": "VALUE = 'seed'\n",
            "ops/implementation.txt": "implementation seed\n",
        },
    )

    _bootstrap_version_with_seed(real_daemon_harness, epic_version_id, seed_files_path)
    _bootstrap_version_from_parent(real_daemon_harness, phase_version_id, epic_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, implementation_phase_version_id, epic_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, plan_version_id, phase_version_id)
    _bootstrap_version_from_parent(real_daemon_harness, task_version_id, plan_version_id)

    return {
        "epic_id": epic_id,
        "phase_id": phase_id,
        "implementation_phase_id": implementation_phase_id,
        "plan_id": plan_id,
        "task_id": task_id,
        "epic_version_id": epic_version_id,
        "phase_version_id": phase_version_id,
        "implementation_phase_version_id": implementation_phase_version_id,
        "plan_version_id": plan_version_id,
        "task_version_id": task_version_id,
        "epic_repo": _repo_path_for_version(real_daemon_harness, epic_version_id),
        "phase_repo": _repo_path_for_version(real_daemon_harness, phase_version_id),
        "implementation_phase_repo": _repo_path_for_version(real_daemon_harness, implementation_phase_version_id),
        "plan_repo": _repo_path_for_version(real_daemon_harness, plan_version_id),
        "task_repo": _repo_path_for_version(real_daemon_harness, task_version_id),
    }


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
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_full_epic_tree_live_ai_workspace_merge_propagates_repo_files(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    expected_task_files = {
        "docs/notes.md": "seed docs\nlive ai merged note\n",
        "src/module.py": "VALUE = 'live-ai-merged'\n",
    }
    setup = _setup_bootstrapped_full_tree_git_hierarchy(
        real_daemon_harness,
        tmp_path,
        title="Live AI Workspace Merge",
        root_prompt=(
            "Descend through the hierarchy until you reach the leaf task. "
            "In the leaf task's current git repository, update docs/notes.md so it contains exactly "
            "'seed docs' on the first line and 'live ai merged note' on the second line with a trailing newline. "
            "Update src/module.py so it contains exactly \"VALUE = 'live-ai-merged'\" with a trailing newline. "
            "Do not change shared.txt and do not create extra files. "
            "Then run git add docs/notes.md src/module.py and git commit -m \"Live AI merged content\"."
        ),
    )
    epic_id = str(setup["epic_id"])
    phase_id = str(setup["phase_id"])
    implementation_phase_id = str(setup["implementation_phase_id"])
    plan_id = str(setup["plan_id"])
    task_id = str(setup["task_id"])
    epic_version_id = str(setup["epic_version_id"])
    phase_version_id = str(setup["phase_version_id"])
    plan_version_id = str(setup["plan_version_id"])
    task_repo = Path(setup["task_repo"])
    plan_repo = Path(setup["plan_repo"])
    phase_repo = Path(setup["phase_repo"])
    epic_repo = Path(setup["epic_repo"])

    session_names_to_cleanup: set[str] = set()
    try:
        session_name = _run_live_codex_repo_edit_in_tmux(
            repo_path=task_repo,
            instruction=(
                "In the current git repository, update docs/notes.md so it contains exactly "
                "'seed docs' on the first line and 'live ai merged note' on the second line with a trailing newline. "
                "Update src/module.py so it contains exactly \"VALUE = 'live-ai-merged'\" with a trailing newline. "
                "Do not change shared.txt and do not create extra files. "
                "Then run git add docs/notes.md src/module.py and git commit -m \"Live AI merged content\"."
            ),
            expected_files=expected_task_files,
            expected_commit_subject="Live AI merged content",
        )
        session_names_to_cleanup.add(session_name)

        _dump_tmux_pane(session_name, label="after live codex task repo edit")
        _print_find_snapshot(task_repo, label="task repo after live codex edit")
        _print_repo_snapshot(
            task_repo,
            label="task repo after live codex edit",
            tracked_files=["docs/notes.md", "src/module.py", "shared.txt"],
        )
        assert _repo_matches_expected_files(task_repo, expected_task_files)
        assert _git(task_repo, "status", "--short") == ""
        assert _git(task_repo, "log", "-1", "--pretty=%s") == "Live AI merged content"
        assert (task_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"

        task_finalize = _cli_dump(real_daemon_harness, "task finalize", "git", "finalize-node", "--node", task_id)
        task_final_commit_sha = str(task_finalize["final_commit_sha"])
        _transition_finalized_node_to_complete(real_daemon_harness, node_id=task_id)

        _wait_for(
            lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)
            if any(
                event["child_final_commit_sha"] == task_final_commit_sha
                for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)["events"]
            )
            else None,
            timeout_seconds=90.0,
            failure_message="Timed out waiting for plan incremental merge of the live AI task commit.",
        )

        plan_live_status = _cli_dump(real_daemon_harness, "plan live status", "git", "status", "show", "--version", plan_version_id)
        plan_merge_events = _cli_dump(real_daemon_harness, "plan merge events", "git", "merge-events", "show", "--node", plan_id)
        _print_find_snapshot(plan_repo, label="plan repo after task merge")
        _print_repo_snapshot(
            plan_repo,
            label="plan repo after task merge",
            tracked_files=["docs/notes.md", "src/module.py", "shared.txt"],
        )
        assert plan_live_status["working_tree_state"] == "merged_children"
        assert any(event["child_final_commit_sha"] == task_final_commit_sha for event in plan_merge_events["events"])
        assert _repo_matches_expected_files(plan_repo, expected_task_files)
        assert (plan_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
        assert _git(plan_repo, "status", "--short") == ""

        plan_finalize = _cli_dump(real_daemon_harness, "plan finalize", "git", "finalize-node", "--node", plan_id)
        plan_final_commit_sha = str(plan_finalize["final_commit_sha"])
        _transition_finalized_node_to_complete(real_daemon_harness, node_id=plan_id)

        _wait_for(
            lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)
            if any(
                event["child_final_commit_sha"] == plan_final_commit_sha
                for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)["events"]
            )
            else None,
            timeout_seconds=90.0,
            failure_message="Timed out waiting for phase incremental merge of the live AI plan final commit.",
        )

        phase_live_status = _cli_dump(real_daemon_harness, "phase live status", "git", "status", "show", "--version", phase_version_id)
        phase_merge_events = _cli_dump(real_daemon_harness, "phase merge events", "git", "merge-events", "show", "--node", phase_id)
        _print_find_snapshot(phase_repo, label="phase repo after plan merge")
        _print_repo_snapshot(
            phase_repo,
            label="phase repo after plan merge",
            tracked_files=["docs/notes.md", "src/module.py", "shared.txt"],
        )
        assert phase_live_status["working_tree_state"] == "merged_children"
        assert any(event["child_final_commit_sha"] == plan_final_commit_sha for event in phase_merge_events["events"])
        assert _repo_matches_expected_files(phase_repo, expected_task_files)
        assert (phase_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
        assert _git(phase_repo, "status", "--short") == ""

        phase_finalize = _cli_dump(real_daemon_harness, "phase finalize", "git", "finalize-node", "--node", phase_id)
        phase_final_commit_sha = str(phase_finalize["final_commit_sha"])
        _transition_finalized_node_to_complete(real_daemon_harness, node_id=phase_id)

        implementation_phase_finalize = _cli_dump(
            real_daemon_harness,
            "implementation phase finalize",
            "git",
            "finalize-node",
            "--node",
            implementation_phase_id,
        )
        implementation_phase_final_commit_sha = str(implementation_phase_finalize["final_commit_sha"])
        _transition_finalized_node_to_complete(real_daemon_harness, node_id=implementation_phase_id)

        _wait_for(
            lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)
            if {
                event["child_final_commit_sha"]
                for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)["events"]
            }
            >= {phase_final_commit_sha, implementation_phase_final_commit_sha}
            else None,
            timeout_seconds=90.0,
            failure_message="Timed out waiting for epic incremental merges after the live AI phase final commit.",
        )

        epic_merge_events = _cli_dump(real_daemon_harness, "epic merge events", "git", "merge-events", "show", "--node", epic_id)
        assert {event["child_final_commit_sha"] for event in epic_merge_events["events"]} >= {
            phase_final_commit_sha,
            implementation_phase_final_commit_sha,
        }
        epic_live_status = _cli_dump(real_daemon_harness, "epic live status", "git", "status", "show", "--version", epic_version_id)
        _print_find_snapshot(epic_repo, label="epic repo after phase merges")
        _print_repo_snapshot(
            epic_repo,
            label="epic repo after phase merges",
            tracked_files=["docs/notes.md", "src/module.py", "shared.txt"],
        )
        assert epic_live_status["working_tree_state"] == "merged_children"
        for repo_path in (task_repo, plan_repo, phase_repo, epic_repo):
            assert _repo_matches_expected_files(repo_path, expected_task_files)
            assert (repo_path / "shared.txt").read_text(encoding="utf-8") == "seed\n"
            assert _git(repo_path, "status", "--short") == ""
    finally:
        for session_name in session_names_to_cleanup:
            subprocess.run(["tmux", "kill-session", "-t", session_name], check=False, capture_output=True, text=True)


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_e2e_full_epic_tree_git_merge_propagates_task_changes_to_plan_phase_and_epic(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    setup = _setup_bootstrapped_full_tree_git_hierarchy(
        real_daemon_harness,
        tmp_path,
        title="Real E2E Full Epic Tree Git Merge",
    )
    epic_id = str(setup["epic_id"])
    phase_id = str(setup["phase_id"])
    implementation_phase_id = str(setup["implementation_phase_id"])
    plan_id = str(setup["plan_id"])
    task_id = str(setup["task_id"])
    epic_version_id = str(setup["epic_version_id"])
    phase_version_id = str(setup["phase_version_id"])
    implementation_phase_version_id = str(setup["implementation_phase_version_id"])
    plan_version_id = str(setup["plan_version_id"])
    task_version_id = str(setup["task_version_id"])
    task_repo = Path(setup["task_repo"])
    phase_repo = Path(setup["phase_repo"])
    plan_repo = Path(setup["plan_repo"])
    epic_repo = Path(setup["epic_repo"])

    (task_repo / "docs/notes.md").write_text("seed docs\ntask merged note\n", encoding="utf-8")
    (task_repo / "src/module.py").write_text("VALUE = 'task-merged'\n", encoding="utf-8")
    _git(task_repo, "add", ".")
    _git(task_repo, "commit", "-m", "Task merged content")

    task_finalize = _cli_dump(real_daemon_harness, "task finalize", "git", "finalize-node", "--node", task_id)
    task_final_commit_sha = str(task_finalize["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=task_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)
        if any(
            event["child_final_commit_sha"] == task_final_commit_sha
            for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)["events"]
        )
        else None,
        failure_message="Timed out waiting for plan incremental merge of the completed task.",
    )

    _assert_incremental_merge_boundary(
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

    implementation_phase_finalize = _cli_dump(
        real_daemon_harness,
        "implementation phase finalize",
        "git",
        "finalize-node",
        "--node",
        implementation_phase_id,
    )
    implementation_phase_final_commit_sha = str(implementation_phase_finalize["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=implementation_phase_id)

    plan_finalize = _cli_dump(real_daemon_harness, "plan finalize", "git", "finalize-node", "--node", plan_id)
    plan_final_show = _cli_dump(real_daemon_harness, "plan final show", "git", "final", "show", "--node", plan_id)
    plan_final_commit_sha = str(plan_final_show["final_commit_sha"])
    assert plan_finalize["final_commit_sha"] == plan_final_commit_sha
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=plan_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)
        if any(
            event["child_final_commit_sha"] == plan_final_commit_sha
            for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)["events"]
        )
        else None,
        failure_message="Timed out waiting for phase incremental merge of the completed plan.",
    )

    _assert_incremental_merge_boundary(
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

    phase_finalize = _cli_dump(real_daemon_harness, "phase finalize", "git", "finalize-node", "--node", phase_id)
    phase_final_show = _cli_dump(real_daemon_harness, "phase final show", "git", "final", "show", "--node", phase_id)
    phase_final_commit_sha = str(phase_final_show["final_commit_sha"])
    assert phase_finalize["final_commit_sha"] == phase_final_commit_sha
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=phase_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)
        if {
            event["child_final_commit_sha"] for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)["events"]
        }
        >= {phase_final_commit_sha, implementation_phase_final_commit_sha}
        else None,
        failure_message="Timed out waiting for epic incremental merges from both completed child phases.",
    )

    epic_child_results = _cli_dump(real_daemon_harness, "epic child results", "node", "child-results", "--node", epic_id)
    epic_reconcile = _cli_dump(real_daemon_harness, "epic reconcile", "node", "reconcile", "--node", epic_id)
    epic_finalize = _cli_dump(real_daemon_harness, "epic finalize", "git", "finalize-node", "--node", epic_id)
    epic_final_status = _cli_dump(real_daemon_harness, "epic final status", "git", "status", "show", "--version", epic_version_id)
    epic_final_show = _cli_dump(real_daemon_harness, "epic final show", "git", "final", "show", "--node", epic_id)
    epic_merge_events = _cli_dump(real_daemon_harness, "epic merge events", "git", "merge-events", "show", "--node", epic_id)

    assert epic_child_results["status"] == "ready_for_reconcile"
    assert len(epic_child_results["children"]) == 2
    event_by_child = {event["child_final_commit_sha"] for event in epic_merge_events["events"]}
    assert phase_final_commit_sha in event_by_child
    assert implementation_phase_final_commit_sha in event_by_child
    assert epic_reconcile["status"] == "ready_for_reconcile"
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


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_e2e_full_epic_tree_rectify_upstream_rebuild_resets_stale_content_and_replays_current_child_finals(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    setup = _setup_bootstrapped_full_tree_git_hierarchy(
        real_daemon_harness,
        tmp_path,
        title="Real E2E Full Epic Tree Rectify Rebuild",
    )
    epic_id = str(setup["epic_id"])
    phase_id = str(setup["phase_id"])
    implementation_phase_id = str(setup["implementation_phase_id"])
    plan_id = str(setup["plan_id"])
    task_id = str(setup["task_id"])
    epic_version_id = str(setup["epic_version_id"])
    phase_version_id = str(setup["phase_version_id"])
    implementation_phase_version_id = str(setup["implementation_phase_version_id"])
    plan_version_id = str(setup["plan_version_id"])
    task_version_id = str(setup["task_version_id"])
    epic_repo = Path(setup["epic_repo"])
    phase_repo = Path(setup["phase_repo"])
    implementation_phase_repo = Path(setup["implementation_phase_repo"])
    plan_repo = Path(setup["plan_repo"])
    task_repo = Path(setup["task_repo"])

    (task_repo / "docs/notes.md").write_text("seed docs\ntask merged note v1\n", encoding="utf-8")
    (task_repo / "src/module.py").write_text("VALUE = 'task-merged-v1'\n", encoding="utf-8")
    _git(task_repo, "add", ".")
    _git(task_repo, "commit", "-m", "Task merged content v1")
    task_finalize_v1 = _cli_dump(real_daemon_harness, "task finalize v1", "git", "finalize-node", "--node", task_id)
    task_final_commit_v1 = str(task_finalize_v1["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=task_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)
        if any(
            event["child_final_commit_sha"] == task_final_commit_v1
            for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", plan_id)["events"]
        )
        else None,
        failure_message="Timed out waiting for plan incremental merge of the first finalized task revision.",
    )

    (implementation_phase_repo / "ops/implementation.txt").write_text("implementation sibling v1\n", encoding="utf-8")
    _git(implementation_phase_repo, "add", ".")
    _git(implementation_phase_repo, "commit", "-m", "Implementation sibling v1")
    implementation_finalize_v1 = _cli_dump(
        real_daemon_harness,
        "implementation finalize v1",
        "git",
        "finalize-node",
        "--node",
        implementation_phase_id,
    )
    implementation_final_commit_v1 = str(implementation_finalize_v1["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=implementation_phase_id)

    plan_finalize_v1 = _cli_dump(real_daemon_harness, "plan finalize v1", "git", "finalize-node", "--node", plan_id)
    plan_final_commit_v1 = str(plan_finalize_v1["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=plan_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)
        if any(
            event["child_final_commit_sha"] == plan_final_commit_v1
            for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", phase_id)["events"]
        )
        else None,
        failure_message="Timed out waiting for phase incremental merge of the first finalized plan revision.",
    )

    phase_finalize_v1 = _cli_dump(real_daemon_harness, "phase finalize v1", "git", "finalize-node", "--node", phase_id)
    phase_final_commit_v1 = str(phase_finalize_v1["final_commit_sha"])
    _transition_finalized_node_to_complete(real_daemon_harness, node_id=phase_id)

    _wait_for(
        lambda: _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)
        if {
            event["child_final_commit_sha"] for event in _cli_json(real_daemon_harness, "git", "merge-events", "show", "--node", epic_id)["events"]
        }
        >= {phase_final_commit_v1, implementation_final_commit_v1}
        else None,
        failure_message="Timed out waiting for epic incremental merges of the first finalized child revisions.",
    )

    epic_finalize_v1 = _cli_dump(real_daemon_harness, "epic finalize v1", "git", "finalize-node", "--node", epic_id)
    first_epic_head = str(epic_finalize_v1["final_commit_sha"])
    assert (epic_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\ntask merged note v1\n"
    assert (epic_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'task-merged-v1'\n"
    assert (epic_repo / "ops/implementation.txt").read_text(encoding="utf-8") == "implementation sibling v1\n"

    task_supersede_v2 = _cli_dump(
        real_daemon_harness,
        "task supersede v2",
        "node",
        "supersede",
        "--node",
        task_id,
        "--title",
        "Rectify Task v2",
    )
    task_version_v2_id = str(task_supersede_v2["id"])
    _cli_dump(
        real_daemon_harness,
        "task bootstrap v2",
        "git",
        "bootstrap-node",
        "--version",
        task_version_v2_id,
        "--base-version",
        task_version_id,
        "--replace-existing",
    )
    task_v2_repo = _repo_path_for_version(real_daemon_harness, task_version_v2_id)
    (task_v2_repo / "docs/notes.md").write_text("seed docs\ntask merged note v2\n", encoding="utf-8")
    (task_v2_repo / "src/module.py").write_text("VALUE = 'task-merged-v2'\n", encoding="utf-8")
    _git(task_v2_repo, "add", ".")
    _git(task_v2_repo, "commit", "-m", "Task merged content v2")
    _cli_dump(real_daemon_harness, "task cutover v2", "node", "version", "cutover", "--version", task_version_v2_id)
    task_finalize_v2 = _cli_dump(real_daemon_harness, "task finalize v2", "git", "finalize-node", "--node", task_id)
    task_final_commit_v2 = str(task_finalize_v2["final_commit_sha"])
    coordination_before_rectify = _cli_dump(
        real_daemon_harness,
        "task rebuild coordination before rectify",
        "node",
        "rebuild-coordination",
        "--node",
        task_id,
        "--scope",
        "upstream",
    )

    rectify_result = _cli_dump(real_daemon_harness, "task rectify upstream", "node", "rectify-upstream", "--node", task_id)
    history_result = _cli_dump(real_daemon_harness, "task rebuild history", "node", "rebuild-history", "--node", task_id)
    epic_versions = _cli_dump(real_daemon_harness, "epic versions after rectify", "node", "versions", "--node", epic_id)
    phase_versions = _cli_dump(real_daemon_harness, "phase versions after rectify", "node", "versions", "--node", phase_id)
    plan_versions = _cli_dump(real_daemon_harness, "plan versions after rectify", "node", "versions", "--node", plan_id)

    epic_candidate_id = str(epic_versions["versions"][-1]["id"])
    phase_candidate_id = str(phase_versions["versions"][-1]["id"])
    plan_candidate_id = str(plan_versions["versions"][-1]["id"])
    plan_candidate_status = _cli_dump(real_daemon_harness, "plan candidate status", "git", "status", "show", "--version", plan_candidate_id)
    phase_candidate_status = _cli_dump(real_daemon_harness, "phase candidate status", "git", "status", "show", "--version", phase_candidate_id)
    epic_candidate_status = _cli_dump(real_daemon_harness, "epic candidate status", "git", "status", "show", "--version", epic_candidate_id)
    plan_candidate_repo = Path(str(plan_candidate_status["repo_path"]))
    phase_candidate_repo = Path(str(phase_candidate_status["repo_path"]))
    epic_candidate_repo = Path(str(epic_candidate_status["repo_path"]))
    plan_candidate_final_commit = str(plan_candidate_status["final_commit_sha"])
    phase_candidate_final_commit = str(phase_candidate_status["final_commit_sha"])
    epic_candidate_final_commit = str(epic_candidate_status["final_commit_sha"])

    assert coordination_before_rectify["status"] == "clear"
    assert not any(item["blocker_type"] == "active_primary_sessions" for item in coordination_before_rectify["blockers"])
    assert rectify_result["scope"] == "upstream"
    assert any(event["scope"] == "upstream" for event in history_result["events"])
    assert _git_show_file(plan_candidate_repo, plan_candidate_final_commit, "docs/notes.md") == "seed docs\ntask merged note v2"
    assert _git_show_file(plan_candidate_repo, plan_candidate_final_commit, "src/module.py") == "VALUE = 'task-merged-v2'"
    assert _git_show_file(phase_candidate_repo, phase_candidate_final_commit, "docs/notes.md") == "seed docs\ntask merged note v2"
    assert _git_show_file(phase_candidate_repo, phase_candidate_final_commit, "src/module.py") == "VALUE = 'task-merged-v2'"
    assert _git_show_file(epic_candidate_repo, epic_candidate_final_commit, "docs/notes.md") == "seed docs\ntask merged note v2"
    assert _git_show_file(epic_candidate_repo, epic_candidate_final_commit, "src/module.py") == "VALUE = 'task-merged-v2'"
    assert _git_show_file(epic_candidate_repo, epic_candidate_final_commit, "ops/implementation.txt") == "implementation sibling v1"
    assert _git_show_file(epic_candidate_repo, epic_candidate_final_commit, "shared.txt") == "seed"
    assert "task merged note v1" not in _git_show_file(epic_candidate_repo, epic_candidate_final_commit, "docs/notes.md")
    assert _git(plan_candidate_repo, "status", "--short") == ""
    assert _git(phase_candidate_repo, "status", "--short") == ""
    assert _git(epic_candidate_repo, "status", "--short") == ""

    readiness_result = _cli_dump(
        real_daemon_harness,
        "epic cutover readiness after rectify",
        "node",
        "version",
        "cutover-readiness",
        "--version",
        epic_candidate_id,
    )
    cutover_result = _cli_dump(real_daemon_harness, "epic cutover after rectify", "node", "version", "cutover", "--version", epic_candidate_id)
    epic_show = _cli_dump(real_daemon_harness, "epic show after rectify cutover", "node", "show", "--node", epic_id)
    phase_show = _cli_dump(real_daemon_harness, "phase show after rectify cutover", "node", "show", "--node", phase_id)
    plan_show = _cli_dump(real_daemon_harness, "plan show after rectify cutover", "node", "show", "--node", plan_id)
    task_show = _cli_dump(real_daemon_harness, "task show after rectify cutover", "node", "show", "--node", task_id)
    epic_merge_events = _cli_dump(real_daemon_harness, "epic merge events after rectify", "git", "merge-events", "show", "--node", epic_id)

    assert readiness_result["status"] == "ready"
    assert cutover_result["authoritative_node_version_id"] == epic_candidate_id
    assert epic_show["authoritative_node_version_id"] == epic_candidate_id
    assert phase_show["authoritative_node_version_id"] == phase_candidate_id
    assert plan_show["authoritative_node_version_id"] == plan_candidate_id
    assert task_show["authoritative_node_version_id"] == task_version_v2_id
    assert _git(epic_candidate_repo, "rev-parse", "HEAD") != first_epic_head
    assert any(event["child_final_commit_sha"] == task_final_commit_v2 for event in epic_merge_events["events"]) or task_final_commit_v2
