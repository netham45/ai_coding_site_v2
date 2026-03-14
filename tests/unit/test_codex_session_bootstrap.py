from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from aicoding.daemon import codex_session_bootstrap
from aicoding.daemon.session_manager import ORCHESTRATOR_SRC_ROOT


def test_run_prompt_cli_command_uses_shared_repo_local_command_contract(monkeypatch) -> None:
    logical_node_id = uuid4()
    captured: dict[str, object] = {}

    def fake_run(argv, **kwargs):
        captured["argv"] = argv
        captured["kwargs"] = kwargs
        return SimpleNamespace(
            returncode=0,
            stdout=json.dumps({"prompt_text": "Do the work."}),
            stderr="",
        )

    monkeypatch.setattr(codex_session_bootstrap.subprocess, "run", fake_run)

    command_text, payload = codex_session_bootstrap._run_prompt_cli_command(logical_node_id=logical_node_id)

    assert command_text.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert command_text.endswith(
        f"python3 -m aicoding.cli.main subtask prompt --node {logical_node_id}"
    )
    assert payload == {"prompt_text": "Do the work."}
    assert captured["argv"] == [
        sys.executable,
        "-m",
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        str(logical_node_id),
    ]
    kwargs = captured["kwargs"]
    assert kwargs["check"] is False
    assert kwargs["text"] is True
    assert kwargs["capture_output"] is True
    assert kwargs["env"]["PYTHONPATH"].split(os.pathsep)[0] == str(ORCHESTRATOR_SRC_ROOT)


def test_exec_codex_fresh_prepares_session_codex_home_and_uses_explicit_cwd(monkeypatch, tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".codex"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text('model = "gpt-5.4"\n', encoding="utf-8")
    (config_dir / "auth.json").write_text('{"auth_mode":"chatgpt"}\n', encoding="utf-8")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    trusted_parent = workspace.parent

    monkeypatch.chdir(workspace)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.setenv(
        "AICODING_CODEX_TRUSTED_PATHS",
        os.pathsep.join((str(workspace.resolve()), str(trusted_parent.resolve()))),
    )
    captured: dict[str, object] = {}

    def fake_execvp(file: str, argv: list[str]) -> None:
        captured["file"] = file
        captured["argv"] = argv
        raise SystemExit(0)

    monkeypatch.setattr(codex_session_bootstrap.os, "execvp", fake_execvp)

    try:
        codex_session_bootstrap._exec_codex_fresh()
    except SystemExit as exc:
        assert exc.code == 0

    config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
    auth_text = (codex_home / "auth.json").read_text(encoding="utf-8")
    assert 'model = "gpt-5.4"' in config_text
    assert f'[projects."{workspace.resolve()}"]' in config_text
    assert f'[projects."{trusted_parent.resolve()}"]' in config_text
    assert '"auth_mode":"chatgpt"' in auth_text
    assert captured["file"] == "codex"
    assert captured["argv"] == [
        "codex",
        "-C",
        str(workspace.resolve()),
        "--yolo",
    ]


def test_main_fresh_prefers_prompt_log_path_when_bootstrapping_codex(monkeypatch, tmp_path: Path) -> None:
    prompt_log_path = tmp_path / "prompt.md"
    captured: dict[str, object] = {}

    monkeypatch.setattr(
        codex_session_bootstrap,
        "_run_prompt_cli_command",
        lambda *, logical_node_id: ("PYTHONPATH=src python3 -m aicoding.cli.main subtask prompt --node node-123", {"prompt_text": "Do the work."}),
    )
    monkeypatch.setattr(
        codex_session_bootstrap,
        "_write_prompt_log",
        lambda path_text, prompt_text: prompt_log_path.write_text(prompt_text, encoding="utf-8"),
    )
    monkeypatch.setattr(
        codex_session_bootstrap,
        "_exec_codex_fresh",
        lambda: captured.setdefault("started", True),
    )

    result = codex_session_bootstrap.main(
        ["fresh", "--node", str(uuid4()), "--prompt-log-path", str(prompt_log_path)]
    )

    assert result == 0
    assert captured["started"] is True
    assert prompt_log_path.read_text(encoding="utf-8") == "Do the work."


def test_exec_codex_resume_prepares_session_codex_home(monkeypatch, tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".codex"
    config_dir.mkdir()
    (config_dir / "auth.json").write_text('{"auth_mode":"chatgpt"}\n', encoding="utf-8")
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    monkeypatch.chdir(workspace)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    monkeypatch.delenv("AICODING_CODEX_TRUSTED_PATHS", raising=False)
    captured: dict[str, object] = {}

    def fake_execvp(file: str, argv: list[str]) -> None:
        captured["file"] = file
        captured["argv"] = argv
        raise SystemExit(0)

    monkeypatch.setattr(codex_session_bootstrap.os, "execvp", fake_execvp)

    try:
        codex_session_bootstrap._exec_codex_resume()
    except SystemExit as exc:
        assert exc.code == 0

    config_text = (codex_home / "config.toml").read_text(encoding="utf-8")
    auth_text = (codex_home / "auth.json").read_text(encoding="utf-8")
    assert f'[projects."{workspace.resolve()}"]' in config_text
    assert '"auth_mode":"chatgpt"' in auth_text
    assert captured["argv"] == [
        "codex",
        "-C",
        str(workspace.resolve()),
        "--yolo",
        "resume",
        "--last",
    ]


def test_exec_codex_prompt_file_prepares_session_codex_home(monkeypatch, tmp_path: Path) -> None:
    codex_home = tmp_path / "codex-home"
    home = tmp_path / "home"
    home.mkdir()
    config_dir = home / ".codex"
    config_dir.mkdir()
    (config_dir / "auth.json").write_text('{"auth_mode":"chatgpt"}\n', encoding="utf-8")
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    prompt_file = workspace / "prompt.md"
    prompt_file.write_text("delegated prompt", encoding="utf-8")

    monkeypatch.chdir(workspace)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("CODEX_HOME", str(codex_home))
    captured: dict[str, object] = {}

    def fake_execvp(file: str, argv: list[str]) -> None:
        captured["file"] = file
        captured["argv"] = argv
        raise SystemExit(0)

    monkeypatch.setattr(codex_session_bootstrap.os, "execvp", fake_execvp)

    try:
        codex_session_bootstrap._exec_codex_prompt_file()
    except SystemExit as exc:
        assert exc.code == 0

    assert captured["file"] == "codex"
    assert captured["argv"] == [
        "codex",
        "-C",
        str(workspace.resolve()),
        "--yolo",
    ]
