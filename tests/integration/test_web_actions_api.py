from __future__ import annotations

import subprocess
from pathlib import Path

from fastapi.testclient import TestClient

from aicoding.daemon.app import create_app


def _write_repo_catalog(workspace_root: Path, *repo_names: str) -> None:
    repos_root = workspace_root / "repos"
    repos_root.mkdir(parents=True, exist_ok=True)
    for repo_name in repo_names:
        repo_dir = repos_root / repo_name
        repo_dir.mkdir(parents=True, exist_ok=True)
        (repo_dir / "README.md").write_text(f"# {repo_name}\n", encoding="utf-8")


def _init_git_repo(repo_dir: Path) -> None:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)


def test_web_action_catalog_returns_bounded_daemon_actions(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha")
    _init_git_repo(workspace_root / "repos" / "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        headers = {"Authorization": "Bearer change-me"}
        create_response = app_client.post(
            "/api/projects/repo_alpha/top-level-nodes",
            headers=headers,
            json={
                "kind": "epic",
                "title": "Website UI bootstrap",
                "prompt": "Create the website UI workflow from the browser entry flow.",
                "start_run": True,
            },
        )
        node_id = create_response.json()["node"]["node_id"]
        actions_response = app_client.get(f"/api/nodes/{node_id}/actions", headers=headers)

    assert create_response.status_code == 200
    assert actions_response.status_code == 200
    payload = actions_response.json()
    assert payload["node_id"] == node_id
    action_ids = {item["action_id"] for item in payload["actions"]}
    assert {"start_run", "pause_run", "resume_run", "session_attach", "session_resume", "session_provider_resume", "regenerate_node"} <= action_ids

    start_run = next(item for item in payload["actions"] if item["action_id"] == "start_run")
    pause_run = next(item for item in payload["actions"] if item["action_id"] == "pause_run")
    regenerate = next(item for item in payload["actions"] if item["action_id"] == "regenerate_node")

    assert start_run["legal"] is False
    assert "already has a running run" in start_run["blocked_reason"]
    assert pause_run["legal"] is True
    assert pause_run["confirmation_label"] == "pause run"
    assert regenerate["confirmation_mode"] == "inline"
