from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import RectificationDefinitionDocument, TaskDefinitionDocument, validate_yaml_document


def _builtin_rectification_paths() -> list[Path]:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "rectification"
    return sorted(root.glob("*.yaml"))


def test_builtin_rectification_library_yaml_is_valid_and_references_known_tasks_and_subtasks() -> None:
    catalog = load_resource_catalog()
    task_root = catalog.yaml_builtin_system_dir / "tasks"
    subtask_root = catalog.yaml_builtin_system_dir / "subtasks"
    known_task_ids = {
        TaskDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8"))).id
        for path in sorted(task_root.glob("*.yaml"))
    }
    known_subtask_ids = {
        yaml.safe_load(path.read_text(encoding="utf-8"))["id"]
        for path in sorted(subtask_root.glob("*.yaml"))
    }
    seen_ids: set[str] = set()
    seen_triggers: set[str] = set()

    for path in _builtin_rectification_paths():
        relative_path = f"rectification/{path.name}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        document = RectificationDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

        assert report.valid is True, relative_path
        assert document.id not in seen_ids, relative_path
        assert document.trigger not in seen_triggers, relative_path
        assert document.entry_task in known_task_ids, relative_path
        assert document.subtasks, relative_path
        assert len(document.subtasks) == len(set(document.subtasks)), relative_path
        for subtask_id in document.subtasks:
            assert subtask_id in known_subtask_ids, f"{relative_path}: unknown subtask '{subtask_id}'"

        seen_ids.add(document.id)
        seen_triggers.add(document.trigger)
