from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from aicoding.config import get_settings
from aicoding.daemon.session_manager import (
    build_child_session_plan,
    build_primary_session_plan,
    build_recovery_primary_session_plan,
    current_stage_prompt_cli_command,
    default_interactive_shell_command,
    prompt_log_path_for_session,
    project_name_for_working_directory,
    session_runtime_environment,
)


def test_primary_session_launch_plan_uses_run_and_session_identity() -> None:
    node_id = uuid4()
    run_id = uuid4()
    session_id = uuid4()

    plan = build_primary_session_plan(
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
    assert plan.environment == session_runtime_environment()
    assert plan.prompt_cli_command == current_stage_prompt_cli_command(logical_node_id=node_id)
    assert plan.prompt_log_path is not None
    assert "prompt_logs" in plan.prompt_log_path


def test_child_session_launch_plan_is_distinct_from_primary_plan() -> None:
    parent_session_id = uuid4()
    session_id = uuid4()

    plan = build_child_session_plan(parent_session_id=parent_session_id, session_id=session_id)

    assert plan.session_name.startswith("aicoding-child-")
    assert str(parent_session_id)[:8] in plan.session_name
    assert str(session_id)[:8] in plan.session_name
    assert plan.attach_command == f"tmux attach-session -t {plan.session_name}"
    assert plan.environment == session_runtime_environment()


def test_default_interactive_shell_command_is_long_lived() -> None:
    command = default_interactive_shell_command()

    assert "-lc" in command
    assert "exec" in command


def test_recovery_primary_session_launch_plan_uses_codex_resume_last() -> None:
    run_id = uuid4()
    session_id = uuid4()

    plan = build_recovery_primary_session_plan(
        node_run_id=run_id,
        run_number=2,
        session_id=session_id,
    )

    assert plan.session_name.startswith("aicoding-pri-r2-")
    assert "codex_session_bootstrap" in plan.command
    assert "resume" in plan.command
    assert plan.launch_mode == "codex_resume_last"
    assert plan.environment == session_runtime_environment()
    assert plan.prompt_cli_command is None
    assert plan.prompt_log_path is None


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
