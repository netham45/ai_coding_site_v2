from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.resources import ResourceCatalog, load_resource_catalog
from aicoding.structural_library import ensure_builtin_structural_library, inspect_builtin_structural_library


def _catalog_with_builtin_root(root: Path) -> ResourceCatalog:
    return ResourceCatalog(
        root=root,
        yaml_builtin_dir=root / "yaml" / "builtin",
        yaml_builtin_system_dir=root / "yaml" / "builtin" / "system-yaml",
        yaml_project_dir=root / "yaml" / "project",
        yaml_project_policies_dir=root / "yaml" / "project" / "project-policies",
        yaml_overrides_dir=root / "yaml" / "overrides",
        yaml_schemas_dir=root / "yaml" / "schemas",
        prompt_layouts_dir=root / "prompts" / "layouts",
        prompt_execution_dir=root / "prompts" / "execution",
        prompt_recovery_dir=root / "prompts" / "recovery",
        prompt_quality_dir=root / "prompts" / "quality",
        prompt_pack_default_dir=root / "prompts" / "packs" / "default",
        prompt_project_dir=root / "prompts" / "project",
        docs_dir=root / "docs",
    )


def test_builtin_structural_library_report_is_valid() -> None:
    report = inspect_builtin_structural_library(load_resource_catalog()).to_payload()

    assert report["valid"] is True
    assert report["missing_required"] == {
        "nodes": [],
        "tasks": [],
        "subtasks": [],
        "layouts": [],
    }
    assert "manual_top_node.yaml" in report["present"]["layouts"]
    assert "research_only_breakdown.yaml" in report["present"]["layouts"]
    assert "replan_after_failure.yaml" in report["present"]["layouts"]


def test_ensure_builtin_structural_library_rejects_missing_required_asset(tmp_path: Path) -> None:
    source_catalog = load_resource_catalog()
    target_root = tmp_path / "resources"
    target_root.mkdir(parents=True)
    for path in source_catalog.root.rglob("*"):
        target_path = target_root / path.relative_to(source_catalog.root)
        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    missing = target_root / "yaml" / "builtin" / "system-yaml" / "layouts" / "plan_to_tasks.yaml"
    missing.unlink()

    with pytest.raises(ValueError, match="missing required layouts"):
        ensure_builtin_structural_library(_catalog_with_builtin_root(target_root))


def test_yaml_structural_library_cli_command_reports_builtins(cli_runner) -> None:
    result = cli_runner(["yaml", "structural-library"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["valid"] is True
    assert "epic.yaml" in payload["present"]["nodes"]
    assert "replan_after_failure.yaml" in payload["present"]["layouts"]
