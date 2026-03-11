from __future__ import annotations

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import DocsDefinitionDocument, validate_yaml_document


def test_builtin_docs_library_is_rigid() -> None:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "docs"
    seen_ids: set[str] = set()

    for path in sorted(root.glob("*.yaml")):
        relative_path = str(path.relative_to(catalog.yaml_builtin_system_dir))
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        assert report.valid is True, f"{relative_path} failed validation: {[issue.message for issue in report.issues]}"

        document = DocsDefinitionDocument.model_validate(yaml.safe_load(path.read_text(encoding="utf-8")))
        assert document.id not in seen_ids, f"duplicate docs id {document.id!r} in {relative_path}"
        seen_ids.add(document.id)
        assert document.scope.strip(), f"{relative_path} has blank scope"
        assert document.outputs, f"{relative_path} has no outputs"

        for index, output in enumerate(document.outputs):
            assert output.path.strip(), f"{relative_path} outputs[{index}] has blank path"
            assert output.view.strip(), f"{relative_path} outputs[{index}] has blank view"
