from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from aicoding.config import get_settings
from tests.helpers.e2e import (
    RealDaemonHarness,
    allocate_local_port,
    build_e2e_database_name,
    build_real_daemon_env,
    create_test_database,
    drop_test_database,
    migrate_test_database,
)


@pytest.fixture
def real_daemon_harness_factory(tmp_path: Path):
    harnesses: list[RealDaemonHarness] = []
    created_databases: list[tuple[str, str]] = []

    def factory(*, session_backend: str = "tmux", extra_env: dict[str, str] | None = None) -> RealDaemonHarness:
        port = allocate_local_port()
        runtime_dir = tmp_path / f".runtime-{len(harnesses)}"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        token_file = runtime_dir / "daemon.token"
        workspace_root = tmp_path / f"workspace-{len(harnesses)}"
        workspace_root.mkdir(parents=True, exist_ok=True)
        base_database_url = get_settings().database_url
        database_name = build_e2e_database_name()
        database_url = create_test_database(database_url=base_database_url, database_name=database_name)
        created_databases.append((base_database_url, database_name))
        migrate_test_database(database_url=database_url)
        env = build_real_daemon_env(
            database_url=database_url,
            port=port,
            token_file=token_file,
            workspace_root=workspace_root,
            session_backend=session_backend,
            extra_env=extra_env,
        )
        process = subprocess.Popen(
            [
                "python3",
                "-m",
                "uvicorn",
                "aicoding.daemon.app:create_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
            ],
            cwd=Path(__file__).resolve().parents[2],
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        harness = RealDaemonHarness(
            env=env,
            base_url=f"http://127.0.0.1:{port}",
            database_url=database_url,
            database_name=database_name,
            token_file=token_file,
            process=process,
            workspace_root=workspace_root,
        )
        harness.wait_until_ready()
        harnesses.append(harness)
        return harness

    try:
        yield factory
    finally:
        for harness in reversed(harnesses):
            harness.terminate()
        for base_database_url, database_name in reversed(created_databases):
            drop_test_database(database_url=base_database_url, database_name=database_name)


@pytest.fixture
def real_daemon_harness(real_daemon_harness_factory) -> RealDaemonHarness:
    return real_daemon_harness_factory()
