from __future__ import annotations

from uuid import uuid4

from aicoding.daemon.session_manager import (
    build_child_session_plan,
    build_primary_session_plan,
    default_interactive_shell_command,
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
    )

    assert plan.session_name.startswith("aicoding-pri-r3-")
    assert str(run_id)[:8] in plan.session_name
    assert str(session_id)[:8] in plan.session_name
    assert plan.attach_command == f"tmux attach-session -t {plan.session_name}"
    assert "exec" in plan.command


def test_child_session_launch_plan_is_distinct_from_primary_plan() -> None:
    parent_session_id = uuid4()
    session_id = uuid4()

    plan = build_child_session_plan(parent_session_id=parent_session_id, session_id=session_id)

    assert plan.session_name.startswith("aicoding-child-")
    assert str(parent_session_id)[:8] in plan.session_name
    assert str(session_id)[:8] in plan.session_name
    assert plan.attach_command == f"tmux attach-session -t {plan.session_name}"


def test_default_interactive_shell_command_is_long_lived() -> None:
    command = default_interactive_shell_command()

    assert "-lc" in command
    assert "exec" in command
