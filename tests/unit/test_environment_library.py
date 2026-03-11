from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import EnvironmentPolicyDefinitionDocument, TaskDefinitionDocument, validate_yaml_document


def _builtin_environment_paths() -> list[Path]:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "environments"
    return sorted(root.glob("*.yaml"))


def test_builtin_environment_library_yaml_is_valid_and_task_references_resolve() -> None:
    catalog = load_resource_catalog()
    task_root = catalog.yaml_builtin_system_dir / "tasks"
    environment_refs = {
        subtask.environment_policy_ref
        for path in sorted(task_root.glob("*.yaml"))
        for subtask in TaskDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8"))).subtasks
        if subtask.environment_policy_ref
    }
    seen_ids: set[str] = set()
    available_relative_paths: set[str] = set()
    custom_profile_count = 0

    for path in _builtin_environment_paths():
        relative_path = f"environments/{path.name}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        document = EnvironmentPolicyDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

        assert report.valid is True, relative_path
        assert document.id not in seen_ids, relative_path
        if document.isolation_mode == "custom_profile":
            custom_profile_count += 1
            assert document.runtime_profile, relative_path
        else:
            assert document.runtime_profile is None, relative_path

        seen_ids.add(document.id)
        available_relative_paths.add(relative_path)

    assert custom_profile_count >= 1
    assert environment_refs <= available_relative_paths
