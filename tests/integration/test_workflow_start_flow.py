from __future__ import annotations

import subprocess
from pathlib import Path

from aicoding.config import get_settings
from aicoding.daemon.app import create_app
from fastapi.testclient import TestClient
from tests.helpers.daemon import DaemonBridgeClient

def test_daemon_workflow_start_creates_compiles_and_optionally_starts_run(app_client, migrated_public_schema) -> None:
    headers = {"Authorization": "Bearer change-me"}

    start_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "epic",
            "prompt": "Create a top-level epic from a prompt and start it.",
        },
    )
    compile_only_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "epic",
            "title": "Compile Only Startup",
            "prompt": "Create a top-level epic from a prompt without starting it.",
            "start_run": False,
        },
    )
    invalid_response = app_client.post(
        "/api/workflows/start",
        headers=headers,
        json={
            "kind": "task",
            "prompt": "This should be rejected because task is not top-level.",
        },
    )

    assert start_response.status_code == 200
    assert start_response.json()["status"] == "started"
    assert start_response.json()["compile"]["status"] == "compiled"
    assert start_response.json()["run_admission"]["status"] == "admitted"
    assert start_response.json()["run_progress"]["run"]["trigger_reason"] == "workflow_start"
    assert start_response.json()["lifecycle"]["lifecycle_state"] == "RUNNING"

    assert compile_only_response.status_code == 200
    assert compile_only_response.json()["status"] == "compiled"
    assert compile_only_response.json()["run_admission"] is None
    assert compile_only_response.json()["run_progress"] is None
    assert compile_only_response.json()["lifecycle"]["lifecycle_state"] == "READY"

    assert invalid_response.status_code == 409


def test_cli_workflow_start_and_top_level_node_create_flags_round_trip(
    cli_runner,
    daemon_bridge_client,
    migrated_public_schema,
    monkeypatch,
) -> None:
    monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: daemon_bridge_client)

    workflow_start = cli_runner(
        [
            "workflow",
            "start",
            "--kind",
            "epic",
            "--prompt",
            "Create and start a top-level epic through the CLI.",
        ]
    )
    node_create_compile = cli_runner(
        [
            "node",
            "create",
            "--kind",
            "epic",
            "--title",
            "Compile Via Node Create",
            "--prompt",
            "Compile without starting through node create.",
            "--compile",
        ]
    )

    assert workflow_start.exit_code == 0
    assert workflow_start.json()["status"] == "started"
    assert workflow_start.json()["run_progress"]["run"]["trigger_reason"] == "workflow_start"

    assert node_create_compile.exit_code == 0
    assert node_create_compile.json()["status"] == "compiled"
    assert node_create_compile.json()["run_admission"] is None


def _init_git_repo(repo_dir: Path) -> str:
    repo_dir.mkdir(parents=True, exist_ok=True)
    (repo_dir / "README.md").write_text("# repo_alpha\n", encoding="utf-8")
    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "add", "."], cwd=repo_dir, check=True, capture_output=True, text=True)
    subprocess.run(["git", "commit", "-m", "Initial source repo commit"], cwd=repo_dir, check=True, capture_output=True, text=True)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()


def test_cli_workflow_start_with_project_uses_repo_backed_route(
    cli_runner,
    migrated_public_schema,
    monkeypatch,
    tmp_path,
) -> None:
    workspace_root = tmp_path / "workspace"
    source_head = _init_git_repo(workspace_root / "repos" / "repo_alpha")
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    get_settings.cache_clear()
    with TestClient(create_app()) as app_client:
        bridge_client = DaemonBridgeClient(client=app_client, token="change-me")
        monkeypatch.setattr("aicoding.cli.handlers.build_daemon_client", lambda settings: bridge_client)

        workflow_start = cli_runner(
            [
                "workflow",
                "start",
                "--project",
                "repo_alpha",
                "--kind",
                "epic",
                "--prompt",
                "Create and compile a repo-backed top-level epic through the CLI.",
                "--no-run",
            ]
        )

        assert workflow_start.exit_code == 0
        payload = workflow_start.json()
        assert payload["status"] == "compiled"
        assert payload["bootstrap"]["repo_bootstrap_status"] == "bootstrapped"
        assert payload["bootstrap"]["seed_commit_sha"] == source_head
        assert payload["route_hint"]["project_id"] == "repo_alpha"
