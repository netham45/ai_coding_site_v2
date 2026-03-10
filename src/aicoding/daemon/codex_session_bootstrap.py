from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import UUID

from aicoding.daemon.session_manager import current_stage_prompt_cli_command


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
    command = [
        sys.executable,
        "-m",
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        str(logical_node_id),
    ]
    result = subprocess.run(command, check=False, text=True, capture_output=True)
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


def _exec_codex_fresh(prompt_cli_command: str) -> None:
    instruction = f"Please read the prompt from `{prompt_cli_command}` and run the prompt"
    os.execvp("codex", ["codex", "--yolo", instruction])


def _exec_codex_resume() -> None:
    os.execvp("codex", ["codex", "--yolo", "resume", "--last"])


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
