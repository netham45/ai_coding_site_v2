from __future__ import annotations

from tests.helpers.resource_loader import list_relative_files, load_text


def test_builtin_system_yaml_library_contains_expected_families(builtin_system_yaml_root) -> None:
    files = list_relative_files(builtin_system_yaml_root)

    for expected in (
        "nodes/epic.yaml",
        "nodes/phase.yaml",
        "nodes/plan.yaml",
        "nodes/task.yaml",
        "tasks/research_context.yaml",
        "tasks/execute_node.yaml",
        "subtasks/run_prompt.yaml",
        "layouts/epic_to_phases.yaml",
        "layouts/manual_top_node.yaml",
        "layouts/research_only_breakdown.yaml",
        "layouts/replan_after_failure.yaml",
        "validations/file_exists.yaml",
        "reviews/layout_against_prompt.yaml",
    ):
        assert expected in files


def test_default_prompt_pack_contains_expected_files(default_prompt_pack_root) -> None:
    files = list_relative_files(default_prompt_pack_root)

    for expected in (
        "layouts/generate_phase_layout.md",
        "layouts/generate_plan_layout.md",
        "layouts/generate_task_layout.md",
        "execution/implement_leaf_task.md",
        "runtime/cli_bootstrap.md",
        "runtime/session_bootstrap.md",
        "recovery/idle_nudge.md",
        "recovery/repeated_missed_step.md",
        "recovery/resume_existing_session.md",
        "recovery/replacement_session_bootstrap.md",
    ):
        assert expected in files


def test_resource_loader_reads_placeholder_yaml() -> None:
    loaded = load_text("yaml_builtin_system", "nodes/epic.yaml")

    assert "node_definition:" in loaded.content
    assert "kind: epic" in loaded.content
    assert loaded.path.name == "epic.yaml"


def test_resource_loader_reads_placeholder_prompt() -> None:
    loaded = load_text("prompt_pack_default", "layouts/generate_phase_layout.md")

    assert "phase layout" in loaded.content
