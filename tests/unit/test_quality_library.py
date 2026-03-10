from __future__ import annotations

from pathlib import Path

import pytest

from aicoding.quality_library import ensure_builtin_quality_library, inspect_builtin_quality_library
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


def test_builtin_quality_library_report_is_valid() -> None:
    report = inspect_builtin_quality_library(load_resource_catalog()).to_payload()

    assert report["valid"] is True
    assert report["missing_required"] == {
        "validations": [],
        "reviews": [],
        "testing": [],
        "docs": [],
    }
    assert "docs_quality_review.yaml" in report["present"]["reviews"]
    assert "pytest_suite.yaml" in report["present"]["testing"]
    assert "build_docs.yaml" in report["present"]["docs"]


def test_ensure_builtin_quality_library_rejects_missing_required_asset(tmp_path: Path) -> None:
    source_catalog = load_resource_catalog()
    target_root = tmp_path / "resources"
    target_root.mkdir(parents=True)
    for path in source_catalog.root.rglob("*"):
        target_path = target_root / path.relative_to(source_catalog.root)
        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    missing = target_root / "yaml" / "builtin" / "system-yaml" / "reviews" / "node_against_requirements.yaml"
    missing.unlink()

    with pytest.raises(ValueError, match="missing required reviews"):
        ensure_builtin_quality_library(_catalog_with_builtin_root(target_root))


def test_quality_library_reports_gate_order_breakage(tmp_path: Path) -> None:
    source_catalog = load_resource_catalog()
    target_root = tmp_path / "resources"
    target_root.mkdir(parents=True)
    for path in source_catalog.root.rglob("*"):
        target_path = target_root / path.relative_to(source_catalog.root)
        if path.is_dir():
            target_path.mkdir(parents=True, exist_ok=True)
        else:
            target_path.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")

    task_node = target_root / "yaml" / "builtin" / "system-yaml" / "nodes" / "task.yaml"
    task_node.write_text(
        "\n".join(
            [
                "node_definition:",
                "  id: task",
                "  kind: task",
                "  tier: 3",
                "  description: Broken order",
                "  main_prompt: prompts/execution/implement_leaf_task.md",
                "  entry_task: execute_node",
                "  available_tasks:",
                "    - execute_node",
                "    - review_node",
                "    - validate_node",
                "  parent_constraints:",
                "    allowed_kinds: [plan]",
                "    allowed_tiers: [2]",
                "    allow_parentless: false",
                "  child_constraints:",
                "    allowed_kinds: []",
                "    allowed_tiers: []",
                "    min_children: 0",
                "    max_children: 0",
                "  policies:",
                "    max_node_regenerations: 3",
                "    max_subtask_retries: 2",
                "    child_failure_threshold_total: 0",
                "    child_failure_threshold_consecutive: 0",
                "    child_failure_threshold_per_child: 0",
                "    require_review_before_finalize: false",
                "    require_testing_before_finalize: false",
                "    require_docs_before_finalize: false",
                "    auto_run_children: false",
                "    auto_rectify_upstream: false",
                "    auto_merge_to_parent: true",
                "    auto_merge_to_base: false",
                "  hooks: []",
            ]
        ),
        encoding="utf-8",
    )

    report = inspect_builtin_quality_library(_catalog_with_builtin_root(target_root)).to_payload()

    assert report["valid"] is False
    assert any("validate_node' must appear before 'review_node" in item for item in report["broken_references"])


def test_yaml_quality_library_cli_command_reports_builtins(cli_runner) -> None:
    result = cli_runner(["yaml", "quality-library"])
    payload = result.json()

    assert result.exit_code == 0
    assert payload["valid"] is True
    assert "node_against_requirements.yaml" in payload["present"]["reviews"]
    assert "default_unit_test_gate.yaml" in payload["present"]["testing"]
