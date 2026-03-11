from __future__ import annotations

import yaml

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import RuntimePolicyDefinitionDocument, validate_yaml_document


def test_builtin_runtime_policy_library_is_rigid() -> None:
    catalog = load_resource_catalog()
    root = catalog.yaml_builtin_system_dir / "policies"
    seen_ids: set[str] = set()

    for path in sorted(root.glob("*.yaml")):
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
        if payload.get("kind") != "runtime_policy_definition":
            continue
        relative_path = str(path.relative_to(catalog.yaml_builtin_system_dir))
        report = validate_yaml_document(catalog, source_group="yaml_builtin_system", relative_path=relative_path)
        assert report.valid is True, f"{relative_path} failed validation: {[issue.message for issue in report.issues]}"

        document = RuntimePolicyDefinitionDocument.model_validate(payload)
        assert document.id not in seen_ids, f"duplicate runtime policy id {document.id!r} in {relative_path}"
        seen_ids.add(document.id)
        assert document.defaults, f"{relative_path} has empty defaults"

        for field_name in ("runtime_policy_refs", "hook_refs", "review_refs", "testing_refs", "docs_refs"):
            values = getattr(document, field_name)
            assert len(values) == len(set(values)), f"{relative_path} repeats entries in {field_name}"

