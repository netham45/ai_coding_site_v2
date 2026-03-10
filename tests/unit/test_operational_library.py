from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.operational_library import ensure_builtin_operational_library, inspect_builtin_operational_library
from aicoding.resources import ResourceCatalog, load_resource_catalog


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


def test_builtin_operational_library_report_is_valid() -> None:
    report = inspect_builtin_operational_library(load_resource_catalog()).to_payload()

    assert report["valid"] is True
    assert report["missing_required"] == {
        "runtime": [],
        "hooks": [],
        "policies": [],
        "prompts": [],
        "environments": [],
    }
    assert "default_runtime_policy.yaml" in report["present"]["policies"]
    assert "default_hooks.yaml" in report["present"]["hooks"]


def test_ensure_builtin_operational_library_rejects_missing_required_asset(tmp_path: Path) -> None:
    source_catalog = load_resource_catalog()
    target_root = tmp_path / "resources"
    target_root.mkdir(parents=True)
    for path in source_catalog.root.rglob("*"):
        target_path = target_root / path.relative_to(source_catalog.root)
        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    missing = target_root / "yaml" / "builtin" / "system-yaml" / "hooks" / "default_hooks.yaml"
    missing.unlink()

    with pytest.raises(ValueError, match="missing required hooks"):
        ensure_builtin_operational_library(_catalog_with_builtin_root(target_root))


def test_operational_library_reports_missing_prompt_binding(tmp_path: Path) -> None:
    source_catalog = load_resource_catalog()
    target_root = tmp_path / "resources"
    target_root.mkdir(parents=True)
    for path in source_catalog.root.rglob("*"):
        target_path = target_root / path.relative_to(source_catalog.root)
        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    prompt_path = target_root / "prompts" / "packs" / "default" / "runtime" / "session_bootstrap.md"
    prompt_path.unlink()

    report = inspect_builtin_operational_library(_catalog_with_builtin_root(target_root)).to_payload()

    assert report["valid"] is False
    assert any("session_bootstrap.md" in item for item in report["broken_references"])


def test_yaml_operational_library_cli_command_reports_builtins(cli_runner) -> None:
    result = cli_runner(["yaml", "operational-library"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["valid"] is True
    assert "default_runtime_policy.yaml" in payload["present"]["policies"]
    assert "session_defaults.yaml" in payload["present"]["runtime"]
