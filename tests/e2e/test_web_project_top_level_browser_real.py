from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest


def _init_source_repo(repo_dir: Path) -> str:
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "README.md").write_text("# repo_alpha\n", encoding="utf-8")
    (repo_dir / "app.py").write_text("print('hello from browser project start')\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "E2E User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "e2e@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()


@pytest.mark.e2e_real
@pytest.mark.requires_git
@pytest.mark.requires_tmux
def test_web_project_top_level_browser_flow_bootstraps_selected_source_repo(real_daemon_harness, tmp_path: Path) -> None:
    repo_root = Path(__file__).resolve().parents[2] / "frontend"
    subprocess.run(["npm", "run", "build"], cwd=repo_root, check=True, capture_output=True, text=True)

    repos_root = real_daemon_harness.workspace_root / "repos"
    source_repo = repos_root / "repo_alpha"
    source_head = _init_source_repo(source_repo)

    result_file = tmp_path / "real-project-start-result.json"
    env = {
        **real_daemon_harness.env,
        "PLAYWRIGHT_REAL_BASE_URL": real_daemon_harness.base_url,
        "PLAYWRIGHT_REAL_RESULT_FILE": str(result_file),
    }

    completed = subprocess.run(
        [
            "npx",
            "playwright",
            "test",
            "tests/e2e/real-project-start.spec.js",
            "-c",
            "playwright.real.config.js",
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr
    assert result_file.exists(), "Playwright real project-start spec did not write its result file."

    browser_result = json.loads(result_file.read_text(encoding="utf-8"))
    node_id = str(browser_result["nodeId"])
    assert browser_result["url"] == f"{real_daemon_harness.base_url}/projects/repo_alpha/nodes/{node_id}/overview"

    summary_response = real_daemon_harness.request("GET", f"/api/nodes/{node_id}/summary")
    audit_result = real_daemon_harness.cli("node", "audit", "--node", node_id)

    assert summary_response.status_code == 200, summary_response.text
    assert audit_result.exit_code == 0, audit_result.stderr

    summary_payload = summary_response.json()
    audit_payload = audit_result.json()
    version_id = str(audit_payload["authoritative_version_id"])

    branch_result = real_daemon_harness.cli("git", "branch", "show", "--version", version_id)
    status_result = real_daemon_harness.cli("git", "status", "show", "--version", version_id)

    assert branch_result.exit_code == 0, branch_result.stderr
    assert status_result.exit_code == 0, status_result.stderr

    branch_payload = branch_result.json()
    status_payload = status_result.json()

    assert summary_payload["title"] == "Website Project Bootstrap Epic"
    assert summary_payload["prompt"] == "Create the website project bootstrap flow from the selected source repo."
    assert summary_payload["run_status"] == "RUNNING"
    assert branch_payload["seed_commit_sha"] == source_head
    assert status_payload["seed_commit_sha"] == source_head
    assert status_payload["head_commit_sha"] == source_head
    assert status_payload["working_tree_state"] in {"seed_ready", "uninitialized"}
    assert Path(status_payload["repo_path"]).exists()
    assert (Path(status_payload["repo_path"]) / "README.md").exists()
    assert (Path(status_payload["repo_path"]) / "app.py").exists()
