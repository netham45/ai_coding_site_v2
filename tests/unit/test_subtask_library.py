from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import yaml

from aicoding.daemon.admission import admit_node_run
from aicoding.daemon.hierarchy import create_hierarchy_node
from aicoding.daemon.lifecycle import seed_node_lifecycle, transition_node_lifecycle
from aicoding.daemon.run_orchestration import (
    advance_workflow,
    complete_current_subtask,
    load_current_run_progress,
    load_current_subtask_prompt,
    start_subtask_attempt,
)
from aicoding.daemon.versioning import initialize_node_version
from aicoding.daemon.workflows import compile_node_workflow
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import SubtaskDefinitionDocument, validate_yaml_document


def _builtin_subtask_paths() -> list[Path]:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "subtasks"
    return sorted(root.glob("*.yaml"))


def _load_subtask_document(path: Path) -> SubtaskDefinitionDocument:
    return SubtaskDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))


def _task_parent_chain(db_session_factory, registry) -> str:
    epic = create_hierarchy_node(db_session_factory, registry, kind="epic", title="Parent Epic", prompt="boot")
    phase = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="phase",
        title="Parent Phase",
        prompt="boot",
        parent_node_id=epic.node_id,
    )
    plan = create_hierarchy_node(
        db_session_factory,
        registry,
        kind="plan",
        title="Parent Plan",
        prompt="boot",
        parent_node_id=phase.node_id,
    )
    return str(plan.node_id)


def test_builtin_subtask_library_yaml_is_valid_and_bound_to_existing_prompt_assets() -> None:
    catalog = load_resource_catalog()
    prompt_root = catalog.root / "prompts" / "packs" / "default"
    supported_types = {
        "build_context",
        "run_prompt",
        "run_command",
        "validate",
        "review",
        "run_tests",
        "wait_for_children",
        "wait_for_sibling_dependency",
        "spawn_child_node",
        "spawn_child_session",
        "merge_children",
        "write_summary",
        "build_docs",
        "update_provenance",
        "reset_to_seed",
        "finalize_node",
    }

    for path in _builtin_subtask_paths():
        relative_path = f"subtasks/{path.name}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        document = _load_subtask_document(path)

        assert report.valid is True, relative_path
        assert document.type in supported_types, relative_path
        if document.prompt:
            prompt_relative_path = document.prompt.removeprefix("prompts/")
            assert (prompt_root / prompt_relative_path).exists(), document.prompt
        if document.command:
            assert "reset --hard" not in document.command
            assert "checkout --" not in document.command


def test_builtin_recovery_oriented_tasks_prefer_recovery_prompt_family() -> None:
    catalog = load_resource_catalog()
    wait_for_children = yaml.safe_load(
        (catalog.yaml_builtin_system_dir / "tasks" / "wait_for_children.yaml").read_text(encoding="utf-8")
    )
    recover_interrupted = yaml.safe_load(
        (catalog.yaml_builtin_system_dir / "tasks" / "recover_interrupted_run.yaml").read_text(encoding="utf-8")
    )

    collect_child = next(item for item in wait_for_children["subtasks"] if item["id"] == "collect_child_summaries")
    recover_session = next(item for item in recover_interrupted["subtasks"] if item["id"] == "recover_session")

    assert collect_child["prompt"] == "prompts/recovery/resume_existing_session.md"
    assert recover_session["prompt"] == "prompts/recovery/replacement_session_bootstrap.md"


def test_builtin_generic_pause_surfaces_prefer_canonical_pause_prompt_family() -> None:
    catalog = load_resource_catalog()
    pause_task = yaml.safe_load(
        (catalog.yaml_builtin_system_dir / "tasks" / "pause_for_user.yaml").read_text(encoding="utf-8")
    )
    pause_flag_subtask = yaml.safe_load(
        (catalog.yaml_builtin_system_dir / "subtasks" / "pause_on_user_flag.yaml").read_text(encoding="utf-8")
    )

    pause_and_summarize = next(item for item in pause_task["subtasks"] if item["id"] == "pause_and_summarize")

    assert pause_and_summarize["prompt"] == "prompts/pause/pause_for_user.md"
    assert pause_flag_subtask["prompt"] == "prompts/pause/pause_for_user.md"


def test_builtin_subtask_library_is_synthetically_compileable_and_startable(
    db_session_factory,
    migrated_public_schema,
    tmp_path,
) -> None:
    base_catalog = load_resource_catalog()
    overrides_root = tmp_path / "overrides"
    (overrides_root / "nodes").mkdir(parents=True)
    (overrides_root / "tasks").mkdir(parents=True)
    (overrides_root / "nodes" / "task_only_execute_node.yaml").write_text(
        "\n".join(
            [
                "target_family: node_definition",
                "target_id: task",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - execute_node",
            ]
        ),
        encoding="utf-8",
    )
    catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
    registry = load_hierarchy_registry(catalog)
    plan_parent_id = _task_parent_chain(db_session_factory, registry)

    for index, subtask_path in enumerate(_builtin_subtask_paths(), start=1):
        document = _load_subtask_document(subtask_path)
        override_path = overrides_root / "tasks" / f"execute_node_{document.id}.yaml"
        override_path.write_text(
            "\n".join(
                [
                    "target_family: task_definition",
                    "target_id: execute_node",
                    "compatibility:",
                    "  min_schema_version: 2",
                    "  built_in_version: builtin-system-v1",
                    "merge_mode: replace_list",
                    "value:",
                    "  subtasks:",
                    *[
                        f"    {line}" if line else "    "
                        for line in yaml.safe_dump([document.model_dump(mode='python', exclude_none=True)], sort_keys=False).splitlines()
                    ],
                ]
            ),
            encoding="utf-8",
        )
        loop_catalog = replace(base_catalog, yaml_overrides_dir=overrides_root)
        loop_registry = load_hierarchy_registry(loop_catalog)
        node = create_hierarchy_node(
            db_session_factory,
            loop_registry,
            kind="task",
            title=f"Subtask {index} {document.id}",
            prompt="boot",
            parent_node_id=plan_parent_id,
        )
        seed_node_lifecycle(db_session_factory, node_id=str(node.node_id), initial_state="DRAFT")
        initialize_node_version(db_session_factory, logical_node_id=node.node_id)
        compiled = compile_node_workflow(db_session_factory, logical_node_id=node.node_id, catalog=loop_catalog)

        assert compiled.status == "compiled", subtask_path.name
        assert compiled.compiled_workflow is not None
        execute_task = compiled.compiled_workflow.tasks[0]
        library_subtask = next(item for item in execute_task.subtasks if item.inserted_by_hook is False)
        assert library_subtask.subtask_type == document.type
        assert library_subtask.source_subtask_key == f"execute_node.{document.id}"

        transition_node_lifecycle(db_session_factory, node_id=str(node.node_id), target_state="READY")
        admission = admit_node_run(db_session_factory, node_id=node.node_id)
        assert admission.status == "admitted", subtask_path.name

        expected_subtask_id = str(library_subtask.id)
        progress = load_current_run_progress(db_session_factory, logical_node_id=node.node_id)
        while (
            progress.current_subtask is not None
            and progress.current_subtask["id"] != expected_subtask_id
        ):
            current_subtask_id = progress.state.current_compiled_subtask_id
            start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
            complete_current_subtask(
                db_session_factory,
                logical_node_id=node.node_id,
                compiled_subtask_id=current_subtask_id,
                summary="hook complete",
            )
            progress = advance_workflow(db_session_factory, logical_node_id=node.node_id, catalog=loop_catalog)

        current_subtask_id = progress.state.current_compiled_subtask_id
        prompt = load_current_subtask_prompt(db_session_factory, logical_node_id=node.node_id)
        assert current_subtask_id is not None, subtask_path.name
        assert str(current_subtask_id) == expected_subtask_id, subtask_path.name
        assert str(prompt.compiled_subtask_id) == str(current_subtask_id)
        if document.prompt:
            assert prompt.prompt_text
        if document.command:
            assert prompt.command_text

        started = start_subtask_attempt(db_session_factory, logical_node_id=node.node_id, compiled_subtask_id=current_subtask_id)
        assert started.latest_attempt is not None, subtask_path.name
        assert started.latest_attempt.status == "RUNNING", subtask_path.name
