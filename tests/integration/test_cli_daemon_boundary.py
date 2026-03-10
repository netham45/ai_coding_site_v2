from __future__ import annotations

import json

from aicoding.cli.app import run


def test_mutating_command_fails_cleanly_when_daemon_is_unavailable(capsys, monkeypatch) -> None:
    monkeypatch.setenv("AICODING_DAEMON_PORT", "9")

    exit_code = run(["node", "run", "start", "--node", "node-123"])
    payload = json.loads(capsys.readouterr().err)

    assert exit_code == 1
    assert payload["error"] == "daemon_unavailable"


def test_yaml_sources_command_reports_yaml_resource_paths(capsys) -> None:
    exit_code = run(["yaml", "sources", "--scope", "builtin"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "yaml_builtin" in payload["resources"]


def test_prompts_show_command_reports_prompt_resource_paths(capsys) -> None:
    exit_code = run(["prompts", "show", "--scope", "layouts"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert "prompt_layouts" in payload["resources"]
