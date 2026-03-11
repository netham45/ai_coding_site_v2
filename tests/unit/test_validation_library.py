from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import ValidationDefinitionDocument, validate_yaml_document


def _builtin_validation_paths() -> list[Path]:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "validations"
    return sorted(root.glob("*.yaml"))


def test_builtin_validation_library_yaml_is_valid_unique_and_covers_authored_check_types() -> None:
    catalog = load_resource_catalog()
    seen_ids: set[str] = set()
    seen_check_types: set[str] = set()

    for path in _builtin_validation_paths():
        relative_path = f"validations/{path.name}"
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        document = ValidationDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))

        assert report.valid is True, relative_path
        assert document.id not in seen_ids, relative_path
        seen_ids.add(document.id)
        seen_check_types.add(document.check.type)

        if document.check.type in {"file_exists", "file_updated", "file_contains", "docs_built", "provenance_updated", "summary_written"}:
            assert document.check.path, relative_path
        if document.check.type == "file_contains":
            assert document.check.pattern, relative_path
        if document.check.type == "command_exit_code":
            assert document.check.exit_code is not None, relative_path
        if document.check.type in {"json_schema", "yaml_schema"}:
            assert document.check.schema_name, relative_path
        if document.check.type == "ai_json_status":
            assert document.check.value is not None, relative_path

    assert seen_check_types == {
        "ai_json_status",
        "command_exit_code",
        "dependencies_satisfied",
        "docs_built",
        "file_contains",
        "file_exists",
        "file_updated",
        "git_clean",
        "git_dirty",
        "json_schema",
        "provenance_updated",
        "session_bound",
        "summary_written",
        "yaml_schema",
    }
