from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from subprocess import CompletedProcess, run
from typing import Protocol

from aicoding.config import Settings, get_settings
from aicoding.errors import ConfigurationError


@dataclass(frozen=True, slots=True)
class SessionSnapshot:
    session_name: str
    command: str
    working_directory: str
    backend: str
    exists: bool
    created_at: datetime
    last_activity_at: datetime
    pane_text: str = ""
    in_alt_screen: bool = False
    process_alive: bool = True
    exit_status: int | None = None


@dataclass(frozen=True, slots=True)
class SessionPollResult:
    snapshot: SessionSnapshot
    idle_seconds: float
    is_idle: bool


class SessionAdapter(Protocol):
    backend_name: str

    def create_session(
        self,
        session_name: str,
        command: str,
        working_directory: str,
        environment: dict[str, str] | None = None,
    ) -> SessionSnapshot: ...
    def session_exists(self, session_name: str) -> bool: ...
    def capture_pane(self, session_name: str, *, include_alt_screen: bool = False) -> str: ...
    def send_input(self, session_name: str, text: str, *, press_enter: bool = True) -> None: ...
    def kill_session(self, session_name: str) -> None: ...
    def list_sessions(self) -> list[str]: ...
    def latest_snapshot(self) -> SessionSnapshot | None: ...
    def describe(self, session_name: str) -> SessionSnapshot | None: ...


class TmuxSessionAdapter:
    backend_name = "tmux"

    def _run(self, *args: str) -> CompletedProcess[str]:
        return run(["tmux", *args], check=False, text=True, capture_output=True)

    def create_session(
        self,
        session_name: str,
        command: str,
        working_directory: str,
        environment: dict[str, str] | None = None,
    ) -> SessionSnapshot:
        args = ["new-session", "-d", "-s", session_name, "-c", working_directory]
        if environment:
            for key, value in sorted(environment.items()):
                args.extend(["-e", f"{key}={value}"])
        args.extend(
            [
                ";",
                "set-option",
                "-t",
                session_name,
                "remain-on-exit",
                "on",
                ";",
                "respawn-pane",
                "-k",
                "-t",
                session_name,
                command,
            ]
        )
        result = self._run(*args)
        if result.returncode != 0:
            raise ConfigurationError(
                message="Failed to create tmux session.",
                code="tmux_create_failed",
                details={"session_name": session_name, "stderr": result.stderr.strip()},
            )
        return self.describe(session_name) or SessionSnapshot(
            session_name=session_name,
            command=command,
            working_directory=working_directory,
            backend=self.backend_name,
            exists=True,
            created_at=datetime.now(timezone.utc),
            last_activity_at=datetime.now(timezone.utc),
            process_alive=True,
            exit_status=None,
        )

    def session_exists(self, session_name: str) -> bool:
        return self._run("has-session", "-t", session_name).returncode == 0

    def capture_pane(self, session_name: str, *, include_alt_screen: bool = False) -> str:
        args = ["capture-pane", "-p", "-t", session_name]
        if include_alt_screen:
            args.insert(1, "-a")
        result = self._run(*args)
        if include_alt_screen and result.returncode != 0 and "no alternate screen" in result.stderr:
            result = self._run("capture-pane", "-p", "-t", session_name)
        if result.returncode != 0:
            raise ConfigurationError(
                message="Failed to capture tmux pane.",
                code="tmux_capture_failed",
                details={"session_name": session_name, "stderr": result.stderr.strip()},
            )
        return result.stdout

    def send_input(self, session_name: str, text: str, *, press_enter: bool = True) -> None:
        args = ["send-keys", "-t", session_name, text]
        if press_enter:
            args.append("Enter")
        result = self._run(*args)
        if result.returncode != 0:
            raise ConfigurationError(
                message="Failed to send input to tmux session.",
                code="tmux_send_failed",
                details={"session_name": session_name, "stderr": result.stderr.strip()},
            )

    def kill_session(self, session_name: str) -> None:
        self._run("kill-session", "-t", session_name)

    def list_sessions(self) -> list[str]:
        result = self._run("list-sessions", "-F", "#{session_name}")
        if result.returncode != 0:
            return []
        return [line for line in result.stdout.splitlines() if line]

    def latest_snapshot(self) -> SessionSnapshot | None:
        sessions = self.list_sessions()
        if not sessions:
            return None
        return self.describe(sessions[-1])

    def describe(self, session_name: str) -> SessionSnapshot | None:
        if not self.session_exists(session_name):
            return None
        pane_text = self.capture_pane(session_name)
        metadata = self._load_metadata(session_name)
        return SessionSnapshot(
            session_name=session_name,
            command=metadata["command"],
            working_directory=metadata["working_directory"],
            backend=self.backend_name,
            exists=True,
            created_at=metadata["created_at"],
            last_activity_at=metadata["last_activity_at"],
            pane_text=pane_text,
            in_alt_screen=metadata["in_alt_screen"],
            process_alive=bool(metadata["process_alive"]),
            exit_status=metadata["exit_status"],
        )

    def _load_metadata(self, session_name: str) -> dict[str, object]:
        template = (
            "#{pane_current_command}\t#{pane_current_path}\t#{session_created}\t#{session_activity}\t"
            "#{alternate_on}\t#{pane_dead}\t#{pane_dead_status}"
        )
        result = self._run("display-message", "-p", "-t", session_name, template)
        if result.returncode != 0:
            now = datetime.now(timezone.utc)
            return {
                "command": "tmux-managed",
                "working_directory": str(Path.cwd()),
                "created_at": now,
                "last_activity_at": now,
                "in_alt_screen": False,
                "process_alive": True,
                "exit_status": None,
            }
        command, working_directory, created_raw, activity_raw, alt_raw, pane_dead_raw, exit_status_raw = (
            result.stdout.rstrip("\n").split("\t") + ["", "", "", "", "", "", ""]
        )[:7]
        process_alive = pane_dead_raw != "1"
        exit_status: int | None = None
        if pane_dead_raw == "1":
            try:
                exit_status = int(exit_status_raw)
            except (TypeError, ValueError):
                exit_status = None
        return {
            "command": command or "tmux-managed",
            "working_directory": working_directory or str(Path.cwd()),
            "created_at": self._parse_tmux_epoch(created_raw),
            "last_activity_at": self._parse_tmux_epoch(activity_raw),
            "in_alt_screen": alt_raw == "1",
            "process_alive": process_alive,
            "exit_status": exit_status,
        }

    def _parse_tmux_epoch(self, raw: str) -> datetime:
        try:
            return datetime.fromtimestamp(int(raw), tz=timezone.utc)
        except (TypeError, ValueError):
            return datetime.now(timezone.utc)


@dataclass
class FakeSessionState:
    session_name: str
    command: str
    working_directory: str
    created_at: datetime
    last_activity_at: datetime
    pane_text: str = ""
    in_alt_screen: bool = False
    process_alive: bool = True
    exit_status: int | None = None


@dataclass
class FakeSessionAdapter:
    backend_name: str = "fake"
    now: callable = field(default=lambda: datetime.now(timezone.utc))
    _sessions: dict[str, FakeSessionState] = field(default_factory=dict)
    _creation_order: list[str] = field(default_factory=list)

    def create_session(
        self,
        session_name: str,
        command: str,
        working_directory: str,
        environment: dict[str, str] | None = None,
    ) -> SessionSnapshot:
        current_time = self.now()
        state = FakeSessionState(
            session_name=session_name,
            command=command,
            working_directory=working_directory,
            created_at=current_time,
            last_activity_at=current_time,
            pane_text=f"$ {command}\n",
        )
        self._sessions[session_name] = state
        if session_name not in self._creation_order:
            self._creation_order.append(session_name)
        return self._snapshot(state)

    def session_exists(self, session_name: str) -> bool:
        return session_name in self._sessions

    def capture_pane(self, session_name: str, *, include_alt_screen: bool = False) -> str:
        state = self._sessions[session_name]
        if state.in_alt_screen and not include_alt_screen:
            return ""
        return state.pane_text

    def send_input(self, session_name: str, text: str, *, press_enter: bool = True) -> None:
        state = self._sessions[session_name]
        suffix = "\n" if press_enter else ""
        state.pane_text += f"{text}{suffix}"
        state.last_activity_at = self.now()

    def kill_session(self, session_name: str) -> None:
        self._sessions.pop(session_name, None)
        self._creation_order = [name for name in self._creation_order if name != session_name]

    def list_sessions(self) -> list[str]:
        return list(self._creation_order)

    def latest_snapshot(self) -> SessionSnapshot | None:
        if not self._creation_order:
            return None
        return self.describe(self._creation_order[-1])

    def describe(self, session_name: str) -> SessionSnapshot | None:
        state = self._sessions.get(session_name)
        if state is None:
            return None
        return self._snapshot(state)

    def set_alt_screen(self, session_name: str, enabled: bool) -> None:
        self._sessions[session_name].in_alt_screen = enabled

    def advance_idle(self, session_name: str, *, seconds: float) -> None:
        state = self._sessions[session_name]
        state.last_activity_at = state.last_activity_at - timedelta(seconds=seconds)

    def terminate_process(self, session_name: str, *, exit_status: int = 0) -> None:
        state = self._sessions[session_name]
        state.process_alive = False
        state.exit_status = exit_status

    def _snapshot(self, state: FakeSessionState) -> SessionSnapshot:
        return SessionSnapshot(
            session_name=state.session_name,
            command=state.command,
            working_directory=state.working_directory,
            backend=self.backend_name,
            exists=True,
            created_at=state.created_at,
            last_activity_at=state.last_activity_at,
            pane_text=state.pane_text,
            in_alt_screen=state.in_alt_screen,
            process_alive=state.process_alive,
            exit_status=state.exit_status,
        )


@dataclass(frozen=True, slots=True)
class SessionPoller:
    adapter: SessionAdapter
    idle_threshold_seconds: float
    now: callable

    def poll(self, session_name: str) -> SessionPollResult:
        snapshot = self.adapter.describe(session_name)
        if snapshot is None:
            raise ConfigurationError(
                message="Session does not exist.",
                code="session_not_found",
                details={"session_name": session_name},
            )
        idle_seconds = max((self.now() - snapshot.last_activity_at).total_seconds(), 0.0)
        return SessionPollResult(
            snapshot=snapshot,
            idle_seconds=idle_seconds,
            is_idle=idle_seconds >= self.idle_threshold_seconds,
        )


def build_session_adapter(settings: Settings | None = None) -> SessionAdapter:
    active_settings = settings or get_settings()
    session_settings = active_settings.session
    if session_settings.backend == "fake":
        return FakeSessionAdapter()
    if session_settings.backend == "tmux":
        return TmuxSessionAdapter()
    raise ConfigurationError(
        message="Unknown session backend configured.",
        code="session_backend_unknown",
        details={"session_backend": session_settings.backend},
    )
