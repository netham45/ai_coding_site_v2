from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, text

from tests.helpers.e2e import RealDaemonHarness


class _ExitedProcess:
    def poll(self) -> int:
        return 0

    def terminate(self) -> None:
        raise AssertionError("terminate should not be called for an exited process")

    def wait(self, timeout: float | None = None) -> int:
        return 0

    def kill(self) -> None:
        raise AssertionError("kill should not be called for an exited process")


def test_real_daemon_harness_terminate_cleans_up_recorded_tmux_sessions(monkeypatch, tmp_path: Path) -> None:
    database_path = tmp_path / "e2e-harness.sqlite"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    try:
        with engine.begin() as connection:
            connection.execute(text("create table sessions (tmux_session_name text)"))
            connection.execute(
                text(
                    """
                    insert into sessions (tmux_session_name)
                    values ('aicoding-pri-r1-testaaaa-aaaa1111'),
                           (null),
                           (''),
                           ('aicoding-child-testbbbb-bbbb2222')
                    """
                )
            )
    finally:
        engine.dispose()

    calls: list[tuple[list[str], dict[str, str] | None]] = []

    def fake_run(command, **kwargs):
        calls.append((list(command), kwargs.get("env")))

        class _Result:
            returncode = 0
            stdout = ""
            stderr = ""

        return _Result()

    monkeypatch.setattr("tests.helpers.e2e.subprocess.run", fake_run)

    harness = RealDaemonHarness(
        env={"TMUX_TMPDIR": str(tmp_path / ".tmux")},
        base_url="http://127.0.0.1:9999",
        database_url=f"sqlite:///{database_path}",
        database_name="unused",
        token_file=tmp_path / "daemon.token",
        process=_ExitedProcess(),
        workspace_root=tmp_path / "workspace",
        stdout_log=tmp_path / "daemon.stdout.log",
        stderr_log=tmp_path / "daemon.stderr.log",
    )

    harness.terminate()

    assert calls == [
        (
            ["tmux", "kill-session", "-t", "aicoding-child-testbbbb-bbbb2222"],
            harness.env,
        ),
        (
            ["tmux", "kill-session", "-t", "aicoding-pri-r1-testaaaa-aaaa1111"],
            harness.env,
        ),
    ]
