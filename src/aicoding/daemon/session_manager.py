from __future__ import annotations

import os
import shlex
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID


@dataclass(frozen=True, slots=True)
class SessionLaunchPlan:
    session_name: str
    command: str
    working_directory: str
    attach_command: str | None


def default_session_working_directory() -> str:
    return str(Path.cwd())


def default_interactive_shell_command() -> str:
    shell = os.environ.get("SHELL", "").strip() or "/bin/bash"
    quoted_shell = shlex.quote(shell)
    return f"{quoted_shell} -lc 'exec {quoted_shell} -li'"


def tmux_attach_command(session_name: str) -> str:
    return f"tmux attach-session -t {shlex.quote(session_name)}"


def build_primary_session_plan(
    *,
    logical_node_id: UUID,
    node_run_id: UUID,
    run_number: int,
    session_id: UUID,
) -> SessionLaunchPlan:
    session_name = f"aicoding-pri-r{run_number}-{str(node_run_id)[:8]}-{str(session_id)[:8]}"
    return SessionLaunchPlan(
        session_name=session_name,
        command=default_interactive_shell_command(),
        working_directory=default_session_working_directory(),
        attach_command=tmux_attach_command(session_name),
    )


def build_child_session_plan(
    *,
    parent_session_id: UUID,
    session_id: UUID,
) -> SessionLaunchPlan:
    session_name = f"aicoding-child-{str(parent_session_id)[:8]}-{str(session_id)[:8]}"
    return SessionLaunchPlan(
        session_name=session_name,
        command=default_interactive_shell_command(),
        working_directory=default_session_working_directory(),
        attach_command=tmux_attach_command(session_name),
    )
