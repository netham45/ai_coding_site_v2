from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url

from aicoding.db.migrations import create_alembic_config, upgrade_database


REPO_ROOT = Path(__file__).resolve().parents[2]


def reserve_local_listener(*, host: str = "127.0.0.1") -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, 0))
    sock.listen(socket.SOMAXCONN)
    sock.set_inheritable(True)
    return sock


@dataclass(frozen=True, slots=True)
class RealCLIResult:
    args: tuple[str, ...]
    exit_code: int
    stdout: str
    stderr: str

    def json(self) -> dict[str, object]:
        return json.loads(self.stdout)

    def stderr_json(self) -> dict[str, object]:
        start = self.stderr.find("{")
        if start == -1:
            raise json.JSONDecodeError("Expecting value", self.stderr, 0)
        return json.loads(self.stderr[start:])


class RealDaemonHarness:
    def __init__(
        self,
        *,
        env: dict[str, str],
        base_url: str,
        database_url: str,
        database_name: str,
        token_file: Path,
        process: subprocess.Popen[str],
        workspace_root: Path,
        stdout_log: Path,
        stderr_log: Path,
    ) -> None:
        self.env = env
        self.base_url = base_url
        self.database_url = database_url
        self.database_name = database_name
        self.token_file = token_file
        self.process = process
        self.workspace_root = workspace_root
        self.stdout_log = stdout_log
        self.stderr_log = stderr_log
        self._restart_count = 0

    def wait_until_ready(self, *, timeout_seconds: float = 45.0) -> None:
        deadline = time.time() + timeout_seconds
        last_error: str | None = None
        while time.time() < deadline:
            if self.process.poll() is not None:
                raise RuntimeError(self.dead_process_message("Real daemon process exited before becoming ready."))
            try:
                response = httpx.get(f"{self.base_url}/healthz", timeout=1.0)
                if response.status_code == 200 and self.token_file.exists():
                    return
            except httpx.HTTPError as exc:
                last_error = str(exc)
            time.sleep(0.1)
        raise RuntimeError(f"Timed out waiting for daemon readiness at {self.base_url}. Last error: {last_error}")

    def dead_process_message(self, prefix: str) -> str:
        stdout = self.stdout_log.read_text(encoding="utf-8") if self.stdout_log.exists() else ""
        stderr = self.stderr_log.read_text(encoding="utf-8") if self.stderr_log.exists() else ""
        return f"{prefix}\nstdout:\n{stdout}\nstderr:\n{stderr}"

    def assert_process_alive(self, *, prefix: str = "Real daemon process exited during E2E.") -> None:
        if self.process.poll() is not None:
            raise AssertionError(self.dead_process_message(prefix))

    def read_token(self) -> str:
        deadline = time.time() + 10.0
        while time.time() < deadline:
            if self.token_file.exists():
                token = self.token_file.read_text(encoding="utf-8").strip()
                if token:
                    return token
            time.sleep(0.1)
        raise RuntimeError(f"Timed out waiting for daemon token file: {self.token_file}")

    def cli(self, *args: str) -> RealCLIResult:
        command = [sys.executable, "-m", "aicoding.cli.main", *args]
        completed = subprocess.run(
            command,
            cwd=REPO_ROOT,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )
        return RealCLIResult(
            args=tuple(args),
            exit_code=int(completed.returncode),
            stdout=completed.stdout,
            stderr=completed.stderr,
        )

    def request(self, method: str, path: str, *, json_payload: dict[str, object] | None = None) -> httpx.Response:
        token = self.read_token()
        with httpx.Client(timeout=5.0) as client:
            return client.request(
                method,
                f"{self.base_url.rstrip('/')}/{path.lstrip('/')}",
                json=json_payload,
                headers={"Authorization": f"Bearer {token}"},
            )

    def terminate(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5.0)
        self.cleanup_tmux_sessions()

    def restart(self, *, extra_env: dict[str, str] | None = None) -> None:
        self.terminate()
        self._restart_count += 1
        listener = reserve_local_listener()
        port = int(listener.getsockname()[1])
        next_env = dict(self.env)
        next_env["AICODING_DAEMON_PORT"] = str(port)
        if extra_env:
            next_env.update(extra_env)
        next_stdout_log = self.stdout_log.with_name(f"{self.stdout_log.stem}.restart-{self._restart_count}{self.stdout_log.suffix}")
        next_stderr_log = self.stderr_log.with_name(f"{self.stderr_log.stem}.restart-{self._restart_count}{self.stderr_log.suffix}")
        process = launch_real_daemon_process(
            env=next_env,
            listener=listener,
            stdout_log=next_stdout_log,
            stderr_log=next_stderr_log,
        )
        self.env = next_env
        self.base_url = f"http://127.0.0.1:{port}"
        self.process = process
        self.stdout_log = next_stdout_log
        self.stderr_log = next_stderr_log
        self.wait_until_ready()

    def cleanup_tmux_sessions(self) -> None:
        for session_name in self._recorded_tmux_session_names():
            subprocess.run(
                ["tmux", "kill-session", "-t", session_name],
                cwd=REPO_ROOT,
                env=self.env,
                text=True,
                capture_output=True,
                check=False,
            )

    def _recorded_tmux_session_names(self) -> list[str]:
        engine = create_engine(self.database_url, future=True)
        try:
            with engine.connect() as connection:
                result = connection.execute(
                    text(
                        """
                        select distinct tmux_session_name
                        from sessions
                        where tmux_session_name is not null
                          and trim(tmux_session_name) <> ''
                        order by tmux_session_name
                        """
                    )
                )
                return [str(row[0]) for row in result if row[0]]
        except Exception:
            return []
        finally:
            engine.dispose()


def build_real_daemon_env(
    *,
    database_url: str,
    port: int,
    token_file: Path,
    workspace_root: Path,
    session_backend: str = "tmux",
    extra_env: dict[str, str] | None = None,
) -> dict[str, str]:
    env = os.environ.copy()
    python_path_parts = [str(REPO_ROOT / "src")]
    if env.get("PYTHONPATH"):
        python_path_parts.append(env["PYTHONPATH"])
    env.update(
        {
            "PYTHONPATH": os.pathsep.join(python_path_parts),
            "AICODING_DATABASE_URL": database_url,
            "AICODING_DAEMON_HOST": "127.0.0.1",
            "AICODING_DAEMON_PORT": str(port),
            # Real E2E flows exercise multi-step git merge/reconcile paths that
            # legitimately exceed the CLI's 30s default request timeout.
            "AICODING_DAEMON_REQUEST_TIMEOUT_SECONDS": "120",
            "AICODING_AUTH_TOKEN_FILE": str(token_file),
            "AICODING_AUTH_TOKEN": "change-me",
            "AICODING_SESSION_BACKEND": session_backend,
            "AICODING_ENV": "test",
            "AICODING_WORKSPACE_ROOT": str(workspace_root),
        }
    )
    if extra_env:
        env.update(extra_env)
    return env


def launch_real_daemon_process(
    *,
    env: dict[str, str],
    listener: socket.socket,
    stdout_log: Path,
    stderr_log: Path,
) -> subprocess.Popen[str]:
    try:
        with stdout_log.open("w", encoding="utf-8") as stdout_handle, stderr_log.open(
            "w", encoding="utf-8"
        ) as stderr_handle:
            process = subprocess.Popen(
                [
                    "python3",
                    "-m",
                    "uvicorn",
                    "aicoding.daemon.app:create_app",
                    "--factory",
                    "--fd",
                    str(listener.fileno()),
                ],
                cwd=REPO_ROOT,
                env=env,
                text=True,
                stdout=stdout_handle,
                stderr=stderr_handle,
                pass_fds=(listener.fileno(),),
            )
    finally:
        listener.close()
    return process


def build_e2e_database_name(*, prefix: str = "aicoding_e2e") -> str:
    return f"{prefix}_{uuid4().hex}"


def derive_admin_database_url(database_url: str, *, admin_database: str = "postgres") -> str:
    return make_url(database_url).set(database=admin_database).render_as_string(hide_password=False)


def derive_test_database_url(database_url: str, *, database_name: str) -> str:
    return make_url(database_url).set(database=database_name).render_as_string(hide_password=False)


def create_test_database(*, database_url: str, database_name: str) -> str:
    admin_url = derive_admin_database_url(database_url)
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(text(f'CREATE DATABASE "{database_name}"'))
    finally:
        engine.dispose()
    return derive_test_database_url(database_url, database_name=database_name)


def migrate_test_database(*, database_url: str) -> None:
    config = create_alembic_config()
    config.attributes["override_sqlalchemy_url"] = database_url
    upgrade_database("head", config=config)


def drop_test_database(*, database_url: str, database_name: str) -> None:
    admin_url = derive_admin_database_url(database_url)
    engine = create_engine(admin_url, isolation_level="AUTOCOMMIT", pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            connection.execute(
                text(
                    """
                    select pg_terminate_backend(pid)
                    from pg_stat_activity
                    where datname = :database_name
                      and usename = current_user
                      and pid <> pg_backend_pid()
                    """
                ),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
    finally:
        engine.dispose()
