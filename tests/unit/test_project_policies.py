from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from aicoding.daemon.errors import DaemonConflictError
from aicoding.hierarchy import load_hierarchy_registry
from aicoding.project_policies import list_project_policies, policy_impact_for_node_kind, resolve_effective_policy
from aicoding.resources import ResourceCatalog, load_resource_catalog


def test_resolve_effective_policy_merges_project_policy_defaults() -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    effective = resolve_effective_policy(catalog, hierarchy_registry=registry)

    assert effective.base_policy_id == "default_runtime_policy"
    assert effective.project_policy_ids == ["default_project_policy"]
    assert "hooks/default_hooks.yaml" in effective.hook_refs
    assert "testing/default_smoke_test_gate.yaml" in effective.testing_refs
    assert effective.prompt_pack == "default"


def test_policy_impact_for_node_kind_reports_project_additions() -> None:
    catalog = load_resource_catalog()
    registry = load_hierarchy_registry(catalog)

    impact = policy_impact_for_node_kind("epic", catalog, hierarchy_registry=registry)

    assert impact.enabled_for_node_kind is True
    assert "default_project_policy" in impact.project_policy_ids
    assert "hooks/default_hooks.yaml" in impact.added_hook_refs
    assert impact.prompt_pack == "default"


def test_invalid_project_policy_node_kind_is_rejected(tmp_path: Path) -> None:
    catalog = load_resource_catalog()
    root = tmp_path
    (root / "yaml" / "project" / "project-policies").mkdir(parents=True, exist_ok=True)
    (root / "yaml" / "builtin" / "system-yaml").mkdir(parents=True, exist_ok=True)
    (root / "prompts" / "project").mkdir(parents=True, exist_ok=True)
    bad_policy = root / "yaml" / "project" / "project-policies" / "bad.yaml"
    bad_policy.write_text(
        yaml.safe_dump(
            {
                "project_policy_definition": {
                    "id": "bad",
                    "description": "bad",
                    "defaults": {
                        "auto_run_children": True,
                        "auto_merge_to_parent": False,
                        "auto_merge_to_base": False,
                        "require_review_before_finalize": True,
                        "require_testing_before_finalize": True,
                        "require_docs_before_finalize": True,
                    },
                    "enabled_node_kinds": ["unknown_kind"],
                }
            }
        ),
        encoding="utf-8",
    )
    test_catalog = ResourceCatalog(
        root=root,
        yaml_builtin_dir=catalog.yaml_builtin_dir,
        yaml_builtin_system_dir=catalog.yaml_builtin_system_dir,
        yaml_project_dir=root / "yaml" / "project",
        yaml_project_policies_dir=root / "yaml" / "project" / "project-policies",
        yaml_overrides_dir=catalog.yaml_overrides_dir,
        yaml_schemas_dir=catalog.yaml_schemas_dir,
        prompt_layouts_dir=catalog.prompt_layouts_dir,
        prompt_execution_dir=catalog.prompt_execution_dir,
        prompt_recovery_dir=catalog.prompt_recovery_dir,
        prompt_quality_dir=catalog.prompt_quality_dir,
        prompt_pack_default_dir=catalog.prompt_pack_default_dir,
        prompt_project_dir=root / "prompts" / "project",
        docs_dir=catalog.docs_dir,
    )
    registry = load_hierarchy_registry(catalog)

    with pytest.raises(DaemonConflictError):
        list_project_policies(test_catalog, hierarchy_registry=registry)


def test_missing_project_policy_ref_asset_is_rejected(tmp_path: Path) -> None:
    catalog = load_resource_catalog()
    root = tmp_path
    (root / "yaml" / "project" / "project-policies").mkdir(parents=True, exist_ok=True)
    bad_policy = root / "yaml" / "project" / "project-policies" / "bad_ref.yaml"
    bad_policy.write_text(
        yaml.safe_dump(
            {
                "project_policy_definition": {
                    "id": "bad_ref",
                    "description": "missing ref",
                    "defaults": {
                        "auto_run_children": True,
                        "auto_merge_to_parent": False,
                        "auto_merge_to_base": False,
                        "require_review_before_finalize": True,
                        "require_testing_before_finalize": True,
                        "require_docs_before_finalize": True,
                    },
                    "runtime_policy_refs": ["runtime/not_real.yaml"],
                    "enabled_node_kinds": ["epic"],
                    "prompt_pack": "default",
                }
            }
        ),
        encoding="utf-8",
    )
    test_catalog = ResourceCatalog(
        root=root,
        yaml_builtin_dir=catalog.yaml_builtin_dir,
        yaml_builtin_system_dir=catalog.yaml_builtin_system_dir,
        yaml_project_dir=root / "yaml" / "project",
        yaml_project_policies_dir=root / "yaml" / "project" / "project-policies",
        yaml_overrides_dir=catalog.yaml_overrides_dir,
        yaml_schemas_dir=catalog.yaml_schemas_dir,
        prompt_layouts_dir=catalog.prompt_layouts_dir,
        prompt_execution_dir=catalog.prompt_execution_dir,
        prompt_recovery_dir=catalog.prompt_recovery_dir,
        prompt_quality_dir=catalog.prompt_quality_dir,
        prompt_pack_default_dir=catalog.prompt_pack_default_dir,
        prompt_project_dir=root / "prompts" / "project",
        docs_dir=catalog.docs_dir,
    )
    registry = load_hierarchy_registry(catalog)

    with pytest.raises(DaemonConflictError, match="missing runtime_policy_refs asset"):
        list_project_policies(test_catalog, hierarchy_registry=registry)
