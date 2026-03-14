from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

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


def _write_json(path: Path, payload: dict[str, str]) -> None:
    path.write_text(json.dumps(payload), encoding="utf-8")


@pytest.mark.e2e_real
@pytest.mark.requires_git
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_e2e_live_git_merge_and_finalize_verifies_parent_repo_contents(real_daemon_harness, tmp_path: Path) -> None:
    parent_create = real_daemon_harness.cli(
        "workflow",
        "start",
        "--kind",
        "epic",
        "--title",
        "Real Git Content Parent",
        "--prompt",
        "Create the merge parent node.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node"]["node_id"])

    parent_bind = real_daemon_harness.cli("session", "bind", "--node", parent_id)
    assert parent_bind.exit_code == 0, parent_bind.stderr
    parent_session_name = str(parent_bind.json()["session_name"])
    parent_run_show_payload = None
    parent_last_pane_text = ""
    parent_deadline = time.time() + 60.0
    while time.time() < parent_deadline:
        run_show = real_daemon_harness.cli("node", "run", "show", "--node", parent_id)
        assert run_show.exit_code == 0, run_show.stderr
        parent_run_show_payload = run_show.json()
        parent_last_pane_text = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", parent_session_name],
            text=True,
            capture_output=True,
            check=False,
        ).stdout
        if (
            parent_run_show_payload["latest_attempt"] is not None
            or parent_run_show_payload["state"]["last_completed_compiled_subtask_id"] is not None
            or parent_run_show_payload["run"]["run_status"] in {"FAILED", "PAUSED", "COMPLETED", "COMPLETE"}
        ):
            break
        time.sleep(2.0)

    assert parent_run_show_payload is not None, (
        "Expected the live git merge parent flow to produce durable run state after binding a real tmux/provider session.\n"
        f"session_name={parent_session_name}\n"
        f"pane_text=\n{parent_last_pane_text}"
    )

    child_a_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Content Child A",
        "--prompt",
        "Create the first merge child node.",
    )
    child_b_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Content Child B",
        "--prompt",
        "Create the second merge child node.",
    )
    assert child_a_create.exit_code == 0, child_a_create.stderr
    assert child_b_create.exit_code == 0, child_b_create.stderr
    child_a_id = str(child_a_create.json()["node_id"])
    child_b_id = str(child_b_create.json()["node_id"])

    child_a_compile = real_daemon_harness.cli("workflow", "compile", "--node", child_a_id)
    child_b_compile = real_daemon_harness.cli("workflow", "compile", "--node", child_b_id)
    assert child_a_compile.exit_code == 0, child_a_compile.stderr
    assert child_b_compile.exit_code == 0, child_b_compile.stderr
    assert child_a_compile.json()["status"] == "compiled", child_a_compile.stdout
    assert child_b_compile.json()["status"] == "compiled", child_b_compile.stdout
    child_a_start = real_daemon_harness.cli("node", "run", "start", "--node", child_a_id)
    child_b_start = real_daemon_harness.cli("node", "run", "start", "--node", child_b_id)
    assert child_a_start.exit_code == 0, child_a_start.stderr
    assert child_b_start.exit_code == 0, child_b_start.stderr
    assert child_a_start.json()["status"] == "admitted", child_a_start.stdout
    assert child_b_start.json()["status"] == "admitted", child_b_start.stdout
    child_a_bind = real_daemon_harness.cli("session", "bind", "--node", child_a_id)
    child_b_bind = real_daemon_harness.cli("session", "bind", "--node", child_b_id)
    assert child_a_bind.exit_code == 0, child_a_bind.stderr
    assert child_b_bind.exit_code == 0, child_b_bind.stderr

    parent_versions = real_daemon_harness.cli("node", "versions", "--node", parent_id)
    child_a_versions = real_daemon_harness.cli("node", "versions", "--node", child_a_id)
    child_b_versions = real_daemon_harness.cli("node", "versions", "--node", child_b_id)
    assert parent_versions.exit_code == 0, parent_versions.stderr
    assert child_a_versions.exit_code == 0, child_a_versions.stderr
    assert child_b_versions.exit_code == 0, child_b_versions.stderr
    parent_version_id = str(parent_versions.json()["versions"][0]["id"])
    child_a_version_id = str(child_a_versions.json()["versions"][0]["id"])
    child_b_version_id = str(child_b_versions.json()["versions"][0]["id"])

    seed_files_path = tmp_path / "seed-files.json"
    _write_json(
        seed_files_path,
        {
            "shared.txt": "seed\n",
            "docs/notes.md": "seed docs\n",
            "src/module.py": "VALUE = 'seed'\n",
        },
    )

    parent_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        parent_version_id,
        "--files-file",
        str(seed_files_path),
        "--replace-existing",
    )
    child_a_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_a_version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    child_b_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_b_version_id,
        "--base-version",
        parent_version_id,
        "--replace-existing",
    )
    assert parent_bootstrap.exit_code == 0, parent_bootstrap.stderr
    assert child_a_bootstrap.exit_code == 0, child_a_bootstrap.stderr
    assert child_b_bootstrap.exit_code == 0, child_b_bootstrap.stderr

    parent_status = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    child_a_status = real_daemon_harness.cli("git", "status", "show", "--version", child_a_version_id)
    child_b_status = real_daemon_harness.cli("git", "status", "show", "--version", child_b_version_id)
    assert parent_status.exit_code == 0, parent_status.stderr
    assert child_a_status.exit_code == 0, child_a_status.stderr
    assert child_b_status.exit_code == 0, child_b_status.stderr
    parent_repo = Path(parent_status.json()["repo_path"])
    child_a_repo = Path(child_a_status.json()["repo_path"])
    child_b_repo = Path(child_b_status.json()["repo_path"])

    (child_a_repo / "docs/notes.md").write_text("seed docs\nchild a docs\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A docs change")

    (child_b_repo / "src/module.py").write_text("VALUE = 'child-b'\n", encoding="utf-8")
    _git(child_b_repo, "add", ".")
    _git(child_b_repo, "commit", "-m", "Child B code change")

    child_a_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    child_b_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_b_id)
    assert child_a_finalize.exit_code == 0, child_a_finalize.stderr
    assert child_b_finalize.exit_code == 0, child_b_finalize.stderr
    child_a_final_payload = child_a_finalize.json()
    child_b_final_payload = child_b_finalize.json()

    merge_children = real_daemon_harness.cli("git", "merge-children", "--node", parent_id)
    assert merge_children.exit_code == 0, merge_children.stderr
    merge_payload = merge_children.json()

    assert merge_payload["status"] == "merged"
    assert len(merge_payload["merge_events"]) == 2
    assert merge_payload["merge_events"][0]["child_final_commit_sha"] == child_a_final_payload["final_commit_sha"]
    assert merge_payload["merge_events"][1]["child_final_commit_sha"] == child_b_final_payload["final_commit_sha"]

    assert (parent_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
    assert (parent_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\nchild a docs\n"
    assert (parent_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'child-b'\n"

    merged_head_sha = _git(parent_repo, "rev-parse", "HEAD")
    assert merged_head_sha == str(merge_payload["context_json"]["head_commit_sha"])
    assert _git(parent_repo, "status", "--short") == ""

    merge_commit_line = _git(parent_repo, "rev-list", "--parents", "-n", "1", merged_head_sha)
    assert len(merge_commit_line.split()) == 3
    diff_from_seed = set(_git(parent_repo, "diff", "--name-only", f"{parent_status.json()['seed_commit_sha']}..{merged_head_sha}").splitlines())
    assert diff_from_seed == {"docs/notes.md", "src/module.py"}

    finalize_parent = real_daemon_harness.cli("git", "finalize-node", "--node", parent_id)
    final_status = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    final_show = real_daemon_harness.cli("git", "final", "show", "--node", parent_id)
    merge_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
    assert finalize_parent.exit_code == 0, finalize_parent.stderr
    assert final_status.exit_code == 0, final_status.stderr
    assert final_show.exit_code == 0, final_show.stderr
    assert merge_events.exit_code == 0, merge_events.stderr

    finalize_payload = finalize_parent.json()
    final_status_payload = final_status.json()
    final_show_payload = final_show.json()
    merge_events_payload = merge_events.json()

    assert finalize_payload["final_commit_sha"] == _git(parent_repo, "rev-parse", "HEAD")
    assert final_show_payload["final_commit_sha"] == finalize_payload["final_commit_sha"]
    assert final_status_payload["working_tree_state"] == "finalized_clean"
    assert _git(parent_repo, "status", "--short") == ""
    assert (parent_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
    assert (parent_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\nchild a docs\n"
    assert (parent_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'child-b'\n"
    assert len(merge_events_payload["events"]) == 2
    assert [event["child_final_commit_sha"] for event in merge_events_payload["events"]] == [
        child_a_final_payload["final_commit_sha"],
        child_b_final_payload["final_commit_sha"],
    ]


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_e2e_live_git_merge_rerun_resets_to_seed_and_replays_current_child_finals(
    real_daemon_harness,
    tmp_path: Path,
) -> None:
    parent_create = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real Git Rerun Parent",
        "--prompt",
        "Create the merge parent node.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    child_a_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Rerun Child A",
        "--prompt",
        "Create the first child.",
    )
    child_b_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Rerun Child B",
        "--prompt",
        "Create the second child.",
    )
    assert child_a_create.exit_code == 0, child_a_create.stderr
    assert child_b_create.exit_code == 0, child_b_create.stderr
    child_a_id = str(child_a_create.json()["node_id"])
    child_b_id = str(child_b_create.json()["node_id"])

    parent_version_id = str(real_daemon_harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    child_a_version_id = str(real_daemon_harness.cli("node", "versions", "--node", child_a_id).json()["versions"][0]["id"])
    child_b_version_id = str(real_daemon_harness.cli("node", "versions", "--node", child_b_id).json()["versions"][0]["id"])

    seed_files_path = tmp_path / "rerun-seed-files.json"
    _write_json(
        seed_files_path,
        {
            "shared.txt": "seed\n",
            "docs/notes.md": "seed docs\n",
            "src/module.py": "VALUE = 'seed'\n",
        },
    )
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(seed_files_path), "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_a_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_b_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = real_daemon_harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    parent_repo = Path(real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id).json()["repo_path"])
    child_a_repo = Path(real_daemon_harness.cli("git", "status", "show", "--version", child_a_version_id).json()["repo_path"])
    child_b_repo = Path(real_daemon_harness.cli("git", "status", "show", "--version", child_b_version_id).json()["repo_path"])

    (child_a_repo / "docs/notes.md").write_text("seed docs\nchild a v1\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A v1")
    child_a_finalize_v1 = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    assert child_a_finalize_v1.exit_code == 0, child_a_finalize_v1.stderr

    (child_b_repo / "src/module.py").write_text("VALUE = 'child-b-v1'\n", encoding="utf-8")
    _git(child_b_repo, "add", ".")
    _git(child_b_repo, "commit", "-m", "Child B v1")
    child_b_finalize_v1 = real_daemon_harness.cli("git", "finalize-node", "--node", child_b_id)
    assert child_b_finalize_v1.exit_code == 0, child_b_finalize_v1.stderr

    first_merge = real_daemon_harness.cli("git", "merge-children", "--node", parent_id)
    assert first_merge.exit_code == 0, first_merge.stderr
    first_head = _git(parent_repo, "rev-parse", "HEAD")
    assert (parent_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\nchild a v1\n"
    assert (parent_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'child-b-v1'\n"
    assert _git(parent_repo, "status", "--short") == ""

    child_a_supersede = real_daemon_harness.cli("node", "supersede", "--node", child_a_id, "--title", "Real Git Rerun Child A v2")
    assert child_a_supersede.exit_code == 0, child_a_supersede.stderr
    child_a_version_v2_id = str(child_a_supersede.json()["id"])
    child_a_v2_bootstrap = real_daemon_harness.cli(
        "git",
        "bootstrap-node",
        "--version",
        child_a_version_v2_id,
        "--base-version",
        child_a_version_id,
        "--replace-existing",
    )
    assert child_a_v2_bootstrap.exit_code == 0, child_a_v2_bootstrap.stderr
    child_a_v2_repo = Path(real_daemon_harness.cli("git", "status", "show", "--version", child_a_version_v2_id).json()["repo_path"])
    (child_a_v2_repo / "docs/notes.md").write_text("seed docs\nchild a v2\n", encoding="utf-8")
    _git(child_a_v2_repo, "add", ".")
    _git(child_a_v2_repo, "commit", "-m", "Child A v2")
    child_a_cutover_v2 = real_daemon_harness.cli("node", "version", "cutover", "--version", child_a_version_v2_id)
    assert child_a_cutover_v2.exit_code == 0, child_a_cutover_v2.stderr
    child_a_finalize_v2 = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    assert child_a_finalize_v2.exit_code == 0, child_a_finalize_v2.stderr

    rerun_merge = real_daemon_harness.cli("git", "merge-children", "--node", parent_id)
    finalize_parent = real_daemon_harness.cli("git", "finalize-node", "--node", parent_id)
    assert rerun_merge.exit_code == 0, rerun_merge.stderr
    assert finalize_parent.exit_code == 0, finalize_parent.stderr

    rerun_head = _git(parent_repo, "rev-parse", "HEAD")
    assert rerun_head != first_head
    assert (parent_repo / "shared.txt").read_text(encoding="utf-8") == "seed\n"
    assert (parent_repo / "docs/notes.md").read_text(encoding="utf-8") == "seed docs\nchild a v2\n"
    assert (parent_repo / "src/module.py").read_text(encoding="utf-8") == "VALUE = 'child-b-v1'\n"
    assert "child a v1" not in (parent_repo / "docs/notes.md").read_text(encoding="utf-8")
    assert _git(parent_repo, "status", "--short") == ""

    rerun_events = real_daemon_harness.cli("git", "merge-events", "show", "--node", parent_id)
    assert rerun_events.exit_code == 0, rerun_events.stderr
    event_shas = [event["child_final_commit_sha"] for event in rerun_events.json()["events"]]
    assert event_shas[-2:] == [
        str(child_a_finalize_v2.json()["final_commit_sha"]),
        str(child_b_finalize_v1.json()["final_commit_sha"]),
    ]


@pytest.mark.e2e_real
@pytest.mark.requires_git
def test_e2e_live_git_conflict_abort_restores_seed_contents(real_daemon_harness, tmp_path: Path) -> None:
    parent_create = real_daemon_harness.cli(
        "node",
        "create",
        "--kind",
        "epic",
        "--title",
        "Real Git Conflict Parent",
        "--prompt",
        "Create the merge parent node.",
    )
    assert parent_create.exit_code == 0, parent_create.stderr
    parent_id = str(parent_create.json()["node_id"])

    child_a_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Conflict Child A",
        "--prompt",
        "Create the first child.",
    )
    child_b_create = real_daemon_harness.cli(
        "node",
        "child",
        "create",
        "--parent",
        parent_id,
        "--kind",
        "phase",
        "--title",
        "Real Git Conflict Child B",
        "--prompt",
        "Create the second child.",
    )
    assert child_a_create.exit_code == 0, child_a_create.stderr
    assert child_b_create.exit_code == 0, child_b_create.stderr
    child_a_id = str(child_a_create.json()["node_id"])
    child_b_id = str(child_b_create.json()["node_id"])

    parent_version_id = str(real_daemon_harness.cli("node", "versions", "--node", parent_id).json()["versions"][0]["id"])
    child_a_version_id = str(real_daemon_harness.cli("node", "versions", "--node", child_a_id).json()["versions"][0]["id"])
    child_b_version_id = str(real_daemon_harness.cli("node", "versions", "--node", child_b_id).json()["versions"][0]["id"])

    seed_files_path = tmp_path / "conflict-seed-files.json"
    _write_json(seed_files_path, {"shared.txt": "seed\nsame line\n"})
    for args in [
        ("git", "bootstrap-node", "--version", parent_version_id, "--files-file", str(seed_files_path), "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_a_version_id, "--base-version", parent_version_id, "--replace-existing"),
        ("git", "bootstrap-node", "--version", child_b_version_id, "--base-version", parent_version_id, "--replace-existing"),
    ]:
        result = real_daemon_harness.cli(*args)
        assert result.exit_code == 0, result.stderr

    parent_status = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    child_a_status = real_daemon_harness.cli("git", "status", "show", "--version", child_a_version_id)
    child_b_status = real_daemon_harness.cli("git", "status", "show", "--version", child_b_version_id)
    assert parent_status.exit_code == 0, parent_status.stderr
    assert child_a_status.exit_code == 0, child_a_status.stderr
    assert child_b_status.exit_code == 0, child_b_status.stderr
    parent_repo = Path(parent_status.json()["repo_path"])
    child_a_repo = Path(child_a_status.json()["repo_path"])
    child_b_repo = Path(child_b_status.json()["repo_path"])

    (child_a_repo / "shared.txt").write_text("seed\nchild a line\n", encoding="utf-8")
    _git(child_a_repo, "add", ".")
    _git(child_a_repo, "commit", "-m", "Child A conflict change")
    child_a_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_a_id)
    assert child_a_finalize.exit_code == 0, child_a_finalize.stderr

    (child_b_repo / "shared.txt").write_text("seed\nchild b line\n", encoding="utf-8")
    _git(child_b_repo, "add", ".")
    _git(child_b_repo, "commit", "-m", "Child B conflict change")
    child_b_finalize = real_daemon_harness.cli("git", "finalize-node", "--node", child_b_id)
    assert child_b_finalize.exit_code == 0, child_b_finalize.stderr

    merge_children = real_daemon_harness.cli("git", "merge-children", "--node", parent_id)
    assert merge_children.exit_code == 4
    assert merge_children.stderr_json()["error"] == "daemon_conflict"

    conflicted_text = (parent_repo / "shared.txt").read_text(encoding="utf-8")
    assert "<<<<<<< HEAD" in conflicted_text
    assert "child a line" in conflicted_text
    assert "child b line" in conflicted_text

    conflicts = real_daemon_harness.cli("git", "merge-conflicts", "show", "--node", parent_id)
    status_during_conflict = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    assert conflicts.exit_code == 0, conflicts.stderr
    assert status_during_conflict.exit_code == 0, status_during_conflict.stderr
    assert conflicts.json()["conflicts"]
    assert conflicts.json()["conflicts"][0]["resolution_status"] == "unresolved"
    assert "shared.txt" in conflicts.json()["conflicts"][0]["files_json"]
    assert status_during_conflict.json()["working_tree_state"] == "merge_conflict"

    abort_merge = real_daemon_harness.cli("git", "abort-merge", "--node", parent_id)
    status_after_abort = real_daemon_harness.cli("git", "status", "show", "--version", parent_version_id)
    assert abort_merge.exit_code == 0, abort_merge.stderr
    assert status_after_abort.exit_code == 0, status_after_abort.stderr
    assert (parent_repo / "shared.txt").read_text(encoding="utf-8") == "seed\nsame line\n"
    assert _git(parent_repo, "status", "--short") == ""
    assert _git(parent_repo, "rev-parse", "HEAD") == str(parent_status.json()["seed_commit_sha"])
    assert status_after_abort.json()["working_tree_state"] == "seed_ready"
