from __future__ import annotations

import json
from dataclasses import dataclass

from aicoding.cli.app import run


@dataclass(frozen=True, slots=True)
class CLIResult:
    exit_code: int
    stdout: str
    stderr: str

    def json(self) -> dict[str, object]:
        return json.loads(self.stdout)

    def stderr_json(self) -> dict[str, object]:
        return _parse_json_payload(self.stderr)


def _parse_json_payload(content: str) -> dict[str, object]:
    start = content.find("{")
    if start == -1:
        raise json.JSONDecodeError("Expecting value", content, 0)
    return json.loads(content[start:])


def invoke_cli(args: list[str], capsys) -> CLIResult:
    exit_code = run(args)
    captured = capsys.readouterr()
    return CLIResult(exit_code=exit_code, stdout=captured.out, stderr=captured.err)
