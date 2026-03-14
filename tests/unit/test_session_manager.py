from __future__ import annotations

import os
from pathlib import Path
from uuid import uuid4

from aicoding.config import get_settings
from aicoding.daemon.live_git import repo_path_for_version
from aicoding.daemon.session_manager import (
    ORCHESTRATOR_SRC_ROOT,
    build_child_session_plan,
    build_primary_session_plan,
    build_recovery_primary_session_plan,
    child_prompt_path_for_session,
    codex_home_path_for_run,
    codex_home_path_for_child_session,
    current_stage_prompt_cli_command,
    default_interactive_shell_command,
    delegated_prompt_file_bootstrap_command,
    prompt_log_path_for_session,
    primary_session_execution_working_directory,
    project_name_for_working_directory,
    repo_local_python_module_command,
    codex_prompt_instruction,
    session_runtime_environment,
    trusted_workspace_paths_for_codex,
)


def test_primary_session_launch_plan_uses_run_and_session_identity() -> None:
    node_id = uuid4()
    run_id = uuid4()
    session_id = uuid4()

    plan = build_primary_session_plan(
        node_version_id=uuid4(),
        logical_node_id=node_id,
        node_run_id=run_id,
        run_number=3,
        session_id=session_id,
        compiled_subtask_id=uuid4(),
    )

    assert plan.session_name.startswith("aicoding-pri-r3-")
    assert str(run_id)[:8] in plan.session_name
    assert str(session_id)[:8] in plan.session_name
    assert plan.attach_command == f"tmux attach-session -t {plan.session_name}"
    assert "aicoding.daemon.codex_session_bootstrap" in plan.command
    assert plan.launch_mode == "codex_fresh"
    assert plan.environment is not None
    expected_environment = session_runtime_environment()
    for key, value in expected_environment.items():
        assert plan.environment[key] == value
    assert plan.prompt_cli_command == current_stage_prompt_cli_command(logical_node_id=node_id)
    assert plan.prompt_cli_command.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert "python3 -m aicoding.cli.main subtask prompt --node " in plan.prompt_cli_command
    assert plan.command.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert "python3 -m aicoding.daemon.codex_session_bootstrap fresh --node " in plan.command
    assert plan.prompt_log_path is not None
    assert "prompt_logs" in plan.prompt_log_path
    assert plan.codex_home_path is not None
    assert plan.environment is not None
    assert plan.environment["CODEX_HOME"] == plan.codex_home_path
    assert plan.environment["AICODING_CODEX_TRUSTED_PATHS"]
    assert plan.trusted_workspace_paths


def test_child_session_launch_plan_is_distinct_from_primary_plan() -> None:
    parent_session_id = uuid4()
    session_id = uuid4()

    plan = build_child_session_plan(parent_session_id=parent_session_id, session_id=session_id)

    assert plan.session_name.startswith("aicoding-child-")
    assert str(parent_session_id)[:8] in plan.session_name
    assert str(session_id)[:8] in plan.session_name
    assert plan.attach_command == f"tmux attach-session -t {plan.session_name}"
    assert "aicoding.daemon.codex_session_bootstrap" in plan.command
    assert "prompt-file" in plan.command
    assert plan.launch_mode == "codex_prompt_file"
    assert plan.prompt_log_path == child_prompt_path_for_session(
        working_directory=plan.working_directory,
        parent_session_id=parent_session_id,
        session_id=session_id,
    )
    assert plan.codex_home_path == codex_home_path_for_child_session(
        parent_session_id=parent_session_id,
        session_id=session_id,
    )
    assert plan.environment is not None
    expected_environment = session_runtime_environment()
    for key, value in expected_environment.items():
        assert plan.environment[key] == value
    assert plan.environment["CODEX_HOME"] == plan.codex_home_path
    assert plan.environment["AICODING_CODEX_TRUSTED_PATHS"]
    assert plan.trusted_workspace_paths


def test_default_interactive_shell_command_is_long_lived() -> None:
    command = default_interactive_shell_command()

    assert "-lc" in command
    assert "exec" in command


def test_delegated_prompt_file_bootstrap_command_uses_repo_local_pythonpath() -> None:
    command = delegated_prompt_file_bootstrap_command(prompt_file="/tmp/prompt.md")

    assert command.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert command.endswith("python3 -m aicoding.daemon.codex_session_bootstrap prompt-file --prompt-file /tmp/prompt.md")


def test_codex_prompt_instruction_for_prompt_file_forbids_immediate_subtask_prompt_refetch() -> None:
    rendered = codex_prompt_instruction(prompt_target="/tmp/prompt.md", prompt_source="file")

    assert "Read the full task prompt from `/tmp/prompt.md`" in rendered
    assert "Do not start by re-fetching `subtask prompt`" in rendered
    assert "execute the concrete next workflow step" in rendered


def test_recovery_primary_session_launch_plan_uses_codex_resume_last() -> None:
    run_id = uuid4()
    session_id = uuid4()

    plan = build_recovery_primary_session_plan(
        node_version_id=uuid4(),
        node_run_id=run_id,
        run_number=2,
        session_id=session_id,
    )

    assert plan.session_name.startswith("aicoding-pri-r2-")
    assert "codex_session_bootstrap" in plan.command
    assert "resume" in plan.command
    assert plan.command.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert plan.command.endswith("python3 -m aicoding.daemon.codex_session_bootstrap resume")
    assert plan.launch_mode == "codex_resume_last"
    assert plan.environment is not None
    expected_environment = session_runtime_environment()
    for key, value in expected_environment.items():
        assert plan.environment[key] == value
    assert plan.environment["CODEX_HOME"] == plan.codex_home_path
    assert plan.prompt_cli_command is None
    assert plan.prompt_log_path is None
    assert plan.trusted_workspace_paths


def test_project_name_and_prompt_log_path_are_deterministic() -> None:
    node_id = uuid4()
    run_id = uuid4()
    subtask_id = uuid4()

    assert project_name_for_working_directory("/tmp/my project") == "my_project"

    path = prompt_log_path_for_session(
        working_directory="/tmp/my project",
        logical_node_id=node_id,
        node_run_id=run_id,
        compiled_subtask_id=subtask_id,
    )

    assert path == f"/tmp/my project/prompt_logs/my_project/{node_id}/{run_id}/{subtask_id}.md"


def test_primary_session_launch_plan_uses_workspace_root_when_configured(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(tmp_path))
    get_settings.cache_clear()
    try:
        plan = build_primary_session_plan(
            node_version_id=uuid4(),
            logical_node_id=uuid4(),
            node_run_id=uuid4(),
            run_number=1,
            session_id=uuid4(),
            compiled_subtask_id=uuid4(),
        )
        assert plan.working_directory == str(tmp_path)
    finally:
        get_settings.cache_clear()


def test_session_runtime_environment_does_not_forward_parent_term(monkeypatch) -> None:
    monkeypatch.setenv("TERM", "dumb")

    environment = session_runtime_environment()

    assert "TERM" not in environment


def test_primary_session_execution_working_directory_uses_node_runtime_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    node_version_id = uuid4()
    repo_path = repo_path_for_version(node_version_id)
    repo_path.mkdir(parents=True, exist_ok=True)
    (repo_path / ".git").mkdir()

    resolved = primary_session_execution_working_directory(node_version_id=node_version_id)

    assert resolved == str(repo_path)


def test_recovery_primary_session_launch_plan_uses_node_runtime_repo(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    node_version_id = uuid4()
    repo_path = repo_path_for_version(node_version_id)
    repo_path.mkdir(parents=True, exist_ok=True)
    (repo_path / ".git").mkdir()

    plan = build_recovery_primary_session_plan(
        node_version_id=node_version_id,
        node_run_id=uuid4(),
        run_number=1,
        session_id=uuid4(),
    )

    assert plan.working_directory == str(repo_path)


def test_repo_local_python_module_command_exposes_shell_text_and_subprocess_environment() -> None:
    command = repo_local_python_module_command(
        "aicoding.cli.main",
        "subtask",
        "prompt",
        "--node",
        "node-123",
    )

    assert command.command_text.startswith(f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}")
    assert command.command_text.endswith("python3 -m aicoding.cli.main subtask prompt --node node-123")
    assert command.argv[1:] == ("-m", "aicoding.cli.main", "subtask", "prompt", "--node", "node-123")
    assert command.environment["PYTHONPATH"].split(os.pathsep)[0] == str(ORCHESTRATOR_SRC_ROOT)


def test_repo_local_python_module_command_preserves_existing_pythonpath(monkeypatch) -> None:
    monkeypatch.setenv("PYTHONPATH", "/tmp/existing-path")

    command = repo_local_python_module_command("aicoding.daemon.codex_session_bootstrap", "resume")

    assert command.environment["PYTHONPATH"] == f"{ORCHESTRATOR_SRC_ROOT}{os.pathsep}/tmp/existing-path"
    assert command.command_text.startswith(
        f"PYTHONPATH={ORCHESTRATOR_SRC_ROOT}{os.pathsep}/tmp/existing-path python3 -m aicoding.daemon.codex_session_bootstrap resume"
    )


def test_codex_home_path_uses_runtime_artifact_root_from_auth_token_file(monkeypatch, tmp_path: Path) -> None:
    token_file = tmp_path / "runtime" / "daemon.token"
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text("token", encoding="utf-8")
    monkeypatch.setenv("AICODING_AUTH_TOKEN_FILE", str(token_file))

    resolved = codex_home_path_for_run(node_run_id=uuid4())

    assert resolved.startswith(str(token_file.parent / "codex-home"))


def test_trusted_workspace_paths_include_working_directory_parent_and_workspace_root(monkeypatch, tmp_path: Path) -> None:
    workspace_root = tmp_path / "workspace"
    workspace_root.mkdir()
    working_directory = workspace_root / "node-repo"
    working_directory.mkdir()
    monkeypatch.setenv("AICODING_WORKSPACE_ROOT", str(workspace_root))
    get_settings.cache_clear()
    try:
        paths = trusted_workspace_paths_for_codex(working_directory=str(working_directory))
    finally:
        get_settings.cache_clear()

    assert paths[0] == str(working_directory.resolve())
    assert str(working_directory.parent.resolve()) in paths
    assert str(workspace_root.resolve()) in paths
