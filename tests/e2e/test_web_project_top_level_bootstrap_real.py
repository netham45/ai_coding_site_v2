from __future__ import annotations

import subprocess
from pathlib import Path

import httpx
import pytest


def _init_source_repo(repo_dir: Path) -> str:
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "README.md").write_text("# repo_alpha\n", encoding="utf-8")
    (repo_dir / "app.py").write_text("print('hello from source repo')\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "E2E User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "e2e@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()


@pytest.mark.e2e_real
def test_web_project_top_level_create_bootstraps_from_selected_source_repo(real_daemon_harness) -> None:
    repos_root = real_daemon_harness.workspace_root / "repos"
    source_repo = repos_root / "repo_alpha"
    source_head = _init_source_repo(source_repo)

    token = real_daemon_harness.read_token()
    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            f"{real_daemon_harness.base_url}/api/projects/repo_alpha/top-level-nodes",
            json={
                "kind": "epic",
                "title": "Website Project Bootstrap Epic",
                "prompt": "Create the website project bootstrap flow from the selected source repo.",
                "start_run": False,
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200, response.text
    payload = response.json()
    node_id = str(payload["node"]["node_id"])
    version_id = str(payload["node_version_id"])

    assert payload["status"] == "compiled"
    assert payload["bootstrap"]["repo_bootstrap_status"] == "bootstrapped"
    assert payload["bootstrap"]["seed_commit_sha"] == source_head
    assert payload["bootstrap"]["head_commit_sha"] == source_head
    assert payload["route_hint"]["url"] == f"/projects/repo_alpha/nodes/{node_id}/overview"

    branch_result = real_daemon_harness.cli("git", "branch", "show", "--version", version_id)
    status_result = real_daemon_harness.cli("git", "status", "show", "--version", version_id)
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert branch_result.exit_code == 0, branch_result.stderr
    assert status_result.exit_code == 0, status_result.stderr
    assert audit_result.exit_code == 0, audit_result.stderr

    branch_payload = branch_result.json()
    status_payload = status_result.json()
    audit_payload = audit_result.json()

    assert branch_payload["node_version_id"] == version_id
    assert branch_payload["seed_commit_sha"] == source_head
    assert branch_payload["active_branch_name"] == payload["bootstrap"]["branch_name"]
    assert status_payload["seed_commit_sha"] == source_head
    assert status_payload["head_commit_sha"] == source_head
    assert status_payload["working_tree_state"] == "seed_ready"
    assert Path(status_payload["repo_path"]).exists()
    assert (Path(status_payload["repo_path"]) / "README.md").exists()
    assert (Path(status_payload["repo_path"]) / "app.py").exists()
    assert audit_payload["authoritative_version_id"] == version_id
