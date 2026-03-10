from __future__ import annotations

import os
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from aicoding.config import get_settings


@dataclass(frozen=True, slots=True)
class SessionLaunchPlan:
    session_name: str
    command: str
    working_directory: str
    attach_command: str | None
    environment: dict[str, str] | None = None
    launch_mode: str | None = None
    prompt_cli_command: str | None = None
    prompt_log_path: str | None = None


def default_session_working_directory() -> str:
    workspace_root = get_settings().workspace_root
    if workspace_root is not None:
        return str(workspace_root)
    return str(Path.cwd())


def session_runtime_environment() -> dict[str, str]:
    allowed_exact_keys = {
        "CODEX_HOME",
        "HOME",
        "LANG",
        "LOGNAME",
        "PATH",
        "PYTHONPATH",
        "SHELL",
        "TMP",
        "TMPDIR",
        "TEMP",
        "USER",
        "VIRTUAL_ENV",
        "XDG_CACHE_HOME",
        "XDG_CONFIG_HOME",
        "XDG_DATA_HOME",
    }
    allowed_prefixes = (
        "AICODING_",
        "OPENAI_",
    )
    environment: dict[str, str] = {}
    for key, value in os.environ.items():
        if key in allowed_exact_keys or key.startswith(allowed_prefixes):
            environment[key] = value
    return environment


def project_name_for_working_directory(working_directory: str) -> str:
    raw_name = Path(working_directory).resolve().name or "project"
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_name).strip("._-")
    return sanitized or "project"


def current_stage_prompt_cli_command(*, logical_node_id: UUID) -> str:
    parts = [
        sys.executable,
        "-m",
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        str(logical_node_id),
    ]
    return " ".join(shlex.quote(part) for part in parts)


def prompt_log_path_for_session(
    *,
    working_directory: str,
    logical_node_id: UUID,
    node_run_id: UUID,
    compiled_subtask_id: UUID | None,
) -> str | None:
    if compiled_subtask_id is None:
        return None
    project_name = project_name_for_working_directory(working_directory)
    return str(
        Path(working_directory)
        / "prompt_logs"
        / project_name
        / str(logical_node_id)
        / str(node_run_id)
        / f"{compiled_subtask_id}.md"
    )


def _fresh_codex_instruction(*, prompt_cli_command: str) -> str:
    return f"Please read the prompt from `{prompt_cli_command}` and run the prompt"


def fresh_codex_bootstrap_command(
    *,
    logical_node_id: UUID,
    prompt_log_path: str | None,
) -> str:
    parts = [
        sys.executable,
        "-m",
        "aicoding.daemon.codex_session_bootstrap",
        "fresh",
        "--node",
        str(logical_node_id),
    ]
    if prompt_log_path is not None:
        parts.extend(["--prompt-log-path", prompt_log_path])
    return " ".join(shlex.quote(part) for part in parts)


def recovery_codex_resume_command() -> str:
    parts = [
        sys.executable,
        "-m",
        "aicoding.daemon.codex_session_bootstrap",
        "resume",
    ]
    return " ".join(shlex.quote(part) for part in parts)


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
    compiled_subtask_id: UUID | None = None,
) -> SessionLaunchPlan:
    session_name = f"aicoding-pri-r{run_number}-{str(node_run_id)[:8]}-{str(session_id)[:8]}"
    working_directory = default_session_working_directory()
    prompt_cli_command = current_stage_prompt_cli_command(logical_node_id=logical_node_id)
    prompt_log_path = prompt_log_path_for_session(
        working_directory=working_directory,
        logical_node_id=logical_node_id,
        node_run_id=node_run_id,
        compiled_subtask_id=compiled_subtask_id,
    )
    return SessionLaunchPlan(
        session_name=session_name,
        command=fresh_codex_bootstrap_command(logical_node_id=logical_node_id, prompt_log_path=prompt_log_path),
        working_directory=working_directory,
        attach_command=tmux_attach_command(session_name),
        environment=session_runtime_environment(),
        launch_mode="codex_fresh",
        prompt_cli_command=prompt_cli_command,
        prompt_log_path=prompt_log_path,
    )


def build_recovery_primary_session_plan(
    *,
    node_run_id: UUID,
    run_number: int,
    session_id: UUID,
) -> SessionLaunchPlan:
    session_name = f"aicoding-pri-r{run_number}-{str(node_run_id)[:8]}-{str(session_id)[:8]}"
    return SessionLaunchPlan(
        session_name=session_name,
        command=recovery_codex_resume_command(),
        working_directory=default_session_working_directory(),
        attach_command=tmux_attach_command(session_name),
        environment=session_runtime_environment(),
        launch_mode="codex_resume_last",
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
        environment=session_runtime_environment(),
    )
