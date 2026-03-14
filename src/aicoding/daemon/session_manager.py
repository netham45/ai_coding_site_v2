from __future__ import annotations

import os
import re
import shlex
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from aicoding.config import get_settings
from aicoding.daemon.live_git import repo_path_for_version

ORCHESTRATOR_SRC_ROOT = Path(__file__).resolve().parents[2]


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
    codex_home_path: str | None = None
    trusted_workspace_paths: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LocalPythonModuleCommand:
    command_text: str
    argv: tuple[str, ...]
    environment: dict[str, str]


def default_session_working_directory() -> str:
    workspace_root = get_settings().workspace_root
    if workspace_root is not None:
        return str(workspace_root)
    return str(Path.cwd())


def primary_session_execution_working_directory(*, node_version_id: UUID) -> str:
    repo_path = repo_path_for_version(node_version_id)
    if repo_path.exists() and (repo_path / ".git").exists():
        return str(repo_path)
    return default_session_working_directory()


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


def _runtime_artifact_root() -> Path:
    auth_token_file = os.environ.get("AICODING_AUTH_TOKEN_FILE", "").strip()
    if auth_token_file:
        return Path(auth_token_file).expanduser().resolve().parent
    workspace_root = get_settings().workspace_root
    if workspace_root is not None:
        return workspace_root / ".runtime"
    return Path.cwd() / ".runtime"


def codex_home_path_for_run(*, node_run_id: UUID) -> str:
    return str(_runtime_artifact_root() / "codex-home" / str(node_run_id))


def codex_home_path_for_child_session(*, parent_session_id: UUID, session_id: UUID) -> str:
    return str(_runtime_artifact_root() / "codex-home" / "child-sessions" / str(parent_session_id) / str(session_id))


def trusted_workspace_paths_for_codex(*, working_directory: str) -> tuple[str, ...]:
    working_path = Path(working_directory).expanduser().resolve()
    candidates: list[Path] = [working_path]
    parent = working_path.parent
    if parent != working_path:
        candidates.append(parent)
    workspace_root = get_settings().workspace_root
    if workspace_root is not None:
        workspace_path = workspace_root.expanduser().resolve()
        candidates.append(workspace_path)
        if workspace_path.parent != workspace_path:
            candidates.append(workspace_path.parent)
    unique: list[str] = []
    seen: set[str] = set()
    for candidate in candidates:
        normalized = str(candidate)
        if normalized not in seen:
            unique.append(normalized)
            seen.add(normalized)
    return tuple(unique)


def project_name_for_working_directory(working_directory: str) -> str:
    raw_name = Path(working_directory).resolve().name or "project"
    sanitized = re.sub(r"[^A-Za-z0-9._-]+", "_", raw_name).strip("._-")
    return sanitized or "project"


def _orchestrator_pythonpath() -> str:
    path_entries: list[str] = [str(ORCHESTRATOR_SRC_ROOT)]
    existing = os.environ.get("PYTHONPATH", "").strip()
    if existing:
        for entry in existing.split(os.pathsep):
            normalized = entry.strip()
            if normalized and normalized not in path_entries:
                path_entries.append(normalized)
    return os.pathsep.join(path_entries)


def repo_local_python_module_command(module: str, *args: str) -> LocalPythonModuleCommand:
    pythonpath = _orchestrator_pythonpath()
    command_parts = [f"PYTHONPATH={pythonpath}", "python3", "-m", module, *args]
    command_text = " ".join([command_parts[0], *[shlex.quote(part) for part in command_parts[1:]]])
    return LocalPythonModuleCommand(
        command_text=command_text,
        argv=(sys.executable, "-m", module, *args),
        environment={"PYTHONPATH": pythonpath},
    )


def current_stage_prompt_cli_command(*, logical_node_id: UUID) -> str:
    return repo_local_python_module_command(
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        str(logical_node_id),
    ).command_text


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


def child_prompt_path_for_session(
    *,
    working_directory: str,
    parent_session_id: UUID,
    session_id: UUID,
) -> str:
    project_name = project_name_for_working_directory(working_directory)
    return str(
        Path(working_directory)
        / "prompt_logs"
        / project_name
        / "child_sessions"
        / str(parent_session_id)
        / f"{session_id}.md"
    )


def _fresh_codex_instruction(*, prompt_cli_command: str) -> str:
    return (
        f"Please read the prompt from `{prompt_cli_command}` and run the prompt. "
        "When the prompt tells you to run a shell command, your next response must be an `exec_command` tool call for that exact command rather than prose. "
        "Use foreground shell commands for the requested daemon CLI steps; do not ask for `/review`, and do not leave short-lived CLI commands waiting in a background terminal. "
        "For fresh daemon subtask prompts, immediately run the foreground startup sequence described in the prompt, including `subtask current`, `subtask start`, and `subtask context`, before broader repository work."
    )


def _prompt_file_codex_instruction(*, prompt_file: str) -> str:
    return (
        f"Read the full task prompt from `{prompt_file}` and treat that file as the authoritative current-stage prompt for this turn. "
        "Do not start by re-fetching `subtask prompt`; only do that if the file is missing or unreadable and you must report that bounded failure. "
        "When the prompt tells you to run a shell command, your next response must be an `exec_command` tool call for that exact command rather than prose. "
        "Use foreground shell commands for the requested daemon CLI steps; do not ask for `/review`, and do not leave short-lived CLI commands waiting in a background terminal. "
        "After reading the file, execute the concrete next workflow step from that prompt instead of restating or reloading it."
    )


def codex_prompt_instruction(*, prompt_target: str, prompt_source: str = "cli") -> str:
    if prompt_source == "file":
        return _prompt_file_codex_instruction(prompt_file=prompt_target)
    return _fresh_codex_instruction(prompt_cli_command=prompt_target)


def fresh_codex_bootstrap_command(
    *,
    logical_node_id: UUID,
    prompt_log_path: str | None,
) -> str:
    parts = ["fresh", "--node", str(logical_node_id)]
    if prompt_log_path is not None:
        parts.extend(["--prompt-log-path", prompt_log_path])
    return repo_local_python_module_command(
        "aicoding.daemon.codex_session_bootstrap",
        *parts,
    ).command_text


def recovery_codex_resume_command() -> str:
    return repo_local_python_module_command(
        "aicoding.daemon.codex_session_bootstrap",
        "resume",
    ).command_text


def delegated_prompt_file_bootstrap_command(*, prompt_file: str) -> str:
    return repo_local_python_module_command(
        "aicoding.daemon.codex_session_bootstrap",
        "prompt-file",
        "--prompt-file",
        prompt_file,
    ).command_text


def default_interactive_shell_command() -> str:
    shell = os.environ.get("SHELL", "").strip() or "/bin/bash"
    quoted_shell = shlex.quote(shell)
    return f"{quoted_shell} -lc 'exec {quoted_shell} -li'"


def tmux_attach_command(session_name: str) -> str:
    return f"tmux attach-session -t {shlex.quote(session_name)}"


def build_primary_session_plan(
    *,
    node_version_id: UUID,
    logical_node_id: UUID,
    node_run_id: UUID,
    run_number: int,
    session_id: UUID,
    compiled_subtask_id: UUID | None = None,
) -> SessionLaunchPlan:
    session_name = f"aicoding-pri-r{run_number}-{str(node_run_id)[:8]}-{str(session_id)[:8]}"
    working_directory = primary_session_execution_working_directory(node_version_id=node_version_id)
    codex_home_path = codex_home_path_for_run(node_run_id=node_run_id)
    trusted_workspace_paths = trusted_workspace_paths_for_codex(working_directory=working_directory)
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
        environment={
            **session_runtime_environment(),
            "CODEX_HOME": codex_home_path,
            "AICODING_CODEX_TRUSTED_PATHS": os.pathsep.join(trusted_workspace_paths),
        },
        launch_mode="codex_fresh",
        prompt_cli_command=prompt_cli_command,
        prompt_log_path=prompt_log_path,
        codex_home_path=codex_home_path,
        trusted_workspace_paths=trusted_workspace_paths,
    )


def build_recovery_primary_session_plan(
    *,
    node_version_id: UUID,
    node_run_id: UUID,
    run_number: int,
    session_id: UUID,
) -> SessionLaunchPlan:
    session_name = f"aicoding-pri-r{run_number}-{str(node_run_id)[:8]}-{str(session_id)[:8]}"
    working_directory = primary_session_execution_working_directory(node_version_id=node_version_id)
    codex_home_path = codex_home_path_for_run(node_run_id=node_run_id)
    trusted_workspace_paths = trusted_workspace_paths_for_codex(working_directory=working_directory)
    return SessionLaunchPlan(
        session_name=session_name,
        command=recovery_codex_resume_command(),
        working_directory=working_directory,
        attach_command=tmux_attach_command(session_name),
        environment={
            **session_runtime_environment(),
            "CODEX_HOME": codex_home_path,
            "AICODING_CODEX_TRUSTED_PATHS": os.pathsep.join(trusted_workspace_paths),
        },
        launch_mode="codex_resume_last",
        codex_home_path=codex_home_path,
        trusted_workspace_paths=trusted_workspace_paths,
    )


def build_child_session_plan(
    *,
    parent_session_id: UUID,
    session_id: UUID,
) -> SessionLaunchPlan:
    session_name = f"aicoding-child-{str(parent_session_id)[:8]}-{str(session_id)[:8]}"
    working_directory = default_session_working_directory()
    codex_home_path = codex_home_path_for_child_session(parent_session_id=parent_session_id, session_id=session_id)
    trusted_workspace_paths = trusted_workspace_paths_for_codex(working_directory=working_directory)
    prompt_log_path = child_prompt_path_for_session(
        working_directory=working_directory,
        parent_session_id=parent_session_id,
        session_id=session_id,
    )
    return SessionLaunchPlan(
        session_name=session_name,
        command=delegated_prompt_file_bootstrap_command(prompt_file=prompt_log_path),
        working_directory=working_directory,
        attach_command=tmux_attach_command(session_name),
        environment={
            **session_runtime_environment(),
            "CODEX_HOME": codex_home_path,
            "AICODING_CODEX_TRUSTED_PATHS": os.pathsep.join(trusted_workspace_paths),
        },
        launch_mode="codex_prompt_file",
        prompt_log_path=prompt_log_path,
        codex_home_path=codex_home_path,
        trusted_workspace_paths=trusted_workspace_paths,
    )
