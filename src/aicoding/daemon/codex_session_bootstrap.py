from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import shutil
import sys
import tomllib
from uuid import UUID

from aicoding.daemon.session_manager import current_stage_prompt_cli_command, repo_local_python_module_command


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap or resume a Codex-backed tmux session.")
    subparsers = parser.add_subparsers(dest="mode", required=True)

    fresh_parser = subparsers.add_parser("fresh", help="Fetch the current-stage prompt, log it, and exec into Codex.")
    fresh_parser.add_argument("--node", required=True)
    fresh_parser.add_argument("--prompt-log-path")

    subparsers.add_parser("resume", help="Resume the last Codex session.")
    return parser


def _extract_prompt_text(payload: dict[str, object]) -> str:
    prompt_text = payload.get("prompt_text")
    if isinstance(prompt_text, str) and prompt_text.strip():
        return prompt_text
    command_text = payload.get("command_text")
    if isinstance(command_text, str) and command_text.strip():
        return command_text
    return json.dumps(payload, indent=2, sort_keys=True)


def _run_prompt_cli_command(*, logical_node_id: UUID) -> tuple[str, dict[str, object]]:
    command = repo_local_python_module_command(
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        str(logical_node_id),
    )
    result = subprocess.run(
        list(command.argv),
        check=False,
        text=True,
        capture_output=True,
        env={**os.environ, **command.environment},
    )
    if result.returncode != 0:
        if result.stderr:
            print(result.stderr, file=sys.stderr, end="" if result.stderr.endswith("\n") else "\n")
        raise SystemExit(result.returncode)
    try:
        payload = json.loads(result.stdout)
    except ValueError as exc:
        print("Failed to parse subtask prompt output as JSON.", file=sys.stderr)
        if result.stdout:
            print(result.stdout, file=sys.stderr, end="" if result.stdout.endswith("\n") else "\n")
        raise SystemExit(2) from exc
    return current_stage_prompt_cli_command(logical_node_id=logical_node_id), payload


def _write_prompt_log(path_text: str | None, prompt_text: str) -> None:
    if not path_text:
        return
    path = Path(path_text)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(prompt_text, encoding="utf-8")


def _trusted_workspace_paths() -> tuple[Path, ...]:
    configured = os.environ.get("AICODING_CODEX_TRUSTED_PATHS", "").strip()
    if configured:
        raw_paths = [item.strip() for item in configured.split(os.pathsep) if item.strip()]
    else:
        cwd = str(Path.cwd().resolve())
        parent = str(Path.cwd().resolve().parent)
        raw_paths = [cwd, parent]
    unique: list[Path] = []
    seen: set[str] = set()
    for raw_path in raw_paths:
        normalized = str(Path(raw_path).expanduser().resolve())
        if normalized not in seen:
            unique.append(Path(normalized))
            seen.add(normalized)
    return tuple(unique)


def _source_codex_config_path() -> Path | None:
    home = os.environ.get("HOME", "").strip()
    if not home:
        return None
    path = Path(home).expanduser() / ".codex" / "config.toml"
    return path if path.is_file() else None


def _source_codex_auth_path() -> Path | None:
    home = os.environ.get("HOME", "").strip()
    if not home:
        return None
    path = Path(home).expanduser() / ".codex" / "auth.json"
    return path if path.is_file() else None


def _trusted_projects_from_config(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return set()
    projects = payload.get("projects")
    if not isinstance(projects, dict):
        return set()
    return {str(key) for key in projects.keys()}


def _trusted_project_table(path: Path) -> str:
    return f"[projects.{json.dumps(str(path))}]\ntrust_level = \"trusted\"\n"


def _ensure_codex_trusted_workspace_config() -> Path | None:
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if not codex_home:
        return None
    codex_home_path = Path(codex_home).expanduser().resolve()
    codex_home_path.mkdir(parents=True, exist_ok=True)
    config_path = codex_home_path / "config.toml"
    source_path = _source_codex_config_path()
    base_text = ""
    existing_trusted_paths: set[str] = set()
    if source_path is not None:
        base_text = source_path.read_text(encoding="utf-8")
        existing_trusted_paths = _trusted_projects_from_config(source_path)
    missing_blocks = [
        _trusted_project_table(path)
        for path in _trusted_workspace_paths()
        if str(path) not in existing_trusted_paths
    ]
    body = base_text.rstrip()
    if body and missing_blocks:
        body += "\n\n"
    body += "\n\n".join(block.rstrip() for block in missing_blocks)
    if body:
        body += "\n"
    config_path.write_text(body, encoding="utf-8")
    return config_path


def _ensure_codex_auth_state() -> Path | None:
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    if not codex_home:
        return None
    source_path = _source_codex_auth_path()
    if source_path is None:
        return None
    codex_home_path = Path(codex_home).expanduser().resolve()
    codex_home_path.mkdir(parents=True, exist_ok=True)
    target_path = codex_home_path / "auth.json"
    shutil.copy2(source_path, target_path)
    return target_path


def _codex_base_argv() -> list[str]:
    return ["codex", "-C", str(Path.cwd().resolve())]


def _exec_codex_fresh(prompt_cli_command: str) -> None:
    instruction = f"Please read the prompt from `{prompt_cli_command}` and run the prompt"
    _ensure_codex_auth_state()
    _ensure_codex_trusted_workspace_config()
    os.execvp("codex", [*_codex_base_argv(), "--yolo", instruction])


def _exec_codex_resume() -> None:
    _ensure_codex_auth_state()
    _ensure_codex_trusted_workspace_config()
    os.execvp("codex", [*_codex_base_argv(), "--yolo", "resume", "--last"])


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    if args.mode == "resume":
        _exec_codex_resume()
        return 0

    logical_node_id = UUID(args.node)
    prompt_cli_command, payload = _run_prompt_cli_command(logical_node_id=logical_node_id)
    _write_prompt_log(args.prompt_log_path, _extract_prompt_text(payload))
    _exec_codex_fresh(prompt_cli_command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
