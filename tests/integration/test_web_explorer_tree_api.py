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


def test_project_bootstrap_returns_null_root_when_project_has_no_created_root(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.get("/api/projects/repo_alpha/bootstrap", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert response.json() == {
        "project": {
            "project_id": "repo_alpha",
            "label": "repo_alpha",
            "source_path": "repos/repo_alpha",
        },
        "root_node_id": None,
        "route_hint": None,
    }


def test_project_bootstrap_returns_latest_root_for_project(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha", "repo_beta")
    _init_git_repo(workspace_root / "repos" / "repo_alpha")
    _init_git_repo(workspace_root / "repos" / "repo_beta")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        headers = {"Authorization": "Bearer change-me"}
        first = app_client.post(
            "/api/projects/repo_alpha/top-level-nodes",
            headers=headers,
            json={
                "kind": "epic",
                "title": "First root",
                "prompt": "Create the first root for repo alpha.",
            },
        )
        second = app_client.post(
            "/api/projects/repo_beta/top-level-nodes",
            headers=headers,
            json={
                "kind": "epic",
                "title": "Beta root",
                "prompt": "Create the root for repo beta.",
            },
        )
        latest = app_client.post(
            "/api/projects/repo_alpha/top-level-nodes",
            headers=headers,
            json={
                "kind": "epic",
                "title": "Latest root",
                "prompt": "Create the latest root for repo alpha.",
            },
        )
        bootstrap = app_client.get("/api/projects/repo_alpha/bootstrap", headers=headers)

    assert first.status_code == 200
    assert second.status_code == 200
    assert latest.status_code == 200
    assert bootstrap.status_code == 200
    payload = bootstrap.json()
    assert payload["project"]["project_id"] == "repo_alpha"
    assert payload["root_node_id"] == latest.json()["node"]["node_id"]
    assert payload["route_hint"]["node_id"] == latest.json()["node"]["node_id"]
    assert payload["route_hint"]["url"] == f"/projects/repo_alpha/nodes/{latest.json()['node']['node_id']}/overview"
