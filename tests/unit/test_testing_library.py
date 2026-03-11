from __future__ import annotations

import yaml

from aicoding.resources import load_resource_catalog
from aicoding import yaml_schemas


def test_builtin_testing_library_is_rigid() -> None:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "testing"
    seen_ids: set[str] = set()

    for path in sorted(root.glob("*.yaml")):
        relative_path = str(path.relative_to(catalog.yaml_builtin_system_dir))
        report = yaml_schemas.validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        assert report.valid is True, f"{relative_path} failed validation: {[issue.message for issue in report.issues]}"

        document = yaml_schemas.TestingDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        assert document.id not in seen_ids, f"duplicate testing id {document.id!r} in {relative_path}"
        seen_ids.add(document.id)
        assert document.scope.strip(), f"{relative_path} has blank scope"

        for index, command in enumerate(document.commands):
            assert command.command.strip(), f"{relative_path} commands[{index}] has blank command"
            assert command.working_directory.strip(), f"{relative_path} commands[{index}] has blank working_directory"

        assert document.on_result.pass_action.strip(), f"{relative_path} has blank pass_action"
        assert document.on_result.fail_action.strip(), f"{relative_path} has blank fail_action"
