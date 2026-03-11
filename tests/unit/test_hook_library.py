from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import HookDefinitionDocument, validate_yaml_document


def test_builtin_hook_library_is_rigid_and_prompt_bound() -> None:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "hooks"
    seen_ids: set[str] = set()

    for path in sorted(root.glob("*.yaml")):
        relative_path = str(path.relative_to(catalog.yaml_builtin_system_dir))
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        assert report.valid is True, f"{relative_path} failed validation: {[issue.message for issue in report.issues]}"

        document = HookDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        assert document.id not in seen_ids, f"duplicate hook id {document.id!r} in {relative_path}"
        seen_ids.add(document.id)
        assert document.when.strip(), f"{relative_path} has blank when"

        for index, step in enumerate(document.run):
            assert step.type.strip(), f"{relative_path} run[{index}] has blank type"
            if step.type == "run_prompt":
                assert step.prompt and step.prompt.strip(), f"{relative_path} run[{index}] is missing prompt"
            if step.type in {"run_command", "validate"}:
                assert step.command and step.command.strip(), f"{relative_path} run[{index}] is missing command"

