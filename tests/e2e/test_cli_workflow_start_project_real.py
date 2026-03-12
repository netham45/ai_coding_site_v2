from __future__ import annotations

import subprocess
import time
from pathlib import Path

import pytest


def _init_source_repo(repo_dir: Path) -> str:
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "README.md").write_text("# repo_alpha\n", encoding="utf-8")
    (repo_dir / "app.py").write_text("print('hello from cli project start')\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "E2E User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "e2e@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()


@pytest.mark.e2e_real
@pytest.mark.requires_tmux
@pytest.mark.requires_ai_provider
def test_cli_workflow_start_project_bootstraps_selected_source_repo(real_daemon_harness) -> None:
    source_repo = real_daemon_harness.workspace_root / "repos" / "repo_alpha"
    source_head = _init_source_repo(source_repo)

    start_result = real_daemon_harness.cli(
        "workflow",
        "start",
        "--project",
        "repo_alpha",
        "--kind",
        "epic",
        "--prompt",
        "Create a repo-backed top level epic through the CLI workflow start path.",
    )

    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    version_id = str(start_payload["node_version_id"])

    bind_result = real_daemon_harness.cli("session", "bind", "--node", node_id)
    assert bind_result.exit_code == 0, bind_result.stderr
    session_name = str(bind_result.json()["session_name"])

    run_show_payload = None
    last_pane_text = ""
    deadline = time.time() + 60.0
    while time.time() < deadline:
        run_show = real_daemon_harness.cli("node", "run", "show", "--node", node_id)
        assert run_show.exit_code == 0, run_show.stderr
        run_show_payload = run_show.json()
        last_pane_text = subprocess.run(
            ["tmux", "capture-pane", "-p", "-t", session_name],
            text=True,
            capture_output=True,
            check=False,
        ).stdout
        if (
            run_show_payload["latest_attempt"] is not None
            or run_show_payload["state"]["last_completed_compiled_subtask_id"] is not None
            or run_show_payload["run"]["run_status"] in {"FAILED", "PAUSED", "COMPLETED", "COMPLETE"}
        ):
            break
        time.sleep(2.0)

    branch_result = real_daemon_harness.cli("git", "branch", "show", "--version", version_id)
    status_result = real_daemon_harness.cli("git", "status", "show", "--version", version_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert branch_result.exit_code == 0, branch_result.stderr
    assert status_result.exit_code == 0, status_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    branch_payload = branch_result.json()
    status_payload = status_result.json()
    audit_payload = audit_result.json()

    assert start_payload["status"] == "started"
    assert start_payload["requested_start_run"] is True
    assert start_payload["bootstrap"]["repo_bootstrap_status"] == "bootstrapped"
    assert start_payload["bootstrap"]["seed_commit_sha"] == source_head
    assert run_show_payload is not None, (
        "Expected the repo-backed workflow start to produce durable run state after binding a real tmux/provider session.\n"
        f"session_name={session_name}\n"
        f"pane_text=\n{last_pane_text}"
    )
    assert branch_payload["seed_commit_sha"] == source_head
    assert status_payload["seed_commit_sha"] == source_head
    assert status_payload["head_commit_sha"] == source_head
    assert Path(status_payload["repo_path"]).exists()
    assert (Path(status_payload["repo_path"]) / "app.py").exists()
    assert audit_payload["authoritative_version_id"] == version_id
    assert audit_payload["run_count"] >= 1
