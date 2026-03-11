from __future__ import annotations

from pathlib import Path

import yaml

from aicoding.hierarchy import load_hierarchy_registry
from aicoding.project_policies import list_project_policies
from aicoding.resources import load_resource_catalog
from aicoding.yaml_schemas import validate_yaml_document


def test_project_policy_library_validates_refs_and_declared_node_kinds() -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)
    policy_root = catalog.yaml_project_policies_dir
    seen_ids: set[str] = set()

    for path in sorted(policy_root.glob("*.yaml")):
        relative_path = str(Path("project-policies") / path.name)
        report = validate_yaml_document(catalog, source_group="yaml_project", relative_path=relative_path)

        assert report.valid is True, f"{relative_path}: {report.issues}"

        payload = yaml.safe_load(path.read_text(encoding="utf-8"))["project_policy_definition"]
        policy_id = payload["id"]
        assert policy_id not in seen_ids, f"duplicate project policy id {policy_id!r} in {relative_path}"
        seen_ids.add(policy_id)
        assert payload["prompt_pack"] in {"default", "project"}, f"{relative_path}: unsupported prompt pack"
        assert len(set(payload["enabled_node_kinds"])) == len(payload["enabled_node_kinds"]), (
            f"{relative_path}: duplicate enabled node kinds"
        )
        assert len(set(payload["environment_profiles"])) == len(payload["environment_profiles"]), (
            f"{relative_path}: duplicate environment profiles"
        )

    snapshots = list_project_policies(catalog, hierarchy_registry=registry)
    assert {snapshot.policy_id for snapshot in snapshots} == seen_ids
