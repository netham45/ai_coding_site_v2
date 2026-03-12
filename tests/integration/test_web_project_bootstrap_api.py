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


def _init_git_repo(repo_dir: Path) -> str:
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()


def test_project_catalog_lists_directories_under_workspace_repos(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha", "repo_beta")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.get("/api/projects", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert response.json() == {
        "daemon_context": {
            "reachability_state": "reachable",
            "auth_status": "valid",
            "daemon_app_name": "AI Coding Orchestrator",
            "daemon_version": "0.1.0",
            "authority": "daemon",
            "session_backend": "fake",
        },
        "projects": [
            {
                "project_id": "repo_alpha",
                "label": "repo_alpha",
                "source_path": "repos/repo_alpha",
                "bootstrap_ready": False,
                "readiness_code": "not_git_repo",
                "readiness_message": "Directory is not a git repository.",
                "default_branch": None,
                "head_commit_sha": None,
            },
            {
                "project_id": "repo_beta",
                "label": "repo_beta",
                "source_path": "repos/repo_beta",
                "bootstrap_ready": False,
                "readiness_code": "not_git_repo",
                "readiness_message": "Directory is not a git repository.",
                "default_branch": None,
                "head_commit_sha": None,
            },
        ]
    }


def test_project_catalog_returns_empty_list_when_repos_root_missing(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.get("/api/projects", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    assert response.json() == {
        "daemon_context": {
            "reachability_state": "reachable",
            "auth_status": "valid",
            "daemon_app_name": "AI Coding Orchestrator",
            "daemon_version": "0.1.0",
            "authority": "daemon",
            "session_backend": "fake",
        },
        "projects": [],
    }


def test_project_catalog_marks_git_bootstrap_readiness(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha", "repo_beta")
    source_head = _init_git_repo(workspace_root / "repos" / "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.get("/api/projects", headers={"Authorization": "Bearer change-me"})

    assert response.status_code == 200
    payload = response.json()
    projects = {item["project_id"]: item for item in payload["projects"]}

    assert projects["repo_alpha"]["bootstrap_ready"] is True
    assert projects["repo_alpha"]["readiness_code"] == "ready"
    assert projects["repo_alpha"]["readiness_message"] is None
    assert projects["repo_alpha"]["default_branch"] == "main"
    assert projects["repo_alpha"]["head_commit_sha"] == source_head

    assert projects["repo_beta"]["bootstrap_ready"] is False
    assert projects["repo_beta"]["readiness_code"] == "not_git_repo"
    assert projects["repo_beta"]["readiness_message"] == "Directory is not a git repository."
    assert projects["repo_beta"]["default_branch"] is None
    assert projects["repo_beta"]["head_commit_sha"] is None


def test_project_top_level_create_rejects_unknown_project(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.post(
            "/api/projects/repo_missing/top-level-nodes",
            headers={"Authorization": "Bearer change-me"},
            json={
                "kind": "epic",
                "title": "Missing project startup",
                "prompt": "This should fail because the project does not exist.",
            },
        )

    assert response.status_code == 404
    assert "project 'repo_missing' not found" in response.json()["detail"]


def test_project_top_level_create_starts_workflow_and_returns_route_hint(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha")
    source_head = _init_git_repo(workspace_root / "repos" / "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.post(
            "/api/projects/repo_alpha/top-level-nodes",
            headers={"Authorization": "Bearer change-me"},
            json={
                "kind": "epic",
                "title": "Website UI bootstrap",
                "prompt": "Create the website UI workflow from the browser entry flow.",
                "start_run": True,
            },
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "started"
    assert payload["project"] == {
        "project_id": "repo_alpha",
        "label": "repo_alpha",
        "source_path": "repos/repo_alpha",
        "bootstrap_ready": True,
        "readiness_code": "ready",
        "readiness_message": None,
        "default_branch": "main",
        "head_commit_sha": source_head,
    }
    assert payload["source_repo"] == payload["project"]
    assert payload["bootstrap"]["repo_bootstrap_status"] == "bootstrapped"
    assert payload["bootstrap"]["branch_name"]
    assert payload["bootstrap"]["seed_commit_sha"] == source_head
    assert payload["bootstrap"]["head_commit_sha"] == source_head
    assert payload["bootstrap"]["working_tree_state"] == "seed_ready"
    assert payload["node"]["kind"] == "epic"
    assert payload["node"]["title"] == "Website UI bootstrap"
    assert payload["compile"]["status"] == "compiled"
    assert payload["session"]["status"] == "bound"
    assert payload["session"]["backend"] == "fake"
    assert payload["route_hint"]["project_id"] == "repo_alpha"
    assert payload["route_hint"]["node_id"] == payload["node"]["node_id"]
    assert payload["route_hint"]["url"] == f"/projects/repo_alpha/nodes/{payload['node']['node_id']}/overview"


def test_project_top_level_create_rejects_non_git_source_repo(monkeypatch, tmp_path, migrated_public_schema) -> None:
    workspace_root = tmp_path / "workspace"
    _write_repo_catalog(workspace_root, "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))

    with TestClient(create_app()) as app_client:
        response = app_client.post(
            "/api/projects/repo_alpha/top-level-nodes",
            headers={"Authorization": "Bearer change-me"},
            json={
                "kind": "epic",
                "title": "Website UI bootstrap",
                "prompt": "Create the website UI workflow from the browser entry flow.",
                "start_run": True,
            },
        )

    assert response.status_code == 409
    assert "selected source repo is not a git repository" in response.json()["detail"]
