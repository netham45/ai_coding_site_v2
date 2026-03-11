from __future__ import annotations

import subprocess
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
        "--no-run",
    )

    assert start_result.exit_code == 0, start_result.stderr
    start_payload = start_result.json()
    node_id = str(start_payload["node"]["node_id"])
    version_id = str(start_payload["node_version_id"])

    branch_result = real_daemon_harness.cli("git", "branch", "show", "--version", version_id)
    status_result = real_daemon_harness.cli("git", "status", "show", "--version", version_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert branch_result.exit_code == 0, branch_result.stderr
    assert status_result.exit_code == 0, status_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    branch_payload = branch_result.json()
    status_payload = status_result.json()
    audit_payload = audit_result.json()

    assert start_payload["status"] == "compiled"
    assert start_payload["bootstrap"]["repo_bootstrap_status"] == "bootstrapped"
    assert start_payload["bootstrap"]["seed_commit_sha"] == source_head
    assert branch_payload["seed_commit_sha"] == source_head
    assert status_payload["seed_commit_sha"] == source_head
    assert status_payload["head_commit_sha"] == source_head
    assert Path(status_payload["repo_path"]).exists()
    assert (Path(status_payload["repo_path"]) / "app.py").exists()
    assert audit_payload["authoritative_version_id"] == version_id
