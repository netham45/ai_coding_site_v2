from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import validate_yaml_document


def test_override_fixture_library_validates_supported_target_families_and_merge_modes(tmp_path: Path) -> None:
    catalog = load_resource_catalog()
    overrides_root = tmp_path / "yaml" / "overrides"
    overrides_root.mkdir(parents=True, exist_ok=True)
    prompt_project_dir = tmp_path / "prompts" / "project"
    fixture_catalog = replace(
        catalog,
        yaml_overrides_dir=overrides_root,
        yaml_project_dir=tmp_path / "yaml" / "project",
        yaml_project_policies_dir=tmp_path / "yaml" / "project" / "project-policies",
        prompt_project_dir=prompt_project_dir,
    )
    valid_documents = {
        "nodes/epic_available_tasks.yaml": "\n".join(
            [
                "target_family: node_definition",
                "target_id: epic",
                "compatibility:",
                "  min_schema_version: 2",
                "  built_in_version: builtin-system-v1",
                "merge_mode: replace_list",
                "value:",
                "  available_tasks:",
                "    - research_context",
                "    - execute_node",
            ]
        ),
        "policies/default_project_policy.yaml": "\n".join(
            [
                "target_family: project_policy_definition",
                "target_id: default_project_policy",
                "compatibility:",
                "  min_schema_version: 2",
                "merge_mode: append_list",
                "value:",
                "  hook_refs:",
                "    - hooks/default_hooks.yaml",
            ]
        ),
        "prompts/default_prompt_refs.yaml": "\n".join(
            [
                "target_family: prompt_reference_definition",
                "target_id: default_prompt_refs",
                "compatibility:",
                "  min_schema_version: 2",
                "merge_mode: deep_merge",
                "value:",
                "  references:",
                "    runtime.cli_bootstrap: runtime/cli_bootstrap.md",
            ]
        ),
    }

    for relative_path, content in valid_documents.items():
        path = overrides_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    seen_targets: set[tuple[str, str]] = set()
    for path in sorted(overrides_root.rglob("*.yaml")):
        relative_path = str(path.relative_to(overrides_root))
        report = validate_yaml_document(fixture_catalog, source_group="yaml_overrides", relative_path=relative_path)

        assert report.valid is True, f"{relative_path}: {report.issues}"

        payload = path.read_text(encoding="utf-8")
        target_family = next(line.split(": ", 1)[1] for line in payload.splitlines() if line.startswith("target_family:"))
        target_id = next(line.split(": ", 1)[1] for line in payload.splitlines() if line.startswith("target_id:"))
        assert (target_family, target_id) not in seen_targets, (
            f"duplicate override target {(target_family, target_id)!r} in {relative_path}"
        )
        seen_targets.add((target_family, target_id))
